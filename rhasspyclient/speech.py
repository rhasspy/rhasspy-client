"""
Data structures for speech to text.
"""
from enum import Enum

import attr


class TranscriptionResult(str, Enum):
    """Result of a transcription."""

    SUCCESS = "success"
    FAILURE = "failure"


@attr.s
class Transcription:
    """Output of speech to text."""

    result: TranscriptionResult = attr.ib()
    text: str = attr.ib(default="")
    likelihood: float = attr.ib(default=0)
    transcribe_seconds: float = attr.ib(default=0)
    wav_seconds: float = attr.ib(default=0)
