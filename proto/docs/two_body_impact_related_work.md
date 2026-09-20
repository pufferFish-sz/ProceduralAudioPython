# Related Work: Collisions Between Two Resonant Bodies of Comparable Scale (Two-Body Impact)

Question: The current Stage 3 uses a “hammer-object” simplification in which the striker does not ring. What prior research covers collisions such as one glass cup striking another, where the two objects have comparable scale and both produce sound?

Conclusion: This is a mature research area with two main traditions. Graphics research generally assumes that every object has its own modal bank and that the contact force excites both objects (one-way/open-loop coupling). Acoustics research solves the coupling more rigorously but often simplifies the striker. Our “open-loop dual-bank” approach is the standard graphics method and has directly citable precedent.

Notation: ✔ = bibliographic details verified online in DBLP on 2026-08-06; ◇ = based on model knowledge and should be confirmed by opening the source before citation.

## A. Graphics / Animation Tradition (Multiple Objects, All Ringing, Open-Loop Excitation)

- ✔ van den Doel, Kry & Pai, “FoleyAutomatic: Physically-based sound effects for interactive simulation and animation,” SIGGRAPH 2001. A foundational contact-sound framework: every object in the scene is a modal model, and contact forces from the physics engine excite each object's modal bank separately. Having “both objects ring” is the default. Covers impact, rolling, and sliding.
- ✔ O'Brien, Shen & Gatchalian, “Synthesizing sounds from rigid-body simulations,” SCA 2002. Automatically extracts modes for each rigid body from its mesh and feeds collision impulses to both objects. This is the published standard form of the project's inexpensive “open-loop approach.”
- ✔ Raghuvanshi & Lin, “Interactive sound synthesis for large scale environments,” I3D 2006. A real-time budgeting method for collisions among hundreds of modal objects, using mode culling and mass-based level of detail. A direct citation for the game-performance budgeting section.
- ✔ Zheng & James, “Toward high-quality modal contact sound,” SIGGRAPH 2011. The work most directly relevant to this question. It shows how naive impulse excitation becomes inaccurate when one resonant body strikes another, and introduces coupled handling of contact damping (mutual suppression during sustained contact), micro-collision sequences, and multi-point frictional contact. It provides a source for the distortion mechanism in cup-on-cup collisions and also connects to our observed micro-bounces.
- ✔ Chadwick, Zheng & James, “Precomputed acceleration noise for improved rigid-body sound,” SIGGRAPH 2012. Covers the “acceleration noise” beyond ringing during a collision, caused when whole-body acceleration pushes air. This provides a theoretical source for the ground layer's noise burst.
- ✔ Ante Qu, “Computer methods for collision processing: from sound to topology,” Stanford PhD thesis, 2021. The complete treatment of the Qu & James ground-sound work.

## B. Acoustics / Physical-Modeling Tradition (Rigorous Coupling, Often with a Simplified Striker)

- ◇ Rocchesso & Fontana (eds.), “The Sounding Object,” 2003 (free PDF at soundobject.org). The book-length presentation of the Avanzini model. The impact chapter gives the equation form for two colliding modal objects: a separate modal expansion for each object plus a shared contact force. SDT implements a point mass striking a modal body, but the theoretical framework supports two modal bodies.
- ◇ Papetti, Avanzini & Rocchesso, “Numerical methods for a nonlinear impact model,” IEEE TASLP 2011. A systematic comparison of the K-method and other discretization schemes. This is the direct methodological source for the project's implicit integrator; the numerical scheme is unchanged when extended to two modal bodies.
- ◇ Chaigne & Doutaut, xylophone-strike modeling, JASA 1997. A classic acoustics treatment of two-body coupling in which the mallet is modeled as “mass + nonlinear spring,” the simplest form of a deformable striker.
- ◇ Piano hammer-string literature (Hall; Stulov hysteretic hammer model): an extreme example in which the striker has its own internal dynamics.

## Three Direct Applications to This Project

1. The open-loop dual-bank method has strong precedent in O'Brien 2002 and Raghuvanshi 2006. Cite these sources directly in the thesis to justify the approximation;
2. Cite Zheng & James 2011 for the limits of the approximation: mutual damping during sustained contact and micro-collision sequences are cases in which the naive method breaks down;
3. For bodies of comparable scale, correct the contact duration using the reduced mass: substitute `m_eff = m₁m₂/(m₁+m₂)` into `hertz_contact_time()`.
