# Perceptual Evaluation Protocol (draft for thesis evaluation chapter)

Sources: Klatzky, Pai & Krotkov (Presence 9(4), 2000) for the material
identification paradigm; Turchet (Applied Acoustics 104, 2016) for the
realism-rating / surface-identification paradigm. This is a working summary
written from the papers' methodology sections — verify exact stimulus
counts/scales against the PDFs before writing the thesis chapter.

## 1. Material identification & rating (after Klatzky/Pai/Krotkov 2000)

**Paradigm.** Synthesized contact sounds where fundamental frequency and the
frequency-dependent decay parameter (tan phi in our implementation) are
varied factorially and independently. Participants either (a) categorize the
material of the struck object from a closed set (e.g., rubber, wood, glass,
steel) or (b) rate perceived material attributes on continuous scales.

**Stimuli construction (mapped to this codebase).**
- One fixed mode set ("shape") from `core/materials.SHAPES`.
- Cross tan_phi values spanning the material table (log-spaced, ~5–8 steps)
  with several base frequencies (transpose the mode set, ~4–6 steps).
- Impulse excitation only (isolate resonator cues from exciter cues).
- Loudness-equalize stimuli (our `write_wav_group` preserves relative level;
  for the experiment, normalize each to equal loudness instead).

**Key findings to test against.**
- The decay parameter dominates material categorization; frequency mainly
  shifts judgments of size/shape (and interacts weakly with material).
- Expected result for our synth: material identification should follow
  tan_phi regardless of which shape/mode set is used.

**Measures.** Confusion matrices (category task), rating scales vs. tan_phi
(regression). Include catch trials with recorded sounds.

## 2. Realism & surface identification (after Turchet 2016)

**Paradigm.** For each synthesized surface type (solid: wood/metal/creaking;
aggregate: gravel/snow/dirt/grass): (a) absolute realism ratings on a 7-point
or continuous scale, (b) forced-choice surface identification from the set of
simulated surfaces, (c) paired comparison against recorded samples of the
same surface (which sounds more realistic / are they the same surface).

**Stimuli construction (mapped to this codebase).**
- Impact chain: `stage3` renders (velocity/stiffness variants).
- Aggregate chain: `core/aggregate.AGGREGATE_PRESETS` driven by the same
  energy envelope per surface so only the surface model varies.
- Matched recordings from `recordings/` (same interaction, comparable
  duration/level).

**Design notes from Turchet worth copying.**
- Identification confusions between acoustically similar surfaces (e.g.,
  gravel vs. dirt) are expected and worth reporting as a matrix, not just
  accuracy.
- Interaction realism (temporal pattern) matters as much as timbre: use the
  same event/gesture timing for synthetic and recorded stimuli.

## 3. Audio-visual congruence (UE stage, optional condition)

Rate plausibility of the same physical event with and without game visuals
(video captures from the UE component driving the same DSP). Python phase
produces no visuals by design; this condition is deferred to the UE stage.

## Practicalities

- Within-subjects; randomized order; ~15–25 participants (both papers are in
  this range); headphone delivery, level-calibrated.
- Log stimulus parameter values alongside responses so psychometric curves
  (e.g., P(material=wood) vs. tan_phi) can be fit directly.
