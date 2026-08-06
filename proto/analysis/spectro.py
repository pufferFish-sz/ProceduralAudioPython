"""Spectrogram + spectral centroid utilities and standard figure layouts.

All figures: dark-on-light, labeled, saved into proto/figures/.
"""
from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import stft

from ..util import FIG_DIR


def spectrogram_db(y: np.ndarray, fs: int, nfft: int = 2048,
                   overlap: float = 0.75):
    """Return (freqs, times, S_db) with floor at -100 dB rel. max."""
    nover = int(nfft * overlap)
    f, t, Z = stft(y, fs=fs, nperseg=nfft, noverlap=nover, padded=False)
    S = np.abs(Z)
    ref = S.max() or 1.0
    S_db = 20 * np.log10(np.maximum(S / ref, 1e-5))
    return f, t, S_db


def spectral_centroid(y: np.ndarray, fs: int,
                      fmin: float = 20.0, fmax: float = 18000.0) -> float:
    """Energy-weighted mean frequency of the whole signal (Hz)."""
    Y = np.abs(np.fft.rfft(y)) ** 2
    f = np.fft.rfftfreq(len(y), 1.0 / fs)
    m = (f >= fmin) & (f <= fmax)
    denom = Y[m].sum()
    if denom <= 0:
        return 0.0
    return float((f[m] * Y[m]).sum() / denom)


def plot_wave_spec(y: np.ndarray, fs: int, fname: str, title: str,
                   fmax: float | None = 12000.0) -> Path:
    """Standard per-render figure: waveform on top, spectrogram below."""
    t = np.arange(len(y)) / fs
    f, ts, S_db = spectrogram_db(y, fs)
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(9, 6), sharex=True,
                                   gridspec_kw={"height_ratios": [1, 2]})
    ax1.plot(t, y, lw=0.5, color="#204060")
    ax1.set_ylabel("amplitude")
    ax1.set_title(title)
    pm = ax2.pcolormesh(ts, f, S_db, shading="gouraud", cmap="magma",
                        vmin=-90, vmax=0)
    ax2.set_ylabel("frequency (Hz)")
    ax2.set_xlabel("time (s)")
    if fmax:
        ax2.set_ylim(0, fmax)
    fig.colorbar(pm, ax=[ax1, ax2], label="dB", pad=0.02)
    path = FIG_DIR / fname
    fig.savefig(path, dpi=130)
    plt.close(fig)
    return path


def plot_spec_compare(signals: list[tuple[str, np.ndarray, int]], fname: str,
                      suptitle: str, fmax: float | None = 12000.0) -> Path:
    """Side-by-side spectrograms, e.g. synthetic vs. real recording."""
    ncol = len(signals)
    fig, axes = plt.subplots(1, ncol, figsize=(4.5 * ncol, 4.5), sharey=True)
    if ncol == 1:
        axes = [axes]
    for ax, (label, y, fs) in zip(axes, signals):
        f, ts, S_db = spectrogram_db(y, fs)
        ax.pcolormesh(ts, f, S_db, shading="gouraud", cmap="magma",
                      vmin=-90, vmax=0)
        ax.set_title(label)
        ax.set_xlabel("time (s)")
        if fmax:
            ax.set_ylim(0, fmax)
    axes[0].set_ylabel("frequency (Hz)")
    fig.suptitle(suptitle)
    fig.tight_layout()
    path = FIG_DIR / fname
    fig.savefig(path, dpi=130)
    plt.close(fig)
    return path
