# make_video.py

Turns a voice recording, a folder of images, and a transcript into a single
narrated video: each image is shown on screen for a share of the audio's
runtime, with the matching transcript text burned in as bold white captions
over a dark gradient (see example below).

## Requirements

- [ffmpeg](https://ffmpeg.org/) on your `PATH` (`ffmpeg -version` to check)
- Python 3.8+
- `pip install -r requirements.txt`

## Setup

1. **Images**: put your images in a folder, named so they sort in the order
   you want them to appear (e.g. `01.jpg`, `02.jpg`, ... or `scene1.png`,
   `scene2.png`, ...).
2. **Audio**: a single voice/narration file covering the whole video
   (`mp3`, `wav`, `m4a`, etc).
3. **Transcript**: a plain text file with **one section per image**, in the
   same order as the sorted image files, separated by a line containing only
   `---`. A blank line inside a section starts a new on-screen paragraph.

   ```
   He migrated with his wife Ruqayyah, the daughter of the
   Prophet Muhammad. This made his life even more closely
   connected to the household of the Prophet.

   Their migration showed the cost of faith. Uthman had
   wealth and status in Makkah.
   ---
   Next image's caption text goes here...
   ---
   Third image's caption...
   ```

   The number of `---`-separated sections must match the number of images.

## Usage

```bash
pip install -r requirements.txt

python3 make_video.py \
  --images ./images \
  --audio ./voice.mp3 \
  --transcript ./transcript.txt \
  --output ./output.mp4
```

Each image's on-screen time is weighted by how much caption text it has (a
section with more text stays up longer), so pacing loosely follows the
narration without needing word-level timestamps. Pass `--equal-duration` to
split the audio evenly across images instead.

## Useful flags

| Flag | Default | Purpose |
|---|---|---|
| `--width` / `--height` | `1920` / `1080` | Output resolution |
| `--fps` | `25` | Output frame rate |
| `--font` | DejaVu Sans Bold | Path to a `.ttf` font for captions |
| `--font-size` | `48` | Caption font size in pixels |
| `--margin` | `70` | Caption padding from the frame edges |
| `--text-color` | `255,255,255` | Caption color as `R,G,B` |
| `--gradient-height` | `0.55` | Fraction of frame height covered by the readability gradient |
| `--equal-duration` | off | Split audio evenly instead of by caption length |
| `--keep-temp` | off | Keep rendered frame images for inspection |

No audio file? Omit `--audio` and every image gets a flat 4 seconds
(or use `--equal-duration` with `--audio` for even pacing).

## If your transcript has real timestamps (SRT/VTT)

This script expects one text block per image, not timestamped cues. If you
already have an SRT/VTT transcript and want images synced to exact spoken
timestamps instead of proportional pacing, say so and the script can be
extended to read cue start/end times directly instead of weighting by text
length.
