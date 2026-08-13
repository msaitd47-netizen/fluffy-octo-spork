#!/usr/bin/env python3
"""
Render the cockroach birthday video as a hand-drawn cartoon.

Everything here is generated locally: the characters are drawn with Pillow,
the animation is computed per frame, and the Turkish dialogue is synthesised
with espeak-ng. This is not the photoreal Veo/Flow look the prompts in
bocek_script_01.md target — it is a complete, finished version of the same
script that can be produced without an AI video model.

Requires: ffmpeg, espeak-ng, Pillow.

Usage:
    python3 make_cartoon.py --output bocek_cizgifilm.mp4
"""
import argparse
import math
import os
import shutil
import subprocess
import tempfile

from PIL import Image, ImageDraw, ImageFont

WIDTH, HEIGHT = 1920, 1080
FPS = 25
GROUND_Y = 760          # counter surface the cockroaches stand on

# ---------------------------------------------------------------- palette
NIGHT_TOP = (32, 36, 52)
NIGHT_BOT = (58, 50, 60)
COUNTER = (108, 84, 64)
COUNTER_EDGE = (74, 56, 42)
LAMP = (255, 214, 150)
SHELL = (108, 74, 46)
SHELL_DARK = (74, 50, 30)
WHITE = (242, 245, 250)
MUTED = (150, 158, 175)

FB = [(20, 38, 80), (255, 237, 0)]        # lacivert - sarı
BJK = [(22, 24, 30), (238, 240, 245)]     # siyah - beyaz
TS = [(139, 30, 63), (27, 58, 139)]       # bordo - mavi

NAME_COLOR = {"Sait": FB[1], "Mustafa": FB[1], "Afsan": FB[1],
              "Özcan": BJK[1], "Mete": (232, 74, 106), "Tuna": BJK[1]}

FONT_DIR = "/usr/share/fonts/truetype/dejavu"
F_BOLD = os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf")

# ------------------------------------------------------------- characters
# x is the standing position; entrance characters get theirs from the scene.
CHARS = {
    "Sait":    dict(x=470, scale=1.18, wide=1.05, team=FB,  phase=0.0,
                    chipped=True, armband=True),
    "Mustafa": dict(x=750, scale=1.02, wide=1.30, team=FB,  phase=1.1,
                    headband=True, moustache=True),
    "Afsan":   dict(x=1020, scale=0.82, wide=0.95, team=FB, phase=2.2,
                    long_antennae=True, cap=True),
    "Özcan":   dict(x=1300, scale=1.10, wide=0.82, team=BJK, phase=3.0,
                    scar=True),
    "Mete":    dict(x=1580, scale=0.92, wide=1.25, team=TS, phase=4.1,
                    shades=True),
    "Tuna":    dict(x=185, scale=0.86, wide=0.98, team=BJK, phase=5.2,
                    glossy=True),
}

# ------------------------------------------------------------------ script
# (start_second, speaker, text). Durations come from the synthesised audio.
SCRIPT = [
    (0.9,  "Sait",    "Nasıl gidiyor hayat?"),
    (3.9,  "Mustafa", "İyi ya, malum, memleketle uğraştık yine bugün."),
    (8.7,  "Afsan",   "Sweetie ile date vardı, oradan geliyorum."),
    (12.4, "Özcan",   "Biz de hafta sonu konserdeydik ya, iyi dağıttık kafayı."),
    (16.7, "Mete",    "Kankaaaa aynen, Salah gelince biz de kutlamaya çıktık."),
    (25.0, "Tuna",    "Olummmmm Vlahovic geldi, Trossard da var, "
                      "bu sene şampiyon Beşiktaş lan!"),
    (32.4, "HERKES",  "Hahahaha! Hahaha!"),
    (35.6, "Mustafa", "Doğum günün kutlu olsun Arap!"),
]

TOTAL = 40.0
TUNA_ENTERS = 24.2      # slides in from the left edge
LAUGH_START, LAUGH_END = 32.2, 35.2


# ------------------------------------------------------------------ helpers
def lerp(a, b, t):
    return a + (b - a) * max(0.0, min(1.0, t))


def background():
    """Pre-render the night kitchen counter once."""
    img = Image.new("RGB", (WIDTH, HEIGHT), NIGHT_TOP)
    d = ImageDraw.Draw(img)

    for y in range(HEIGHT):
        t = y / HEIGHT
        d.line([(0, y), (WIDTH, y)],
               fill=tuple(int(lerp(NIGHT_TOP[i], NIGHT_BOT[i], t)) for i in range(3)))

    # warm pool of light from an off-screen lamp
    glow = Image.new("RGB", (WIDTH, HEIGHT), (0, 0, 0))
    gd = ImageDraw.Draw(glow)
    for r in range(30, 0, -1):
        k = r / 30
        gd.ellipse([WIDTH // 2 - 900 * k, GROUND_Y - 620 * k,
                    WIDTH // 2 + 900 * k, GROUND_Y + 320 * k],
                   fill=tuple(int(c * 0.09) for c in LAMP))
    img = Image.blend(img, glow, 0.42)
    d = ImageDraw.Draw(img)

    # backsplash tile lines, only just visible
    for x in range(0, WIDTH, 160):
        d.line([(x, 0), (x, GROUND_Y)], fill=(44, 48, 64), width=2)
    for y in range(0, GROUND_Y, 160):
        d.line([(0, y), (WIDTH, y)], fill=(44, 48, 64), width=2)

    # teapot silhouette, kept clear of Mete at the right end of the row
    d.ellipse([1772, GROUND_Y - 150, 1898, GROUND_Y - 54], fill=(58, 48, 56))
    d.ellipse([1794, GROUND_Y - 210, 1878, GROUND_Y - 144], fill=(66, 55, 63))
    d.polygon([(1896, GROUND_Y - 126), (1920, GROUND_Y - 108),
               (1896, GROUND_Y - 88)], fill=(58, 48, 56))

    # counter
    d.rectangle([0, GROUND_Y, WIDTH, HEIGHT], fill=COUNTER)
    d.rectangle([0, GROUND_Y, WIDTH, GROUND_Y + 10], fill=COUNTER_EDGE)
    return img


def tea_glass(d, x, y, s=1.0):
    """A tiny tulip-shaped tea glass."""
    w, h = 16 * s, 30 * s
    d.polygon([(x - w, y - h), (x - w * 0.55, y), (x + w * 0.55, y),
               (x + w, y - h)], fill=(196, 108, 44))
    d.ellipse([x - w * 1.5, y, x + w * 1.5, y + 7 * s], fill=(210, 210, 214))


def draw_char(img, ch, name, t, state, x_override=None, alpha_fade=1.0):
    """Draw one cockroach at time t. state: idle | speak | laugh | frozen."""
    d = ImageDraw.Draw(img)
    s = ch["scale"]
    x = ch["x"] if x_override is None else x_override

    bw, bh = 150 * s * ch["wide"], 112 * s
    if state == "laugh":
        bob = math.sin(t * 15 + ch["phase"]) * 13 * s
        lean = math.sin(t * 15 + ch["phase"]) * 6
    elif state == "frozen":
        bob, lean = 0.0, 0.0
    else:
        bob = math.sin(t * 2.6 + ch["phase"]) * 4 * s
        lean = 0.0
    if state == "speak":
        bob += math.sin(t * 9) * 2.5 * s

    cy = GROUND_Y - bh / 2 - 16 * s + bob
    left, right = x - bw / 2, x + bw / 2
    top, bot = cy - bh / 2, cy + bh / 2

    # legs
    leg_c = SHELL_DARK
    for i, ly in enumerate((-0.25, 0.05, 0.35)):
        sway = math.sin(t * (5 if state == "laugh" else 2.2) + i + ch["phase"]) * 5
        for sgn in (-1, 1):
            x0 = x + sgn * bw * 0.36
            y0 = cy + bh * ly
            d.line([(x0, y0), (x0 + sgn * (34 * s + sway), y0 + 40 * s)],
                   fill=leg_c, width=max(3, int(6 * s)))
            d.line([(x0 + sgn * (34 * s + sway), y0 + 40 * s),
                    (x0 + sgn * (44 * s + sway), GROUND_Y)],
                   fill=leg_c, width=max(3, int(5 * s)))

    # shell with jersey stripes, masked to the body ellipse
    body = Image.new("RGBA", (int(bw), int(bh)), (0, 0, 0, 0))
    bd = ImageDraw.Draw(body)
    bd.rectangle([0, 0, bw, bh], fill=SHELL + (255,))
    stripe_w = max(10, int(bw / 7))
    for i, sx in enumerate(range(0, int(bw), stripe_w)):
        bd.rectangle([sx, bh * 0.18, sx + stripe_w, bh],
                     fill=ch["team"][i % 2] + (255,))
    mask = Image.new("L", (int(bw), int(bh)), 0)
    ImageDraw.Draw(mask).ellipse([0, 0, bw - 1, bh - 1], fill=255)
    img.paste(body, (int(left), int(top)), mask)
    d.ellipse([left, top, right, bot], outline=SHELL_DARK, width=max(2, int(3 * s)))

    if ch.get("glossy"):
        d.ellipse([left + bw * 0.16, top + bh * 0.12,
                   left + bw * 0.40, top + bh * 0.30], fill=(255, 255, 255, 90))
    if ch.get("scar"):
        d.line([(left + bw * 0.28, top + bh * 0.55),
                (left + bw * 0.62, top + bh * 0.38)],
               fill=(198, 176, 160), width=max(2, int(3 * s)))

    # head
    hw, hh = bw * 0.52, bh * 0.46
    hx, hy = x + lean, top - hh * 0.42
    d.ellipse([hx - hw / 2, hy - hh / 2, hx + hw / 2, hy + hh / 2], fill=SHELL)
    d.ellipse([hx - hw / 2, hy - hh / 2, hx + hw / 2, hy + hh / 2],
              outline=SHELL_DARK, width=max(2, int(3 * s)))

    # antennae
    a_len = (95 if ch.get("long_antennae") else 66) * s
    for sgn in (-1, 1):
        wig = math.sin(t * 3.4 + ch["phase"] + sgn) * 12
        length = a_len * (0.55 if (ch.get("chipped") and sgn < 0) else 1.0)
        d.line([(hx + sgn * hw * 0.24, hy - hh * 0.36),
                (hx + sgn * hw * 0.6 + wig, hy - hh * 0.36 - length)],
               fill=SHELL_DARK, width=max(2, int(4 * s)))

    # eyes
    ew = hw * 0.19
    for sgn in (-1, 1):
        ex = hx + sgn * hw * 0.23
        ey = hy - hh * 0.08
        d.ellipse([ex - ew, ey - ew, ex + ew, ey + ew], fill=WHITE)
        squint = 0.45 if state == "laugh" else 1.0
        pr = ew * 0.55 * squint
        d.ellipse([ex - pr, ey - pr, ex + pr, ey + pr], fill=(20, 20, 26))

    # mouth
    if state == "speak":
        open_h = (0.5 + 0.5 * abs(math.sin(t * 17))) * hh * 0.30
    elif state == "laugh":
        open_h = hh * 0.32
    else:
        open_h = hh * 0.05
    d.ellipse([hx - hw * 0.19, hy + hh * 0.16,
               hx + hw * 0.19, hy + hh * 0.16 + open_h], fill=(46, 22, 22))

    # accessories
    if ch.get("headband"):
        d.rectangle([hx - hw * 0.52, hy - hh * 0.40,
                     hx + hw * 0.52, hy - hh * 0.22], fill=(220, 60, 70))
    if ch.get("cap"):
        d.pieslice([hx - hw * 0.55, hy - hh * 0.78,
                    hx + hw * 0.55, hy + hh * 0.10], 180, 360, fill=(40, 46, 62))
        d.rectangle([hx + hw * 0.40, hy - hh * 0.40,
                     hx + hw * 0.95, hy - hh * 0.26], fill=(40, 46, 62))
    if ch.get("shades"):
        d.rounded_rectangle([hx - hw * 0.48, hy - hh * 0.52,
                             hx + hw * 0.48, hy - hh * 0.28],
                            radius=int(6 * s), fill=(24, 24, 30))
    if ch.get("moustache"):
        d.line([(hx - hw * 0.26, hy + hh * 0.13),
                (hx + hw * 0.26, hy + hh * 0.13)],
               fill=SHELL_DARK, width=max(3, int(6 * s)))
    if ch.get("armband"):
        # captain's band, sitting inside the shell outline so it reads as a
        # patch rather than a rectangle poking out of the body
        d.rounded_rectangle([x - bw * 0.40, cy - bh * 0.26,
                             x - bw * 0.25, cy - bh * 0.04],
                            radius=int(4 * s), fill=(240, 208, 48))


def caption(img, speaker, text):
    d = ImageDraw.Draw(img)
    f_name = ImageFont.truetype(F_BOLD, 34)
    f_line = ImageFont.truetype(F_BOLD, 52)

    words, lines, cur = text.split(), [], ""
    for w in words:
        trial = f"{cur} {w}".strip()
        if d.textlength(trial, font=f_line) <= WIDTH - 300 or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)

    box_h = len(lines) * 62 + 78
    d.rectangle([0, HEIGHT - box_h, WIDTH, HEIGHT], fill=(10, 11, 16))
    y = HEIGHT - box_h + 20
    if speaker != "HERKES":
        d.text((150, y), speaker.upper(), font=f_name,
               fill=NAME_COLOR.get(speaker, MUTED))
    y += 46
    for line in lines:
        d.text((150, y), line, font=f_line, fill=WHITE)
        y += 62


def synthesise(tmp):
    """espeak-ng one wav per line; returns [(start, end, speaker, text, path)]."""
    out = []
    for i, (start, speaker, text) in enumerate(SCRIPT):
        path = os.path.join(tmp, f"line{i}.wav")
        pitch = "70" if speaker == "HERKES" else "45"
        subprocess.run(["espeak-ng", "-v", "tr", "-s", "148", "-p", pitch,
                        "-w", path, text], check=True, capture_output=True)
        dur = float(subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "csv=p=0", path],
            check=True, capture_output=True, text=True).stdout.strip())
        out.append((start, start + dur, speaker, text, path))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output", default="bocek_cizgifilm.mp4")
    args = ap.parse_args()

    for tool in ("ffmpeg", "espeak-ng"):
        if not shutil.which(tool):
            raise SystemExit(f"{tool} bulunamadı.")

    tmp = tempfile.mkdtemp(prefix="cartoon_")
    try:
        timed = synthesise(tmp)
        bg = background()
        frames = int(TOTAL * FPS)

        for f in range(frames):
            t = f / FPS
            img = bg.copy()
            d = ImageDraw.Draw(img)

            active = next(((s, e, sp, tx) for s, e, sp, tx, _ in timed
                           if s <= t <= e), None)
            laughing = LAUGH_START <= t <= LAUGH_END

            for name, ch in CHARS.items():
                if name == "Tuna":
                    if t < TUNA_ENTERS:
                        continue
                    slide = min(1.0, (t - TUNA_ENTERS) / 0.8)
                    x = lerp(-160, ch["x"], slide)
                else:
                    x = None

                if laughing:
                    state = "laugh"
                elif active and active[2] == name:
                    state = "speak"
                elif LAUGH_START - 1.6 < t < LAUGH_START and name != "Mete":
                    state = "frozen"
                else:
                    state = "idle"
                draw_char(img, ch, name, t, state, x_override=x)

            for name, ch in CHARS.items():
                if name == "Tuna" and t < TUNA_ENTERS:
                    continue
                tea_glass(d, ch["x"] + 74 * ch["scale"], GROUND_Y + 26,
                          ch["scale"])

            if active:
                caption(img, active[2], active[3])

            img.save(os.path.join(tmp, f"{f:05d}.png"))

        # audio: place each line at its start offset and mix
        inputs, filters, labels = [], [], []
        for i, (start, _e, _sp, _tx, path) in enumerate(timed):
            inputs += ["-i", path]
            # input 0 is the PNG sequence, so audio inputs start at 1
            filters.append(f"[{i + 1}:a]adelay={int(start * 1000)}|"
                           f"{int(start * 1000)}[a{i}]")
            labels.append(f"[a{i}]")
        mix = (";".join(filters) + ";" + "".join(labels) +
               f"amix=inputs={len(timed)}:normalize=0,"
               f"apad,atrim=0:{TOTAL}[aout]")

        subprocess.run(
            ["ffmpeg", "-y", "-framerate", str(FPS),
             "-i", os.path.join(tmp, "%05d.png")] + inputs +
            ["-filter_complex", mix, "-map", "0:v", "-map", "[aout]",
             "-c:v", "libx264", "-crf", "19", "-pix_fmt", "yuv420p",
             "-c:a", "aac", "-shortest", args.output],
            check=True, capture_output=True)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print(f"{args.output} yazıldı — {TOTAL:.0f} saniye, sesli.")


if __name__ == "__main__":
    main()
