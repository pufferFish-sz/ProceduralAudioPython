"""Rolling exciter: a round object riding over a surface profile.

What the rolling recordings in proto/recordings/Rolling show (analysis in
docs/rolling_sliding_vs_recordings.md), and where each feature comes from:

1. Energy sits below ~300 Hz (75-99 % for ball, can, barrel, orange): a
   rolling object cannot follow fine detail, so the contact force carries
   the LONG wavelengths of the surface at f = v / lambda, and those drive the
   floor's low modes. -> the profile is filtered by the object's own shape
   (point 1 below), not by a free lowpass.
2. A slow, deep level modulation (1.7-5 Hz, 11-21 dB) at the revolution
   rate v / (2 pi R) or a small multiple: out-of-round objects, dents,
   seams. -> the object carries its own periodic profile around its
   circumference, read by rolled distance.
3. Strongly impulsive >1 kHz band (kurtosis 13-600) with 4-60 clicks/s:
   grout lines, board joints, grit. -> where the dilated profile falls away
   faster than gravity can pull the object down, it lifts off and lands:
   each landing is a Hunt-Crossley micro-impact, the same law as impacts.

Model (one vertical degree of freedom, after van den Doel, Kry & Pai 2001
and Rath & Rocchesso 2005: a ball rides the "upper envelope" of the
surface, not the surface itself):

    s(x)    = max_u [ z(x+u) - (R - sqrt(R^2 - u^2)) ]   circle dilation,
              then averaged over the Hertz contact width
    h(x)    = s(x) + r_obj(x mod 2 pi R)                 + object profile
    delta   = h(x(t)) - y                                penetration
    f       = k delta^alpha + c(delta) ddelta/dt,  f >= 0
    c       = 2 zeta sqrt(m k_lin(delta)),  k_lin = alpha k delta^(alpha-1)
    m y''   = f - m g

Sphere: alpha = 1.5, k = 4/3 E* sqrt(R) (Hertz point contact).
Cylinder rolling on its side: alpha = 1, k = pi/4 E* L (Hertz line
contact, log term dropped).

Damping: NOT Hunt-Crossley here. HC (f ~ k delta^a (1 + mu ddelta/dt))
loses energy in proportion to the landing speed (e ~ 1 - 2/3 mu v), so the
~1 cm/s micro-landings of rolling are almost elastic (e ~ 0.997 at
mu = 0.6 s/m) and a hard object chatters for seconds (measured: battery
airborne 98 % of the time). Real micro-bounces lose their energy into
floor and object vibration, which this rigid solve does not contain. The
Kelvin-Voigt term with a local damping ratio zeta gives a roughly
speed-independent restitution e ~ exp(-pi zeta / sqrt(1 - zeta^2)), chosen
per surface. (Mapping zeta onto HC mu instead gives mu ~ 1e3 s/m for a
stiff contact, and mu * ddelta/dt then multiplies the force ~200x at a
grout edge and launches the object.)

The vertical solve runs at oversample * fs (semi-implicit Euler; contact
resonance sqrt(k_lin/m) stays far below the step rate) and is decimated
with an anti-alias filter. Output: force fluctuation f - m g (N), for
core/bodies.body_sound (object sign -1, floor sign +1).

Simplifications: no tangential/rolling-resistance force fluctuation, no
slip, one contact track (a real ball wanders sideways), no contents
(pills, liquid slosh), the object profile is not itself dilated.
"""
from __future__ import annotations

import numpy as np
from scipy.ndimage import grey_dilation
from scipy.signal import resample_poly

from .impact import effective_modulus
from .slide_profile import DX, read_profile, surface_profile

G = 9.81


def contact_law(shape: str, radius: float, length: float,
                obj_mat, floor_mat) -> tuple[float, float]:
    """(k, alpha) for a sphere (point) or a cylinder on its side (line)."""
    e_star = effective_modulus(obj_mat, floor_mat)
    if shape == "sphere":
        return 4.0 / 3.0 * e_star * np.sqrt(radius), 1.5
    if shape == "cylinder":
        return np.pi / 4.0 * e_star * length, 1.0
    raise ValueError(shape)


def static_contact(k: float, alpha: float, m: float):
    """Static penetration, linearized stiffness, contact resonance (Hz)."""
    d0 = (m * G / k) ** (1.0 / alpha)
    k_lin = alpha * k * d0 ** (alpha - 1.0)
    return d0, k_lin, np.sqrt(k_lin / m) / (2 * np.pi)


def dilate_by_circle(z: np.ndarray, radius: float) -> np.ndarray:
    """Upper envelope traced by the lowest point of a circle of `radius`
    rolling over profile z (grid DX)."""
    span = float(z.max() - z.min())
    w = min(np.sqrt(2 * radius * max(span, DX * 1e-3)), 0.5 * radius)
    half = max(1, int(w / DX))
    u = np.arange(-half, half + 1) * DX
    sag = radius - np.sqrt(np.maximum(radius**2 - u**2, 0.0))
    return grey_dilation(z, structure=-sag, mode="nearest")


def object_profile(spec: dict | None, n: int, radius: float,
                   seed: int = 0) -> np.ndarray:
    """Periodic height of the object's own rim on one circumference, n
    samples of DX: eccentricity (once per revolution), seams/dents (narrow
    bumps, + = raised, - = dent) and random lumpiness (orders 2-8)."""
    z = np.zeros(n)
    if not spec:
        return z
    s = np.arange(n) / n                       # 0..1 around the rim
    z += spec.get("ecc", 0.0) * np.cos(2 * np.pi * s)
    for pos, height, width in spec.get("bumps", []):
        d = (s - pos + 0.5) % 1.0 - 0.5        # wrapped distance, in turns
        sig = width / (2 * np.pi * radius) / 2.355
        z += height * np.exp(-0.5 * (d / sig) ** 2)
    rough = spec.get("rough")
    if rough:
        # the object's own surface texture: with the floor's roughness this
        # is the "combined roughness" of rolling-noise theory (Thompson,
        # Railway Noise and Vibration, 2009). Periodic by construction.
        rng = np.random.default_rng(seed + 11)
        kk = np.fft.rfftfreq(n, DX)
        amp = np.where(kk > 0, np.maximum(kk, 1.0) ** (-rough["gamma"] / 2), 0.0)
        zr = np.fft.irfft(amp * np.exp(2j * np.pi * rng.random(len(kk))), n)
        z += rough["h_rms"] * zr / (np.std(zr) or 1.0)
    lump = spec.get("lumps", 0.0)
    if lump:
        rng = np.random.default_rng(seed + 7)
        orders = np.arange(2, 9)
        amp = rng.standard_normal(len(orders)) / orders
        ph = rng.random(len(orders)) * 2 * np.pi
        zl = sum(a * np.cos(2 * np.pi * o * s + p)
                 for a, o, p in zip(amp, orders, ph))
        z += lump * zl / (np.std(zl) or 1.0)
    return z


def gaussian_smooth(z: np.ndarray, sigma: float) -> np.ndarray:
    """Contact-patch average of a profile on grid DX (Gaussian, sigma m)."""
    k = np.fft.rfftfreq(len(z), DX)
    return np.fft.irfft(np.fft.rfft(z) * np.exp(-0.5 * (2 * np.pi * k * sigma) ** 2),
                        len(z))


def roll_force(speed: np.ndarray, fs: int, surface: dict, radius: float,
               mass: float, k: float, alpha: float, zeta: float,
               obj_spec: dict | None = None, track_width: float = 0.0,
               oversample: int | None = None, seed: int = 0,
               t_on: float = 3e-4) -> tuple[np.ndarray, dict]:
    """Normal-force fluctuation (N) of a rolling object; returns
    (force at fs, info).

    t_on: the Kelvin-Voigt term c * ddelta/dt is at full strength the
    instant a landing starts (the elastic term starts at 0), so the force
    STEPPED by ~2 mg within one audio sample at every touchdown: every floor
    mode up to 10 kHz kicked at once, a hard edge in the waveform heard as
    clipping. The damping now builds up linearly over t_on (0.3 ms) after
    each touchdown. Steady rolling has no touchdowns and is unchanged.
    (Fading by penetration instead does not work: 10 % of delta0 passes in
    ~1 sample at landing speed, and fading over the whole delta0
    under-damps steady rolling -- baseball LTAS 5.4 -> 14 dB.)
    track_width: length of a line contact (cylinder). Random roughness is
    uncorrelated across the track beyond the surface's l_corr (default
    1 mm), so a long roller sees its rms reduced by sqrt(l_corr / width);
    straight features (board joints, grout) and single grit grains are not
    averaged away.
    The contact is solved at oversample * fs (None: 4x, raised up to 16x
    for stiff contacts). A contact resonance above fs_s / 20 is softened to
    fs_s / 20 (at 16x that is ~35 kHz: far above hearing, so audibly still
    rigid). Landings then span >= 10 steps; with fewer, the semi-implicit
    Euler step gains or loses energy at each contact switch and a light,
    hard object chatters forever."""
    speed = np.maximum(np.asarray(speed, dtype=float), 0.0)
    n0 = len(speed)
    k_phys = k
    d0, k_lin, f_c = static_contact(k, alpha, mass)
    if oversample is None:
        oversample = int(np.clip(np.ceil(20.0 * f_c / fs), 4, 16))
    fs_s = fs * oversample
    v = np.interp(np.arange(n0 * oversample) / oversample, np.arange(n0), speed)
    x = np.cumsum(v) / fs_s
    f_cap = fs_s / 20.0
    if f_c > f_cap:
        k *= (f_cap / f_c) ** 2 if alpha == 1.0 else (f_cap / f_c) ** 3
    d0, k_lin, f_c_used = static_contact(k, alpha, mass)
    a_hertz = np.sqrt(radius * static_contact(k_phys, alpha, mass)[0])

    surf = dict(surface)
    if track_width > 0:
        surf["h_rms"] = surface["h_rms"] * min(
            1.0, np.sqrt(surface.get("l_corr", 1e-3) / track_width))
    z = surface_profile(surf, x[-1] + 0.1, sigma_c=DX, seed=seed)
    # ride the asperity tops first (rigid circle), THEN average over the
    # contact patch: smoothing after the max() removes the dilation's kinks
    s_tab = gaussian_smooth(dilate_by_circle(z, radius), max(a_hertz, DX))
    circ = 2 * np.pi * radius
    n_c = max(8, int(round(circ / DX)))
    r_tab = gaussian_smooth(object_profile(obj_spec, n_c, radius, seed),
                           max(a_hertz, DX))      # circular FFT = periodic
    h = read_profile(s_tab, x) + read_profile(r_tab, x, periodic=True)
    hd = np.gradient(h) * fs_s

    dt = 1.0 / fs_s
    inv_m = 1.0 / mass
    c0 = 2.0 * zeta * np.sqrt(mass * alpha * k)   # c = c0 delta^((alpha-1)/2)
    ce = (alpha - 1.0) / 2.0
    n_on = max(1, int(round(t_on * fs_s)))
    on_len = n_on                 # steps since touchdown (start in contact)
    y, yd = h[0] - d0, hd[0]
    f = np.zeros(len(h))
    hl, hdl = h.tolist(), hd.tolist()
    airborne = 0
    clamped = 0                   # in contact, but damping pulled f below 0
    landings = 0
    was_off = False
    off_len = 0
    min_flight = int(2e-4 * fs_s)             # ignore sub-0.2 ms chatter
    for i in range(len(hl)):
        dlt = hl[i] - y
        if dlt > 0.0:
            c = c0 * (dlt if dlt > d0 else d0) ** ce if ce else c0
            if on_len < n_on:                 # just touched down: damping
                c *= on_len / n_on            # builds up over t_on (no step)
            on_len += 1
            fi = k * dlt ** alpha + c * (hdl[i] - yd)
            if fi < 0.0:
                fi = 0.0
                clamped += 1
            if was_off and off_len >= min_flight:
                landings += 1
            was_off, off_len = False, 0
        else:
            fi = 0.0
            on_len = 0
            airborne += 1
            was_off = True
            off_len += 1
        yd += dt * (fi * inv_m - G)
        y += dt * yd
        f[i] = fi
    force = resample_poly(f - mass * G, 1, oversample)[:n0]
    moving = speed > 1e-4
    t_roll = max(moving.sum() / fs, 1e-9)
    info = dict(k=k_phys, k_used=k, alpha=alpha, zeta=zeta,
                restitution=float(np.exp(-np.pi * zeta / np.sqrt(1 - zeta**2))),
                delta0=static_contact(k_phys, alpha, mass)[0], f_contact=f_c,
                f_contact_used=f_c_used, a_contact=a_hertz,
                h_rms_seen=surf["h_rms"], oversample=oversample,
                airborne=airborne / len(hl), clamped=clamped / len(hl),
                landings_per_s=landings / t_roll,
                rev_hz=float(np.median(speed[moving])) / circ
                if moving.any() else 0.0)
    return force, info
