"""(Stretch goal) Extract modes from a recorded tap.

Peak-pick the magnitude spectrum of a recording, then decay-fit each picked
partial with analysis.decay_fit -> a list of Mode objects usable by the
synthesizer. Quality depends heavily on the recording (single clean tap,
low noise floor).
"""
from __future__ import annotations

import numpy as np
from scipy.signal import find_peaks

from ..core.modal_bank import Mode
from .decay_fit import measure_decay_times


def extract_modes(y: np.ndarray, fs: int, n_modes: int = 8,
                  fmin: float = 80.0, fmax: float = 10000.0,
                  prominence_db: float = 12.0) -> list[Mode]:
    Y = np.abs(np.fft.rfft(y * np.hanning(len(y))))
    f = np.fft.rfftfreq(len(y), 1.0 / fs)
    m = (f >= fmin) & (f <= fmax)
    mag_db = 20 * np.log10(np.maximum(Y[m] / (Y[m].max() or 1.0), 1e-8))
    fm = f[m]
    peaks, props = find_peaks(mag_db, prominence=prominence_db, distance=20)
    if len(peaks) == 0:
        return []
    order = np.argsort(mag_db[peaks])[::-1][:n_modes]
    sel = np.sort(peaks[order])
    freqs = fm[sel]
    gains = 10 ** (mag_db[sel] / 20.0)
    taus = measure_decay_times(y, fs, freqs)
    modes = []
    for f0, g, tau in zip(freqs, gains, taus):
        if np.isfinite(tau) and tau > 0:
            modes.append(Mode(freq=float(f0), decay=1.0 / tau, gain=float(g)))
    return modes
