"""Texture statistics for continuous contact sounds (sliding, rolling).

Used to compare real recordings (proto/recordings/) against renders. All
measures are taken over the ACTIVE part of a file (frames within 30 dB of
the loudest 5 ms frame) so silence before/after does not count.

Measures (each has a perceptual reading):
- ltas         long-term spectrum, 1/6-octave smoothed, dB re its max
- centroid     median spectral centroid (Hz) and its 10-90 % spread:
               brightness, and how much it moves with speed
- flatness     median spectral flatness (0 = tonal, 1 = white noise)
- env_std_db   std of the 5 ms level in dB: "smooth" vs "gritty" texture
- kurtosis     of the >1 kHz band signal: 3 = Gaussian hiss, >> 3 = clicks
- events_s     clicks per second: >1 kHz envelope peaks 9 dB over the
               local (50 ms) median level
- mod_peak_hz  strongest envelope modulation in 1.5-40 Hz and its depth
               (dB over the modulation floor): rolling periodicity
               (one bump per revolution) and stick-slip rhythms
- low_share    energy share below 300 Hz: rumble / body weight
- tonal        strongest narrow spectral peaks (Hz, dB over the smoothed
               LTAS): object or floor resonances that a texture "knows"
"""
from __future__ import annotations

import numpy as np
from scipy.signal import butter, find_peaks, resample_poly, sosfiltfilt, stft

FS_A = 48000


def load(path, fs_target: int = FS_A, max_s: float | None = None):
    import soundfile as sf
    y, fs = sf.read(str(path), always_2d=True)
    y = y.mean(axis=1)
    if fs != fs_target:
        from math import gcd
        g = gcd(fs, fs_target)
        y = resample_poly(y, fs_target // g, fs // g)
    if max_s is not None:
        y = y[:int(max_s * fs_target)]
    return y, fs_target


def _frame_rms(y, n):
    m = len(y) // n
    return np.sqrt(np.mean(y[:m * n].reshape(m, n) ** 2, axis=1) + 1e-20)


def active_mask(y, fs, win_s=0.005, floor_db=30.0):
    n = int(win_s * fs)
    r = 20 * np.log10(_frame_rms(y, n))
    return r > r.max() - floor_db, n


def stats(y, fs: int = FS_A) -> dict:
    y = np.asarray(y, dtype=float)
    y = y - y.mean()
    act, n5 = active_mask(y, fs)
    keep = np.repeat(act, n5)
    ya = y[:len(keep)][keep]
    out: dict = {"active_s": len(ya) / fs}

    # spectrum over time (only active frames)
    f, t, Z = stft(y, fs, nperseg=2048, noverlap=1536)
    P = np.abs(Z) ** 2
    e = P.sum(axis=0)
    a = e > e.max() * 10 ** (-30 / 10)
    Pa = P[:, a]
    ltas = Pa.mean(axis=1) + 1e-30
    cen = (f[:, None] * Pa).sum(0) / Pa.sum(0)
    flat = np.exp(np.mean(np.log(Pa[1:] + 1e-30), 0)) / Pa[1:].mean(0)
    out["centroid"] = float(np.median(cen))
    out["centroid_p10_p90"] = (float(np.percentile(cen, 10)),
                               float(np.percentile(cen, 90)))
    out["flatness"] = float(np.median(flat))
    out["low_share"] = float(ltas[f < 300].sum() / ltas.sum())

    # 1/6-octave smoothed LTAS on a fixed grid (for plots / distances)
    grid = 50.0 * 2 ** (np.arange(0, 54) / 6)          # 50 Hz .. ~23 kHz
    sm = np.array([ltas[(f >= g / 2 ** (1 / 12)) & (f < g * 2 ** (1 / 12))].mean()
                   if np.any((f >= g / 2 ** (1 / 12)) & (f < g * 2 ** (1 / 12)))
                   else np.nan for g in grid])
    sm_db = 10 * np.log10(sm)
    out["ltas_grid"] = grid
    out["ltas_db"] = sm_db - np.nanmax(sm_db)

    # tonal peaks: narrow peaks over a 1/3-octave running median
    ldb = 10 * np.log10(ltas)
    base = np.array([np.median(ldb[(f >= fi / 2 ** (1 / 6)) & (f <= fi * 2 ** (1 / 6))])
                     if fi > 40 else ldb[i] for i, fi in enumerate(f)])
    prom = ldb - base
    pk, _ = find_peaks(prom, height=6.0, distance=4)
    pk = pk[(f[pk] > 60) & (f[pk] < 16000)]
    order = np.argsort(prom[pk])[::-1][:6]
    out["tonal"] = [(float(f[pk[i]]), float(prom[pk[i]])) for i in order]

    # level texture
    lev = 20 * np.log10(_frame_rms(y, n5))[act]
    out["env_std_db"] = float(np.std(lev - _smooth(lev, 20)))   # remove 100 ms trend

    # impulsiveness of the >1 kHz band
    sos = butter(4, 1000.0, "highpass", fs=fs, output="sos")
    yh = sosfiltfilt(sos, y)[:len(keep)][keep]
    out["kurtosis"] = float(np.mean(yh**4) / np.mean(yh**2) ** 2)

    # click events
    n1 = int(0.001 * fs)
    eh = _frame_rms(sosfiltfilt(sos, y), n1)
    med = _running_median(eh, 50)
    act1 = np.repeat(act, n5 // n1)[:len(eh)]
    eh, med = eh[:len(act1)], med[:len(act1)]
    pk, _ = find_peaks(np.where(act1, eh / (med + 1e-20), 0), height=10 ** (9 / 20),
                       distance=3)
    out["events_s"] = float(len(pk) / max(out["active_s"], 1e-3))

    # envelope modulation spectrum (10 ms envelope, active stretch)
    n10 = int(0.01 * fs)
    env = _frame_rms(y, n10)
    mask = np.repeat(act, n5)
    mask = np.pad(mask, (0, max(0, len(env) * n10 - len(mask))))
    actm = mask[:len(env) * n10].reshape(-1, n10).any(1)
    env = np.log(env[actm] + 1e-12)
    if len(env) > 300:
        env = env - _smooth(env, 150)           # drop < ~0.7 Hz trend
        M = np.abs(np.fft.rfft(env * np.hanning(len(env)))) ** 2
        fm = np.fft.rfftfreq(len(env), 0.01)
        band = (fm > 1.5) & (fm < 40)
        i = np.argmax(M[band])
        floor = np.median(M[band])
        out["mod_peak_hz"] = float(fm[band][i])
        out["mod_depth_db"] = float(10 * np.log10(M[band][i] / floor))
        out["mod_fm"], out["mod_spec"] = fm[band], 10 * np.log10(M[band] / floor)
    else:
        out["mod_peak_hz"], out["mod_depth_db"] = float("nan"), float("nan")
    return out


def _smooth(x, n):
    n = max(1, min(n, len(x)))
    k = np.ones(n) / n
    return np.convolve(np.pad(x, (n // 2, n - 1 - n // 2), mode="edge"), k, "valid")


def _running_median(x, n):
    from scipy.ndimage import median_filter
    return median_filter(x, size=n, mode="nearest")


def summary_row(name, s) -> str:
    ton = ", ".join(f"{fr:.0f}" for fr, _ in s["tonal"][:4]) or "-"
    return (f"{name[:46]:46s} {s['active_s']:5.1f} {s['centroid']:6.0f} "
            f"{s['centroid_p10_p90'][0]:5.0f}-{s['centroid_p10_p90'][1]:<5.0f} "
            f"{s['flatness']:.2f} {s['env_std_db']:4.1f} {s['kurtosis']:6.1f} "
            f"{s['events_s']:5.0f} {s['mod_peak_hz']:5.1f}/{s['mod_depth_db']:4.1f} "
            f"{s['low_share']:.2f}  {ton}")


COMPARE_KEYS = [("centroid", "centroid Hz", "{:.0f}"),
                ("low_share", "<300 Hz share", "{:.2f}"),
                ("env_std_db", "level sd dB", "{:.1f}"),
                ("kurtosis", ">1k kurtosis", "{:.0f}"),
                ("events_s", "clicks/s", "{:.0f}"),
                ("mod_peak_hz", "mod peak Hz", "{:.1f}"),
                ("mod_depth_db", "mod depth dB", "{:.0f}"),
                ("n_tonal", "narrow peaks", "{:d}")]


def ltas_distance(a: dict, b: dict, lo: float = 80.0, hi: float = 12000.0) -> float:
    """RMS dB difference of the two 1/6-octave LTAS shapes (both normalized
    to their own max; levels of recordings are uncalibrated)."""
    g = a["ltas_grid"]
    m = (g >= lo) & (g <= hi) & np.isfinite(a["ltas_db"]) & np.isfinite(b["ltas_db"])
    d = a["ltas_db"][m] - b["ltas_db"][m]
    d -= d.mean()                                  # shape, not level
    return float(np.sqrt(np.mean(d**2)))


def compare_line(render: dict, rec: dict) -> str:
    """One manifest line: render vs recording on every measure."""
    for s in (render, rec):
        s["n_tonal"] = len(s["tonal"])
    parts = [f"{label} {fmt.format(render[k])} vs {fmt.format(rec[k])}"
             for k, label, fmt in COMPARE_KEYS]
    return ("vs recording (render vs real): " + "; ".join(parts)
            + f"; LTAS shape distance {ltas_distance(render, rec):.1f} dB "
            f"(above 300 Hz: {ltas_distance(render, rec, lo=300.0):.1f} dB)")


def pair_figure(pairs: list, path, title: str, dur: float = 6.0) -> None:
    """Per pair: render spectrogram, recording spectrogram, LTAS overlay,
    envelope modulation overlay. pairs = [(label, y_r, fs_r, y_rec, fs_rec,
    stats_r, stats_rec, rec_name)]."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from scipy.signal import spectrogram
    fig, axs = plt.subplots(len(pairs), 4, figsize=(18, 2.9 * len(pairs)),
                            squeeze=False,
                            gridspec_kw=dict(width_ratios=[3, 3, 2, 2]))
    for row, (label, yr, fr, yc, fc, sr, sc, rec_name) in zip(axs, pairs):
        for ax, y, fs, name in ((row[0], yr, fr, "RENDER " + label),
                                (row[1], yc, fc, "REAL " + rec_name)):
            y = y[:int(dur * fs)]
            f, t, S = spectrogram(y, fs, nperseg=1024, noverlap=768)
            S = 10 * np.log10(S + 1e-30)
            S -= S.max()
            ax.pcolormesh(t, f, S, vmin=-80, vmax=0, shading="auto",
                          cmap="magma")
            ax.set_yscale("symlog", linthresh=500)
            ax.set_ylim(30, 20000)
            ax.set_title(name[:72], fontsize=7)
        g = sr["ltas_grid"]
        row[2].semilogx(g, sr["ltas_db"], label="render")
        row[2].semilogx(g, sc["ltas_db"], label="real", ls="--")
        row[2].set_ylim(-70, 3)
        row[2].set_title(f"LTAS (1/6 oct), shape dist "
                         f"{ltas_distance(sr, sc):.1f} dB "
                         f"(>300 Hz {ltas_distance(sr, sc, lo=300.0):.1f})",
                         fontsize=7)
        row[2].legend(fontsize=7)
        for s, lab, ls in ((sr, "render", "-"), (sc, "real", "--")):
            if "mod_fm" in s:
                row[3].plot(s["mod_fm"], s["mod_spec"], ls, label=lab)
        row[3].set_title("envelope modulation (dB over floor)", fontsize=7)
        row[3].set_xlabel("Hz", fontsize=7)
        row[3].legend(fontsize=7)
    fig.suptitle(title)
    fig.tight_layout()
    fig.savefig(path, dpi=80)
    plt.close(fig)


HEADER = (f"{'file':46s} {'act_s':>5s} {'centr':>6s} {'p10-p90':>11s} "
          f"{'flat':>4s} {'envsd':>4s} {'kurt':>6s} {'ev/s':>5s} {'mod Hz/dB':>10s} "
          f"{'<300':>4s}  tonal peaks Hz")
