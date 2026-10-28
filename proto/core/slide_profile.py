"""Surface-profile sliding exciter ("model B"; core/friction.py is model A).

Built from the literature reviewed in docs/sliding_sound_literature.md:

1. Profile read by POSITION (van den Doel, Kry & Pai 2001, "phonograph
   needle"): each surface owns a fixed 1-D height profile z(x): fractal
   roughness (PSD ~ k^-gamma) + reson bumps at a spatial frequency k_r
   (FoleyAutomatic's speed-scaled resons: heard at f = v k_r) + optional
   meso features (board joints, tread pattern; Ren, Yeh & Lin 2010's
   "visible bumpiness" level). The contact reads z(x(t)), x = integral of v,
   so the same patch always sounds the same and the texture's pitch glides
   with speed.
   The contact patch AVERAGES the profile (Gaussian kernel, sigma = SIGMA_C
   ~ 0.1 mm): a contact cannot follow detail finer than itself
   (FoleyAutomatic: a large contact "only sees" large-scale structure;
   Agarwal et al. smooth after their limiter). Finer roughness reaches the
   sound only through lift-off and landings (3). The same Gaussian also
   removes aliasing: at 2.5 m/s it is ~ -130 dB at fs/2.
2. Curvature limit (Agarwal et al. 2021 bound the scraper path's curvature
   with tanh): here in its physical form. A probe of effective contact mass
   m_p pressed by N can follow the surface downward only while
   z_tt > -N/m_p. Where the surface falls away faster it LIFTS OFF and
   flies (y_tt = -N/m_p) until it lands again. Upward following
   accelerations are soft-limited with tanh (Agarwal's limiter) at
   UP_RATIO * N/m_p.
3. Micro-impacts: every landing is a collision with impulse
   J = m_p (z_t - y_t), shaped as a Hertz half-sine whose duration comes from
   impact.hertz_contact_time with asperity stiffness from Hertz theory. So
   impact density and strength come from the surface and the speed, not
   from preset statistics (the cue Conan et al. 2014 found separates
   scratching from rubbing).
4. Normal-force variation (Agarwal et al.): N(t) = N0 (1 + w n(t)), with
   n(t) slow (< 6 Hz) noise -- rocking/yaw of the sliding object. It moves
   the lift-off threshold, so the texture breathes.

Output: the fluctuating NORMAL force on the surface (contact following
force m_p z_tt, zero in flight, landing pulses; mean removed), in newtons,
for core/bodies.body_sound.

Simplifications: one effective contact point (a flat face really averages
over a contact area), tangential force not used to drive flexural modes,
no stick-slip (model A's squeak remains for that).
"""
from __future__ import annotations

import numpy as np
from scipy.signal import butter, sosfilt

from .impact import hertz_contact_time, hertz_stiffness

DX = 20e-6          # profile table resolution (m)
SIGMA_C = 1.0e-4    # m, contact-patch averaging length (Gaussian sigma)
UP_RATIO = 10.0     # upward following-acceleration limit, x N/m_p
R_ASPERITY = 5e-4   # m, asperity tip radius for landing stiffness
T_ON = 3e-4         # s, contact force build-up after a landing

# floor slug -> profile spec. Values are ear-plausible presets with a
# physical reading, not measurements.
#   h_rms: roughness rms (m); gamma: PSD slope of the 1-D profile (measured
#   engineering surfaces are self-affine with Hurst H ~ 0.7-0.9, i.e.
#   gamma = 1 + 2H ~ 2.4-2.8; higher = smoother/duller)
#   k_r, q, reson_share: speed-scaled texture resonance (cycles per m)
#   features: meso pattern (period m, width m, height m; negative = groove)
#   l_corr (optional, default 1 mm): roughness correlation length ACROSS
#     the track (averages roughness under a long line contact)
#   grit (optional): loose particles on the surface -- Poisson positions
#     (per_m), lognormal heights (median height m, sigma), Gaussian bumps of
#     FWHM width. Rolled over, each one is a tiny bump-and-landing (the
#     sparse crackle in the rolling recordings).
SURFACE_PROFILES = {
    "wood-floor": dict(h_rms=6e-6, gamma=2.6, k_r=600.0, q=3.0,
                       reson_share=0.5,
                       features=dict(period=0.12, width=1.5e-3, height=-3e-4),
                       grit=dict(per_m=15.0, height=15e-6, sigma=0.8,
                                 width=0.4e-3),
                       note="sanded boards, grain ~1.7 mm, a groove between "
                            "12 cm boards, a little household grit"),
    # same boards, varnished: the finish fills the grain. The sanded preset's
    # 1.7 mm grain ripple (~4 um rms) is fine for a sliding plank, but a
    # small ball (R <~ 2 cm) at 0.6 m/s cannot follow it (needs > g down)
    # and hops every ripple, ~250 landings/s: heard as static.
    "varnished-wood-floor": dict(h_rms=1.5e-6, gamma=2.6, k_r=600.0, q=3.0,
                                 reson_share=0.1,
                                 features=dict(period=0.12, width=1.5e-3,
                                               height=-3e-4),
                                 grit=dict(per_m=15.0, height=15e-6, sigma=0.8,
                                           width=0.4e-3),
                                 note="varnished boards (grain filled, 1.5 um "
                                      "rms), a groove between 12 cm boards, a "
                                      "little household grit"),
    # same varnished boards, tight flush tongue-and-groove joints (1 mm,
    # 0.1 mm deep): a 1-2 cm ball dips ~28 um into the 1.5 x 0.3 mm joints
    # above, is kicked up at the far edge and bounces -- the loudest ticks
    # of the small-ball renders
    "varnished-wood-floor-tight": dict(h_rms=1.5e-6, gamma=2.6, k_r=600.0,
                                       q=3.0, reson_share=0.1,
                                       features=dict(period=0.12, width=1.0e-3,
                                                     height=-1e-4),
                                       grit=dict(per_m=15.0, height=15e-6,
                                                 sigma=0.8, width=0.4e-3),
                                       note="varnished boards (1.5 um rms), "
                                            "tight flush joints every 12 cm "
                                            "(1 mm, 0.1 mm deep), a little grit"),
    "tile-floor": dict(h_rms=0.5e-6, gamma=2.8, k_r=2000.0, q=2.0,
                       reson_share=0.1,
                       features=dict(period=0.30, width=4e-3, height=-1.2e-3),
                       grit=dict(per_m=80.0, height=15e-6, sigma=0.8,
                                 width=0.4e-3),
                       note="glazed ceramic tiles, 30 cm grid, 4 mm grout "
                            "lines 1.2 mm deep, a little grit"),
    "rug": dict(h_rms=150e-6, gamma=2.0, k_r=330.0, q=1.0, reson_share=0.4,
                features=None, l_corr=3e-3,
                note="cut-pile rug: tufts ~3 mm, very soft and lossy"),
    "concrete-slab": dict(h_rms=60e-6, gamma=2.4, k_r=250.0, q=1.5,
                          reson_share=0.3, features=None,
                          note="broom-finish concrete: rough, aggregate "
                               "texture ~4 mm"),
    "steel-plate-floor": dict(h_rms=1.5e-6, gamma=2.8, k_r=1500.0, q=4.0,
                              reson_share=0.3,
                              features=dict(period=0.025, width=5e-3,
                                            height=4e-4),
                              note="smooth steel with a raised tread "
                                   "pattern every 25 mm"),
}


def surface_profile(spec: dict, length: float, sigma_c: float = SIGMA_C,
                    seed: int = 0) -> np.ndarray:
    """Height profile z on a grid of DX as SEEN by a contact patch of size
    sigma_c (Gaussian average), including meso features."""
    rng = np.random.default_rng(seed)
    n = int(length / DX)
    k = np.fft.rfftfreq(n, DX)
    band = k > 10.0
    phase = np.exp(2j * np.pi * rng.random(len(k)))

    def from_amp(amp):
        z = np.fft.irfft(amp * phase, n)
        return z / (np.sqrt(np.mean(z**2)) or 1.0)

    fractal = from_amp(np.where(band, np.maximum(k, 1.0) ** (-spec["gamma"] / 2), 0))
    reson = from_amp(np.where(band, np.exp(-0.5 * ((k - spec["k_r"]) /
                                                   (spec["k_r"] / spec["q"]))**2), 0))
    s = spec["reson_share"]
    z = spec["h_rms"] * (np.sqrt(1 - s) * fractal + np.sqrt(s) * reson)
    feat = spec.get("features")
    if feat:
        x = np.arange(n) * DX
        d = (x % feat["period"]) - feat["period"] / 2
        z += feat["height"] * np.exp(-0.5 * (d / (feat["width"] / 2.355))**2)
    grit = spec.get("grit")
    if grit:
        z += grit_profile(grit, n, rng)
    patch = np.exp(-0.5 * (2 * np.pi * k * sigma_c) ** 2)    # contact averaging
    return np.fft.irfft(np.fft.rfft(z) * patch, n)


def read_profile(tab: np.ndarray, x: np.ndarray,
                 periodic: bool = False) -> np.ndarray:
    """Height at positions x (m) from a profile table on grid DX, by cubic
    spline (continuous curvature). Linear interpolation puts a curvature
    impulse at every grid point: the contact force then carries a line at
    v / DX (10 kHz at 0.2 m/s), or, above Nyquist, folded-back arcs that
    move as the speed changes. periodic: the table is one period (a rim)."""
    from scipy.interpolate import CubicSpline
    if periodic:
        tab = np.append(tab, tab[0])
        cs = CubicSpline(np.arange(len(tab)) * DX, tab, bc_type="periodic")
        return cs(np.mod(x, (len(tab) - 1) * DX))
    return CubicSpline(np.arange(len(tab)) * DX, tab)(x)


def grit_profile(grit: dict, n: int, rng) -> np.ndarray:
    """Height of loose grit particles on a grid of n * DX (see grit spec)."""
    z = np.zeros(n)
    count = rng.poisson(grit["per_m"] * n * DX)
    pos = rng.integers(0, n, count)
    h = grit["height"] * np.exp(grit["sigma"] * rng.standard_normal(count))
    s = grit["width"] / 2.355 / DX
    half = int(4 * s) + 1
    bump = np.exp(-0.5 * (np.arange(-half, half + 1) / s) ** 2)
    for p, hi in zip(pos, h):
        lo, hi_i = max(p - half, 0), min(p + half + 1, n)
        z[lo:hi_i] = np.maximum(z[lo:hi_i],
                                hi * bump[lo - p + half:hi_i - p + half])
    return z


def normal_force(n: int, fs: int, N0: float, wobble: float,
                 seed: int = 0) -> np.ndarray:
    rng = np.random.default_rng(seed + 100)
    sos = butter(2, 6.0, fs=fs, output="sos")
    w = sosfilt(sos, rng.standard_normal(n + fs))[fs:]
    w /= np.sqrt(np.mean(w**2)) or 1.0
    return N0 * np.maximum(1.0 + wobble * w, 0.2)


def profile_slide_force(speed: np.ndarray, fs: int, spec: dict, N0: float,
                        m_p: float, slider_mat: str, floor_mat: str,
                        wobble: float = 0.15, seed: int = 0,
                        oversample: int = 1, n_tracks: int = 1,
                        sigma_c: float | tuple = SIGMA_C,
                        wobble_seed: int | None = None):
    """Normal-force fluctuation (N) for a slide; returns (force, info).

    speed may be SIGNED (back-and-forth strokes re-trace the same patch).
    oversample > 1 runs the non-linear contact (lift-off, tanh limit,
    sub-sample landing pulses) at oversample * fs and decimates with an
    anti-alias filter. At 1x the folded-back harmonics are audible as
    arcs that rise while the slide slows down.
    n_tracks > 1: a FLAT FACE rides on many asperity contacts at once. Each
    track gets N0/n and m_p/n and its own random roughness (seed + j); the
    meso features (board joints) are shared, so they still click across the
    whole face, and so is the normal-force wobble (the whole object rocks).
    One track lifts off and clicks; the sum of several is the
    near-Gaussian texture measured in the sliding recordings.
    sigma_c: contact-patch averaging length. Brightness of the texture is
    set by v / (2 pi sigma_c): 0.1 mm puts it near 1.3 kHz at 0.8 m/s,
    asperity-scale contacts (~30 um) near 4 kHz. One scale gives a hump at
    that frequency; a (lo, hi) tuple gives each track its own scale,
    log-spaced (asperity contacts come in many sizes), and the summed
    spectrum flattens out like the recordings'."""
    if n_tracks > 1:
        tot, infos = 0.0, []
        if isinstance(sigma_c, tuple):
            sigmas = np.geomspace(sigma_c[0], sigma_c[1], n_tracks)
        else:
            sigmas = np.full(n_tracks, sigma_c)
        for j in range(n_tracks):
            f, inf = profile_slide_force(speed, fs, spec, N0 / n_tracks,
                                         m_p / n_tracks, slider_mat, floor_mat,
                                         wobble, seed + 101 * j, oversample,
                                         1, float(sigmas[j]), wobble_seed=seed)
            tot = tot + f
            infos.append(inf)
        info = {k: float(np.mean([i[k] for i in infos])) for k in infos[0]}
        fl = tot[np.abs(np.asarray(speed)) > 1e-4]
        info["kurtosis"] = float(np.mean(fl**4) / np.mean(fl**2) ** 2) \
            if fl.size else 0.0
        info["n_tracks"] = n_tracks
        return tot, info
    if oversample > 1:
        from scipy.signal import resample_poly
        n0 = len(speed)
        t0 = np.arange(n0)
        v_os = np.interp(np.arange(n0 * oversample) / oversample, t0, speed)
        f, info = profile_slide_force(v_os, fs * oversample, spec, N0, m_p,
                                      slider_mat, floor_mat, wobble, seed,
                                      sigma_c=sigma_c, wobble_seed=wobble_seed)
        return resample_poly(f, 1, oversample)[:n0], info
    vel = np.asarray(speed, dtype=float)
    speed = np.abs(vel)
    n = len(speed)
    x = np.cumsum(vel) / fs
    x0 = min(x.min(), 0.0)
    z_tab = surface_profile(spec, x.max() - x0 + 0.05, sigma_c=sigma_c,
                            seed=seed)
    z = read_profile(z_tab, x - x0)
    zt = np.gradient(z) * fs
    ztt = np.gradient(zt) * fs
    N = normal_force(n, fs, N0, wobble,
                     seed if wobble_seed is None else wobble_seed)
    a_dn = N / m_p
    k_asp = hertz_stiffness(slider_mat, floor_mat, R_ASPERITY)

    f = np.zeros(n)
    landings = []
    y = z[0]
    yt = zt[0]
    contact = True
    moving = speed > 1e-4
    t_flight = 0
    # after a landing the contact force builds back up over T_ON instead
    # of snapping from 0 to N in one sample: that step kicked every mode up
    # to Nyquist at once (a hard edge in the waveform, heard as clipping;
    # same fix as core/rolling.py). The landing impulse itself is the
    # separate Hertz pulse below.
    n_on = max(1, int(round(T_ON * fs)))
    on_len = n_on
    for i in range(n):
        if not moving[i]:
            contact, y, yt = True, z[i], zt[i]
            f[i] = N[i]
            continue
        if contact:
            if ztt[i] < -a_dn[i]:                      # surface drops away
                contact = False
                y, yt = z[i], zt[i]
            else:
                a_up = UP_RATIO * a_dn[i]
                f[i] = N[i] + m_p * a_up * np.tanh(ztt[i] / a_up)
                if on_len < n_on:
                    f[i] *= on_len / n_on
                on_len += 1
                continue
        # flight: pressed down by N, no contact force
        t_flight += 1
        yt -= a_dn[i] / fs
        y += yt / fs
        if y <= z[i]:                                  # lands
            v_rel = zt[i] - yt
            if v_rel > 0:
                landings.append((i, m_p * v_rel, v_rel))
            contact, y, yt = True, z[i], zt[i]
            on_len = 0                                 # f[i] = 0, builds up
    for i, J, v_rel in landings:
        tau = hertz_contact_time(m_p, k_asp, v_rel)
        L = max(2, int(round(tau * fs)))
        pulse = np.sin(np.pi * (np.arange(L) + 0.5) / L)
        pulse *= J * fs / pulse.sum()
        m = min(L, n - i)
        f[i:i + m] += pulse[:m]

    sliding = moving.sum() or 1
    fluct = f - N                                      # DC + slow wobble are silent
    fl = fluct[moving]
    kurt = float(np.mean(fl**4) / (np.mean(fl**2) ** 2)) if fl.size else 0.0
    info = dict(lift_off_fraction=t_flight / sliding,
                landings_per_s=len(landings) / (sliding / fs),
                kurtosis=kurt, k_asperity=k_asp)
    return fluct, info
