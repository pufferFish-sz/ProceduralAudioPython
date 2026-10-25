# Modal Archetype List — Materials, Primitives, Equations, Sources

Expands `plan_and_brainstorm.md` §1.3 (written 2026-10-25). An **archetype**
is a named everyday object ("wooden plank", "glass bottle") defined as one
or more **primitives** with default dimensions and a material. Every number
the synthesizer uses follows from that definition. Designers only move
macros (Size, Material, Hollow, Ring); see §4.

Legend:
- ✔ = implemented in `proto/core` (shapes.py / bodies.py).
- ◐ = formula known, not yet coded.
- ✖ = no closed form: Tier 2 (FEM once per family, or a published table).
- ◇ = value from memory or secondary source; verify before quoting in the thesis.

---

## 0. Archetype record (what each entry specifies)

| field | meaning |
|---|---|
| primitive(s) | which formula(s) in §2 give the modes |
| default dims | sizes the macros scale from |
| material | row in §1 (E, ρ, ν, damping, contact modulus, restitution) |
| contact radius | curvature of the part that touches first (Hertz k) |
| contact point | default strike/landing position (sets which modes are excited) |
| radiation | compact dipole or plate (Maidanik); see `core/radiation.py` |
| hollow / cavity | wall thickness, shell modes, air cavity (Helmholtz) |
| tier | 1 = closed form, 2 = precomputed table/FEM, 3 = measured or user-supplied |

---

## 1. Materials

Elastic constants are rounded engineering values (as in `materials.PHYSICAL`).
Damping is shown three ways: our current preset tan φ; tan φ derived from
**measured** Rayleigh damping (Ren, Yeh & Lin 2013, Table I); and loss-factor
ranges from Cremer & Heckl as tabulated by Irvine.

Ren et al. fit `d = ½(α + β·ω²)` (Rayleigh damping) to recordings. In our
notation that is `tan φ_eq(f) = 2d/ω = α/ω + β·ω`, which depends on
frequency:

| material | E (GPa) | ρ (kg/m³) | ν | √(E/ρ) (m/s) | our tan φ | Ren 2013 tan φ_eq at 250 Hz / 1 kHz / 4 kHz | Cremer–Heckl loss factor | restitution preset |
|---|---|---|---|---|---|---|---|---|
| steel ("metal") | 200 | 7850 | 0.29 | 5050 | 2e-4 | 4.1e-3 / 1.1e-3 / 7.8e-4 | order 1e-4 (◇ partly illegible) | 0.70 |
| aluminium | 70 | 2700 | 0.33 | 5090 | — | — | very low (◇) | 0.70 |
| glass | 70 | 2500 | 0.22 | 5290 | 8e-4 | 1.2e-2 / 3.8e-3 / 4.3e-3 | ◇ | 0.75 |
| porcelain / ceramic | 70 ◇ | 2400 ◇ | 0.22 ◇ | 5400 | — | 1.6e-4 / 5.4e-4 / 2.1e-3 | — | — |
| hardwood (along grain) | 11 (E_contact 1 across grain) | 650 | 0.30 | 4110 | 0.012 | 6.2e-3 / 2.0e-2 / 7.8e-2 | oak 1e-2, fir 8e-3 | 0.60 |
| plywood / pressed wood | 8 ◇ | 600 ◇ | 0.30 | 3650 | — | — | 1–3e-2 | — |
| hard plastic (ABS) | 2.5 | 1100 | 0.37 | 1510 | 0.05 | 3.5e-2 / 1.4e-2 / 2.4e-2 | Plexiglas 2–4e-2 | 0.60 |
| PET (bottles) | 3 ◇ | 1380 | 0.40 ◇ | 1470 | — | — | — | — |
| rubber | 0.01 | 1100 | 0.49 | 95 | 0.15 | — | (0.1–1, ◇) | 0.80 |
| stone (granite) | 50 | 2700 | 0.25 | 4300 | 0.004 (preset) | — | — | 0.50 |
| brick | 15 ◇ | 1900 ◇ | 0.20 ◇ | 2800 | — | — | 1–2e-2 | — |
| dense concrete | 30 | 2400 | 0.20 | 3540 | (installed 0.05) | — | 4–8e-3 | — |
| cardboard | ? | ? | ? | — | — | — | — | needs measurement |

**What the measured damping tells us:**
- **Use frequency-dependent damping.** Constant tan φ (Klatzky's model, our
  current code) is a good one-parameter perceptual control. Real materials
  (Ren's fits) are **not** proportional to frequency. Wood's high modes die
  far faster (tan φ_eq 0.078 at 4 kHz), while plastic is closer to flat.
  Recommendation: store α and β per material (Rayleigh, the graphics
  standard since O'Brien 2002), and expose "Ring" as a multiplier on both.
- **Our steel and glass presets ring much longer than Ren's measured
  objects** (2e-4 and 8e-4 vs ~1e-3 and ~4e-3 at 1 kHz). Measured values
  include losses into supports and the hand. Treat ours as "freely
  suspended" and Ren's as "lying on a table". That is an archetype
  *situation* parameter, like the installed loss factor of floors.

Restitution presets: see `bodies.RESTITUTION` (plausibility values, not
measurements).

---

## 2. Primitive formula sheet

Each mode's coupling at the contact point: `Mode.mass = M / φₙ(x_s)²` with
mode shapes normalized to mean(φ²) = 1, so modal mass = total mass M (see
`core/shapes.py`).

### P1 · Free-free beam, bending — bars, planks, sticks ✔ `shapes.bar`
```
fₙ = (βₙL)² / (2π L²) · √(E I / (ρ A))     βₙL = 4.7300, 7.8532, 10.9956, 14.1372, 17.2788, …
I/A = t²/12 (rectangle, thickness t)         ratios 1 : 2.757 : 5.404 : 8.933 : 13.34
φₙ(x) = cosh βx + cos βx − σₙ(sinh βx + sin βx),  σₙ = (cosh βL − cos βL)/(sinh βL − sin βL)
```
- **Valid when** L/t ≳ 6–10. Stubby bodies such as bricks need Timoshenko
  corrections (shear and rotary inertia lower the frequencies), or FEM.
- **Sources:** Blevins, *Formulas for Natural Frequency and Mode Shape*;
  Fletcher & Rossing, *The Physics of Musical Instruments*, ch. 2.

### P2 · Rod / pipe (annular section) ✔ `shapes.tube`
Same as P1 with `I/A = (R_o² + R_i²)/4` (R_i = 0 for a solid rod). At the
same outer radius, hollow means higher pitch: up to √2 ≈ +6 semitones for a
thin wall.

### P3 · Longitudinal rod modes — end-on hits (chimes, poles) ◐
```
fₙ = n · √(E/ρ) / (2L)       (free-free)
```
**Source:** standard (Blevins; Fletcher & Rossing).

### P4 · Thin cylindrical shell, circumferential modes — cans, bottles, pipes, mugs ◐ (long-ring form ✔ in `tube`)
(a) **Long ring / inextensional** (only valid when L ≫ R and the ends are
open):
```
ωₙ = (h/R²) √(E / (12ρ(1−ν²))) · n(n²−1)/√(n²+1),   n = 2, 3, …
```
(b) **Short shell with ends** (Donnell simplified form, ◇ verify):
```
Ω² = (1−ν²) λ⁴/(λ²+n²)² + k (λ²+n²)²,   λ = mπR/L,  k = h²/(12R²)
ω  = (Ω/R) √(E / (ρ(1−ν²)))
```
- **Why (b) is needed:** (a) gives 61 Hz for a soda can (R 33 mm, wall
  0.1 mm), which is clearly wrong because the ends stiffen it. (b) gives
  ≈ 0.9–1.2 kHz.
- **Donnell is inaccurate for n ≤ 2.** For a steel pipe it gives n=2 at
  7.2 kHz, where the long-ring formula gives 4.8 kHz. Use Flügge's
  equations or FEM to settle this. The current `tube` code uses (a) and
  should switch.
- **Sources:** Leissa, *Vibration of Shells*, NASA SP-288 (1973); Soedel,
  *Vibrations of Shells and Plates*. For cups and glasses, French, "In vino
  veritas", Am. J. Phys. 51:688 (1983), whose fill-level model is
  `(f₀/f)² = 1 + kF⁴` (◇ via secondary source).

### P5 · Free-edge circular plate — dishes, lids, cymbal-like ✔ `shapes.disc`
```
f = λ² / (2π a²) · √(D / (ρh)),   D = E h³ / (12(1−ν²))
λ² (ν = 0.3) = 5.359 (2,0), 9.005 (0,1), 12.441 (3,0), 20.489 (1,1), 21.840 (4,0), 33.511 (5,0), 35.293 (2,1)
```
- **Source:** Malison & Sompornjaroensuk, *Engineering Transactions* 18(1),
  2015 (FEM benchmark of the first 80 coefficients, consistent with Leissa
  SP-160).
- **Shape caveat:** real dishes are shallow shells, and curvature raises the
  frequencies.

### P6 · Clamped circular plate — pot or pan bottoms, jar lids ◐
`λ² = 10.216 (0,0), 21.26 (1,0), 34.88 (2,0), 39.77 (0,1)` (same formula as
P5). Source: tabulated values confirmed in a University of Cluj study and in
Malison & Sompornjaroensuk 2015.

### P7 · Simply supported rectangular plate — floors, panes in frames, decks, crate panels ✔ `shapes.plate_ss`
```
f_mn = (π/2) √(D/(ρh)) ((m/a)² + (n/b)²),   φ_mn = 2 sin(mπx/a) sin(nπy/b)
```
**Source:** exact Kirchhoff result (Leissa, NASA SP-160, 1969).

### P8 · Free rectangular plate — loose sheets, cutting boards, trays ✖
No closed form. Use Leissa's tables or Warburton's approximation. Square
plate, ν = 0.3, first parameter ≈ 13.47 (◇ verify against Leissa 1973,
*J. Sound Vib.* 31:257). Large thin metal sheets are also **non-linear**
(thunder-sheet behaviour) and out of scope for linear modes.

### P9 · Solid sphere — balls, marbles, ball bearings, rough stand-in for rocks ✔ `shapes.sphere`
Lamb's (1882) spheroidal equation is solved numerically for η = ωa/c_T. For
l = 2, η = 2.640 at ν = 0.25, which validates the solver.
**Consequence: small hard balls do not ring audibly.**
- glass marble, r = 8 mm → about 180 kHz;
- steel ball, r = 10 mm → about 130 kHz;
- fist-sized rock as an equivalent sphere (r = 5 cm) → about 23 kHz.

You hear only the contact click and the surface. Rubber balls ring low:
r = 15 mm → 1.56 kHz; r = 40 mm → 586 Hz.

### P10 · Thin spherical shell — ping-pong ball, hollow metal ball, ornaments ✖
Treated by Lamb (1882), Baker (1961) and Silbiger (1962). Membrane theory
gives two branches. Bending matters for the low modes of thin shells. Use a
published table or FEM; pressurized balls (tennis, basketball) also need
their air cavity.

### P11 · Air cavity (Helmholtz) — bottles, jars, boxes with openings ◐
```
f = (c / 2π) √( A / (V · L_eff) ),   A = πa²,  L_eff ≈ L + 1.46a  (≈0.85a inner + 0.61a outer end correction)
```
- **Source:** standard acoustics (Kinsler et al., *Fundamentals of
  Acoustics*).
- **Examples:** 0.75 L wine bottle (neck a = 9 mm, L = 70 mm) ≈ 110 Hz;
  0.5 L PET bottle ≈ 250 Hz.
- **Coupling:** wall impacts excite it weakly. It is strong when air moves
  (rolling, sloshing, an open mouth hitting a surface).

### P12 · Compact solids — blocks, bricks, cubes, rocks, toys ✖
No closed form. For geometrically similar solids, `f = Λ · c_T / L`. Compute
the dimensionless Λ once per shape family with FEM and store it. Rough
fallback: a sphere of equal volume (P9). In practice their sound is mostly
contact, floor and rattling, because their modes are high and heavily
damped.

### Scaling laws (what the Size, Material and Hollow macros do)
| change | beam (P1–2) | plate (P5–8) | shell (P4) | solid (P9, P12) |
|---|---|---|---|---|
| all dimensions × s | f × 1/s | f × 1/s | f × 1/s | f × 1/s |
| thickness × s only | f × s | f × s | ring f × s | — |
| material | f ∝ √(E/ρ) | f ∝ √(E/(ρ(1−ν²))) | same | f ∝ √(G/ρ) (+ν) |
| mass | × s³ | × s³ | × s³ | × s³ |

So the **Size** macro is a pure pitch shift of 1/s with mass × s³, and
**Hollow** (wall thickness) moves pitch *and* mass independently. The
`ball_drop` scene gate checks the 1/r scaling exactly for the Lamb sphere.

---

## 3. Archetype list (v1, 25 entries)

Frequencies are computed with the formulas above for the default
dimensions; "status" says whether the scene code can build the archetype
today.

| # | archetype | material | primitive(s) | default dims | mass | lowest modes (Hz) | contact radius | status | notes |
|---|---|---|---|---|---|---|---|---|---|
| 1 | wooden stick | wood | P2 (solid) | 30 cm, Ø12 mm | 22 g | 488, 1346, 2639 | 6 mm tip | ✔ (rigid as a striker) | own ring off until a grip model exists |
| 2 | wooden plank | wood | P1 | 40×8×2 cm | 0.42 kg | 529, 1457, 2856 | 3 mm edge | ✔ | |
| 3 | wooden bar | wood | P1 | 30×4×2 cm | 0.16 kg | 940, 2590, 5078 | flat | ✔ | xylophone-like when suspended |
| 4 | wooden block (toy) | wood | P12 | 5 cm cube | 81 g | FEM | 3 mm edge | ✖ | mostly click + floor |
| 5 | wooden crate | plywood | P7 panels + P11 | 40×30×30 cm, 10 mm | ~4 kg | panel (1,1) ≈ 300 | edge | ◐ | panels as SS plates |
| 6 | wooden floor (surface) | wood | P7 | 2.4×1.2 m, 22 mm | 41 kg | 37, 60, 97 | flat | ✔ | installed loss 0.03 |
| 7 | steel rod | steel | P2 (solid) | 50 cm, Ø30 mm | 2.8 kg | 539, 1486, 2914 | 3 mm | ✔ | |
| 8 | steel pipe | steel | P2 + P4 | 50 cm, Ø30, wall 1.5 mm | 0.53 kg | 725, 2000, 3920 + shell n=2 (4.8–7.2 k, verify) | 3 mm | ✔ / ◐ shell | switch shell to P4(b)/Flügge |
| 9 | steel sheet | steel | P8 (P7 if framed) | 60×40 cm, 1 mm | 1.9 kg | dense; framed ≈ 22 first | edge | ✖ | non-linear at high level |
| 10 | aluminium can (empty) | aluminium | P4(b) + P11 | Ø66×120 mm, 0.1 mm | ~15 g | ≈ 920–1160 (n = 4–6) | rim | ◐ | crushable; out of scope |
| 11 | steel pot | steel | P6 bottom + P4 wall | Ø20 cm, 1.5 mm | — | bottom 371, 773 | rim / flat | ◐ | |
| 12 | steel deck plate (surface) | steel | P7 | 1×1 m, 6 mm | 47 kg | 29, 72, 72 | flat | ✔ | installed loss 0.005 |
| 13 | glass bottle | glass | P4(b) + P11 | 0.75 L, Ø70 mm, 3 mm wall | ~0.4 kg | shell ≈ 3100; cavity ≈ 110 | 3 mm | ◐ | |
| 14 | glass pane (framed) | glass | P7 | 60×40 cm, 4 mm | 2.4 kg | 89 … | flat | ✔ | needs plate radiation, already supported |
| 15 | glass marble | glass | P9 | r = 8 mm | 5 g | ≈ 180 kHz (none audible) | 8 mm | ✔ | click + floor only |
| 16 | ceramic plate (dish) | porcelain | P5 (flat approx.) | Ø26 cm, 5 mm | 0.64 kg | 403, 678 | rim | ✔ (disc) | curvature raises f |
| 17 | ceramic mug | porcelain | P4 + bottom | Ø80 mm, 4 mm wall | ~0.3 kg | n=2 ≈ 1.7 k (long-ring approx.) | rim | ◐ / ✖ | handle splits degenerate pairs |
| 18 | plastic bar / ruler | ABS | P1 | 30×3×0.4 cm | 40 g | (P1) | edge | ✔ | |
| 19 | plastic bottle (PET) | PET | P4(b) + P11 | 0.5 L, 0.3 mm wall | ~20 g | shell ≈ 270; cavity ≈ 250 | — | ✖ | crinkle is non-linear |
| 20 | plastic crate | ABS/PP | P7 panels + P11 | 40×30×25 cm | — | — | edge | ◐ | |
| 21 | rubber ball, small | rubber | P9 | r = 15 mm | 16 g | 1562, 2344, 3022 | 15 mm | ✔ | |
| 22 | rubber ball, large | rubber | P9 | r = 40 mm | 295 g | 586, 879, 1133 | 40 mm | ✔ | |
| 23 | hollow ball (ping-pong / playground) | celluloid / rubber | P10 + P11 | r = 20 / 100 mm | — | — | r | ✖ | pressurized cavity |
| 24 | brick | brick | P12 (P1 overestimates) | 21.5×10.25×6.5 cm | 2.7 kg | P1 gives 4.1 k (too high; L/t = 3.3) | 3 mm edge | ✖ | mostly contact + floor |
| 25 | rock | stone | P12 (P9 approx.) | r ≈ 5 cm / 15 cm | 1.4 / 38 kg | ≈ 23 k / 7.6 k | 5 mm | ✔ (sphere approx.) | small rocks: click + floor |
| — | cardboard box | cardboard | P7 + P11 | — | — | — | — | ✖ | material data missing |
| — | concrete slab (surface) | concrete | P7 | 4×4 m, 15 cm | 5.8 t | 31, 77 | flat | ✔ | barely moves |

**Patterns worth stating in the thesis:**
- **Ringing archetypes** (bars, pipes, panes, dishes, bottles, cans) are
  where the modal model earns its keep. Tier 1 covers most of them; add P4(b)
  and P11.
- **Compact solids** (blocks, bricks, rocks, marbles) mostly don't ring
  audibly. Their identity comes from contact hardness, mass, the surface
  and rattling. For them, invest in contact and surface models, not more
  modes.
- **Thin crushable containers** (cans, PET bottles, cardboard) are
  dominated by non-linear crinkle and buckling. Mark them out of scope or
  handle them with a separate granular "crumple" exciter (cf. SDT).

---

## 4. Designer macros → parameters

| macro | changes | archetype fields touched |
|---|---|---|
| Material | E, ρ, ν, α/β (or tan φ), E_contact, restitution | §1 row |
| Size (s) | all dimensions × s → f × 1/s, M × s³, contact radius × s | dims |
| Hollow / Wall | wall or thickness × w → shell/plate f × w, M changes, cavity on/off | P2, P4, P10, P11 |
| Ring | multiplies damping (α, β) — dead ↔ ringing; also the situation (held / lying / suspended) | §1 |
| Brightness | default contact point (towards antinodes = brighter), contact radius (smaller = harder) | contact |
| Surface | which floor archetype is the other body | #6, #12, slab, … |

---

## 5. Next steps this list implies

1. Code P4(b) (Donnell; check against Flügge or FEM for n ≤ 2), P6 and P11,
   then build archetypes 10, 11, 13 and 17.
2. Switch material damping to Rayleigh α/β, seeded from Ren 2013 for wood,
   plastic, metal, glass and porcelain; keep tan φ as the "Ring" control.
3. Run a Tier-2 FEM pass (scikit-fem or FEniCS) for cube/block, brick, mug
   and dish; store dimensionless Λ and the contact-point mode shapes.
4. Measure (or find) data for cardboard and PET, or mark them out of scope.
5. Verify every ◇ item before it appears in the thesis.

---

## Sources

**Measured material damping**
- Z. Ren, H. Yeh, M. C. Lin, "Example-Guided Physically Based Modal Sound Synthesis", *ACM TOG* 32(1), 2013 — Table I (α, β per material). [PDF](http://gamma-web.iacs.umd.edu/AUDIO_MATERIAL/examplebasedsoundsynthesis.pdf) · [DOI](https://doi.org/10.1145/2421636.2421637)
- R. L. Klatzky, D. K. Pai, E. P. Krotkov, "Perception of Material from Contact Sounds", *Presence* 9(4), 2000 (tan φ model). [PDF](https://www.cs.ubc.ca/labs/lci/papers/docs2000/pai-KlaPai00.pdf)
- L. Cremer, M. Heckl, *Structure-Borne Sound*, Springer 1988, loss-factor tables as reproduced in T. Irvine, "Damping Properties of Materials" (vibrationdata). [copy](https://pdf4pro.com/view/damping-properties-of-materials-vibrationdata-613dfd.html) (scrape partly illegible; check the original).

**Modal formulas and tables**
- A. W. Leissa, *Vibration of Plates*, NASA SP-160, 1969. [NTRS](https://ntrs.nasa.gov/citations/19700009156)
- A. W. Leissa, *Vibration of Shells*, NASA SP-288, 1973; W. Soedel, *Vibrations of Shells and Plates* (Donnell and Flügge forms).
- M. Malison, Y. Sompornjaroensuk, "Numerical finite element determination on free transverse vibrations of circular plates", *Engineering Transactions* 18(1), 2015 (first 80 coefficients, clamped / SS / free, ν = 0.3). [PDF](https://ph02.tci-thaijo.org/index.php/ET/article/download/244797/166000/858618)
- Clamped circular plate λ² table (University of Cluj study). [PDF](https://studia.reviste.ubbcluj.ro/index.php/subbengineering/article/download/6642/6329/12435)
- R. D. Blevins, *Formulas for Natural Frequency and Mode Shape* (beams, plates, shells, cavities: the standard compendium).
- N. H. Fletcher, T. D. Rossing, *The Physics of Musical Instruments* (bars, plates, shells, bells).
- H. Lamb, "On the vibrations of an elastic sphere", 1882; spheroidal-mode equation as used in the nanoparticle literature (Saviot & Murray). Free spherical shell: Baker 1961, Silbiger 1962 (see the Abaqus benchmark summary, [link](https://ceae-server.colorado.edu/v2016/books/bmk/ch01s04ach37.html)).
- A. P. French, "In vino veritas: A study of wineglass acoustics", *Am. J. Phys.* 51:688, 1983 (◇ details via secondary sources).
- L. E. Kinsler et al., *Fundamentals of Acoustics* (Helmholtz resonator, end corrections).

**Modal synthesis frameworks using primitives or FEM**
- K. van den Doel, D. K. Pai, "The Sounds of Physical Shapes", *Presence* 7(4), 1998 (analytic shapes).
- J. F. O'Brien, C. Shen, C. M. Gatchalian, "Synthesizing sounds from rigid-body simulations", SCA 2002 (FEM, Rayleigh damping).
- N. Raghuvanshi, M. C. Lin, "Interactive sound synthesis for large scale environments", I3D 2006 (mode culling, budgeting).
