#!/usr/bin/env python3
"""
Get exact word-level timestamps for voice.mp3 by matching it against the
script text with ElevenLabs' Forced Alignment API. This replaces guessed/
silence-based timing with the real timing ElevenLabs itself computed.

Run this on YOUR OWN computer with YOUR OWN ElevenLabs API key — never
paste the key into chat. Get a key from https://elevenlabs.io (account
settings > API keys), then:

    pip install requests
    export ELEVENLABS_API_KEY=your_key_here      # macOS/Linux
    set ELEVENLABS_API_KEY=your_key_here          # Windows cmd
    $env:ELEVENLABS_API_KEY="your_key_here"       # Windows PowerShell

    python3 elevenlabs_align.py --audio voice.mp3 --transcript transcript.txt --output alignment.json

Then send the resulting alignment.json back so the video can be rebuilt
with exact timing instead of estimated/silence-snapped timing.
"""
import argparse
import json
import os
import re
import sys

import requests

API_URL = "https://api.elevenlabs.io/v1/forced-alignment"


def load_full_text(transcript_path):
    """Flatten transcript.txt (----separated sections, blank-line-separated
    paragraphs) back into the plain running text that was fed to the TTS
    engine, since that's what forced alignment needs to match against."""
    with open(transcript_path, "r", encoding="utf-8") as f:
        raw = f.read()
    sections = [s.strip() for s in re.split(r"\n\s*---\s*\n", raw.strip()) if s.strip()]
    parts = []
    for section in sections:
        paragraphs = [p.strip() for p in section.split("\n\n") if p.strip()]
        parts.append(" ".join(paragraphs))
    return " ".join(parts)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                  formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--audio", required=True)
    ap.add_argument("--transcript", required=True)
    ap.add_argument("--output", default="alignment.json")
    args = ap.parse_args()

    api_key = os.environ.get("ELEVENLABS_API_KEY")
    if not api_key:
        sys.exit("Set the ELEVENLABS_API_KEY environment variable first (see the "
                  "instructions at the top of this script).")

    text = load_full_text(args.transcript)
    print(f"Reference text: {len(text)} characters")

    with open(args.audio, "rb") as f:
        files = {"file": (os.path.basename(args.audio), f, "audio/mpeg")}
        data = {"text": text}
        headers = {"xi-api-key": api_key}
        print("Uploading audio + script to ElevenLabs for alignment "
              "(this can take a few minutes for a long file)...")
        resp = requests.post(API_URL, headers=headers, files=files, data=data, timeout=1200)

    if resp.status_code != 200:
        sys.exit(f"Request failed ({resp.status_code}): {resp.text[:2000]}\n\n"
                  f"If this mentions a file size/duration limit, tell me and I'll "
                  f"adapt the script to send the audio in per-section chunks instead.")

    result = resp.json()
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"\nSaved alignment to {args.output}")
    print("Top-level keys:", list(result.keys()))
    if "words" in result:
        print(f"{len(result['words'])} words aligned. First 5:")
        for w in result["words"][:5]:
            print(" ", w)
    if "characters" in result:
        print(f"{len(result['characters'])} characters aligned")


if __name__ == "__main__":
    main()
