# Procedural Contact Audio — Python Prototype

## Project summary

This is a master's thesis project (CMU 2026–27). It builds **real-time procedural
audio for physical contact in games**: impacts, drops, sliding/scraping,
granular surfaces (gravel/dirt/grass) and floor "thump". Sound is synthesized
from the physics event (what hit what, how hard, how fast) instead of
being picked from a library of recorded samples.

The end goal is a middleware plugin (FMOD and/or Wwise) driven from Unity /
Unreal physics callbacks. A sound designer chooses an object (shape, size,
material) and a surface. The engine supplies impact velocity and slide
speed. The plugin renders a matching sound with no sample library.

This repository is the **offline Python phase**. It checks the math from
the reference papers, renders WAVs for listening and produces thesis figures
before anything is ported to C++.

### Signal model (one object, many exciters)

```
             exciter (force f(t))                       resonator                 layers
 impact  ── Hunt–Crossley contact (m, v, k) ──┐
 slide   ── speed-driven friction noise    ───┼──> modal bank of the object ──┐
 debris  ── PhISEM grain streams (no modal) ──────────────────────────────────┼──> mix
 floor   ── momentum-scaled LF thump + noise ─────────────────────────────────┘
 object  = shape (mode frequencies) × material (tan φ → per-mode decay)
```

### What has been achieved (status 2026-10)

| # | stage | what it shows | gate result |
|---|-------|---------------|-------------|
| 1 | modal bank | exact-pole modal resonator; analytic vs measured decay | PASS, err < 0.1 % |
| 2 | object + impact | **A** one scalar (tan φ) swaps 5 materials; **B** Hunt–Crossley contact: contact time falls with k and v, harder = brighter, stable for k = 1e5…1e12 at 44.1 kHz with an audio-rate implicit solver (real-time shape); **C** mode sets computed from geometry + E/ρ (bar, rod, pipe, disc) and hardness k from the two materials (Hertz) | PASS |
| 3 | friction + aggregate | slide level tracks speed (corr 0.987), silent after stop; gravel/dirt/grass textures (grass v3, layered) | PASS (verify grass by ear) |
| 4 | ground | floor drop as a two-body contact: one force pulse drives the object, its contact click and the floor (shared pressure units); legacy hand-mixed layer kept for A/B | PASS: impulse conserved, wood floor is 39 dB over concrete (needs real recordings) |
| 5 | full pipeline | bouncing ball (wood floor + concrete) / sliding box / tumble driven by simulated physics; `*_legacy.wav` for A/B | PASS (verify by ear) |

Key results so far:
- **Material is one number.** tan φ (Klatzky et al.) moves the same shape from
  metal to rubber, and the measured decay matches theory within a few percent.
- **Impact is modal + velocity + hardness.** The impact layer adds no resonator.
  It shapes a force pulse from (striker mass, v, k), and that pulse drives the
  object's own modes. Material therefore enters twice: as tan φ (ring time) and
  as E (hardness k, pitch scale).
- **A real-time integrator exists.** The implicit audio-rate scheme matches the
  RK4 reference within about 6 % in contact time and 0 % in centroid, so it is
  the C++ candidate.
- **Shapes can come from geometry.** `core/shapes.py` derives modes for bars,
  rods, pipes and discs. The old `SHAPES` presets are hand-authored and come
  from no 3D shape.

Next steps, open questions and the plugin roadmap are in
[`proto/docs/plan_and_brainstorm.md`](proto/docs/plan_and_brainstorm.md).

## Environment

Conda env `procaudio` (python 3.11 + numpy/scipy/matplotlib via conda,
soundfile via pip). On this machine it lives in the user's miniconda:

```powershell
conda create -n procaudio -y python=3.11 numpy scipy matplotlib
& $env:USERPROFILE\miniconda3\envs\procaudio\python.exe -m pip install soundfile
```

## Running the stage gates

Run from the repo root. Each stage writes WAVs to `proto/renders/` and
figures to `proto/figures/`, and prints PASS/FAIL:

```powershell
$py = "$env:USERPROFILE\miniconda3\envs\procaudio\python.exe"
& $py -m proto.stages.stage1_modal_bank
& $py -m proto.stages.stage2_object_impact
& $py -m proto.stages.stage3_friction_aggregate
& $py -m proto.stages.stage4_ground
& $py -m proto.stages.stage5_full_pipeline
```

## Listening scenes (consistent renders)

The stage scripts above are **math checks**: their renders use test
objects (hand-typed mode sets, a generic mallet). For listening, use the
**scenes**. In a scene, every body is a real, fully specified object
(size + material), its modes come from physics (`core/shapes.py`), contact
hardness comes from Hertz theory, and every body radiates through one
radiation-efficiency model. Nothing is hand-mixed.

```powershell
& $py -m proto.scenes.ball_drop      # rubber ball, small/large, onto 3 floors
& $py -m proto.scenes.stick_strike   # wooden stick strikes wood/steel/stone bars
& $py -m proto.scenes.slide          # plank slides to a stop: A noise vs B surface-profile model
& $py -m proto.scenes.tumble         # small wood/steel block tumbles to rest
& $py -m proto.scenes.footsteps      # 4 steps on gravel/dirt/grass (+ old grass)
```

These replace the stage 3–5 listening renders (sliding box, aggregate
textures, ground drop, bouncing ball, tumble). Footsteps are the one
family without physical levels: the aggregate layer is normalized per
layer, and its manifest says so.

File names say what happens:
`<action>_<mover>_<how>_<onto|on>_<target>.wav`, e.g.
`drop_rubber-ball-small-r15mm_from-1m_onto_wood-floor.wav`,
`slide_wood-plank-40x8x2cm_shoved-2.5mps_on_concrete-slab.wav`,
`walk_4-steps_every-0.55s_on_grass.wav`. Each family
folder in `proto/renders/scenes/` has:
- a `README.md` manifest (what you hear, object specs, modes, contact
  time, restitution, which body carries how much energy);
- `stems/` with each body on its own (`...__ONLY-<body>.wav`).

All files in a family share one gain, so loudness differences are physical.
Spectrogram overview: `proto/figures/scenes_<family>.png` (each panel is
normalized on its own).

## Layout

```
proto/
  core/       modal_bank, materials (tan_phi + E/rho/nu) [ref2], shapes
              (analytic bar/rod/pipe/disc), impact [ref1] (+ Hertz k),
              friction [ref4], aggregate [ref4], ground [ref3],
              contact (unified two-body impact), radiation (pressure proxy +
              radiation efficiency), bodies (scene objects + 2-body contact)
  analysis/   decay_fit (band-env fitting), spectro (specgram/centroid),
              mode_extract (stretch: modes from a recorded tap)
  sim/        trajectories (bouncing_ball, sliding_box, tumble)
  stages/     runnable stage gates 1..5 (math checks, test objects)
  scenes/     listening scenes from fully specified bodies (core/bodies.py)
  renders/    WAV output          figures/  PNG output
  docs/       formulas_explained.md (per-stage formulas, plain language)
              evaluation_protocol.md (thesis eval chapter draft)
              two_body_impact_related_work.md
              plan_and_brainstorm.md (next steps, design questions)
              archetypes.md (sourced archetype list: materials, formulas)
              sliding_sound_literature.md (sliding models, diagnosis)
  recordings/ put real reference recordings here (see its README)
```

## Implementation notes / deviations from spec

- **Notebooks → scripts.** `proto/stages/*.py` are plain runnable scripts with
  printed PASS/FAIL gates. They are easier to re-run and diff than .ipynb, and
  can be converted later if the thesis needs notebooks.
- **Stage renumbering (2026-10).** The former stage 2 (materials) and stage 3
  (impact) are now one stage, `stage2_object_impact`, because they are one
  layer: the impact is just the force that excites the object. Former stages
  4–6 are now 3–5.
- **Impact integrators.** `core/impact.py` has three paths:
  RK4 at an adaptive oversampled rate (ground truth); an audio-rate implicit
  trapezoidal scheme that solves the per-sample delay-free nonlinearity
  (K-method in spirit, and the real-time C++ shape); and an open-loop
  rigid-wall force pulse as a fallback. At k=1e8 the implicit scheme matches
  RK4 contact time within ~6 % and centroid exactly. Both are stable for
  k=1e5..1e12.
- **Contact time = first x>0 segment.** With a light, strongly damped
  resonator the surface re-collides with the barely-rebounding striker
  (micro-bounces; `info["n_contacts"]`). The paper's monotone trends hold in
  the hammer-vs-heavy-resonator regime (stage 2B uses modal mass 0.5 kg vs a
  striker of 8 g for the trend gates). With light objects, contact time vs v
  can flatten, which is worth a thesis remark. Stage 2C drops whole objects,
  where the object's own mass is the striker. That gives 0.5–1.6 ms contacts
  and a darker sound.
- **Hunt–Crossley force clamped at f >= 0** (no adhesion pull-off).
- **Aggregate v2/v3.** v1 pushed all grains through one shared bandpass
  ("beads on a drum head"). v2 randomizes each grain's resonance and adds an
  AM-noise bed. v3 rebuilds grass, which v2 rendered as a stationary hiss
  swell, from layered swish grains, crackles and a thin bed with lognormal
  amplitudes. `stage3_aggregate_grass_v2.wav` is kept for A/B listening.
- **No "is it ground?" branch.** `core/contact.py` treats every hit as two
  bodies sharing one contact force. The floor is just the other body, and
  its sound model (light plank floor vs massive slab) decides how much it
  adds. Every body is converted to one pressure proxy (`core/radiation.py`),
  so levels are not hand-mixed. The legacy `ground_layer` (momentum-driven,
  hand gain) is kept only for A/B renders.
- **Ground layer** is deliberately far simpler than Qu & James. See the
  docstring in `core/ground.py` for the exact list of simplifications (thesis
  subsection "real-time approximation of an offline method").
- **Windows note:** run with `$env:PYTHONIOENCODING='utf-8'` if you add any
  non-ASCII prints (all current output is ASCII).
