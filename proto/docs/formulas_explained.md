# Guide to the Formulas and Models in Each Stage

> Corresponding code: modules under `proto/core/`; validation scripts: `proto/stages/`.

## Citation and Provenance Convention

Every displayed formula below is followed by a **Formula provenance** note using one of these labels:

- **Literature** — stated in, or directly adapted from, a cited source;
- **Derived here** — an algebraic or discrete-time implementation derived for this prototype from a cited continuous model;
- **Project heuristic** — a deliberately simplified or ear-tuned rule used by this prototype, not a formula claimed by the cited paper;
- **Standard mechanics/DSP** — a textbook identity included without claiming that it originated in the project references.

Reference numbers correspond to the complete bibliography at the end. 

**The central idea of this document**: `q` is what you ultimately hear. The instantaneous displacement of a particular vibration pattern on an object's surface. Plotted over time, it is a decaying sine wave of the sound waveform itself. Every other formula (contact force, friction noise, and grain triggering) answers the same question of **what kind of force should push these little mass-and-spring systems?**

---

## Stage 1 · Modal Oscillators (Modal Bank) — `core/modal_bank.py`

**Analogy**: Strike a bowl and it vibrates simultaneously in several fixed patterns. Each pattern is one mode, represented as a small mass attached to a spring. The sound you hear is the sum of these oscillating masses.

```
q̈ₙ + 2·dₙ·q̇ₙ + ωₙ²·qₙ = f(t) / mₙ
```

**Formula provenance — Literature.** This is the standard mass-normalized modal oscillator used in modal sound synthesis; see van den Doel & Pai [1] and the contact-driven modal framework in van den Doel, Kry & Pai [2]. Avanzini & Rocchesso also write the struck resonator as one or more second-order oscillators driven by the contact force [4, Eqs. 4–5]. The notation here matches `core/modal_bank.py`.

**How to read it**: the mass's acceleration, plus a friction term that slows it down, plus a spring term that pulls it back, equals the external force divided by mass. This is simply Newton's second law, F = ma, with terms rearranged.

| Symbol | Meaning |
|--------|---------|
| qₙ | How far the nth mass is displaced from rest at this instant (how far the bowl's surface is pushed inward or outward). Plotted over time, it is a decaying sine wave—the sound itself |
| q̇, q̈ | A dot over q means a derivative with respect to time. One dot is velocity; two dots are acceleration |
| ωₙ | The oscillation rate set by the spring stiffness: the pitch of this mode. ω = 2πf |
| dₙ | The amount of damping: how long the sound rings. A larger d makes the sound disappear faster, with amplitude shrinking as e^(−d·t) |
| mₙ | The mass, or inertia. The heavier it is, the less it moves under the same force |
| f(t) | The external striking force as it changes over time. Stage 3 calculates the shape of this force |

**Digital implementation (impulse-invariant discretization)**:

```
y[i] = a₁·y[i−1] + a₂·y[i−2] + b₁·f[i−1]

a₁ = 2·e^(−d·T)·cos(ω_d·T)     a₂ = −e^(−2·d·T)
b₁ = T·e^(−d·T)·sin(ω_d·T)/(m·ω_d)     ω_d = √(ω₀² − d²)
```

**Formula provenance — Derived here.** The continuous modal oscillator comes from [1, 2, 4]. These particular recurrence coefficients are the prototype's impulse-invariant discretization, obtained by sampling the oscillator's impulse response. They are not quoted verbatim from those papers. Including `b₁` here makes the documentation match `ModalBank.__init__()` exactly.

A computer cannot solve the equation continuously, it can only record one value every 1/44100 second (`T` is one sample interval). This recurrence says that remembering the previous two values is enough to calculate the next one—two old points are sufficient to extend a decaying sinusoid by one step. The coefficients a₁ and a₂ are derived from ω and d so that the digital version has **exactly the same** pitch and decay as the continuous equation (its pole locations are exact). That is why the Stage 1 gate agrees to within 0.1%.

---

## Stage 2 · Material = One Number (`tanφ`) — `core/materials.py`

**Analogy**: Tap a glass and it rings for a long time; tap rubber and the sound dies immediately. The main difference is not pitch but how quickly the sound decays. Klatzky, Pai & Krotkov [3] found that decay contributed more strongly than frequency to material judgments, while also cautioning that both variables mattered and interacted in categorization.

```
dₙ = π·fₙ·tanφ        ⟺        τₙ = 1 / (π·fₙ·tanφ)
```

**Formula provenance — Literature.** Klatzky, Pai & Krotkov [3, Eqs. 1–2] write the frequency-dependent damping as `b(f) = π·tan(φ)·f` and the 1/e decay time as `t_e = 1/(π·f·tan(φ))`. This implementation renames `b(f)` to `dₙ` and `t_e` to `τₙ`; the mathematics is unchanged.

**How to read it**: a mode's loss per second (`d`) equals its frequency multiplied by a material constant. Why does frequency matter? Each internal bending cycle loses a little energy. A mode that vibrates faster undergoes more bending cycles per second and therefore loses energy faster. In every material, **high frequencies die away first**; only the rate differs.

| Symbol | Meaning |
|--------|---------|
| tanφ | The material's “internal friction”: the proportion of energy lost in each bending cycle. This is the only value adjusted for the entire material system |
| τₙ | Decay time: the number of seconds required for amplitude to fall to 37% (1/e) of its original value. It is the reciprocal of d |

Material table: metal 0.0002 → glass 0.0008 → wood 0.012 → plastic 0.05 → rubber 0.15 (a larger tanφ means a shorter ring). The set of modal frequencies, or the “shape”, does not change at all. **These five numbers are order-of-magnitude project presets for listening tests, not measured values copied from [3].** Klatzky et al. motivate the single-parameter model and cite earlier material-loss measurements, but the exact preset table belongs to this implementation.

### Q&A: Metal has high frequencies and vibrates more times per second, so why does it have low internal friction?

**Separate “per second” from “per cycle”**: `d = π·f·tanφ` already has the structure “loss per cycle × cycles per second.” `tanφ` is the percentage of stored energy lost during one complete bending cycle (independent of frequency), while `f` is the number of cycles per second. Multiplying them gives the decay rate per second. The intuition that “faster vibrations die faster” is already built into the formula: within a single material, high-frequency modes really do disappear first. Metal and rubber differ not in frequency but in their loss per cycle, which differs by three orders of magnitude.

For a numerical example, consider the same 5000 Hz mode: metal with tanφ=0.0002 gives τ≈0.3 s, while wood with tanφ=0.012 gives τ≈5 ms. At the same frequency, the ringing differs by a factor of 60, entirely because of tanφ.

**What material property determines tanφ?** At the microscopic scale, it depends on whether internal structures rub against one another. Elastic deformation stores energy in atomic bonds and, ideally, returns all of it. Loss comes from microscopic processes that turn coordinated vibration into heat:

- Metal: an orderly crystal lattice with stiff, elastic atomic bonds; only crystal defects (dislocations, grain boundaries, and thermoelastic effects) leak a little energy → ~10⁻⁴
- Glass: amorphous, but still a rigid network of strong bonds with little internal rubbing → also very low
- Wood: a composite of cellulose fibers and lignin, with friction from microscopic sliding between fibers and chain segments → moderate
- Plastic/rubber: entangled long-chain molecules slide, disentangle, and rearrange—microscopically like stirring honey → extremely high
  (Rubber has its greatest loss near its glass-transition temperature; when frozen rigid, it sounds brittle and rings more clearly when struck.)

**Where the name tanφ comes from**: when a lossy material is stretched periodically, its strain lags behind its stress by a phase angle φ (0° for a purely elastic material, 90° for a purely viscous one). The area of the stress-strain hysteresis loop equals the energy converted to heat per cycle and is proportional to tanφ, so tanφ is naturally a measure of “loss per cycle.”

**A common source of confusion**: a metal's high frequencies are determined by stiffness and geometry (`f ∝ √(E/ρ) × shape factor`), not by loss. A large bell is also metal; it has a low frequency but still rings for a long time. Stiffness (energy storage) and internal friction (energy leakage) are independent properties. Stage 2 relies on exactly this separation: the frequency set controls shape, while tanφ independently controls material.

---

## Stage 3 · Contact Force (Hunt–Crossley) — `core/impact.py`

**Analogy**: When a hammer strikes a table, the impact is not a single instantaneous “click”; it is a short process of compressing the surfaces and then releasing them. A hard ping-pong ball has a short, sharp contact, while a soft rubber ball remains in contact longer and sounds duller.

```
f(x, ẋ) = k·x^α + λ·x^α·ẋ        (while compression x > 0; otherwise 0; clamped to f ≥ 0)
```

**Formula provenance — Literature, with implementation conventions.** Avanzini & Rocchesso [4, Eq. 1] use the nonlinear elastic-plus-dissipative contact law `f = −kx^α − λx^αẋ`; the sign is reversed here because this document reports the nonnegative force magnitude. The `x > 0` contact condition follows the same model. Clamping the result to `f ≥ 0` is a project safeguard for non-adhesive contact. The paper uses `α = 2.8` for its piano-hammer-like example; this prototype's `α = 1.5` setting is instead the classical Hertz exponent for spherical contact, not a value taken from that example.

**How to read it**: contact force equals a spring term plus a loss term. `x` is how deeply the two surfaces compress into one another—like the indentation made by pressing a finger into a balloon. Force exists only while the surfaces are in contact (`x > 0`).

| Symbol | Meaning |
|--------|---------|
| k·x^α | A nonlinear spring: the deeper the compression, the harder it pushes back. α = 1.5 comes from the geometry of spherical contact—as compression grows, the contact area grows and further compression becomes harder, so the exponent is not the 1 used by an ordinary spring |
| λ·x^α·ẋ | Impact loss (like heating modeling clay by squeezing it). Multiplication by x^α makes the loss approach zero at initial contact and just before separation, so the force curve is smooth and does not jump. This is the advantage over a simple “spring plus ordinary damper” |
| ẋ | The rate at which compression depth changes: whether the surfaces are moving farther into each other or springing apart |

**Two-way coupling**:

```
mₛ·s̈ = −f          x = s − Σqₙ
```

**Formula provenance — Literature.** This is the multimode extension of Avanzini & Rocchesso [4, Eqs. 4–5]: penetration is striker displacement minus the summed resonator displacement, and the same contact force decelerates the striker while driving every resonator mode. Signs differ only with coordinate convention.

The force slows and rebounds the hammer (the equation on the left) while simultaneously bending the table by driving every small mass from Stage 1. The compression depth is `x = hammer position − displaced table surface`. When the table bends, the compression changes, which changes the force again.

**Three solution paths** (all in `core/impact.py`):

1. RK4 reference solution: integrate at an oversampled rate (at least 40 steps per contact), then use the analytical free-decay solution for the modes after contact ends;
2. Audio-rate implicit scheme (in the spirit of the K-method): after trapezoidal discretization at 44.1 kHz, the force at the current instant depends on the compression, but the compression also depends on the force at that instant—a delay-free loop. After expressing both `x` and `ẋ` as linear functions of `f`, solve one scalar equation per sample: `f = HC(P − G·f, P_d − G_d·f)`. The future real-time C++ implementation will have this form;
3. Open-loop fallback: first calculate the force pulse from a striker hitting a rigid wall, then feed it to the modal bank as an ordinary input.

**Formula provenance for the implicit equation — Derived here.** Avanzini & Rocchesso [4, Sec. 2.2] identify the non-computable loop, apply the K-method, and solve the force iteratively with Newton–Raphson. The affine `P`, `G`, `P_d`, and `G_d` form above is this prototype's trapezoidal-rule derivation of the same delay-free-loop structure; it is solved with Brent's method in Python.

**Contact-duration estimate (Hertz theory, lossless case with α=1.5)**:

```
τ_H ≈ 2.87 · (m_eff² / (R_eff·E*²·v))^(1/5)      conventional material/geometry form

k = (4/3)·E*·√R_eff
τ_H ≈ 3.21 · (m_eff² / (k²·v))^(1/5)             equivalent force-law form
```

**Formula provenance — Standard Hertz mechanics.** The `2.87` form uses effective mass `m_eff`, effective radius `R_eff`, effective modulus `E*`, and relative normal speed `v`; it is used, for example, in the Hertz pulse model of Chadwick, Zheng & James [8, Sec. 3]. Substituting `k = (4/3)E*√R_eff` for the force law `f = kx^(3/2)` changes the numerical coefficient to approximately `3.21`. Avanzini & Rocchesso derive a more general damped power-law contact-time relation [4, Eqs. 8–9], not this compact lossless Hertz formula.

**Implementation note.** `hertz_contact_time()` currently evaluates `2.87·(m²/(k²v))^(1/5)`. Because its argument named `k` is the force-law coefficient rather than `E*√R_eff`, this is an approximate timestep estimator, not the exact algebraic conversion shown above. It does not determine the rendered force or reported contact time; RK4 measures those from the simulated compression history.

The harder the material (larger `k`) and the faster the impact (larger `v`), the shorter the contact. A shorter contact produces a “sharper” force pulse containing more high-frequency energy. This is the physical origin of why hard objects sound bright, and it is the theoretical curve used in the Stage 3 validation figure.

**A real behavior discovered during implementation**: with a light resonator and strong dissipation, the striker barely rebounds, and the vibrating surface can catch up with it, causing two or three micro-bounces (`info["n_contacts"]`). The monotonic contact-duration trend holds only in the “light hammer striking a heavy resonator” regime (the trend gate uses a modal mass of 0.5 kg versus a striker mass of 8 g).

### Q&A: Is the striker's material considered? (Glass cup on concrete / glass cup on glass / wood against a glass cup)

The current model uses the classic asymmetric “hammer-object” simplification. The struck object has a complete modal bank (shape + tanφ), while the striker is only a point mass—it **does not ring**. Its material enters only through the contact parameters `k`, `α`, and `λ`.

**Half of the answer is already included—inside `k`.** Contact stiffness is physically a property of the pair of surfaces. In Hertz theory,

```
1/E* = (1−ν₁²)/E₁ + (1−ν₂²)/E₂
```

**Formula provenance — Standard Hertz mechanics.** This effective-modulus relation is the conventional two-body Hertz reduction and is also used by Chadwick, Zheng & James [8, Sec. 3]. Each object contributes a term, so **the softer one dominates**.

A felt mallet and an iron hammer striking the same bell do not change the bell's modes; they change `k`, which changes contact duration, pulse sharpness, and the number of modes excited. The current model can therefore already express why wood striking a glass cup sounds duller than one cup striking another by assigning an intermediate value of `k`. Rounded engineering reference values used for intuition—not citation-grade material measurements—are: steel 200 GPa, glass 70 GPa, concrete 30 GPa, wood 10 GPa, plastic 2 GPa, and rubber 0.01 GPa. In “object hitting floor” scenarios, the struck floor's sound is handled separately by the Stage 5 ground layer.

**What is genuinely missing is the striker's own ringing.** When two glass cups collide, both ring; the current model rings only one. There are two ways to add the missing sound:

1. Inexpensive approach (open-loop and sufficient for games): feed the force pulse in `info["force"]` into a second object's modal bank, then sum the two outputs. Object B's surface motion does not feed back into the contact force, so this is not exact, but it captures the main perceptual effect of “two timbres lit up by the same pulse”;
2. Rigorous approach: upgrade the striker to “mass + its own modal bank,” with `x = (s + Σq_A) − Σq_B`, and apply `±f` to the two sides. This only lengthens the RK4 state vector; the framework remains the same. It would make a suitable thesis extension section, along with an argument for why the real-time plug-in can use the open-loop approximation.

Planned implementation: make `k` a material-pair lookup based on the `E*` formula, and add a supplementary glass-on-glass dual-ring render using the open-loop method.

---

## Stage 4a · Friction / Sliding — `core/friction.py`

**Analogy**: Under a microscope, a tabletop is covered in tiny hills. Sliding a box across it means striking thousands of these hills every second. The sum of all those microscopic impacts becomes a “shhh” noise.

```
loudness ∝ (v / v_ref)^1.2          cutoff frequency = 120 + 9000·v  (Hz)
```

**Formula provenance — Project heuristic.** Turchet [6, Sec. 3.2.3] describes a substantially more detailed bristle/fractal-noise friction model governed by a differential equation. The power law, exponent `1.2`, 120 Hz floor, and 9000 Hz-per-(m/s) slope above are not formulas from Turchet; they are this prototype's cheaper speed-to-level and speed-to-bandwidth mapping, chosen for smooth real-time control and tuned by ear.

Faster sliding means hitting more hills per second (greater loudness), and each impact is more abrupt (sharper, with more high-frequency content, and therefore brighter). Both effects are driven by the sliding speed `v`; below 1 cm/s, the sound fades smoothly to silence. The generated noise is then fed into the Stage 1 modal bank so that it acquires the resonant timbre of “this particular box.” Optional stick-slip behavior modulates the noise with a relaxation oscillator whose rate is proportional to sliding speed, producing a periodic squeak.

### Q&A: Where do the two numbers in the cutoff frequency `120 + 9000·v` come from?

They are ear-tuned heuristic parameters, not constants from a paper, but each has a physical interpretation:

**The slope 9000 (Hz per m/s) represents surface roughness.** Moving at speed `v` over asperities spaced by distance `λ` produces impacts at the fundamental frequency `f = v/λ`. Frequency therefore increases linearly with speed, which is the physical basis for `cutoff ∝ v`. Solving backward gives `λ = 1/9000 ≈ 0.11 mm`, implicitly assuming one small surface bump every 0.11 millimeters—roughly the scale of an ordinary tabletop or wood surface. `cut_per_v` is fundamentally a surface-material parameter: set it lower for a coarse, rumbling surface and higher for a polished, hissing surface.

**Formula provenance for `f = v/λ` — Standard kinematics.** This is the encounter rate for features spaced by `λ`, used here only as a physical interpretation of the heuristic cutoff slope. The claim that `λ≈0.11 mm` represents a typical tabletop is an intuitive design interpretation, not a measured value reported by [6].

**The 120 Hz base value is both a numerical and perceptual safety floor.** Without a lower bound, `v→0` would make the one-pole coefficient `a = exp(−2π·cutoff/fs) → 1`, turning the filter into an integrator with an infinitely long tail. Perceptually, an object about to stop should produce a low rumble rather than collapse to zero bandwidth. The choice of 120 rather than 80 or 200 is purely ear-tuned.

The two values are the `cut_min` and `cut_per_v` parameters of `friction_exciter()`. The design intent is to provide one pair of values per surface, in the same way that tanφ describes material. The upper limit is clamped to `0.45·fs` to stay below Nyquist.

---

## Stage 4b · Aggregate Layer (Gravel/Dirt/Grass, PhISEM v2) — `core/aggregate.py`

**Analogy**: Stepping on a pile of gravel makes many stones collide with one another over a short time. The timing, loudness, and pitch of every collision are random.

```
P(a collision in this sample) = density / fs      loudness ~ Exp(1)      pitch ~ LogUniform(lo, hi)
```

**Formula provenance — Mixed.** Cook's PhISM/PhISEM framework [5] and Turchet's summary [6, Sec. 3.2.1] motivate stochastic particle events with a constant per-step probability, i.e. a Poisson process. `P ≈ density/fs` is the prototype's discrete-time Bernoulli approximation to that process. The exponential **amplitude** draw and log-uniform pitch draw are project heuristics; the exponential quantity explicitly discussed by Turchet is the distribution of waiting times between Poisson events, not grain amplitudes. Per-grain pitch randomization is a v2 change introduced after listening tests.

At every sample, a die roll decides whether two stones collide—the greater the density, the more frequent the collisions. Collision amplitudes are drawn from an exponential distribution: many quiet events and an occasional loud one, as in reality. The **key change in v2** is that each grain's pitch is also drawn randomly because real stones have different sizes. In v1, every grain passed through the same fixed resonant filter. Hundreds of same-pitch “dings” combined into something that sounded like a resonating drumhead; that is the source of the perceptual “awning/drum-skin” quality.

```
bed = band-passed white noise × √(smoothed energy envelope)      out = (1−mix)·grains + mix·bed
```

**Formula provenance — Project heuristic.** The continuous AM-noise bed, square-root envelope mapping, and `mix` blend are v2 design additions. They are inspired by the perceptual goal of aggregate-surface synthesis in [5, 6] but are not equations from either source.

Grass is different: rubbing grass blades do not produce “dings.” The sound is fundamentally a continuous rustle formed from a vast number of microscopic friction events. The model takes high-frequency white noise and modulates its amplitude with fluctuations in grain energy—random amplitude modulation. The grass preset uses `mix = 0.8`: 80% of the result is this noise and 20% is fine, brittle impacts.

---

## Stage 5 · Ground Layer (Simplified Qu & James 2019) — `core/ground.py`

**Analogy**: The same cup falling on a thin wooden floor produces an extra low “thud” compared with falling on solid concrete. That is the entire floor panel sounding, not the cup.

```
impulse area = m·v  →  several heavily damped 55–240 Hz modes   +   low-pass noise × e^(−t/0.012)
```

**Formula provenance — Mixed, mostly a project approximation.** `∫f(t)dt = Δp ≈ m·v` is the standard impulse–momentum relation. Qu & James [7] derive ground sound from a regularized elastic half-space response and acoustic radiation; they do **not** propose this low-mode bank or the 12 ms exponential noise burst. The 55–240 Hz modes, decay rates, noise filter, and `0.012` s value are project presets standing in for a perceptually useful floor “thump.” Qu & James motivate keeping ground radiation as a distinct sound component, while the acceleration-noise concept is treated explicitly by Chadwick, Zheng & James [8].

The floor is approximated as a large, heavy plate with low resonant frequencies and rapid energy dispersal, producing a low, short “thud.” Its weight is controlled by the falling momentum `m·v`. A 12-millisecond flash of noise adds fine “clack” detail at contact. This is only a perceptual stand-in for acceleration noise, not a reduced derivation of the acceleration-noise field in [8] or the ground-radiation solution in [7]. See the docstring in `core/ground.py` for the omitted components, including the elastic half-space solution, radiation directivity, and detailed force coupling. Qu & James explicitly note that finite-depth floors and building resonances are outside their half-space model [7, Sec. 6]; the modal floor approximation here is therefore an added real-time design choice.

---

## Stage 6 · Simulated Physical Trajectories — `sim/trajectories.py`

**Analogy**: Instead of using a game engine, apply high-school physics directly to calculate when a ball lands and how fast it is moving at impact, then feed this sequence of numbers into all the preceding models.

**Bouncing ball**:

```
v₀ = √(2·g·h₀)        v_{k+1} = ε·v_k  (ε = 0.72)        Δt_k = 2·v_k / g
```

**Formula provenance — Standard mechanics plus a project parameter.** The first and third expressions are constant-gravity kinematics, and the second is the definition of a constant coefficient of restitution. The chosen value `ε = 0.72` is a demo parameter, not a value taken from the cited contact-sound papers.

Free fall gives the first impact speed. After each bounce, only 72% of the speed remains (coefficient of restitution `ε`). The time to rise and fall again is `2v/g`. The speed decreases and the intervals become shorter, producing the familiar rhythm of “faster and quieter with every bounce.” Each landing triggers one Stage 3 impact plus the Stage 5 ground layer.

**Sliding box**:

```
v(t) = v₀ − μ·g·t
```

**Formula provenance — Standard mechanics.** This follows from constant Coulomb kinetic friction on level ground, `a = −μg`. It generates a control trajectory for the sound model; it is not Turchet's friction-force equation.

Friction decelerates the box uniformly until it stops (`μ` is the coefficient of friction). Its velocity curve drives Stage 4a directly, so the sliding sound naturally becomes quieter and duller before fading to silence.

**Tumbling**: a random Poisson-burst event stream of `(time, velocity)` pairs used to stress-test overlapping voices. **This is a project test-signal heuristic**, not a physical tumbling model taken from a cited paper.

---

## References

[1] K. van den Doel and D. K. Pai, “The Sounds of Physical Shapes,” *Presence: Teleoperators and Virtual Environments*, 7(4), 382–395, 1998. [DOI](https://doi.org/10.1162/105474698565794) · [author publication list](https://www.cs.ubc.ca/labs/lci/papers/1998.html)

[2] K. van den Doel, P. G. Kry, and D. K. Pai, “FoleyAutomatic: Physically-Based Sound Effects for Interactive Simulation and Animation,” *Proceedings of SIGGRAPH 2001*, 537–544, 2001. [DOI](https://doi.org/10.1145/383259.383322) · [PDF](https://www.cs.ubc.ca/labs/lci/papers/docs2001/van-foleyautomatic.pdf)

[3] R. L. Klatzky, D. K. Pai, and E. P. Krotkov, “Perception of Material from Contact Sounds,” *Presence: Teleoperators and Virtual Environments*, 9(4), 399–410, 2000. [DOI](https://doi.org/10.1162/105474600566907) · [PDF](https://www.cs.ubc.ca/labs/lci/papers/docs2000/pai-KlaPai00.pdf)

[4] F. Avanzini and D. Rocchesso, “Modeling Collision Sounds: Non-Linear Contact Force,” *Proceedings of DAFx-01*, 2001. [PDF](https://avanzini.di.unimi.it/downloads/publications/avanzini_dafx01_revised.pdf)

[5] P. R. Cook, “Physically Informed Sonic Modeling (PhISM): Synthesis of Percussive Sounds,” *Computer Music Journal*, 21(3), 38–49, 1997. [DOI](https://doi.org/10.2307/3681012) · [Princeton Sound Lab index](https://soundlab.cs.princeton.edu/research/phymod/)

[6] L. Turchet, “Footstep Sounds Synthesis: Design, Implementation, and Evaluation of Foot–Floor Interactions, Surface Materials, Shoe Types, and Walkers' Features,” *Applied Acoustics*, 107, 46–68, 2016. [DOI](https://doi.org/10.1016/j.apacoust.2015.05.013) · [PDF](https://www.lucaturchet.it/PUBLIC_DOWNLOADS/publications/journals/Footstep_sounds_synthesis.pdf)

[7] A. Qu and D. L. James, “On the Impact of Ground Sound,” *Proceedings of DAFx-19*, 2019. [PDF](https://graphics.stanford.edu/papers/ground/assets/GroundSound_Combined.pdf)

[8] J. N. Chadwick, C. Zheng, and D. L. James, “Precomputed Acceleration Noise for Improved Rigid-Body Sound,” *ACM Transactions on Graphics (SIGGRAPH 2012)*, 31(4), 2012. [project page and PDF](https://www.cs.cornell.edu/projects/Sound/impact/)
