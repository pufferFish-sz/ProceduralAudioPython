"""Per-partial decay-time measurement from rendered audio.

For each expected mode frequency: 4th-order Butterworth bandpass around the
partial, Hilbert envelope, linear fit of log-envelope over the usable range
(from just after the global peak down to -45 dB or the noise floor).
Measured tau_n is compared against the analytic tau_n = 1/(pi f_n tan_phi);
agreement validates synthesis AND analysis tooling in one shot (spec, ref 2).
"""
from __future__ import annotations

import numpy as np
from scipy.signal import butter, hilbert, sosfiltfilt


def _fit_once(y: np.ndarray, fs: int, f0: float, bw: float,
              start_offset: float, drop_db: float) -> float:
    lo, hi = f0 - bw, f0 + bw
    if lo <= 0 or hi >= fs / 2:
        return np.nan
    sos = butter(4, [lo, hi], btype="bandpass", fs=fs, output="sos")
    band = sosfiltfilt(sos, y)
    env = np.abs(hilbert(band))
    env_db = 20 * np.log10(np.maximum(env, 1e-12))
    peak_idx = int(np.argmax(env_db))
    peak_db = env_db[peak_idx]
    start = peak_idx + max(1, int(start_offset * fs))
    below = np.nonzero(env_db[start:] < peak_db - drop_db)[0]
    stop = start + (below[0] if len(below) else len(env_db) - start)
    if stop - start < max(8, int(0.002 * fs)):
        return np.nan
    t = np.arange(start, stop) / fs
    ln_env = np.log(np.maximum(env[start:stop], 1e-12))
    slope, _ = np.polyfit(t, ln_env, 1)
    return -1.0 / slope if slope < 0 else np.nan


def measure_decay_times(y: np.ndarray, fs: int, freqs,
                        rel_bw: float = 0.06, drop_db: float = 45.0):
    """Return measured tau (s) per frequency; np.nan where the fit failed.

    Two-pass adaptive fit: fast-decaying partials have a wide spectral
    footprint, and a narrow analysis bandpass then rings LONGER than the
    signal itself, biasing tau upward. Pass 1 estimates tau with a narrow
    band; if the filter is the bottleneck (bandwidth not >> signal
    bandwidth 1/(2 pi tau)), pass 2 refits with a widened band and a fit
    window scaled to the estimated tau.
    """
    freqs = np.atleast_1d(np.asarray(freqs, dtype=float))
    taus = np.full(len(freqs), np.nan)
    for i, f0 in enumerate(freqs):
        bw1 = max(25.0, rel_bw * f0)
        tau1 = _fit_once(y, fs, f0, bw1, 0.005, drop_db)
        if not np.isfinite(tau1):
            taus[i] = tau1
            continue
        needed_bw = 10.0 / (2 * np.pi * tau1)     # 10x signal half-bandwidth
        if needed_bw > bw1:
            bw2 = min(needed_bw, 0.35 * f0)
            off2 = float(np.clip(0.3 * tau1, 0.001, 0.01))
            tau2 = _fit_once(y, fs, f0, bw2, off2, drop_db)
            taus[i] = tau2 if np.isfinite(tau2) else tau1
        else:
            taus[i] = tau1
    return taus
