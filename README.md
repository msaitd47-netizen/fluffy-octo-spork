# make_video.py

Turns a voice recording, a folder of images, and a transcript into a single
narrated video: each image is shown on screen for a share of the audio's
runtime, with the matching transcript text burned in as bold white captions
over a dark gradient (see example below).

If you have fewer images than sentences/paragraphs (one image per chapter
instead of per sentence), that's the normal case: give each image a whole
section of text, and the image stays on screen for the section's full
duration while the caption advances page by page (sentence by sentence
by default) in sync with that duration — the image itself doesn't change,
only the caption underneath it.

Timing starts from a text-length estimate, then (when `--audio` is given)
gets corrected against real pauses detected in the audio, so captions
change where the narrator actually pauses instead of at a guessed instant.
This works far better in `--split-mode sentence` (the default) than in
`paragraph` mode: with several sentences grouped into one page, the pause
detector can lock onto a pause *inside* the paragraph and cut its last
sentence off before it's spoken. Only use `paragraph` mode if your caption
style needs multiple sentences on screen at once and you're not relying on
audio-synced timing.

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

Within a single image's on-screen time, if its transcript section has more
than one paragraph (or sentence, with `--split-mode sentence`), the caption
advances through it page by page — each page's share of that image's time is
also weighted by its length, and every page is held for at least
`--page-min-seconds`.

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
| `--split-mode` | `sentence` | Page a section's captions by `sentence` or by `paragraph` |
| `--page-min-seconds` | `1.2` | Minimum time each caption page stays on screen |
| `--no-silence-align` | off | Disable snapping caption boundaries onto detected pauses in the audio |
| `--silence-noise-db` | `-30` | Threshold (dB) below which audio counts as silent, for pause detection |
| `--silence-min-duration` | `0.4` | Minimum gap length (seconds) to count as a pause |
| `--keep-temp` | off | Keep rendered frame images for inspection |

No audio file? Omit `--audio` and every image gets a flat 4 seconds
(or use `--equal-duration` with `--audio` for even pacing).

## If your transcript has real timestamps (SRT/VTT)

This script expects one text block per image, not timestamped cues. If you
already have an SRT/VTT transcript and want images synced to exact spoken
timestamps instead of proportional pacing, say so and the script can be
extended to read cue start/end times directly instead of weighting by text
length.
