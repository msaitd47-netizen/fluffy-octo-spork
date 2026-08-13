#!/usr/bin/env python3
"""
Render a timing animatic for the cockroach birthday video.

This is not the finished video — it is a 9:16 previz pass that plays the
script at its real length (5 clips x 8 seconds) with the dialogue on screen
and a progress bar per clip, so the pacing can be judged before spending
generation credits in Flow/Veo.

Usage:
    python3 make_animatic.py --output bocek_animatic.mp4
"""
import argparse
import os
import shutil
import subprocess
import tempfile

from PIL import Image, ImageDraw, ImageFont

WIDTH, HEIGHT = 1080, 1920
FPS = 25
CLIP_SECONDS = 8

BG = (18, 20, 26)
MUTED = (122, 130, 148)
WHITE = (240, 243, 248)
BAR_BG = (38, 42, 52)

# Jersey-derived accent per character, brightened for a dark background.
FB = (255, 237, 0)       # lacivert-sarı
BJK = (238, 240, 245)    # siyah-beyaz
TS = (232, 74, 106)      # bordo-mavi

CLIPS = [
    {
        "shot": "GENİŞ PLAN → YAKINLAŞMA",
        "lines": [
            ("Sait", FB, "Nasıl gidiyor hayat?"),
            ("Mustafa", FB, "İyi ya, malum, memleketle uğraştık yine bugün."),
        ],
    },
    {
        "shot": "İKİLİ PLAN → SAĞA KAYDIRMA",
        "lines": [
            ("Afsan", FB, "Sweetie ile date vardı, oradan geliyorum."),
            ("Özcan", BJK, "Biz de hafta sonu konserdeydik ya, iyi dağıttık kafayı."),
        ],
    },
    {
        "shot": "YAKIN PLAN → GERİ ÇEKİLME",
        "lines": [
            ("Mete", TS, "Kankaaaa aynen, Salah gelince biz de kutlamaya çıktık."),
            (None, MUTED, "(dördü donar, sessizlik)"),
        ],
    },
    {
        "shot": "ORTA PLAN → SOLA WHIP PAN",
        "lines": [
            ("Tuna", BJK, "Olummmmm Vlahovic geldi, Trossard da var, "
                          "bu sene şampiyon Beşiktaş lan!"),
        ],
    },
    {
        "shot": "GENİŞ PLAN → KAMERAYA DÖNÜŞ",
        "lines": [
            (None, MUTED, "(hep birlikte kahkaha)"),
            ("Mustafa", FB, "Doğum günün kutlu olsun Arap!"),
        ],
    },
]

FONT_DIR = "/usr/share/fonts/truetype/dejavu"
FONT_BOLD = os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf")
FONT_REG = os.path.join(FONT_DIR, "DejaVuSans.ttf")


def wrap(draw, text, font, max_width):
    """Greedy word wrap to a pixel width."""
    words, lines, cur = text.split(), [], ""
    for w in words:
        trial = f"{cur} {w}".strip()
        if draw.textlength(trial, font=font) <= max_width or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def render_card(clip, index, total):
    """Draw the static part of one clip's card."""
    img = Image.new("RGB", (WIDTH, HEIGHT), BG)
    d = ImageDraw.Draw(img)

    f_label = ImageFont.truetype(FONT_BOLD, 34)
    f_shot = ImageFont.truetype(FONT_REG, 38)
    f_name = ImageFont.truetype(FONT_BOLD, 44)
    f_line = ImageFont.truetype(FONT_BOLD, 66)

    margin = 90
    max_w = WIDTH - 2 * margin

    d.text((margin, 130), f"KLİP {index + 1} / {total}", font=f_label, fill=MUTED)
    d.text((margin, 190), clip["shot"], font=f_shot, fill=(90, 98, 116))

    # Dialogue block, vertically centred as a whole.
    blocks = []
    for name, color, text in clip["lines"]:
        lines = wrap(d, text, f_line, max_w)
        height = len(lines) * 84 + (58 if name else 0)
        blocks.append((name, color, lines, height))

    total_h = sum(b[3] for b in blocks) + 70 * (len(blocks) - 1)
    y = (HEIGHT - total_h) // 2

    for name, color, lines, height in blocks:
        if name:
            d.text((margin, y), name.upper(), font=f_name, fill=color)
            y += 58
        for line in lines:
            d.text((margin, y), line, font=f_line,
                   fill=WHITE if name else MUTED)
            y += 84
        y += 70

    return img


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output", default="bocek_animatic.mp4")
    ap.add_argument("--seconds", type=float, default=CLIP_SECONDS)
    args = ap.parse_args()

    if not shutil.which("ffmpeg"):
        raise SystemExit("ffmpeg bulunamadı, PATH'e ekleyin.")

    tmp = tempfile.mkdtemp(prefix="animatic_")
    frames_per_clip = int(round(args.seconds * FPS))
    bar_y, bar_h = HEIGHT - 150, 10
    frame_no = 0

    try:
        for i, clip in enumerate(CLIPS):
            card = render_card(clip, i, len(CLIPS))
            for f in range(frames_per_clip):
                frame = card.copy()
                d = ImageDraw.Draw(frame)
                d.rectangle([90, bar_y, WIDTH - 90, bar_y + bar_h], fill=BAR_BG)
                filled = (WIDTH - 180) * (f + 1) / frames_per_clip
                d.rectangle([90, bar_y, 90 + filled, bar_y + bar_h], fill=WHITE)
                frame.save(os.path.join(tmp, f"{frame_no:06d}.png"))
                frame_no += 1

        subprocess.run([
            "ffmpeg", "-y", "-framerate", str(FPS),
            "-i", os.path.join(tmp, "%06d.png"),
            "-c:v", "libx264", "-crf", "20", "-pix_fmt", "yuv420p",
            args.output,
        ], check=True, capture_output=True)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    total = len(CLIPS) * args.seconds
    print(f"{args.output} yazıldı — {len(CLIPS)} klip, {total:.0f} saniye.")


if __name__ == "__main__":
    main()
