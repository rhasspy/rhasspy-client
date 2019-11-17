"""
Command-line interface to RhasspyClient.

For more information on Rhasspy, please see:
https://rhasspy.readthedocs.io/
"""
import asyncio
import argparse
import json
import sys

import aiohttp

from rhasspyclient import RhasspyClient


async def main():
    parser = argparse.ArgumentParser(prog="rhasspyclient")
    parser.add_argument(
        "--api-url",
        default="http://localhost:12101/api",
        help="URL of Rhasspy server (with /api)",
    )

    sub_parsers = parser.add_subparsers()
    sub_parsers.required = True
    sub_parsers.dest = "command"

    # train
    train_parser = sub_parsers.add_parser("train", help="Train Rhasspy profile")
    train_parser.add_argument(
        "--no-cache", action="store_true", help="Clear cache before training"
    )
    train_parser.set_defaults(func=train)

    # speech-to-text
    speech_to_text_parser = sub_parsers.add_parser(
        "speech-to-text", help="Transcribe WAV file(s)"
    )
    speech_to_text_parser.add_argument("wavs", nargs="*", help="WAV file paths")
    speech_to_text_parser.set_defaults(func=speech_to_text)

    # stream-to-text
    stream_to_text_parser = sub_parsers.add_parser(
        "stream-to-text", help="Transcribe raw audio stream (16-bit 16Khz mono)"
    )
    stream_to_text_parser.add_argument(
        "--chunk-size",
        type=int,
        default=1024,
        help="Number of bytes to read/send at a time",
    )
    stream_to_text_parser.set_defaults(func=stream_to_text)

    # text-to-intent
    text_to_intent_parser = sub_parsers.add_parser(
        "text-to-intent", help="Recognize intent from text"
    )
    text_to_intent_parser.add_argument("text", nargs="*", help="Sentences to recognize")
    text_to_intent_parser.add_argument(
        "--handle", action="store_true", help="Handle intent"
    )
    text_to_intent_parser.set_defaults(func=text_to_intent)

    # Parse args
    args = parser.parse_args()

    # Begin client session
    async with aiohttp.ClientSession() as session:
        client = RhasspyClient(args.api_url, session)

        # Call sub-commmand
        await args.func(args, client)


# -----------------------------------------------------------------------------


async def train(args, client):
    result = await client.train(no_cache=args.no_cache)
    print(result)


async def speech_to_text(args, client):
    if len(args.wavs) > 0:
        for wav_path in args.wavs:
            with open(wav_path, "rb") as wav_file:
                result = await client.speech_to_text(wav_file.read())
                print(result)
    else:
        # WAV data from stdin
        result = await client.speech_to_text(sys.stdin.buffer.read())
        print(result)


async def stream_to_text(args, client):
    async def chunk_generator():
        chunk = sys.stdin.buffer.read(args.chunk_size)
        yield chunk
        while len(chunk) > 0:
            chunk = sys.stdin.buffer.read(args.chunk_size)
            yield chunk

    result = await client.stream_to_text(chunk_generator())
    print(result)


async def text_to_intent(args, client):
    if len(args.text) > 0:
        sentences = args.text
    else:
        sentences = sys.stdin

    for sentence in sentences:
        result = await client.text_to_intent(sentence, handle_intent=args.handle)
        print(json.dumps(result))


# -----------------------------------------------------------------------------

if __name__ == "__main__":
    asyncio.run(main())
