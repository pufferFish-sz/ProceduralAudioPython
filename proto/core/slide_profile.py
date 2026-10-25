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

# floor slug -> profile spec. Values are ear-plausible presets with a
# physical reading, not measurements.
#   h_rms: roughness rms (m); gamma: PSD slope of the 1-D profile (measured
#   engineering surfaces are self-affine with Hurst H ~ 0.7-0.9, i.e.
#   gamma = 1 + 2H ~ 2.4-2.8; higher = smoother/duller)
#   k_r, q, reson_share: speed-scaled texture resonance (cycles per m)
#   features: meso pattern (period m, width m, height m; negative = groove)
SURFACE_PROFILES = {
    "wood-floor": dict(h_rms=6e-6, gamma=2.6, k_r=600.0, q=3.0,
                       reson_share=0.5,
                       features=dict(period=0.12, width=1.5e-3, height=-3e-4),
                       note="sanded boards, grain ~1.7 mm, a groove between "
                            "12 cm boards"),
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
    patch = np.exp(-0.5 * (2 * np.pi * k * sigma_c) ** 2)    # contact averaging
    return np.fft.irfft(np.fft.rfft(z) * patch, n)


def normal_force(n: int, fs: int, N0: float, wobble: float,
                 seed: int = 0) -> np.ndarray:
    rng = np.random.default_rng(seed + 100)
    sos = butter(2, 6.0, fs=fs, output="sos")
    w = sosfilt(sos, rng.standard_normal(n + fs))[fs:]
    w /= np.sqrt(np.mean(w**2)) or 1.0
    return N0 * np.maximum(1.0 + wobble * w, 0.2)


def profile_slide_force(speed: np.ndarray, fs: int, spec: dict, N0: float,
                        m_p: float, slider_mat: str, floor_mat: str,
                        wobble: float = 0.15, seed: int = 0):
    """Normal-force fluctuation (N) for a slide; returns (force, info)."""
    speed = np.maximum(np.asarray(speed, dtype=float), 0.0)
    n = len(speed)
    x = np.cumsum(speed) / fs
    z_tab = surface_profile(spec, x[-1] + 0.05, seed=seed)
    z = np.interp(x, np.arange(len(z_tab)) * DX, z_tab)
    zt = np.gradient(z) * fs
    ztt = np.gradient(zt) * fs
    N = normal_force(n, fs, N0, wobble, seed)
    a_dn = N / m_p
    k_asp = hertz_stiffness(slider_mat, floor_mat, R_ASPERITY)

    f = np.zeros(n)
    landings = []
    y = z[0]
    yt = zt[0]
    contact = True
    moving = speed > 1e-4
    t_flight = 0
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
            f[i] = N[i]
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
