"""Common output quantity for every sounding body: a pressure proxy.

Two models live here.

1. Piston proxy (stage 4/5 legacy unified path, core/contact.py):
       p(t) ~= rho_0 * S * a(t) / (2 pi r)
   Low-ka baffled piston. Ignores radiation efficiency, so large plates
   below coincidence and slender objects come out far too loud.

2. Radiation-efficiency model (scenes, core/bodies.py). From the power
   balance W = rho c S sigma <v^2> and a hemispherical far field,
       p_rms = rho c sqrt(sigma S / (2 pi)) v_rms / r
   applied per mode (v_rms = spatial rms velocity of that mode) with a
   body-type radiation efficiency sigma(f):
   - compact body (balls, bars, sticks; size < wavelength): exact result
     for a rigid sphere oscillating as a dipole, radius a_eq = sqrt(S/pi):
         sigma = (ka)^4 / (4 + (ka)^4)            (standard acoustics)
     The same sigma(f) filters the rigid-body "click", whose far field is
     a dipole driven by the body's change of velocity.
   - plate (floors): Maidanik (1962) average for a simply supported baffled
     plate, as quoted by Oppenheimer & Dubowsky (1997):
         below f_c: sigma = corner + edge,  alpha = sqrt(f / f_c)
           corner = 8 lc^2 / (pi^4 S) (1 - 2 a^2) / (a sqrt(1 - a^2))  (f < f_c/2)
           edge   = P lc / (4 pi^2 S) [(1-a^2) ln((1+a)/(1-a)) + 2a] / (1-a^2)^1.5
         above f_c: sigma = (1 - f_c/f)^-0.5
         capped at sigma(f_c) ~= sqrt(l1/lc) + sqrt(l2/lc)
       f_c = c^2 / (2 pi) sqrt(rho h / D)  (coincidence frequency)
   Per-mode use of band-averaged formulas is an approximation (individual
   corner/edge modes differ), as is the zero-phase sqrt(sigma) filter.
"""
from __future__ import annotations

import numpy as np

RHO_AIR = 1.2      # kg/m^3
C_AIR = 343.0      # m/s
R_LISTEN = 1.0     # m


def accel_from_displacement(y: np.ndarray, fs: int) -> np.ndarray:
    """Second derivative by central difference (same length, zero ends)."""
    a = np.zeros_like(y)
    a[1:-1] = (y[2:] - 2.0 * y[1:-1] + y[:-2]) * fs * fs
    return a


def pressure_from_accel(a: np.ndarray, area: float) -> np.ndarray:
    return RHO_AIR * area * a / (2.0 * np.pi * R_LISTEN)


def pressure_from_displacement(y: np.ndarray, fs: int, area: float) -> np.ndarray:
    return pressure_from_accel(accel_from_displacement(y, fs), area)


# ------------------------------------------------- radiation efficiency

def sigma_compact(f, area: float):
    """Dipole (oscillating rigid sphere) radiation efficiency."""
    a = np.sqrt(area / np.pi)
    ka4 = (2 * np.pi * np.asarray(f, dtype=float) / C_AIR * a) ** 4
    return ka4 / (4.0 + ka4)


def coincidence_freq(h: float, phys: dict) -> float:
    D = phys["E"] * h**3 / (12 * (1 - phys["nu"]**2))
    return C_AIR**2 / (2 * np.pi) * np.sqrt(phys["rho"] * h / D)


def sigma_plate(f, a: float, b: float, h: float, phys: dict):
    """Maidanik average radiation efficiency, simply supported baffled plate."""
    f = np.atleast_1d(np.asarray(f, dtype=float))
    fc = coincidence_freq(h, phys)
    lc = C_AIR / fc
    S, P = a * b, 2 * (a + b)
    s_cap = np.sqrt(a / lc) + np.sqrt(b / lc)
    out = np.empty_like(f)
    for i, fi in enumerate(f):
        if fi >= fc:
            s = (1.0 - fc / fi) ** -0.5 if fi > fc else s_cap
        else:
            al = np.sqrt(fi / fc)
            edge = (P * lc / (4 * np.pi**2 * S)
                    * ((1 - al**2) * np.log((1 + al) / (1 - al)) + 2 * al)
                    / (1 - al**2) ** 1.5)
            corner = 0.0
            if fi < fc / 2:
                corner = (8 * lc**2 / (np.pi**4 * S) * (1 - 2 * al**2)
                          / (al * np.sqrt(1 - al**2)))
            s = corner + edge
        out[i] = min(s, s_cap)
    return out


def sigma_of(radiator: dict, area: float, f):
    if radiator["kind"] == "plate":
        return sigma_plate(f, radiator["a"], radiator["b"], radiator["h"],
                           radiator["phys"])
    return sigma_compact(f, area)


def velocity_to_pressure(sigma, area: float):
    """Amplitude factor p / v_rms = rho c sqrt(sigma S / (2 pi)) / r."""
    return RHO_AIR * C_AIR * np.sqrt(sigma * area / (2 * np.pi)) / R_LISTEN


def accel_to_pressure(acc: np.ndarray, fs: int, radiator: dict,
                      area: float) -> np.ndarray:
    """Pressure from a rigid-body ACCELERATION pulse train (the "click"):
    P(w) = rho c sqrt(sigma S / 2 pi) / r * A(w) / (i w). Working from the
    acceleration avoids the velocity step a rigid body keeps after a hit."""
    n = len(acc)
    nfft = 1 << int(np.ceil(np.log2(2 * n)))
    A = np.fft.rfft(acc, nfft)
    f = np.fft.rfftfreq(nfft, 1.0 / fs)
    w = velocity_to_pressure(sigma_of(radiator, area, f), area)
    jw = 2j * np.pi * f
    jw[0] = 1.0
    P = A * w / jw
    P[0] = 0.0
    return np.fft.irfft(P, nfft)[:n]
