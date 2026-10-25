# Plan & Brainstorm: from prototype to designer-facing plugin

Working document (started 2026-10-25). Part 1 records decisions already made
in code. Parts 2–3 are the open design and implementation questions, each
with a recommendation. Items marked **(verify)** come from memory and should
be checked against the source before going into the thesis.

---

## Part 1 — Quick fixes: what was found and decided

### 1.1 Materials + impact are one layer (done)
`stage2_materials` and `stage3_impact` are now merged into
`stage2_object_impact` (old stages 4–6 → 3–5).

**Is impact just modal + velocity + hardness?** Yes. `simulate_impact` adds
no resonator. It turns (striker mass `m`, velocity `v`, stiffness `k`, `α`,
`μ`) into a contact-force pulse, and that pulse drives the object's own
modal bank. Two refinements:
- **Hardness is not free.** `k` follows from the two contacting materials
  and the local curvature (Hertz: `k = 4/3·E*·√R`, now
  `impact.hertz_stiffness`). A designer never needs to type `k`. It comes
  from "wood object on concrete floor", with an optional "hardness offset".
- **Material enters twice.** Once as tan φ (how long it rings) and once as E
  (how hard the contact is, and with ρ how high it rings for a given size).
  The old code only had the first.
- **Dropping an object** maps onto the same model: the striker is the
  object's own rigid-body mass and the floor is the contact partner (stage
  2C). The floor's own sound is the separate ground layer.

### 1.2 Where did the modal data come from? (done)
`materials.SHAPES` (`generic`, `wood_block`, `ceramic_mug`, `metal_pot`) is
**hand-authored**: plausible partial lists, not derived from any 3D shape.
None of them matches the ratio series of a bar, plate or shell. They are
fine for tests of decay and materials but cannot be defended as "the sound
of a mug".

`core/shapes.py` now derives mode sets from geometry + E/ρ/ν:

| primitive | theory | covers |
|---|---|---|
| `bar` | free-free Euler–Bernoulli beam, rectangular section | planks, sticks, rulers, bricks (roughly) |
| `tube` | same with annular section + ring modes if hollow | rods, pipes, poles, cans (roughly) |
| `disc` | free-edge Kirchhoff circular plate (Leissa table **(verify)**) | plates, lids, pans (bottom), cymbal-ish |

**Do we want everything from simple geometric shapes?** Recommended: yes as
the base, in three tiers:

1. **Tier 1, analytic primitives** (bar, rod, pipe, rectangular plate,
   disc, ring). Closed form, so Size/Thickness/Hollowness are live sliders
   at zero cost. Already started.
2. **Tier 2, precomputed shape families** for shapes with no closed form
   (cube/block, sphere/ball shell, cup/bowl, bottle, thin box/crate,
   frying pan). Run FEM **once per family** offline (e.g. scikit-fem or
   FEniCS + a tet mesher) and store **dimensionless** eigenvalues and
   mode-shape gains at a few strike points. Linear elasticity scales
   exactly: for geometrically similar solids `f ∝ (1/L)·√(E/ρ)`, so one
   solve serves every size and every material (only ν changes the ratios
   slightly; store 2–3 ν values). Precedent: O'Brien et al. 2002 (modes
   from meshes) and Raghuvanshi & Lin 2006 (budgeting).
3. **Tier 3, user/measured.** `analysis/mode_extract.py` (modes from a
   recorded tap) or a mesh imported in an editor tool (FEM in the editor,
   not at runtime). This is the "custom" escape hatch.

Caveat for bricks/rocks/solid blocks: their low modes are high and heavily
damped, so their sound is mostly contact transient + floor + debris. A
rough bar/block approximation is perceptually enough there; precision
matters most for ringing objects (metal, glass, ceramic).

### 1.3 Model bank: fixed list vs user-defined?
> Expanded into a full, sourced list with materials, formulas and computed
> default modes: [`archetypes.md`](archetypes.md).

Recommend **a curated archetype list built on the primitives, with every
archetype editable**. That gives one mental model and no separate "custom
mode":

```
Archetype (list) ──> primitive + default dims + default material
      │                       │
      └─ designer sees: Size · Material · Hollowness/Wall · Ring (damping) · Brightness
                              └─ Advanced (collapsed): raw dims, E/ρ/tanφ, mode table, strike pos
```

Starter archetype list (≈20, each just a preset over Tier 1/2):
wood plank, wood stick, wood crate*, wood block; metal pipe, metal rod,
metal sheet, metal can*, metal pot/pan*; glass bottle*, glass pane,
ceramic plate, ceramic mug*; plastic bottle*, plastic crate*, plastic toy;
rubber ball; brick, rock; cardboard box*. (* = needs Tier 2 or an air
cavity.)

Rules that keep it from getting confusing:
- **Designers move perceptual macros, not physics.** "Size" scales all
  dims; "Ring" scales tan φ; "Hollow" scales wall thickness. The physics
  parameters are derived.
- **Picking an archetype never hides anything.** Advanced shows the exact
  numbers it produced, so there is no "magic" preset.
- **Name archetypes by everyday objects**, not by primitives ("metal pipe",
  not "annular beam").

### 1.4 Aggregate grass (done, needs ears)
v2 grass was 80 % stationary 2.8–11 kHz noise under a slow envelope. Its
spectrogram is a uniform wash, heard as hiss or steam. v3 is layered:
swish grains (10–60 ms, soft attack, own band in 0.7–6 kHz), sparse
sub-ms crackles, and a thin bed, with lognormal amplitudes. The centroid
moved from 7.2 to 3.9 kHz and the 10 ms level fluctuation doubled
(1.6 → 3.4 dB). **Listen to `stage3_aggregate_grass.wav` vs
`stage3_aggregate_grass_v2.wav`.** The next real improvement needs a
recorded grass footstep in `recordings/` to tune against.

Still open for all aggregate surfaces: the stage's footstep envelope is two
slow Gaussians. Real steps have a sharp heel strike followed by a roll. A
better excitation envelope (or driving from the ground-contact force of the
physics engine) will help gravel and dirt too.

---

## Part 2 — Defining the project

### 2.1 Use cases: scope the thesis
Proposed priority (★ = core thesis scope):

| use case | exciters needed | status |
|---|---|---|
| ★ drop / single impact | impact + ground | done (stage 2C/4) |
| ★ bounce & settle | impact sequence | done (stage 5) |
| ★ slide / scrape | friction | done (stage 3) |
| ★ **roll** | rolling exciter (micro-impacts filtered by surface profile; van den Doel 2001, Rath & Rocchesso 2005 **(verify)**) | **missing**, and needed for throw/drop of round objects |
| ★ throw & tumble | impact + roll + slide switching | stage 5 has impacts only |
| footsteps on aggregate | aggregate | done (grass needs work) |
| contact damping (object resting on floor stops ringing faster) | per-mode damping multiplier while in contact (Zheng & James 2011) | missing, cheap |
| both objects ring (cup on cup) | two modal banks, one contact | see `two_body_impact_related_work.md` |
| break / fracture | crack transient + spawn debris objects | stretch goal |

Suggested framing: *"Real-time, designer-controllable procedural sound for
rigid-object contact (impact, bounce, slide, roll) in game engines."*
Fracture is future work unless time allows.

### 2.2 Are we limited to specific materials? Hollow vs solid?
Modal synthesis is not tied to a fixed list. A material is just
(tan φ, E, ρ, ν). It works well when the object **rings linearly**:
metal, glass, ceramic, stone, hard plastic, wood. It degrades when:
- **Very lossy / soft** (rubber, foam, cloth, cardboard): modes are nearly
  overdamped, and the sound is dominated by the contact transient, the
  *other* object and the floor. Treat these as "exciter-like": they mainly
  set `k`/contact time, and the surface carries the sound.
- **Nonlinear** (thin sheet metal oil-canning, crashes, rattling parts):
  needs extra models (mode coupling, rattle = repeated micro-impacts).
- **Composite / filled** (liquid in a bottle, a box full of stuff): needs
  extra layers.
- **Damping model.** tan φ makes decay strictly proportional to frequency.
  Graphics work often uses Rayleigh damping `d = (α + βω²)/2` (e.g. O'Brien
  2002). Worth adding as an option because wood and plastic rarely fit a
  single line.

**Hollow vs solid does matter**, in four audible ways:
1. **Pitch.** Same outer size, hollow → higher bending modes (`I/A` grows;
   up to +6 semitones for thin walls; stage 2C shows +5.1 semitones,
   725 vs 539 Hz).
2. **Mass.** Hollow is lighter, so it moves more for the same force
   (louder, longer contact relative to its mass).
3. **Shell modes.** Thin walls add ring/breathing modes (the "clang" of a
   pipe or can) that a solid object does not have.
4. **Air cavity.** Bottles and boxes have a Helmholtz/cavity resonance,
   `f ≈ c/(2π)·√(A/(V·L_eff))`, which is cheap to add as one extra mode.

→ Expose **"Hollow / Wall thickness"** as a macro on archetypes where it
applies (tube, box, sphere, bottle).

### 2.3 IR convolution on top of modal synthesis?
Two different things get called "IR":

| use | what | cost | recommendation |
|---|---|---|---|
| **Space/room IR** | convolution reverb on the mix bus | one instance for all voices; built into FMOD and Wwise | **yes, trivial**, but it is a mix decision, not part of the model |
| **Body/coloration IR** (commuted synthesis, cf. Smith; Karjalainen) | convolve each voice with a short recorded object IR | per-voice FFT convolution; fine if IR ≤ ~20–50 ms, expensive for long IRs × many voices | **experiment**: may add realism ("texture") the clean modes lack |
| **Replace modes with recorded IR** | force pulse ⊛ recorded tap | cheapest realism | loses Size/Material control, so it defeats the point; keep only as a baseline in the evaluation |

Alternatives that give the same "realistic grit" more cheaply:
- **Modal + residual.** Extract modes from a recording (Tier 3); the
  leftover noisy residual becomes a short sample layered on the onset (in
  the spirit of example-guided modal synthesis, e.g. Ren, Yeh & Lin 2013
  **(verify)**).
- **Transient layer.** A tiny recorded or noise-based attack (5–20 ms) per
  material, blended under the modal tail. This is common practice in game
  audio and very cheap.

**Difficulty:** in Python it is one `scipy.signal.fftconvolve`, so it is a
1-day A/B experiment (modal vs modal ⊛ short IR vs modal + transient layer
vs recording). In real time a per-voice partitioned convolution is
moderate work; FMOD and Wwise already ship convolution effects that can be
tried on a group bus first.

### 2.4 Making it intuitive for sound designers
Recommended structure: **the object is defined once, behaviours come from
physics, surfaces are separate assets.**

```
[Sound Object asset]       Material ▸ Archetype (filtered by material) ▸ Size ▸ Hollow ▸ Ring ▸ Variation
[Surface asset]            Concrete / Wood floor / Tile / Metal grate / Dirt / Gravel / Grass / Carpet
[Interaction (automatic)]  impact v, slide speed, roll speed, contact point  ← from the physics engine
                           k = Hertz(object material, surface material) · hardness offset
[Fracture (later)]         Breakable flag ▸ crack transient + N debris = smaller instances of same object
```

Why **material first, then shape**:
- Material is the most salient category for listeners (Klatzky et al. 2000)
  and designers already think "metal hit", "wood hit".
- Material and shape are already orthogonal in the code (`shape ×
  material`), so the UI can filter archetypes by material (Metal → pipe,
  sheet, can, pot, rod).
- A **"generic <material>"** archetype per material gives the fast path:
  pick "Wood" and you are done. Designers who care pick "wood crate" and a
  size.
- **Fracture is not a separate system to choose up front.** It is a
  behaviour flag on the same object (bricks, rocks and planks are
  archetypes). On break, the debris pieces are smaller copies of the parent
  (higher pitch, the same material), so it reuses everything.

Also map the engine's own physical materials (Unity `PhysicMaterial`,
Unreal `UPhysicalMaterial`) to sound materials, so a level that is already
tagged gets sound "for free".

Proposed designer macro → physics mapping (to validate with 2–3 designers):

| macro | drives |
|---|---|
| Material | tan φ, E, ρ, ν (preset) |
| Size | all dimensions × s → f ∝ 1/s, mass ∝ s³ |
| Hollow | wall thickness / ring modes / cavity mode |
| Ring | tan φ multiplier (dead ↔ ringy) |
| Brightness | strike-position bias + mode-count cap + hardness offset |
| Weight | mass multiplier (contact time, loudness) |
| Variation | per-hit random strike position / ±cents mode jitter (no machine-gun) |

---

## Part 3 — Implementation and builds

### 3.0 Prerequisite: a C++ core shared by every target
Before any engine work, port the DSP to **one engine-agnostic C++ library**
(no FMOD/Wwise headers): modal bank (complex one-pole per mode, SIMD-able),
implicit Hunt–Crossley with 2–3 Newton iterations, friction, aggregate
grains, ground layer, shape primitives + Hertz. Then:
- **Golden-file tests:** pybind11-wrap the core and compare against the
  Python renders (this prototype becomes the reference implementation).
- Every plugin (FMOD, Wwise, MetaSounds) is then a thin wrapper, and the
  thesis can report one algorithm across all hosts.

### 3.1 Unity + FMOD (recommended first target)
- The FMOD **DSP plugin API** is a single `FMOD_DSP_DESCRIPTION` plus
  callbacks, built to a `.dll`. It is loaded in FMOD Studio (plugins folder)
  and in Unity (registered in FMOD settings as a dynamic plugin) **(verify
  current FMOD 2.03 docs)**.
- Game side: a `ContactSoundEmitter` MonoBehaviour. `OnCollisionEnter` →
  impact (`collision.relativeVelocity`, `collision.impulse`, contact
  point/normal). `OnCollisionStay` → tangential relative speed for slide and
  roll. Engine `PhysicMaterial` → surface asset.
- **Event model decision:** prefer **one persistent voice per object**, with
  impacts passed in as timestamped events (FMOD data parameter, struct of
  hits), over one event instance per hit. It is physically right (re-striking
  a ringing object adds to its state; contact damping is possible) and it
  spends CPU once per object instead of once per hit.
- Expected friction: FMOD parameters are not sample-accurate, so sub-block
  hit timing has to be carried inside the data payload.

### 3.2 Same plugin inside Unity via the middleware?
Yes, that is the normal path. The FMOD plugin built in 3.1 *is* what runs
in Unity. Build it once for the Studio authoring tool and once for each
runtime platform (Windows first).

### 3.3 CPU and real-time behaviour tests
Back-of-envelope: one mode ≈ 6–8 flops/sample. 50 modes × 48 kHz ≈
15–20 MFLOP/s per voice, which is well under 1 % of a modern core even
scalar, so dozens of voices are realistic. Measure, don't assume:

| test | metric |
|---|---|
| modes × voices sweep (C++ benchmark) | µs per 512-sample block; "voices per 1 % core" |
| contact solver | Newton iterations per hit; worst case at k=1e12 |
| pile-collapse scene (100 objects) | peak voices, CPU spikes, voice stealing |
| block size 64–1024 | output identical regardless of block size (sub-block event timing) |
| physics tick 50 Hz vs audio rate | slide/roll speed interpolation and smoothing; no zipper noise |
| contact chatter | debounce: min impulse, min interval per object pair, resting-contact suppression |
| culling / LOD | drop modes below −80 dB or out of budget (Raghuvanshi & Lin 2006); voice ends when energy < threshold |
| latency | physics → audible onset (engine buffer + middleware buffer) |

The Python prototype can't give real CPU numbers (it is not real-time
code), but the C++ benchmark harness can run before any engine exists.

### 3.4 Wwise + Unreal 5
- Our synth is a Wwise **Source plugin** (it generates sound with no
  input), with authoring and sound-engine parts. Scaffold it with the Wwise
  plugin dev tool (`wp.py`) **(verify the current SDK workflow)**. Velocity
  and speed arrive as RTPCs or plugin parameters; hit events need the same
  timestamped-payload treatment as FMOD.
- Order: Unity + Wwise first (reuses the Unity sensor component), then
  UE5 + Wwise (sensor = `OnComponentHit` `NormalImpulse`, Chaos collision
  events; `UPhysicalMaterial` → surface).
- **Consider MetaSounds** for UE5: a custom C++ MetaSound node ("Modal
  Impact", "Friction", "Aggregate") might be less work than a Wwise plugin
  and is UE5's native procedural-audio system. It is a strong option if the
  Wwise build gets heavy. One core library makes adding it cheap.

---

## Suggested roadmap (adjust to the actual thesis deadline)

| when | milestone |
|---|---|
| Nov 2026 | Python model decisions: rolling exciter; contact damping; Rayleigh damping option; Tier-2 FEM tables for box, sphere, cup; IR / transient-layer A/B; archetype list v1; real recordings for grass, floor, drops |
| Dec 2026 | C++ core + golden tests; CPU benchmark harness |
| Jan 2027 | FMOD plugin + Unity demo scene (drop / throw / slide / roll); first CPU and real-time results |
| Feb 2027 | Wwise source plugin → Unity + Wwise → UE5 + Wwise (or MetaSounds) |
| Mar 2027 | Perceptual evaluation (`evaluation_protocol.md`) + small designer usability study (task: match a reference sound with the macros; SUS questionnaire) |
| Apr–May 2027 | Writing |

**Possible thesis contribution statement:** not "modal synthesis" (known)
but **a designer-facing parametrization** (material → archetype → size
macros, with hardness and pitch derived physically) **plus a real-time
middleware implementation evaluated on both perception and usability.**

## Open questions for you
1. Thesis deadline and committee expectations: is a usability study with
   designers in scope, or only the perceptual evaluation?
2. Target engine for the final demo: Unity, Unreal, or both?
3. FMOD or Wwise as the *primary* middleware (licence, what your program
   or industry contacts use)?
4. Is fracture in scope, or explicitly future work?
5. Can you record reference sounds (drops on concrete/wood floor, grass and
   gravel steps, a few struck objects)? Every "sounds bad" judgment so far
   has had nothing to compare against.
