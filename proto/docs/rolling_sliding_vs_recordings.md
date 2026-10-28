# Rolling and sliding: analysis of the reference recordings, and model changes

Working document (2026-10-27). It covers four things:
- what the recordings in `proto/recordings/Rolling` and `proto/recordings/Sliding` show;
- why our renders did not sound like them;
- what changed in the models;
- how close the renders now are, measured with the same statistics.

Tools:
- `proto/analysis/texture_stats.py` computes the measures.
- `python -m proto.scenes.roll` and `python -m proto.scenes.drag` render the
  matched scenes. Each manifest entry ends with a "render vs real" line.
- Figures: `figures/roll_vs_recordings.png` and `figures/drag_vs_recordings.png`.

**Caveat on levels:** the recordings are library Foley. They are close-miked
and uncalibrated, and the recording chain is unknown. All comparisons are
therefore of shape (spectrum normalized, statistics of the texture), never of
absolute level.

---

## 1. Measures

All measures are taken over the active part of a file: frames within 30 dB of
the loudest 5 ms frame.

| measure | what it says |
|---|---|
| centroid (median) | brightness |
| <300 Hz share | rumble / body weight |
| level sd (5 ms frames, 100 ms trend removed) | smooth vs gritty |
| >1 kHz kurtosis | 3 = Gaussian hiss; ≫3 = clicks |
| clicks/s | >1 kHz 1 ms peaks ≥ 9 dB over the 50 ms median |
| envelope modulation peak (1.5–40 Hz) and depth | revolution rate, hand strokes |
| narrow peaks | spectral lines ≥ 6 dB over the local 1/3-octave median |
| LTAS shape distance | rms dB difference of the 1/6-octave spectra (mean removed), 80 Hz–12 kHz; also reported above 300 Hz |

## 2. What the recordings show

### Rolling (9 files)

| file | centroid Hz | <300 Hz | >1k kurt | clicks/s | mod Hz / dB |
|---|---|---|---|---|---|
| metal barrel, quick | 275 | 0.75 | 32 | 6 | 1.7 / 21 |
| baseball, hardwood | 223 | 0.96 | 301 | 57 | 4.9 / 11 |
| AA battery, tile | 576 | 0.32 | 607 | 22 | 3.2 / 13 |
| rotten orange, rug | 132 | 0.99 | 38 | 30 | 17.1 / 13 |
| full pill bottle, wood | 2768 | 0.17 | 58 | 36 | 2.3 / 15 |
| empty pill bottle, wood | 918 | 0.24 | 37 | 39 | 2.6 / 14 |
| plastic cup, tile | 1342 | 0.10 | 218 | 34 | 2.3 / 15 |
| full soda can, hardwood | 199 | 0.96 | 25 | 6 | 1.8 / 18 |
| full soda can, rug | 185 | 0.97 | 13 | 4 | 3.0 / 16 |

Three properties hold for every object except the rattling pill bottles:

1. **Low frequencies dominate.** 75–99 % of the energy lies below 300 Hz for
   the barrel, ball, can and orange. This is not background rumble: the
   <300 Hz band level is modulated at the rolling rate by 12–17 dB, and its
   10–90 % range is 10–33 dB.
2. **Slow, deep periodic modulation.** It is 1.7–5 Hz and 11–21 dB deep, at the
   revolution rate v/(2πR) or a small multiple of it (seams, dents). The peak
   therefore *measures the rolling speed*: the soda can comes out at
   0.37 m/s, the battery at 0.15 m/s, and the baseball (2 seams per
   revolution) at 0.56 m/s. The scenes use these speeds.
3. **Strongly impulsive highs.** >1 kHz kurtosis is 13–600, with 4–60 clicks/s,
   from grout lines, board joints, grit and seams. Between the clicks there
   is a continuous low "rumble" bed. There is no silence.

### Sliding (16 files, one of them a duplicate)

| file | centroid Hz | <300 Hz | level sd dB | >1k kurt | clicks/s | narrow peaks | mod Hz / dB |
|---|---|---|---|---|---|---|---|
| metal box big, smooth calm | 1240 | 0.24 | 2.1 | 9 | 0 | 1 (469) | 1.7 / 19 |
| metal box big, smooth intense | 1312 | 0.25 | 2.3 | 7 | 0 | 1 | 1.7 / 17 |
| metal box medium, quick | 855 | 0.45 | 2.7 | 4.5 | 0 | 0 | 2.8 / 16 |
| metal sheet, rapsy slow | 2052 | 0.01 | 2.1 | 7 | 1 | 0 | 2.4 / 24 |
| cardboard boxes (4 files) | 3530–4660 | 0.08–0.42 | 1.3–2.4 | 4–5 | 0–2 | 0 | 2.1 / 25 |
| chess pieces (wood on wood) | 2380 | 0.30 | 2.5 | 20 | 3 | 0 | – |
| wood box on cement, stutter | 269 | 0.92 | 3.0 | 10 | 5 | 0 | – |
| paper-clip box | 2309 | 0.01 | 2.4 | 8 | 1 | 0 | 2.0 / 21 |
| boots/binder debris in box | 1770 | 0.24 | 4.2 | 50–93 | 15–36 | 0 | 1.9 / 12 |

Ordinary slides are the opposite of rolling:

1. **Near-Gaussian.** Kurtosis is 4–9 and there are almost no clicks. The
   exceptions are debris and stick-slip ("stutter").
2. **Broad spectral humps**, with almost no narrow resonances (0–1 peaks).
   The texture is bright (centroid 0.9–4.7 kHz).
3. **Level rides the hand strokes** at about 1.5–2.8 Hz, 15–25 dB deep, but
   never falls to silence. The hand reverses quickly.

## 3. Diagnosis of the old renders

| | old renders (`scenes/slide.py`) | recordings |
|---|---|---|
| narrow peaks | 4 per file: the plank's bending modes as lines (1453, 2859, 4711 … Hz) | 0–1 |
| gesture | one 0.4–0.8 s shove to a stop | seconds of strokes |
| artefacts | model B: arcs above 5 kHz that move with speed | none |
| model B kurtosis (drag) | 54–195 | 4–20 |
| model B centroid (drag) | ≈ 500 Hz | 1.2–2.4 kHz |

Causes found:

- **Mode lines.** A plank lying on its face rang as if it hung free
  (Q = 1/tan φ ≈ 80). In reality the face contact damps its bending modes.
- **Arcs. This was a bug.** `np.interp` (linear) read the 20 µm profile table,
  and z_tt then has a delta at every grid point, i.e. a line at v/DX:
  125 kHz at 2.5 m/s, folded into the audio band. As the slider slows down
  the line passes through hearing. The same bug made the rolling battery
  render a gliding 8–10 kHz line.
- **Too impulsive.** Model B has one contact track. It lifts off and lands,
  so every landing is a click. A flat face rides on many asperity contacts
  at once, and their sum is Gaussian. This is exactly the statistic the
  recordings show.
- **Too dark.** The 0.1 mm contact-patch average cuts the force off near
  v/(2πσ) ≈ 1.3 kHz at 0.8 m/s. Real micro-contacts are tens of µm, and
  they come in many sizes.

## 4. What changed in the code

### Sliding (`core/slide_profile.py`, `scenes/drag.py`)

- `read_profile`: a **cubic-spline** profile read. It removes the v/DX line
  and the arcs, and it fixes old model B too (see the re-rendered
  `renders/scenes/slide/`).
- `oversample=`: the non-linear contact (lift-off, tanh, landing pulses)
  runs at 4× and is decimated with an anti-alias filter.
- **Signed velocity:** back-and-forth strokes re-trace the same patch of
  floor.
- `n_tracks=`: a flat face rides on **N independent asperity tracks**. They
  share the load and m_p. Meso features (board joints) and the
  normal-force wobble are shared across tracks, so a joint still clicks
  across the whole face.
- `sigma_c=(lo, hi)`: each track has its own contact size, log-spaced. One
  size gives a brightness hump at v/(2πσ); a spread flattens the spectrum.
- `bodies.with_contact_damping`: adds a loss factor to the slider's modes
  while it lies on the floor.
- `scenes/drag.py`: hand strokes at 1.7 strokes/s, the recordings'
  modulation peak, with quick reversals (v ∝ sign(s)|s|^0.4). There is also
  a `steel_box` slider (a 40 × 30 cm bottom panel; plate modes with Maidanik
  radiation).
- **Presets chosen by sweep against the matched recordings**
  (`python -m proto.scenes.drag sweep`):

  | parameter | chosen value | result |
  |---|---|---|
  | contact loss | **0.1** | narrow peaks drop from 4–6 to 0–1, LTAS distance improves 1–3 dB |
  | σ range, sanded wood | **20–150 µm** | — |
  | σ range, concrete | **60–200 µm** | steel box: 12.7 → 5.9 dB |

### Rolling (new `core/rolling.py`, `scenes/roll.py`)

The object rides the **circle-dilated** surface profile (Rath & Rocchesso /
FoleyAutomatic). The profile is then **averaged over the Hertz contact
width**; smoothing after the max() removes the dilation's kinks. The object
also carries its **own rim profile**, read by rolled distance: eccentricity,
seams, dents, stitches, and its own fractal surface texture. That last one
is the "combined roughness" of rolling-noise theory (Thompson 2009), and it
supplies the continuous bed between clicks. The vertical motion uses a
Hertz law (point contact for balls, line contact for cylinders) with
gravity. Lift-off and landing come out of the same equation.

Problems found and fixed along the way:

| problem | effect | fix |
|---|---|---|
| Hunt–Crossley damping at micro-landings (~1 cm/s) | almost elastic (e ≈ 0.997): a hard battery chattered, airborne 98 % of the time | Kelvin–Voigt damping with a per-surface micro-restitution (wood 0.5, tile 0.6, rug 0.1) |
| damping ratio mapped onto HC μ | μ ≈ 2000 s/m for a stiff contact; μ·δ̇ multiplied the force ~200× at a grout edge and launched the object | same as above |
| contact resonance above hearing (46 kHz, battery on tile) | unstable step | softened to fs_s/20 (≥ 35 kHz at 16× oversampling): audibly still rigid, ≥ 10 steps per landing |
| a 12 cm can riding the full 1-D roughness | ~10× too many clicks | random roughness averaged along a line contact: rms × √(l_corr/L); grout, joints and grit are not averaged away |

New surfaces in `SURFACE_PROFILES`:
- `tile-floor`: 30 cm grid, 1.2 mm grout lines;
- `rug`: soft pile, l_corr 3 mm;
- optional `grit` (Poisson particles) on wood and tile.

New materials: `ceramic`, and `carpet` (an effective pile modulus).

## 5. Results: render vs real (same statistics)

### Rolling (`renders/scenes/roll/`)

| scene ↔ recording | LTAS dist (>300 Hz) | centroid | <300 Hz | level sd | >1k kurt | clicks/s | mod Hz / dB |
|---|---|---|---|---|---|---|---|
| baseball, wood floor | 12.9 (14.0) dB | 152 vs 223 | 0.87 vs 0.96 | 3.5 vs 4.5 | 38 vs 301 | 60 vs 57 | 4.9/23 vs 4.9/11 |
| soda can, rug | **7.4** (4.1) | 38 vs 185 | 1.00 vs 0.97 | 4.0 vs 4.3 | (few events) vs 13 | 1 vs 4 | 3.0/22 vs 3.0/16 |
| AA battery, tile on slab | **5.7** (6.2) | 1077 vs 576 | 0.37 vs 0.32 | 3.3 vs 3.5 | 1310 vs 607 | 28 vs 22 | – vs 3.2/13 |
| AA battery, tile on timber | 7.8 (7.9) | 944 vs 576 | 0.07 vs 0.32 | 3.7 vs 3.5 | 686 vs 607 | 38 vs 22 | – |
| soda can, hardwood | 12.9 (7.9) | 779 vs 199 | 0.04 vs 0.96 | 6.1 vs 4.1 | 184 vs 25 | 72 vs 6 | 12.9/11 vs 1.8/18 |

(Current numbers, after the smooth start of §8 and the touchdown fix of
§10. Before §10 they were 5.4, 7.4, 6.3, 8.2 and 12.2 dB. The baseball's
5.4 dB match had leaned on an artefact; see §10.)

For scale: the first rolling version (no fixes) had LTAS distances of
10–15 dB.

### Sliding (`renders/scenes/drag/`)

| scene ↔ recording | model | LTAS dist (>300 Hz) | centroid | >1k kurt | clicks/s | narrow peaks |
|---|---|---|---|---|---|---|
| steel box, concrete ↔ metal box, smooth calm | B (old) | 12.7 (12.8) dB | 414 vs 1240 | 6 vs 9 | 1 vs 0 | 6 vs 1 |
| | **C** | **5.9** (5.4) | 985 vs 1240 | 29 vs 9 | 1 vs 0 | 0 vs 1 |
| wood plank, wood floor ↔ chess pieces | A (noise) | 7.8 (5.2) | 4351 vs 2380 | 4 vs 20 | 0 vs 3 | 4 vs 0 |
| | B (old) | 10.8 (10.9) | 519 vs 2380 | 87 vs 20 | 14 vs 3 | 3 vs 0 |
| | **C** | 7.7 (7.0) | 614 vs 2380 | 35 vs 20 | 17 vs 3 | 1 vs 0 |
| wood plank, concrete ↔ wood box on cement, *stutter* | C | 11.2 (7.2) | 1143 vs 269 | 5 vs 10 | 4 vs 5 | 0 vs 0 |

The steel box also matches on the other measures:
- <300 Hz share: 0.20 vs 0.24;
- level sd: 2.1 vs 2.1 dB;
- stroke modulation: 1.6 vs 1.7 Hz.

## 6. What is still off (and why)

- **Soda can on hardwood** is the weakest match.
  - The real recording is 96 % below 300 Hz, with deep once-per-revolution
    thumps. Ours is mid-frequency, with grit clicks.
  - Two likely causes:
    - (a) the close mic and floor near field favour low frequencies, while
      we model the far field at 1 m with plate radiation efficiency, so the
      floor radiates poorly below its 684 Hz coincidence;
    - (b) the real can's out-of-roundness is unknown.
  - A reference recorded at a known distance would separate the two (see
    `recordings/README.md`).
- **The low band in general.** All 52xxxx library rolls are ≥ 0.96 below
  300 Hz. Comparing above 300 Hz removes most of the disagreement (e.g. can
  on hardwood: 12.0 → 6.5 dB).
- **Modulation depth is too deep** in most renders:
  - rolling: 20–22 dB vs 11–16 dB;
  - drags: 23–32 dB vs 19 dB.
  - Real objects wobble less regularly: seams vary along a ball, and hands
    vary their stroke.
- **Wood plank vs chess pieces** is a loose match: a 0.42 kg plank against
  small pieces on a board. Plain noise (A) matches the spectrum as well as C
  does. What C adds is structure that A lacks: the texture re-traces the
  same patch, joints click once per board, and the sound darkens with speed.
- **Stick-slip ("stutter") is not modelled** in B/C. The cement drag
  recording is low-frequency chatter. Model A's squeak option is the only
  stick-slip so far. An elasto-plastic friction model is in the literature
  review (§2.3, §3 layer 6).
- **The rug can's kurtosis is undefined in practice.** The render has
  almost no >1 kHz energy, so a few events dominate the statistic.
- **Presets.** Several values are presets chosen against the matched
  recordings and labelled as such in each manifest: contact loss, σ range,
  dents and stitches, micro-restitution, grit density, carpet modulus. They
  are fits, not measurements.

## 7. Next steps

1. **Listen** to `renders/scenes/roll/` and `renders/scenes/drag/` next to
   the recordings. The statistics say "closer", not "convincing".
2. **Record our own references** at a known distance (phone at 1 m is
   enough): a can and a ball rolled on the same floor, and a box dragged.
   That removes the close-mic ambiguity in the low band.
3. **Cost for the C++ port:**
   - Rolling needs 4–16× oversampling only around contact switches. An
     event-driven scheme (analytic flight, solve only near landings) would
     run at 1×.
   - Model C's 6 tracks are 6 cheap loops. They could become one track plus
     a Gaussian bed with the same spectrum.
4. **Stick-slip** for stutter and squeak, opt-in.

## 8. Listening round 1 (2026-10-27): ball and box sets

Renders: `renders/scenes/roll_spheres/` (`python -m proto.scenes.roll
spheres`) and `renders/scenes/drag_boxes/` (`python -m proto.scenes.drag
boxes`).

Feedback, and what changed:

- **Large balls: "solid".** No change needed.
- **Small balls: "extremely fuzzy, a lot of static".**
  - Cause: the sanded `wood-floor` preset has a 1.7 mm grain ripple, about
    4 µm rms (put there for the sliding texture). At 0.59 m/s, following it
    needs more downward acceleration than g. A small ball's contact patch
    (0.13–0.18 mm) does not average the ripple away, so the ball hopped every
    ripple: 52–74 % airborne, 210–250 landings/s.
  - Ablation: removing grit or board joints changed nothing; removing the
    fractal and grain roughness did.
  - The large balls' 0.6 mm patches average the ripple out.
  - Fix: the ball set now rolls on `varnished-wood-floor` (the same boards,
    grain filled: 1.5 µm rms, weak ripple). Small balls drop to 9–19 %
    airborne and 27–37 landings/s; those are the board-joint and grit hops
    and their bounces. The large balls are unchanged (0–1 %).
- **Drags: "fine, but want one long sustained drag, not repeats".**
  - `steady_pull` is one 3.4 m pull at 0.5 m/s, with a slow ±12 % hand
    variation and smooth 0.6 s start and stop. It is used for the box set.
  - The slower speed makes the texture darker, since brightness scales with
    v/(2πσ).
- **"Get rid of the initial bump".**
  - It was at exactly the start of motion. A speed step gives the profile
    force an acceleration impulse, z′·Δv·δ(t).
  - Pulls now start and stop with zero acceleration. Rolling also starts
    with a 0.3 s raised-cosine speed ramp.
  - Checked: in no box file is the first 0.8 s louder than the rest.
- Fixed along the way:
  - **Free-body click radiation.** A free body's rigid "click" used the
    Maidanik plate efficiency, which does not fall to 0 at low frequency.
    For the light cardboard box this blew up near DC. Rigid-body motion now
    always radiates as a compact dipole.
  - **Box contact mass.** It now comes from the bottom panel's point
    impedance Z = 8√(Dρh) at 1 kHz: 3 g for cardboard, 9.7–15 g for steel.

Open:
- The steel boxes are still 10–14 dB quieter than cardboard, and they are
  not "metallic", because only the damped bottom panel rings.
- To add: the free walls and lid, and the tangential friction force.

## 9. Listening round 2 (2026-10-27)

### Small balls: "still a little fuzzy, cut some high end"

What the measurements show:
- **The floor makes the sound.** The ball's own stem is about 45 dB below
  the floor's.
- **The highs are already low in energy:** 2–16 kHz is 23–38 dB below the
  total.
- **The energy sits at 0.5–2 kHz.** Two things meet there: the small balls'
  contact resonance (≈ 470 Hz, vs ≈ 200 Hz for the large balls) and the wood
  floor's coincidence (684 Hz), where its radiation peaks.

Causes ruled out, and what was tried:

| tried | result |
|---|---|
| ablation: grit or floor roughness off | hardly matters |
| ablation: board joints off | small steel ball 8.5 dB quieter; 1–8 kHz share 3–3.5 dB lower |
| fade the Kelvin–Voigt damping in over δ₀ (no force step at touchdown) | no gain on the small balls; under-damped soft contacts in normal rolling (baseball LTAS 5.4 → 14.0 dB, rug 7.4 → 12.0) — **removed** |
| more micro-landing damping | halves the landings but sharpens each contact: 2–8 kHz +4–7 dB — rejected |
| floor loss rising with frequency | −0.3 dB — no effect |

Kept: an A/B on `varnished-wood-floor-tight` (flush 1 mm × 0.1 mm joints).
The small balls come out 2–4 dB quieter (fewer joint knocks), with the
same spectral tilt. What remains is the physical brightness of a small,
stiff contact on that floor. Cutting it further means a designer tone
control, not physics.

### Steel boxes: "too much, obnoxious"

- **Cause.** The floor rubbed the bottom panel at an interior point (37 %,
  43 % of its sides). That drives the panel's low modes, a steady 50–500 Hz
  roar. Compared with the real metal-box recordings, the renders were also
  far darker: above 4 kHz they were 25–45 dB low.
- **Fix.** A sheet-metal box rests on its folded bottom rim, so contact is
  now 3 % in from an edge, where low modes hardly move (φ ∝ mπx/a).
  - The 50–200 Hz band drops 2–5 dB, and the box is 2–5 dB quieter.
  - The 50 Hz–4 kHz band shape now follows the recording within about
    3 dB.
- **Rejected: finer edge asperities** (σ from 20–40 µm). They add the
  missing top, but always as a 2–4 kHz screech hump, because the
  finest-scale tracks dominate the high band.
- **Still open: the real recordings' smooth 4–16 kHz "air".** It needs a
  different weighting of asperity scales.

## 10. Listening round 3 (2026-10-28): "sounds clipped, then turned down"

**Feedback.** The ball rolls sounded as if they had been clipped and then
turned down.

**What it was not.** The files have no digital clipping: no samples pinned
at full scale, no flat tops, and peaks at −3 dBFS or below.

**Cause: a force step at every touchdown.** The Kelvin–Voigt damping term
c·δ̇ is at full strength the instant a landing starts, while the elastic
term starts at 0. The contact force therefore jumped from −1 mg
(weightless) to about +1.1 mg within one audio sample (22 µs). That kicks
every floor mode up to 10 kHz at once, and it puts a hard edge into the
floor stem's waveform (the floor stem, not the ball's). Large steel ball:
largest sample-to-sample step 18.6 dB over the rms.

**Fix (`rolling.roll_force(t_on=3e-4)`).** After each touchdown the damping
builds up linearly over 0.3 ms. Steady rolling has no touchdowns, so it is
unchanged.

| | largest waveform step, re rms |
|---|---|
| large steel ball | 18.6 → 4.4 dB |
| small balls | 12–13 → 5–7 dB |
| large wooden ball (never hops) | unchanged |

Two fixes that did not work:
- **Fade by penetration** (over δ₀ or 0.1 δ₀). At landing speed, 0.1 δ₀
  passes in about 1 sample. Fading over the full δ₀ under-damps steady
  rolling (baseball LTAS 5.4 → 14 dB).
- **More micro-damping, or a lossier floor.** Neither removes the step.

**Side effect on the matched baseball.** Its LTAS distance goes from 5.4 to
12.9 dB:
- The step had been kicking the ball off the floor (airborne 31 % → 15 %
  now).
- The step had also supplied high frequencies that the real recording
  gets from elsewhere. Kurtosis 89 → 38, against 301 real.
- The click rate still matches: 60 vs 57/s.

The baseball's earlier "good" match therefore leaned on the artefact. A
real high-frequency source for it is still missing, for example micro-slip
or scuffing of the leather and stitches.

## 11. The same check for sliding (2026-10-28)

The question: does sliding have the same hard edges as rolling (§10)?
Each render was checked for its largest sample-to-sample step relative to
the rms. The 99.99th percentile separates isolated edges from noise that
is simply bright.

### Results

- **Box pulls (`drag_boxes/`): clean.** The largest step is −4 to +1 dB re
  rms, with no isolated edges. The heavy boxes never lift off, and the
  pull starts smoothly (§8).
- **Hand-stroke drags (`drag/`): edges at t = 0.100 s, the gesture start.**
  The largest was 31 dB, on the steel box with model C.
- **Old shove slides (`slide/`): an edge at the shove.**

### Causes and fixes

| cause | fix |
|---|---|
| strokes phased from t = 0, so at the 0.1 s start the speed jumped to ~90 % of peak | strokes phased from the start time, with a 0.15 s raised-cosine onset |
| sign(s)\|s\|^0.4 has infinite slope at s = 0: an acceleration impulse z′·Δv·δ(t) at every reversal | v ∝ tanh(3s)/tanh(3): quick reversals, finite acceleration |
| shove: 2.5 m/s from rest in one sample | `slide.SHOVE` = 0.08 s raised-cosine hand push |
| slide counterpart of §10: after a lift-off, the contact force snapped from 0 to N in the landing sample | the force builds back up over `slide_profile.T_ON` = 0.3 ms; the landing impulse stays as its own Hertz pulse |

**After the fixes**, model B/C drags have their largest step at 1.5–6 dB re
rms. Model A is white noise: its sample steps are large everywhere but
none of them is isolated. The slide B files keep some 4–14 dB events near
peak speed. Those are genuine micro-impact landings, not steps.

### Effect on the matched drag numbers (LTAS shape distance)

| scene | before | now |
|---|---|---|
| plank on wood, A | 7.8 (5.2) | 7.9 (5.4) |
| plank on wood, B | 10.8 (10.9) | 15.4 (16.3) |
| plank on wood, C | 7.7 (7.0) | 8.2 (7.5) |
| plank on concrete, C | 11.2 (7.2) | 11.9 (8.9) |
| steel box, B | 12.7 (12.8) | 19.2 (20.2) |
| steel box, C | 5.9 (5.4) | 12.2 (13.1) |

As with the baseball in §10, the stroke-reversal kicks had supplied
broadband highs. Above 6 kHz the steel box now falls well below the
recording: −52 vs −29 dB at 9 kHz. The earlier 5.9 dB match leaned on
that artefact.

The real metal box's 4–16 kHz "air" still needs a real source. A
tangential (friction) force component is the main candidate.
