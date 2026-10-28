# Sliding / Scraping Sound Synthesis — Literature Review and Diagnosis

Written 2026-10-25 after listening feedback: the `scenes/slide` renders "sound
like static, slightly modified white noise". Part 1 diagnoses why. Part 2
reviews published models. Part 3 recommends what to build.

Notation:
- ✔ = read in the full text for this review.
- ◇ = abstract, project page or secondary source only; verify before citing details.

---

## 1. Why our slide renders sound like static

Measured on the current renders (`proto/scenes/slide.py`):

| component | wood floor | concrete | steel plate |
|---|---|---|---|
| plank modes | 25 % | 99 % | 36 % |
| plank rigid "click" (noise radiated directly) | 0.1 % | 0.5 % | 0.2 % |
| floor modes | 75 % | 0 % | 64 % |

So the noise is not leaking in through a direct path. The modes themselves
are driven by **stationary Gaussian noise**, so what you hear is coloured
noise. The excitation (`core/friction.py`) is white noise × a level that
grows with speed, through a one-pole lowpass whose cutoff also grows with
speed. Compared with the literature, it is missing everything that tells
the ear "something is moving over a surface":

1. **There is no surface.** Real sliding traces a fixed surface profile.
   Its features pass the contact at a rate set by the speed, so spectral
   peaks move up and down with velocity, heard as a "pitch" of the scrape
   (FoleyAutomatic). White noise has no features to move.
2. **There are no micro-impacts.** Scraping and rubbing are sequences of
   discrete asperity collisions. Their density and amplitude statistics
   distinguish scratching from rubbing (Conan et al.), and they are the
   "grain" control in SDT. Gaussian noise is the limit of infinitely many
   tiny impacts, which reads as hiss.
3. **There is no non-linearity.** A probe cannot follow sharp profile
   detail. Bounding its curvature was the single most important ingredient
   for realism in Agarwal et al.'s listening tests.
4. **The normal force never varies.** Hand or object wobble modulates the
   force slowly. Removing that variation measurably lowered realism and
   motion recognition (Agarwal et al.).
5. **Coupling is too dense and flat.** Hundreds of floor modes (10 kHz
   cap), all driven equally by broadband noise, smear into a noise floor.
   Rolling and sliding forces "know" the modes in real recordings
   (FoleyAutomatic, §4.3).

---

## 2. Published approaches

### 2.1 FoleyAutomatic: profile wavetable ("phonograph needle") — van den Doel, Kry & Pai, SIGGRAPH 2001 ✔
- **Needle model.** The audio force is a surface profile read at the contact
  speed: a wavetable built for v_max is played back at rate v/v_max (linear
  interpolation).
- **Effective profile.** Fractal noise with power ∝ ω^β, passed through one
  or more **reson filters whose centre frequency scales with contact
  speed**. That gives "changing pitch at different speeds". The reson
  bandwidth sets how random versus pitched the surface sounds. Fractal
  dimension D = β/2 + 2 tracks perceived roughness. β can be fitted from a
  contact-microphone recording, and reson parameters from a measured profile.
- **Level.** Volume ∝ √(v·F_normal), assuming acoustic energy ∝ frictional
  power loss.
- **Rolling.** The same model plus an adjustable lowpass, since a ball only
  "sees" large-scale structure. The authors note rolling forces couple more
  strongly to the object's modes than an independent force would.
- **Source:** [PDF](https://www.cs.ubc.ca/labs/lci/papers/docs2001/van-foleyautomatic.pdf)

### 2.2 Three-level surface representation — Ren, Yeh & Lin, IEEE VR 2010 ✔ (system parts) ◇ (equations not extracted)
- **Levels:** macro (physics-engine contacts), meso (visible bumpiness from
  the **texture / normal maps the game already has**, turned into impulse
  trains as the contact crosses ridges) and micro (FoleyAutomatic fractal
  noise for fine roughness).
- **Critique of FoleyAutomatic-only:** repetitive, and it only works on
  homogeneous surfaces.
- **Critique of physical friction models:** too many control parameters for
  scenes with many objects.
- **Most game-relevant idea:** drive sliding from the visual texture.
- **Source:** [Project page](https://gamma.cs.unc.edu/SlidingSound/SlidingSound.html), [PDF](https://gamma.cs.unc.edu/SlidingSound/VR2010.pdf)

### 2.3 Physical friction models — Avanzini, Serafin & Rocchesso, IEEE TSAP 13(5), 2005 ◇
- **Model:** an elasto-plastic (LuGre/Dupont-type) dynamic friction model
  coupled to lumped modal resonators, with an efficient discretization.
- **Sounds it produces:** rubbing, braking and squeaky doors, because
  stick-slip comes out of the physics rather than being imposed.
- **Earlier version:** DAFx-02, "Modeling Interactions between Rubbed Dry Surfaces Using an Elasto-Plastic Friction Model".
- **Bowed-string version:** Serafin et al., SMAC 2003, which reproduces the
  hysteresis loop in force versus velocity.
- **Fit for us:** the right tool for **squeaks, creaks and squeals**, and
  costly to tune.
- **Sources:** [DAFx-02](https://dafx.de/paper-archive/details/WJyFGe3ntpjR8BhNqTYFLA), [repository record](https://air.unimi.it/handle/2434/653903)

### 2.4 Sound Design Toolkit (SDT) — Rocchesso, Baldan, Delle Monache et al. ◇
- **What it is:** an open-source C library with Max/Pd externals, built on
  the same impact and friction lineage as our impact model.
- **`SDTScraping`:** a control layer that turns a surface-profile audio
  signal into a normal force on a resonator. Its controls are **grain**
  (micro-impact density, i.e. roughness), **force** (micro-impact energy)
  and **velocity**. A friction model can be layered on for a rubbing
  character.
- **Why it matters:** practical evidence that "profile + micro-impact
  density + force + velocity" is a usable designer control set.
- **Source:** [API doc](https://sdt.lim.di.unimi.it/docs/API/v2.2-078/group__scraping.html)

### 2.5 Action–object synthesizer: rubbing / scratching / rolling — Conan, Thoret, Aramaki, Derrien, Gondre, Ystad & Kronland-Martinet, Computer Music Journal 38(4), 2014 ◇
- **Model:** the interaction is a series of impacts. Scratching and rubbing
  differ in the **statistics of the impact series** (temporal spacing and
  amplitude distribution, smoother for rubbing). This was validated
  perceptually.
- **Controls:** users move continuously through an "action space", for
  example morphing from rubbing to rolling. This is very close to the
  designer-macro idea in `plan_and_brainstorm.md` §2.4.
- **Follow-up:** an audio-tactile version (Aramaki et al., 2024).
- **Sources:** [HAL](https://hal.archives-ouvertes.fr/hal-01050522), [DAFx-13 version](https://dafx.de/paper-archive/details/DUlyWbOKkX27PcuvOhkQXw), [2024 follow-up](https://arxiv.org/pdf/2401.05757)

### 2.6 Non-linear scraper trajectory — Agarwal, Cusimano, Traer & McDermott, DAFx-20in21 ✔ (via full-text HTML)

The most complete recent model, with perceptual tests.

- **Source-filter structure:** a contact force convolved with surface and
  scraper impulse responses (50 strongest modes, interpolated across
  contact positions).
- **Measured surfaces:** depth profiles z(x, y) of everyday materials,
  measured with a confocal microscope.
- **Curvature limit:** the scraper path S cannot follow z exactly; its
  curvature is soft-limited:
  `∂²S/∂x² = (1/α(N))·tanh(α(N)·∂²z/∂x²)`, followed by a short Gaussian
  smoothing. The limit depends on the normal force N:
  `α(N) = (1−ν)α_max + ν·α_min` (α_max = 0.05, α_min = 0.01, ζ = 0.95).
- **Two force terms:**
  - vertical `f_v = m_p·S̈` (velocity² × path curvature);
  - horizontal micro-collisions `f_h = β₁·|v·∇S|^β₂` (β₁ = 0.05, β₂ = 1).
- **Normal-force variation:** follows the motion. For back-and-forth hand
  motion, N_max and N_min come from the arm geometry.
- **Rolling:** adds a Hertz-type term `k·ρ^{3/2} + λ·ρ^{3/2}·ρ̇`, with
  penetration ρ set by the surface profile and the ball's centre-of-mass
  offset.
- **Perceptual results:**
  - The full model is rated more realistic than earlier methods.
  - Removing the non-linearity caused the largest drop.
  - Removing the normal-force variation cut both realism and motion
    recognition.
  - For rolling, the surface's resonance mattered more than the ball's.
- **Sources:** [arXiv](https://arxiv.org/abs/2112.08984), [DAFx archive](https://dafx.de/paper-archive/details/8nGIuMznlirl-AeBOlb1Xg)

### 2.7 Contact mechanics and acoustics background ◇
- **Zheng & James, SIGGRAPH 2011.** Keeps modal vibration active during
  frictional contact (micro-collisions, chattering, contact damping).
  Offline, but it explains why real sliding couples to the modes.
  [Project page](https://www.cs.cornell.edu/projects/Sound/mc)
- **Akay, "Acoustics of friction", JASA 111(4), 2002.** The standard review
  of friction sound, from "roughness noise" (low load, asperity impacts
  weakly exciting modes) to stick-slip and squeal (instabilities). The PDF
  lists a Carnegie Mellon affiliation for the 2002 paper. [PDF (scanned)](https://www.imperial.ac.uk/media/imperial-college/research-centres-and-groups/dynamics/Akay-Acoustics-of-friction.pdf)
- **Dang et al.** Direct numerical simulation of sliding rough surfaces:
  roughness noise from asperity-scale shocks and pinning-release events.
  [arXiv](https://arxiv.org/pdf/1310.5252)

---

## 3. Recommendation for this project

A practical real-time stack, cheapest first, each layer citable:

| layer | what | source | cost |
|---|---|---|---|
| 1. surface profile | precomputed 1-D profile wavetable per surface (fractal β + 1–3 resons), read at **position** x(t) = ∫v dt, not regenerated noise | FoleyAutomatic; Agarwal (profiles) | one table lookup per sample |
| 2. curvature limit | soft-clip the profile's second derivative (tanh, limit set by normal force), then a short smoothing | Agarwal 2021 | a few operations per sample |
| 3. micro-impacts | sparse impulse train: impact when the traced path crosses a threshold or local peak; heavy-tailed amplitudes; "grain" = density | Conan 2014; SDT grain | cheap |
| 4. normal force | slow modulation of F_N (object wobble, hand) and level ∝ √(v·F_N) | Agarwal; FoleyAutomatic | trivial |
| 5. meso texture | ridges from the game's normal/height map → impulses at crossings | Ren 2010 | engine-side |
| 6. squeak | elasto-plastic friction coupled to a few modes, only where needed (doors, rubber on glass) | Avanzini 2005; SDT | moderate; opt-in |

Also cap the floor modes driven by sliding (≈ 2–4 kHz). Fine surface detail
couples poorly into a large plate, and many dense modes driven by
broadband force turn into a noise floor.

**Why reading the profile by position matters:** sliding over the same
patch twice sounds the same, speed-up raises the pitch of the scrape, and
stopping freezes it. That makes a "surface" the listener can track. It is
also the property designers can see (a texture) and control (β, resons,
grain).

**Suggested next experiment:** a Python A/B on the existing slide scenes.
Compare the current noise, profile + speed-scaled resons (layer 1),
layers 1 + 2 + 3, and layers 1–4. Each version needs one new function in
`core/friction.py` and one variant in `scenes/slide.py`.

---

## 4. Implemented: model B (`core/slide_profile.py`), first A/B results

Rendered next to the old exciter in `renders/scenes/slide/` (`..._A-noise-model.wav`
vs `..._B-profile-model.wav`, one shared gain).

**How model B covers layers 1–4:**
- **Profile read by position.** Each floor has a fixed profile: fractal
  roughness (PSD ∝ k^−γ, γ 2.4–2.8, i.e. Hurst exponent 0.7–0.9), plus a
  texture resonance at spatial frequency k_r (heard at k_r·v), plus meso
  features: 12 cm board grooves on the wood floor, a 25 mm tread pattern on
  the steel plate.
- **Contact-patch averaging.** The profile is smoothed with a Gaussian of
  σ = 0.1 mm. Without it, the contact "followed" detail finer than any real
  contact patch, the force was dominated by the finest roughness, and it
  still sounded like hiss. The smoothing also removes aliasing, so there is
  no hard band edge.
- **Curvature limit, in physical form.** A contact of effective mass m_p
  (10 g, preset) pressed by N follows the surface downward only while
  `z_tt > −N/m_p`. Otherwise it lifts off and flies, and each landing is a
  Hertz micro-impact. Upward following is soft-limited with tanh
  (Agarwal-style) at 10·N/m_p.
- **Normal-force wobble.** ±15 %, below 6 Hz. It moves the lift-off
  threshold.

| floor | airborne | micro-impacts/s | force kurtosis (3 = Gaussian) |
|---|---|---|---|
| wood floor | 8 % | ≈ 650 | ≈ 33 |
| concrete (rougher, h_rms 60 µm) | 32 % | ≈ 1200 | ≈ 10 |
| steel deck (smooth + tread) | 5 % | ≈ 430 | ≈ 59 |

**What is visibly different from model A** (`figures/scenes_slide.png`):
- the wood floor's board-joint ticks recur once per 12 cm of travel;
- the spectrum darkens smoothly with speed;
- the slide breaks into separate clicks as it stops;
- on steel, the texture band glides from ≈ 3.7 kHz down to 0 as the plank
  slows, with sparse tread clicks;
- concrete stays close to A, because the slab is silent and the plank's own
  modes shape everything.

**Caveat (measured).** The *rendered* audio still has near-Gaussian
statistics (detrended kurtosis ≈ 2.3–3.6 for both A and B), even though the
B force is strongly impulsive. Hundreds of landings per second each start
floor and plank modes that ring for 50–100 ms, and the overlapping tails
add up to noise-like statistics. So the difference between A and B lies in
**structure over time and frequency** (gliding texture, rhythm, sparse
clicks at low speed), not in the sample statistics. That needs listening
or a perceptual test to judge.

**Open knobs, all presets:**
- contact mass m_p;
- contact-patch σ;
- per-floor h_rms, γ, k_r and features.

Natural next steps:
- **Ablation renders** (no lift-off, no patch averaging, no wobble), to
  repeat Agarwal et al.'s "which ingredient matters" test with our own
  listening.
- **Derive m_p and σ from the slider's local impedance and the Hertz
  contact radius** instead of presets.
- **Record a real plank sliding on each floor** to compare against.

**Follow-up (2026-10-27):** compared with real recordings in
[`rolling_sliding_vs_recordings.md`](rolling_sliding_vs_recordings.md).
The "near-Gaussian" render statistics above turned out to be what real
slides have. The audible problems were the plank's mode lines, a
profile-interpolation bug (the arcs) and single-track clicking. Model C in
`scenes/drag.py` fixes them.
