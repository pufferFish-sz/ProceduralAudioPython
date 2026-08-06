# Procedural Contact Audio — Python Prototype

Offline prototyping phase for real-time procedural contact audio (impact,
sliding, debris, ground). Verifies the math from the reference papers before
the C++/plugin phase, renders WAVs for listening, and produces thesis figures.
Spec: `procedural_audio_python_prototype_spec.md` (Downloads).

## Environment (verified 2026-08-04)

Conda env `procaudio` (python 3.11 + numpy/scipy/matplotlib via conda,
soundfile via pip):

```powershell
& C:\ProgramData\miniconda3\Scripts\conda.exe create -n procaudio -y python=3.11 numpy scipy matplotlib
& C:\ProgramData\miniconda3\envs\procaudio\python.exe -m pip install soundfile
```

## Running the stage gates

Run from `D:\ProceduralAudio` (repo root). Each stage writes WAVs to
`proto/renders/` and figures to `proto/figures/`, and prints PASS/FAIL:

```powershell
& C:\ProgramData\miniconda3\envs\procaudio\python.exe -m proto.stages.stage1_modal_bank
& C:\ProgramData\miniconda3\envs\procaudio\python.exe -m proto.stages.stage2_materials
& C:\ProgramData\miniconda3\envs\procaudio\python.exe -m proto.stages.stage3_impact
& C:\ProgramData\miniconda3\envs\procaudio\python.exe -m proto.stages.stage4_friction_aggregate
& C:\ProgramData\miniconda3\envs\procaudio\python.exe -m proto.stages.stage5_ground
& C:\ProgramData\miniconda3\envs\procaudio\python.exe -m proto.stages.stage6_full_pipeline
```

Status (all run on 2026-08-04): **stage 1–6 all PASS**.

| stage | gate | result |
|-------|------|--------|
| 1 modal bank | analytic vs measured tau per mode | PASS, err < 0.1% |
| 2 materials | 5 tan_phi swaps, decay check | PASS, err < 8% (metal), < 2% others |
| 3 impact | contact time falls with k and v; centroid rises with k; stability k=1e5..1e12 | PASS, all stable |
| 4 friction/aggregate | level tracks speed (corr 0.987), silent after stop; 3 aggregate textures | PASS |
| 5 ground | A/B floor-drop renders + comparison figure | PASS (add real recordings to `proto/recordings/`) |
| 6 full pipeline | bouncing ball / sliding box / tumble from simulated physics | PASS (verify by ear) |

## Layout

```
proto/
  core/       modal_bank, materials [ref2], impact [ref1], friction [ref4],
              aggregate [ref4], ground [ref3]
  analysis/   decay_fit (band-env fitting), spectro (specgram/centroid),
              mode_extract (stretch: modes from a recorded tap)
  sim/        trajectories (bouncing_ball, sliding_box, tumble)
  stages/     runnable stage gates 1..6 (stand-ins for the spec's notebooks)
  renders/    WAV output          figures/  PNG output
  docs/       evaluation_protocol.md (thesis eval chapter draft)
              formulas_explained.md (per-stage formulas in plain language, zh)
  recordings/ put real reference recordings here (see its README)
```

## Implementation notes / deviations from spec

- **Notebooks → scripts.** `proto/stages/*.py` are plain runnable scripts with
  printed PASS/FAIL gates (easier to re-run/diff than .ipynb; convert later
  if notebooks are wanted for the thesis).
- **Impact integrators.** `core/impact.py` has three paths:
  RK4 at adaptive oversampled rate (ground truth), an audio-rate implicit
  trapezoidal scheme that solves the per-sample delay-free nonlinearity
  (K-method in spirit; this is the real-time C++ shape), and an open-loop
  rigid-wall force pulse fallback. At k=1e8 the implicit scheme matches RK4
  contact time within ~6% and centroid exactly; both stable k=1e5..1e12.
- **Contact time = first x>0 segment.** With a light, strongly damped
  resonator the surface re-collides with the barely-rebounding striker
  (micro-bounces; `info["n_contacts"]`). The paper's monotone trends hold in
  the hammer-vs-heavy-resonator regime (stage3 uses modal mass 0.5 kg vs
  striker 8 g for the trend gates); with light objects contact time vs v can
  flatten — worth a thesis remark.
- **Hunt–Crossley force clamped at f >= 0** (no adhesion pull-off).
- **Aggregate v2** (after listening tests): v1 pushed all grains through one
  shared bandpass -- the common resonance read as "beads on a drum head".
  v2 randomizes each grain's center frequency/Q/decay and adds a bandpassed
  AM-noise "bed"; grass is mostly bed (high-frequency rustle, no resonance).
- **Ground layer** is deliberately far simpler than Qu & James — see the
  docstring in `core/ground.py` for the exact simplification list (thesis
  subsection "real-time approximation of an offline method").
- **Windows note:** run with `$env:PYTHONIOENCODING='utf-8'` if you add any
  non-ASCII prints (all current output is ASCII).
