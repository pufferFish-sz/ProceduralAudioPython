# Reference recordings

Put real contact-sound recordings here for spectrogram comparison
(phone recordings are fine at this stage). Suggested set:

- wood block tap
- ceramic mug tap
- metal pot tap
- object dropped on floor  (name it `*floor*.wav` — stage4 auto-includes it)
- object dragged on table
- gravel scrape

For each file, note below: device, distance, room.

| file | device | distance | notes |
|------|--------|----------|-------|
|      |        |          |       |

## Library references (added 2026-10-27)

`Rolling/` (9 files) and `Sliding/` (16 files) are library Foley
recordings: close-miked, uncalibrated, recording chain unknown. They are
used for SHAPE comparisons only (spectrum shape, texture statistics), never
for absolute level. The analysis and the render-vs-real numbers are in
`docs/rolling_sliding_vs_recordings.md`.

Matched to renders:
- `scenes/roll.py`:
  - baseball on hardwood;
  - full soda can on hardwood / on rug;
  - AA battery on tile.
- `scenes/drag.py`:
  - metal box, smooth calm;
  - chess pieces;
  - wood box on cement (stutter).

Notes:
- `Sliding/471747-...-CDAP (1).wav` is a duplicate of `471747-...-CDAP.wav`
  and is skipped by the analysis.
- Still missing: our own references at a KNOWN distance (phone at 1 m is
  fine) for the same objects, e.g. a can and a ball rolled on one floor, and
  a box dragged on it. Without them the low band (< 300 Hz) cannot be
  compared: close miking boosts it.
