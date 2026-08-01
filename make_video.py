#!/usr/bin/env python3
"""
Assemble a narrated slideshow video from a voice track, a folder of images,
and a transcript file.

Each image is shown for a portion of the audio's runtime (weighted by how
much transcript text belongs to it, so longer sections stay on screen
longer), with the matching transcript text burned in as bold captions over
a dark gradient, similar to a narrated history/explainer video.

A section can contain much more text than fits in one caption (e.g. a whole
chapter of narration for a single image, when you don't have an image per
sentence). In that case the image stays on screen for the whole section,
but the caption text is split into pages (by paragraph by default, or by
sentence with --split-mode sentence) that advance every few seconds in sync
with the section's runtime, like subtitles over a still photo.

Usage:
    python3 make_video.py \
        --images ./images \
        --audio ./voice.mp3 \
        --transcript ./transcript.txt \
        --output ./output.mp4

Transcript format:
    One section per image, in the same order as the sorted image files,
    separated by a line containing only "---". Blank lines inside a
    section become paragraph breaks on screen.

        He migrated with his wife Ruqayyah, the daughter of the
        Prophet Muhammad.

        Their migration showed the cost of faith.
        ---
        Next image's caption text...
        ---
        ...
"""
import argparse
import bisect
import glob
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

from PIL import Image, ImageDraw, ImageFont, ImageFilter

DEFAULT_FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
IMAGE_EXTS = (".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tif", ".tiff")


def natural_key(path):
    name = os.path.basename(path)
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r"(\d+)", name)]


def find_images(images_dir):
    files = [
        p for p in glob.glob(os.path.join(images_dir, "*"))
        if os.path.splitext(p)[1].lower() in IMAGE_EXTS
    ]
    if not files:
        sys.exit(f"No images found in {images_dir}")
    return sorted(files, key=natural_key)


def parse_transcript(path, expected_count):
    with open(path, "r", encoding="utf-8") as f:
        raw = f.read()
    sections = [s.strip() for s in re.split(r"\n\s*---\s*\n", raw.strip())]
    sections = [s for s in sections if s]
    if len(sections) != expected_count:
        sys.exit(
            f"Transcript has {len(sections)} section(s) separated by '---' "
            f"but there are {expected_count} image(s). Each image needs exactly "
            f"one transcript section, separated by a line containing only '---'."
        )
    return sections


def ffprobe_duration(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "json", path],
        capture_output=True, text=True, check=True,
    )
    return float(json.loads(out.stdout)["format"]["duration"])


def distribute(weights, total, min_each):
    """Split `total` seconds across items proportional to `weights`, while
    keeping every item at least `min_each` seconds (falls back to an even
    split if there isn't enough total time to honor the minimum)."""
    n = len(weights)
    if total is None:
        return [4.0] * n
    if n * min_each >= total:
        return [total / n] * n
    weights = [max(w, 1) for w in weights]
    total_weight = sum(weights)
    durations = [total * w / total_weight for w in weights]
    deficits = [max(0.0, min_each - d) for d in durations]
    if any(deficits):
        extra_needed = sum(deficits)
        flexible = [max(0.0, d - min_each) for d in durations]
        flexible_total = sum(flexible) or 1.0
        durations = [
            min_each + d if deficit > 0
            else max(min_each, d - extra_needed * (d / flexible_total))
            for d, deficit in zip(durations, deficits)
        ]
    return durations


def compute_durations(sections, total_duration, equal=False, min_seconds=2.0):
    n = len(sections)
    if equal or total_duration is None:
        base = (total_duration / n) if total_duration else 4.0
        return [base] * n
    weights = [len(s) for s in sections]
    return distribute(weights, total_duration, min_seconds)


def detect_silences(audio_path, noise_db=-30, min_duration=0.4):
    """Find natural pauses in the narration via ffmpeg's silencedetect filter.
    Returns a list of (start, end) times in seconds."""
    proc = subprocess.run(
        ["ffmpeg", "-i", audio_path, "-af",
         f"silencedetect=noise={noise_db}dB:d={min_duration}", "-f", "null", "-"],
        capture_output=True, text=True,
    )
    starts = [float(m) for m in re.findall(r"silence_start:\s*([\d.]+)", proc.stderr)]
    ends = [float(m) for m in re.findall(r"silence_end:\s*([\d.]+)", proc.stderr)]
    return list(zip(starts, ends))


def snap_boundaries_to_silence(durations, silences, max_window=5.0, min_window=0.75):
    """Nudge each caption's cumulative end time onto the nearest detected
    pause in the audio, so captions change where the narrator actually
    pauses instead of at a length-estimated instant. The very last boundary
    (end of the whole track) is left untouched."""
    if not silences:
        return durations
    silence_mids = sorted((s + e) / 2 for s, e in silences)

    cum = []
    total = 0.0
    for d in durations:
        total += d
        cum.append(total)

    snapped = 0
    adjusted = list(cum)
    for i in range(len(adjusted) - 1):
        naive = cum[i]
        window = min(max_window, max(min_window, 0.5 * min(durations[i], durations[i + 1])))
        lo = bisect.bisect_left(silence_mids, naive - window)
        hi = bisect.bisect_right(silence_mids, naive + window)
        candidates = silence_mids[lo:hi]
        if candidates:
            adjusted[i] = min(candidates, key=lambda m: abs(m - naive))
            snapped += 1

    for i in range(1, len(adjusted)):
        if adjusted[i] < adjusted[i - 1]:
            adjusted[i] = adjusted[i - 1]
    adjusted[-1] = cum[-1]

    print(f"Silence alignment: snapped {snapped}/{len(adjusted) - 1} caption boundaries "
          f"to a detected pause (of {len(silences)} pauses found).")

    new_durations = []
    prev = 0.0
    for b in adjusted:
        new_durations.append(max(0.05, b - prev))
        prev = b
    return new_durations


SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?…])\s+(?=[A-ZÇĞİÖŞÜ0-9])")


def split_pages(text, mode="paragraph"):
    """Split one section's text into on-screen caption pages."""
    if mode == "sentence":
        pages = []
        for paragraph in text.split("\n\n"):
            pages.extend(s.strip() for s in SENTENCE_SPLIT_RE.split(paragraph.strip()) if s.strip())
        return pages or [text.strip()]
    pages = [p.strip() for p in text.split("\n\n") if p.strip()]
    return pages or [text.strip()]


def wrap_text(draw, text, font, max_width):
    lines = []
    for paragraph in text.split("\n\n"):
        words = paragraph.split()
        if not words:
            lines.append("")
            continue
        current = words[0]
        for word in words[1:]:
            candidate = f"{current} {word}"
            if draw.textbbox((0, 0), candidate, font=font)[2] <= max_width:
                current = candidate
            else:
                lines.append(current)
                current = word
        lines.append(current)
        lines.append("")  # paragraph gap
    while lines and lines[-1] == "":
        lines.pop()
    return lines


def render_caption_frame(image_path, text, out_path, width, height, font_path,
                          font_size, margin, text_color, gradient_height_frac):
    img = Image.open(image_path).convert("RGB")

    # Cover-fit crop to target aspect ratio.
    src_w, src_h = img.size
    target_ratio = width / height
    src_ratio = src_w / src_h
    if src_ratio > target_ratio:
        new_w = int(src_h * target_ratio)
        x0 = (src_w - new_w) // 2
        img = img.crop((x0, 0, x0 + new_w, src_h))
    else:
        new_h = int(src_w / target_ratio)
        y0 = (src_h - new_h) // 2
        img = img.crop((0, y0, src_w, y0 + new_h))
    img = img.resize((width, height), Image.LANCZOS)

    # Dark gradient at the top so white text stays readable on any photo.
    gradient_h = int(height * gradient_height_frac)
    gradient = Image.new("L", (1, gradient_h), color=0)
    for y in range(gradient_h):
        alpha = int(200 * (1 - y / gradient_h))
        gradient.putpixel((0, y), alpha)
    gradient = gradient.resize((width, gradient_h))
    overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    black = Image.new("RGBA", (width, gradient_h), (0, 0, 0, 255))
    black.putalpha(gradient)
    overlay.paste(black, (0, 0), black)
    img = Image.alpha_composite(img.convert("RGBA"), overlay)

    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(font_path, font_size)
    max_width = width - 2 * margin
    lines = wrap_text(draw, text, font, max_width)

    line_height = int(font_size * 1.25)
    y = margin
    for line in lines:
        if line:
            # Soft shadow for extra contrast.
            draw.text((margin + 2, y + 2), line, font=font, fill=(0, 0, 0, 160))
            draw.text((margin, y), line, font=font, fill=text_color)
        y += line_height

    img.convert("RGB").save(out_path, quality=95)


def build_video(frame_paths, durations, audio_path, output_path, fps, width, height):
    work_dir = os.path.dirname(frame_paths[0])
    concat_list = os.path.join(work_dir, "concat.txt")
    with open(concat_list, "w") as f:
        for path, dur in zip(frame_paths, durations):
            f.write(f"file '{os.path.abspath(path)}'\n")
            f.write(f"duration {dur:.3f}\n")
        # ffmpeg's concat demuxer ignores the duration of the final entry
        # unless the file is listed once more without a duration.
        f.write(f"file '{os.path.abspath(frame_paths[-1])}'\n")

    silent_video = os.path.join(work_dir, "silent.mp4")
    subprocess.run(
        ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat_list,
         "-vsync", "vfr", "-pix_fmt", "yuv420p",
         "-vf", f"scale={width}:{height},fps={fps}",
         silent_video],
        check=True,
    )

    cmd = ["ffmpeg", "-y", "-i", silent_video]
    if audio_path:
        cmd += ["-i", audio_path, "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                "-shortest", output_path]
    else:
        cmd += ["-c:v", "copy", output_path]
    subprocess.run(cmd, check=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                  formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--images", required=True, help="Folder of images (one per transcript section)")
    ap.add_argument("--audio", help="Voice/narration audio file (mp3, wav, m4a, ...)")
    ap.add_argument("--transcript", required=True, help="Transcript text file, sections separated by '---'")
    ap.add_argument("--output", default="output.mp4", help="Output video path")
    ap.add_argument("--width", type=int, default=1920)
    ap.add_argument("--height", type=int, default=1080)
    ap.add_argument("--fps", type=int, default=25)
    ap.add_argument("--font", default=DEFAULT_FONT)
    ap.add_argument("--font-size", type=int, default=48)
    ap.add_argument("--margin", type=int, default=70)
    ap.add_argument("--text-color", default="255,255,255", help="R,G,B")
    ap.add_argument("--gradient-height", type=float, default=0.55,
                     help="Fraction of frame height covered by the readability gradient")
    ap.add_argument("--equal-duration", action="store_true",
                     help="Give every image the same on-screen time instead of weighting by caption length")
    ap.add_argument("--split-mode", choices=["paragraph", "sentence"], default="paragraph",
                     help="How to page a section's text across its image's on-screen time "
                          "when the section has more than one paragraph/sentence")
    ap.add_argument("--page-min-seconds", type=float, default=1.8,
                     help="Minimum time each caption page stays on screen within its image's duration")
    ap.add_argument("--no-silence-align", action="store_true",
                     help="Don't nudge caption timing onto detected pauses in the audio; "
                          "use pure text-length-proportional timing")
    ap.add_argument("--silence-noise-db", type=float, default=-30,
                     help="Threshold (dB) below which audio is considered silent, for pause detection")
    ap.add_argument("--silence-min-duration", type=float, default=0.4,
                     help="Minimum length (seconds) of a gap to count as a pause")
    ap.add_argument("--keep-temp", action="store_true", help="Keep the rendered frame images for inspection")
    args = ap.parse_args()

    if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
        sys.exit("ffmpeg/ffprobe not found on PATH. Install ffmpeg first.")
    if not os.path.exists(args.font):
        sys.exit(f"Font not found: {args.font}. Pass --font with a path to a .ttf file.")

    images = find_images(args.images)
    sections = parse_transcript(args.transcript, len(images))
    total_duration = ffprobe_duration(args.audio) if args.audio else None
    section_durations = compute_durations(sections, total_duration, equal=args.equal_duration)
    text_color = tuple(int(c) for c in args.text_color.split(","))

    # Build the full flat sequence of (image, caption page) pairs with their
    # text-length-proportional durations first, then optionally correct that
    # timing against real pauses in the audio before rendering anything.
    frame_specs = []  # (image_path, page_text)
    durations = []
    for image_path, text, section_duration in zip(images, sections, section_durations):
        pages = split_pages(text, mode=args.split_mode)
        page_weights = [len(p) for p in pages]
        page_durations = distribute(page_weights, section_duration, args.page_min_seconds)
        for page_text, page_duration in zip(pages, page_durations):
            frame_specs.append((image_path, page_text))
            durations.append(page_duration)

    if args.audio and not args.no_silence_align:
        silences = detect_silences(args.audio, args.silence_noise_db, args.silence_min_duration)
        durations = snap_boundaries_to_silence(durations, silences)

    temp_dir = tempfile.mkdtemp(prefix="make_video_")
    frame_paths = []
    try:
        for idx, ((image_path, page_text), duration) in enumerate(zip(frame_specs, durations)):
            out_path = os.path.join(temp_dir, f"frame_{idx:04d}.jpg")
            render_caption_frame(
                image_path, page_text, out_path, args.width, args.height,
                args.font, args.font_size, args.margin, text_color,
                args.gradient_height,
            )
            frame_paths.append(out_path)
            print(f"[{idx + 1}/{len(frame_specs)}] {os.path.basename(image_path)} -> "
                  f"{duration:.1f}s: {page_text.splitlines()[0][:60]}...")

        build_video(frame_paths, durations, args.audio, args.output,
                    args.fps, args.width, args.height)
        print(f"\nDone: {args.output}")
    finally:
        if args.keep_temp:
            print(f"Frames kept at: {temp_dir}")
        else:
            shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    main()
