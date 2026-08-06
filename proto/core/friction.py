"""Sliding / scraping exciter.

Reference: Turchet, "Footstep sounds synthesis" (Applied Acoustics, 2016),
solid-surface friction layer; same Rocchesso/Fontana/SDT model lineage as
the impact exciter (parameter naming cross-checked with core/impact.py).

Structure: broadband noise whose LEVEL and BANDWIDTH both track the sliding
speed, producing a force signal that is then fed into the same ModalBank as
the impacts (surface + object modes). Below a speed threshold the exciter
gates to silence smoothly.

    level(t)  ~ (speed / v_ref)^level_exp        (more speed = louder)
    cutoff(t) = cut_min + cut_per_v * speed      (more speed = brighter)

The time-varying one-pole lowpass is computed sample-by-sample (offline
prototype; a real-time port is the same loop).

Optional stick-slip: the noise is amplitude-modulated by a relaxation
oscillator whose rate is proportional to speed, giving a periodic squeak
component on top of the noise bed.
"""
from __future__ import annotations

import numpy as np


def friction_exciter(slide_speed: np.ndarray, fs: int,
                     roughness: float = 1.0,
                     v_ref: float = 0.5, level_exp: float = 1.2,
                     cut_min: float = 120.0, cut_per_v: float = 9000.0,
                     v_thresh: float = 0.01,
                     stick_slip: bool = False, squeak_per_v: float = 900.0,
                     seed: int | None = 0) -> np.ndarray:
    """Return an exciter force signal, same length as slide_speed (m/s).

    roughness scales overall level; cut_per_v maps speed to lowpass cutoff
    (rougher/faster = brighter). v_thresh: hard silence below this speed,
    with a smooth fade region up to 2*v_thresh.
    """
    speed = np.maximum(np.asarray(slide_speed, dtype=float), 0.0)
    n = len(speed)
    rng = np.random.default_rng(seed)
    noise = rng.standard_normal(n)

    # smooth gate: 0 below v_thresh, 1 above 2*v_thresh
    gate = np.clip((speed - v_thresh) / v_thresh, 0.0, 1.0)
    level = roughness * (speed / v_ref) ** level_exp * gate

    if stick_slip:
        # relaxation oscillator: phase rate ~ speed; sharp release each cycle
        phase = np.cumsum(squeak_per_v * speed) / fs
        saw = phase - np.floor(phase)
        noise = noise * (0.35 + 0.65 * saw ** 4)

    x = noise * level

    # time-varying one-pole lowpass, cutoff tracks speed
    cutoff = np.minimum(cut_min + cut_per_v * speed, 0.45 * fs)
    a = np.exp(-2.0 * np.pi * cutoff / fs)
    y = np.zeros(n)
    state = 0.0
    for i in range(n):
        state = a[i] * state + (1.0 - a[i]) * x[i]
        y[i] = state
    return y
