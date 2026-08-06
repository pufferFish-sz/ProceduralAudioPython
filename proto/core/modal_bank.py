"""Modal resonator bank.

Canonical background: van den Doel & Pai, "The Sounds of Physical Shapes" (1998);
van den Doel, Kry & Pai, "FoleyAutomatic" (SIGGRAPH 2001).

Each mode is a mass-normalized damped harmonic oscillator driven by a contact
force f(t):

    q_n'' + 2 d_n q_n' + w0_n^2 q_n = f(t) / m_n

The audible output is sum_n gain_n * q_n(t). For open-loop (force known in
advance) processing the modes are discretized with the impulse-invariant
transform, which preserves the exact pole locations (frequency + decay):

    h_n(t)  = exp(-d_n t) sin(wd_n t) / (m_n wd_n),  wd = sqrt(w0^2 - d^2)
    y[i]    = a1 y[i-1] + a2 y[i-2] + b1 f[i-1]
    a1 = 2 exp(-d T) cos(wd T),  a2 = -exp(-2 d T)
    b1 = T exp(-d T) sin(wd T) / (m wd)
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
from scipy.signal import lfilter


@dataclass
class Mode:
    freq: float          # natural frequency f_n in Hz
    decay: float         # decay rate d_n in 1/s  (envelope ~ exp(-d_n t))
    gain: float = 1.0    # output weight (mode shape at listening "pickup")
    mass: float = 0.05   # modal mass in kg (force coupling)

    @property
    def tau(self) -> float:
        """Time constant of the amplitude envelope, seconds."""
        return 1.0 / self.decay


class ModalBank:
    def __init__(self, modes: list[Mode], fs: int):
        self.modes = modes
        self.fs = fs
        T = 1.0 / fs
        self.freqs = np.array([m.freq for m in modes], dtype=float)
        self.decays = np.array([m.decay for m in modes], dtype=float)
        self.gains = np.array([m.gain for m in modes], dtype=float)
        self.masses = np.array([m.mass for m in modes], dtype=float)

        w0 = 2 * np.pi * self.freqs
        d = self.decays
        if np.any(d >= w0):
            raise ValueError("overdamped mode (decay >= omega0) not supported")
        wd = np.sqrt(w0**2 - d**2)
        e = np.exp(-d * T)
        self.a1 = 2 * e * np.cos(wd * T)
        self.a2 = -(e**2)
        self.b1 = T * e * np.sin(wd * T) / (self.masses * wd)
        self.w0, self.wd = w0, wd

    def process(self, force: np.ndarray) -> np.ndarray:
        """Drive the bank open-loop with a force signal (N), return audio sum."""
        out = np.zeros(len(force))
        for i in range(len(self.modes)):
            y = lfilter([0.0, self.b1[i]], [1.0, -self.a1[i], -self.a2[i]], force)
            out += self.gains[i] * y
        return out

    def impulse_response(self, dur: float) -> np.ndarray:
        """Response to a unit force impulse (1 N for one sample)."""
        f = np.zeros(int(round(dur * self.fs)))
        f[0] = 1.0
        return self.process(f)


def ring_out(q0: np.ndarray, v0: np.ndarray, bank: ModalBank,
             tau_offsets: np.ndarray) -> np.ndarray:
    """Analytic free decay of the bank from state (q0, v0).

    Exact homogeneous solution, evaluated at time offsets `tau_offsets` (s)
    relative to the state's time. Returns the summed audio signal.
    """
    d = bank.decays[:, None]
    wd = bank.wd[:, None]
    q0 = q0[:, None]
    v0 = v0[:, None]
    t = tau_offsets[None, :]
    q = np.exp(-d * t) * (q0 * np.cos(wd * t) +
                          ((v0 + d * q0) / wd) * np.sin(wd * t))
    return bank.gains @ q
