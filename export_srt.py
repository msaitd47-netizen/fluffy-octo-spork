#!/usr/bin/env python3
"""
Export the same caption timing make_video.py computes (text-length weighted,
snapped to detected pauses in the audio) as an .srt subtitle file, so it can
be imported directly into an editor like CapCut and fine-tuned by hand
instead of built from scratch.

Usage:
    python3 export_srt.py --images ./images --audio ./voice.mp3 \
        --transcript ./transcript.txt --output captions.srt
"""
import argparse

from make_video import (
    compute_durations, detect_silences, distribute, ffprobe_duration,
    find_images, parse_transcript, snap_boundaries_to_silence, split_pages,
)


def srt_timestamp(seconds):
    ms = round(seconds * 1000)
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                  formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--images", required=True)
    ap.add_argument("--audio", required=True)
    ap.add_argument("--transcript", required=True)
    ap.add_argument("--output", default="captions.srt")
    ap.add_argument("--split-mode", choices=["paragraph", "sentence"], default="paragraph")
    ap.add_argument("--page-min-seconds", type=float, default=1.8)
    ap.add_argument("--equal-duration", action="store_true")
    ap.add_argument("--no-silence-align", action="store_true")
    ap.add_argument("--silence-noise-db", type=float, default=-30)
    ap.add_argument("--silence-min-duration", type=float, default=0.4)
    args = ap.parse_args()

    images = find_images(args.images)
    sections = parse_transcript(args.transcript, len(images))
    total_duration = ffprobe_duration(args.audio)
    section_durations = compute_durations(sections, total_duration, equal=args.equal_duration)

    pages_text = []
    durations = []
    for text, section_duration in zip(sections, section_durations):
        pages = split_pages(text, mode=args.split_mode)
        page_weights = [len(p) for p in pages]
        page_durations = distribute(page_weights, section_duration, args.page_min_seconds)
        pages_text.extend(pages)
        durations.extend(page_durations)

    if not args.no_silence_align:
        silences = detect_silences(args.audio, args.silence_noise_db, args.silence_min_duration)
        durations = snap_boundaries_to_silence(durations, silences)

    with open(args.output, "w", encoding="utf-8") as f:
        t = 0.0
        for i, (text, dur) in enumerate(zip(pages_text, durations), start=1):
            start, end = t, t + dur
            f.write(f"{i}\n{srt_timestamp(start)} --> {srt_timestamp(end)}\n{text}\n\n")
            t = end

    print(f"Wrote {len(pages_text)} subtitle entries to {args.output}")


if __name__ == "__main__":
    main()
