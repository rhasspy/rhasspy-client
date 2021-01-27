"""
Python library for interacting with a Rhasspy server over HTTP.

For more information on Rhasspy, please see:
https://rhasspy.readthedocs.io/
"""
import configparser
import io
import logging
import re
from collections import defaultdict
from typing import Any, Dict, List, Set, Tuple
from urllib.parse import urljoin

import aiohttp

from rhasspyclient.speech import Transcription, TranscriptionResult
from rhasspyclient.train import TrainingComplete, TrainingResult

_LOGGER = logging.getLogger(__name__)

# -----------------------------------------------------------------------------


class RhasspyClient:
    """Client object for remote Rhasspy server."""

    def __init__(self, api_url: str, session: aiohttp.ClientSession):
        self.api_url = api_url
        if not self.api_url.endswith("/"):
            self.api_url += "/"

        # Construct URLs for end-points
        self.sentences_url = urljoin(self.api_url, "sentences")
        self.custom_words_url = urljoin(self.api_url, "custom-words")
        self.slots_url = urljoin(self.api_url, "slots")
        self.train_url = urljoin(self.api_url, "train")
        self.stt_url = urljoin(self.api_url, "speech-to-text")
        self.intent_url = urljoin(self.api_url, "text-to-intent")
        self.tts_url = urljoin(self.api_url, "text-to-speech")
        self.restart_url = urljoin(self.api_url, "restart")
        self.wakeup_url = urljoin(self.api_url, "listen-for-command")
        self.profile_url = urljoin(self.api_url, "profile")
        self.lookup_url = urljoin(self.api_url, "lookup")
        self.version_url = urljoin(self.api_url, "version")

        self.session = session
        assert self.session is not None, "ClientSession is required"

    # -------------------------------------------------------------------------

    async def get_sentences(self) -> Dict[str, List[str]]:
        """GET sentences.ini from server. Return sentences grouped by intent."""
        async with self.session.get(self.sentences_url) as response:
            # Parse ini
            parser = configparser.ConfigParser(
                allow_no_value=True, strict=False, delimiters=["="]
            )

            # case sensitive
            parser.optionxform = str  # type: ignore
            parser.read_string(await response.text())

            # Group sentences by intent
            sentences: Dict[str, List[str]] = defaultdict(list)
            for intent_name in parser.sections():
                for key, value in parser[intent_name]:
                    if value is None:
                        # Sentence
                        sentences[intent_name].append(value)
                    else:
                        # Rule
                        sentences[intent_name].append(f"{key} = {value}")

            return sentences

    async def set_sentences(self, sentences: Dict[str, List[str]]) -> str:
        """POST sentences.ini to server from sentences grouped by intent."""
        with io.StringIO() as sentences_file:
            for intent_name in sorted(sentences):
                print(f"[{intent_name}]", file=sentences_file)
                for sentence in sorted(sentences[intent_name]):
                    if sentence.startswith("["):
                        # Escape initial [
                        sentence = "\\" + sentence

                    print(sentence.strip(), file=sentences_file)

                # Blank line
                print("", file=sentences_file)

            # POST to server
            async with self.session.post(
                self.sentences_url, data=sentences_file.getvalue()
            ) as response:
                response.raise_for_status()
                return await response.text()

    # -------------------------------------------------------------------------

    async def get_custom_words(self) -> Dict[str, Set[str]]:
        """GET custom words from server. Return pronunciations grouped by word."""
        async with self.session.get(self.custom_words_url) as response:
            # Group pronunciations by word
            pronunciations: Dict[str, Set[str]] = defaultdict(set)
            async for line_bytes in response.content:
                line = line_bytes.decode().strip()

                # Skip blank lines
                if len(line) == 0:
                    continue

                word, pronunciation = re.split(r"\s+", line, maxsplit=1)
                pronunciations[word].add(pronunciation)

            return pronunciations

    async def set_custom_words(self, pronunciations: Dict[str, Set[str]]) -> str:
        """POST custom words to server from pronunciations grouped by word."""
        with io.StringIO() as custom_words_file:
            for word in sorted(pronunciations):
                word_pronunciations = pronunciations[word]
                if isinstance(word_pronunciations, str):
                    word_pronunciations = [word_pronunciations]

                for pronunciation in sorted(word_pronunciations):
                    print(word, pronunciation, file=custom_words_file)

            # POST to server
            async with self.session.post(
                self.custom_words_url, data=custom_words_file.getvalue()
            ) as response:
                response.raise_for_status()
                return await response.text()

    # -------------------------------------------------------------------------

    async def train(self, no_cache=False) -> TrainingComplete:
        """Train Rhasspy profile. Delete doit database when no_cache is True."""
        params = {}
        if no_cache:
            params["no_cache"] = "true"

        async with self.session.post(self.train_url, params=params) as response:
            text = await response.text()

            try:
                response.raise_for_status()
                return TrainingComplete(result=TrainingResult.SUCCESS)
            except Exception:
                _LOGGER.exception("train")
                return TrainingComplete(result=TrainingResult.FAILURE, errors=text)

    # -------------------------------------------------------------------------

    async def speech_to_text(self, wav_data: bytes) -> Transcription:
        """Transcribe WAV audio."""
        headers = {"Content-Type": "audio/wav"}
        async with self.session.post(
            self.stt_url, headers=headers, data=wav_data
        ) as response:
            text = await response.text()

            try:
                response.raise_for_status()
                assert text
                return Transcription(result=TranscriptionResult.SUCCESS, text=text)
            except Exception:
                _LOGGER.exception("speech_to_text")
                return Transcription(result=TranscriptionResult.FAILURE)

    # -------------------------------------------------------------------------

    async def text_to_intent(
        self, text: str, handle_intent: bool = False
    ) -> Dict[str, Any]:
        """
        Recognize intent from text.

        If handle_intent is True, Rhasspy will forward to Home Assistant.
        """
        params = {"nohass": str(not handle_intent)}

        async with self.session.post(
            self.intent_url, params=params, data=text
        ) as response:
            response.raise_for_status()
            return await response.json()

    # -------------------------------------------------------------------------

    async def text_to_speech(self, text: str, repeat: bool = False) -> bytes:
        """
        Generate speech from text.

        If repeat is True, Rhasspy wil repeat the last spoken sentence.
        """
        params = {"repeat": str(repeat)}

        async with self.session.post(
            self.tts_url, params=params, data=text
        ) as response:
            response.raise_for_status()
            return await response.read()

    # -------------------------------------------------------------------------

    async def get_slots(self) -> Dict[str, List[str]]:
        """GET slots/values from server. Return values grouped by slot."""
        async with self.session.get(self.slots_url) as response:
            return await response.json()

    async def set_slots(self, slots: Dict[str, List[str]], overwrite=True) -> str:
        """
        POST slots/values to server as values grouped by slot.

        If overwrite is False, values are appended to existing slot.
        """
        params = {"overwrite_all": str(overwrite)}
        async with self.session.post(
            self.slots_url, params=params, json=slots
        ) as response:
            response.raise_for_status()
            return await response.text()

    # -------------------------------------------------------------------------

    async def restart(self) -> str:
        """Restart Rhasspy server."""
        async with self.session.post(self.restart_url) as response:
            response.raise_for_status()
            return await response.text()

    # -------------------------------------------------------------------------

    async def version(self) -> str:
        """Get Rhasspy version."""
        async with self.session.get(self.version_url) as response:
            response.raise_for_status()
            return await response.text()

    # -------------------------------------------------------------------------

    async def wakeup_and_wait(self, handle_intent=False) -> Dict[str, Any]:
        """
        Wake up Rhasspy so it starts listening for a voice command.

        If handle_intent is True, Rhasspy will forward to Home Assistant.
        """
        params = {"nohass": str(not handle_intent)}
        async with self.session.post(self.wakeup_url, params=params) as response:
            response.raise_for_status()
            return await response.json()

    # -------------------------------------------------------------------------

    async def get_profile(self, defaults=True) -> Dict[str, List[str]]:
        """GET current profile. Include default settings when defaults is True."""
        params = {"layers": "all" if defaults else "profile"}
        async with self.session.get(self.profile_url, params=params) as response:
            return await response.json()

    async def set_profile(self, profile: Dict[str, List[str]]) -> str:
        """
        POST slots/values to server as values grouped by slot.

        If overwrite is False, values are appended to existing slot.
        """
        async with self.session.post(self.profile_url, json=profile) as response:
            response.raise_for_status()
            return await response.text()

    # -------------------------------------------------------------------------

    async def get_pronunciations(self, word: str, n: int = 5) -> Tuple[bool, List[str]]:
        """
        Get pronunciations for a word.

        Returns if the word was in the dictionary and the pronunciations.
        """
        params = {"n": str(n)}
        async with self.session.post(
            self.lookup_url, params=params, data=word
        ) as response:
            response.raise_for_status()
            result = await response.json()
            return (result["in_dictionary"], result["pronunciations"])

    # -------------------------------------------------------------------------

    async def stream_to_text(self, raw_stream: aiohttp.StreamReader) -> str:
        """Stream raw 16-bit 16Khz mono audio to server. Return transcription."""
        params = {"noheader": "true"}
        async with self.session.post(
            self.stt_url, params=params, data=raw_stream
        ) as response:
            response.raise_for_status()
            return await response.text()
