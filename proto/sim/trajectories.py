"""Synthetic physics stand-ins for the UE sensor component.

These generate the same signals the game-side physics sensor would send:
impact events (time, velocity) and continuous slide-speed series.
"""
from __future__ import annotations

import numpy as np

G = 9.81


def bouncing_ball(h0: float, restitution: float, mass: float,
                  v_min: float = 0.08, max_bounces: int = 40):
    """Drop from height h0 (m); return list of (impact_time, impact_velocity).

    Velocities decrease by the restitution ratio each bounce; intervals
    shrink accordingly (accelerating rhythm as the ball settles).
    """
    v = np.sqrt(2 * G * h0)
    t = np.sqrt(2 * h0 / G)
    events = [(t, v)]
    for _ in range(max_bounces):
        v = restitution * v
        if v < v_min:
            break
        t += 2 * v / G
        events.append((t, v))
    return events


def sliding_box(v0: float, friction_mu: float, fs: int,
                extra_time: float = 0.3) -> np.ndarray:
    """Slide speed time series: v(t) = max(0, v0 - mu g t), plus a short
    silent tail so the render dies out naturally."""
    t_stop = v0 / (friction_mu * G)
    n = int((t_stop + extra_time) * fs)
    t = np.arange(n) / fs
    return np.maximum(0.0, v0 - friction_mu * G * t)


def tumble(seed: int = 0, dur: float = 3.0, rate_hz: float = 6.0,
           v_lo: float = 0.15, v_hi: float = 2.5):
    """Irregular impact event stream for stress-testing overlap/voices.

    Poisson event times with clustered bursts; mixed impact velocities."""
    rng = np.random.default_rng(seed)
    events = []
    t = 0.0
    while t < dur:
        # burst of 1-4 closely spaced hits, then a gap
        for _ in range(rng.integers(1, 5)):
            t += rng.exponential(1.0 / (rate_hz * 3))
            if t >= dur:
                break
            v = rng.uniform(v_lo, v_hi)
            events.append((t, v))
        t += rng.exponential(1.0 / rate_hz)
    return events
