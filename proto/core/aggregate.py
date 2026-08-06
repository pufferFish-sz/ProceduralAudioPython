"""Aggregate / granular surface exciter (gravel, dirt, grass, debris).

References: Cook, "Physically Informed Sonic Modeling (PhISM/PhISEM)" (1997);
Turchet, "Footstep sounds synthesis" (Applied Acoustics, 2016), aggregate
surface layer.

PhISEM skeleton kept from v1:
- micro-collisions are a Poisson process, density driven by a control signal
  (impact energy / slide speed);
- each event carries a random (exponentially distributed) energy bump.

v2 changes (after listening tests on the v1 renders):
- v1 pushed ALL grains through one shared resonant bandpass. Hundreds of
  identically pitched rings fuse into a common-mode resonance that reads as
  a drum head / awning being hit by beads. v2 synthesizes each grain
  individually with RANDOMIZED center frequency (log-uniform), Q and decay,
  so no shared resonance builds up -- each pebble has its own pitch.
- added a "bed" component: broadband noise, bandpassed, amplitude-modulated
  by the (fast-smoothed) grain energy envelope. Vegetation-like surfaces
  (grass) are mostly THIS -- stochastic AM rustle, no audible resonance --
  per the observation that grass reads better as high-frequency noise.
- per-surface balance via bed_mix (0 = all discrete grains, 1 = all rustle).
"""
from __future__ import annotations

import numpy as np
from scipy.signal import butter, lfilter, sosfilt


def _biquad_bandpass(fc: float, q: float, fs: int):
    w0 = 2 * np.pi * fc / fs
    alpha = np.sin(w0) / (2 * q)
    b = np.array([alpha, 0.0, -alpha])
    a = np.array([1 + alpha, -2 * np.cos(w0), 1 - alpha])
    return b / a[0], a / a[0]


def aggregate_exciter(density_hz, duration: float, fs: int,
                      grain_fc: tuple[float, float] = (1000.0, 4000.0),
                      grain_q: tuple[float, float] = (1.0, 3.0),
                      grain_decay: tuple[float, float] = (0.002, 0.006),
                      bed_mix: float = 0.15,
                      bed_band: tuple[float, float] = (1500.0, 6000.0),
                      bed_smooth: float = 0.008,
                      energy=1.0, seed: int | None = 1) -> np.ndarray:
    """Poisson-triggered grain stream with per-grain randomized resonance.

    density_hz : scalar or per-sample array -- mean micro-impact rate (Hz).
    grain_fc   : (lo, hi) Hz -- per-grain center frequency, log-uniform.
    grain_q    : (lo, hi) -- per-grain resonance Q, uniform.
    grain_decay: (lo, hi) s -- per-grain energy decay, uniform.
    bed_mix    : 0..1 -- blend of continuous AM-noise bed vs discrete grains.
    bed_band   : bandpass (lo, hi) Hz for the bed noise.
    bed_smooth : smoothing time constant (s) for the bed's AM envelope.
    energy     : scalar or per-sample array scaling bump amplitude.
    """
    n = int(round(duration * fs))
    dens = np.broadcast_to(np.asarray(density_hz, dtype=float), (n,))
    en = np.broadcast_to(np.asarray(energy, dtype=float), (n,))
    rng = np.random.default_rng(seed)

    p = np.clip(dens / fs, 0.0, 1.0)
    event_idx = np.nonzero(rng.random(n) < p)[0]
    amps = rng.exponential(1.0, len(event_idx)) * en[event_idx]

    # ---- discrete grains: individual noise bursts, randomized resonance ----
    grains = np.zeros(n)
    if bed_mix < 1.0 and len(event_idx):
        lo_f, hi_f = grain_fc
        fcs = np.exp(rng.uniform(np.log(lo_f), np.log(hi_f), len(event_idx)))
        qs = rng.uniform(*grain_q, len(event_idx))
        decs = rng.uniform(*grain_decay, len(event_idx))
        for i0, amp, fc, q, dec in zip(event_idx, amps, fcs, qs, decs):
            L = min(int(8 * dec * fs) + 32, n - i0)
            if L <= 0:
                continue
            t = np.arange(L) / fs
            burst = rng.standard_normal(L) * np.exp(-t / dec) * amp
            b, a = _biquad_bandpass(min(fc, 0.45 * fs), q, fs)
            grains[i0:i0 + L] += lfilter(b, a, burst)

    # ---- noise bed: bandpassed noise AM'd by smoothed grain energy --------
    bed = np.zeros(n)
    if bed_mix > 0.0:
        bumps = np.zeros(n)
        bumps[event_idx] = amps
        a1 = np.exp(-1.0 / (bed_smooth * fs))
        env = lfilter([1.0 - a1], [1.0, -a1], bumps)
        sos = butter(2, [bed_band[0], min(bed_band[1], 0.47 * fs)],
                     btype="bandpass", fs=fs, output="sos")
        bed = sosfilt(sos, rng.standard_normal(n)) * np.sqrt(np.maximum(env, 0.0))

    def _norm(x):
        pk = float(np.max(np.abs(x)))
        return x / pk if pk > 0 else x

    return (1.0 - bed_mix) * _norm(grains) + bed_mix * _norm(bed) \
        if 0.0 < bed_mix < 1.0 else (_norm(bed) if bed_mix >= 1.0 else _norm(grains))


# Ear-tuned presets (density at full energy; scale density/energy by control)
AGGREGATE_PRESETS: dict[str, dict] = {
    # stones: every grain its own pitch, wide spread, ringy but incoherent
    "gravel": dict(density_hz=300.0, grain_fc=(900.0, 4500.0),
                   grain_q=(1.2, 3.0), grain_decay=(0.002, 0.007),
                   bed_mix=0.15, bed_band=(1500.0, 6000.0)),
    # dull crumble: low, broad, fast-dying grains, some low rustle
    "dirt":   dict(density_hz=350.0, grain_fc=(250.0, 1300.0),
                   grain_q=(0.8, 1.6), grain_decay=(0.0015, 0.004),
                   bed_mix=0.25, bed_band=(300.0, 2000.0)),
    # vegetation: mostly high-frequency AM noise rustle + tiny crackles
    "grass":  dict(density_hz=800.0, grain_fc=(3000.0, 9000.0),
                   grain_q=(0.8, 1.8), grain_decay=(0.0008, 0.002),
                   bed_mix=0.8, bed_band=(2800.0, 11000.0)),
}
