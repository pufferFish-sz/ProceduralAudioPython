"""Shared paths, WAV writing, normalization helpers.

All renders go to proto/renders/, all figures to proto/figures/,
regardless of the current working directory.
"""
from __future__ import annotations

import os
from pathlib import Path

import numpy as np

FS = 44100

PROTO_DIR = Path(__file__).resolve().parent
RENDER_DIR = PROTO_DIR / "renders"
FIG_DIR = PROTO_DIR / "figures"
DOCS_DIR = PROTO_DIR / "docs"

for _d in (RENDER_DIR, FIG_DIR, DOCS_DIR):
    _d.mkdir(parents=True, exist_ok=True)


def db_to_lin(db: float) -> float:
    return 10.0 ** (db / 20.0)


def _write_wav_file(path: Path, y: np.ndarray, fs: int) -> None:
    try:
        import soundfile as sf
        sf.write(str(path), y.astype(np.float32), fs, subtype="PCM_16")
    except ImportError:
        from scipy.io import wavfile
        yi = np.clip(y, -1.0, 1.0)
        wavfile.write(str(path), fs, (yi * 32767).astype(np.int16))


def write_wav(name: str, y: np.ndarray, fs: int = FS, peak_db: float = -6.0) -> Path:
    """Write a single WAV normalized to peak_db dBFS."""
    peak = float(np.max(np.abs(y))) or 1.0
    out = y * (db_to_lin(peak_db) / peak)
    path = RENDER_DIR / name
    _write_wav_file(path, out, fs)
    return path


def write_wav_group(named: dict[str, np.ndarray], fs: int = FS,
                    peak_db: float = -6.0) -> list[Path]:
    """Write a set of WAVs sharing ONE gain so relative levels are preserved.

    Use for sweeps (velocity/stiffness/material) where loudness differences
    between renders are part of what we want to hear.
    """
    peak = max(float(np.max(np.abs(y))) for y in named.values()) or 1.0
    g = db_to_lin(peak_db) / peak
    paths = []
    for name, y in named.items():
        path = RENDER_DIR / name
        _write_wav_file(path, y * g, fs)
        paths.append(path)
    return paths
