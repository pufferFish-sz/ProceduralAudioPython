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
- Excitation scales with impact momentum (mass * velocity); the paper's
  detailed force coupling is reduced to this single scalar.
"""
from __future__ import annotations

import numpy as np

from .modal_bank import ModalBank, Mode

GROUND_PRESETS: dict[str, dict] = {
    # freqs: low "thump" modes; tan_phi-like damping folded into decay rates
    "wood_floor":  dict(freqs=[62.0, 105.0, 158.0, 240.0],
                        gains=[1.0, 0.7, 0.5, 0.3],
                        decays=[38.0, 55.0, 75.0, 105.0],
                        noise_cut=900.0, noise_decay=0.012, noise_mix=0.5),
    "concrete":    dict(freqs=[90.0, 170.0, 310.0],
                        gains=[1.0, 0.6, 0.35],
                        decays=[90.0, 130.0, 190.0],
                        noise_cut=1600.0, noise_decay=0.006, noise_mix=0.8),
}


def ground_layer(v_in: float, mass: float, surface_params: str | dict,
                 fs: int, dur: float = 0.6, seed: int | None = 2) -> np.ndarray:
    """Low-frequency fast-decay layer for floor impacts.

    Layer this under the struck object's modal ring. Amplitude scales with
    impact momentum m*v (see module docstring for simplifications).
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
