"""Simplified ground / large-surface impact layer.

Reference: Qu & James, "On the Impact of Ground Sound" (DAFx-19, 2019).

What the paper contributes vs. a small resonant object: a ground half-space
adds (a) a low-frequency, fast-decaying "thump" from surface waves /
half-space radiation, and (b) broadband contact "acceleration noise" at the
onset. Their full pipeline (elastodynamic half-space solve + acoustic
radiation) is far heavier than a real-time game plugin needs.

SIMPLIFICATIONS MADE HERE (thesis subsection: "real-time approximation of an
offline method"):
- The elastodynamic half-space + BEM radiation solve is replaced by a small
  bank of heavily damped low-frequency modes (the perceptually dominant
  "thump" resonances of a floor panel / slab).
- Acceleration noise is approximated by a short lowpassed noise burst with
  an exponential decay, amplitude tied to impact momentum.
- Radiation directivity, listener position and wave arrival times are
  ignored (a game will spatialize the summed signal downstream).
- LEGACY path (`ground_layer`): excitation scales with impact momentum
  (mass * velocity) and the result is mixed by hand. UNIFIED path
  (`surface_response`, used via core/contact.py): the floor is driven by
  the SAME contact force pulse as the object and output as a pressure
  proxy, so object/floor balance and floor brightness follow from physics.
"""
from __future__ import annotations

import numpy as np

from .modal_bank import ModalBank, Mode
from .radiation import pressure_from_displacement

GROUND_PRESETS: dict[str, dict] = {
    # freqs: low "thump" modes; tan_phi-like damping folded into decay rates.
    # material: contact partner for Hertz k (materials.PHYSICAL).
    # modal_mass (kg): effective mass of the floor patch at the contact
    #   point -- a ~1 m^2 plank-floor panel vs a massive slab. This is what
    #   makes a wood floor "thump" and concrete stay quiet under the same hit.
    # rad_area (m^2): radiating area of the vibrating patch.
    # noise_*: legacy-only (the unified path gets its contact click from the
    #   object's rigid-body acceleration instead, see core/contact.py).
    "wood_floor":  dict(freqs=[62.0, 105.0, 158.0, 240.0],
                        gains=[1.0, 0.7, 0.5, 0.3],
                        decays=[38.0, 55.0, 75.0, 105.0],
                        material="wood", modal_mass=6.0, rad_area=1.0,
                        noise_cut=900.0, noise_decay=0.012, noise_mix=0.5),
    "concrete":    dict(freqs=[90.0, 170.0, 310.0],
                        gains=[1.0, 0.6, 0.35],
                        decays=[90.0, 130.0, 190.0],
                        material="concrete", modal_mass=400.0, rad_area=1.0,
                        noise_cut=1600.0, noise_decay=0.006, noise_mix=0.8),
}


def surface_response(force: np.ndarray, fs: int, surface: str | dict,
                     dur: float) -> np.ndarray:
    """Floor's radiated pressure proxy (Pa @ 1 m) driven by a contact force.

    `force` is the contact force pulse at fs (from the impact sim). Each
    floor mode is coupled with mass modal_mass / gain^2 (gain = relative
    mode-shape amplitude at the contact point), output = acceleration of
    the contact point radiated by rad_area. One-way coupling: the floor's
    compliance is not fed back into the contact (it is treated as a rigid
    wall there), the standard open-loop dual-bank approximation.
    """
    p = GROUND_PRESETS[surface] if isinstance(surface, str) else surface
    n = int(round(dur * fs))
    f = np.zeros(n)
    m = min(len(force), n)
    f[:m] = force[:m]
    modes = [Mode(freq=fr, decay=d, gain=1.0, mass=p["modal_mass"] / g**2)
             for fr, d, g in zip(p["freqs"], p["decays"], p["gains"])]
    disp = ModalBank(modes, fs).process(f)
    return pressure_from_displacement(disp, fs, p["rad_area"])


def ground_layer(v_in: float, mass: float, surface_params: str | dict,
                 fs: int, dur: float = 0.6, seed: int | None = 2) -> np.ndarray:
    """LEGACY low-frequency fast-decay layer for floor impacts.

    Layer this under the struck object's modal ring. Amplitude scales with
    impact momentum m*v (see module docstring for simplifications). Kept
    for A/B against the unified path (core/contact.py).
    """
    p = GROUND_PRESETS[surface_params] if isinstance(surface_params, str) \
        else surface_params
    momentum = mass * v_in
    n = int(round(dur * fs))

    # (a) heavily damped low modes, impulse-excited proportional to momentum
    modes = [Mode(freq=f, decay=d, gain=g, mass=1.0)
             for f, d, g in zip(p["freqs"], p["decays"], p["gains"])]
    bank = ModalBank(modes, fs)
    force = np.zeros(n)
    force[0] = momentum * fs        # impulse of area = momentum
    thump = bank.process(force)

    # (b) acceleration-noise stand-in: lowpassed noise burst, fast exp decay
    rng = np.random.default_rng(seed)
    noise = rng.standard_normal(n)
    t = np.arange(n) / fs
    envelope = np.exp(-t / p["noise_decay"])
    a = np.exp(-2.0 * np.pi * p["noise_cut"] / fs)
    burst = np.zeros(n)
    state = 0.0
    x = noise * envelope
    for i in range(n):
        state = a * state + (1.0 - a) * x[i]
        burst[i] = state
    # scale noise against thump so noise_mix is a meaningful ratio
    tp = np.max(np.abs(thump)) or 1.0
    bp = np.max(np.abs(burst)) or 1.0
    return thump + burst * (tp / bp) * p["noise_mix"]
