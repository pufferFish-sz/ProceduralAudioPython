"""Impact exciter: Hunt-Crossley nonlinear contact force + coupled integration.

Reference: Avanzini & Rocchesso, "Modeling Collision Sounds: Non-Linear
Contact Force" (DAFx-01, 2001).

Model
-----
A lumped striker (mass m_s, incoming velocity v_in) hits a modally described
resonator. With s = striker position and r = sum_n q_n = resonator surface
displacement at the contact point (all mode shape weights t_n = 1), the
compression is x = s - r and the Hunt-Crossley force is

    f(x, xdot) = k x^alpha + lambda x^alpha xdot     for x > 0
               = 0                                    otherwise

with stiffness k, elasticity exponent alpha (~1.5 for Hertzian sphere
contact) and dissipation lambda (often given as mu = lambda / k). The force
is clamped at f >= 0: near the end of contact the raw expression can go
negative (surfaces would have to pull on each other), which is unphysical
for non-adhesive contact.

Coupled system:

    m_s s''  = -f
    q_n'' + 2 d_n q_n' + w0_n^2 q_n = f / m_n

Numerics
--------
Two integrators are provided:

1. `simulate_impact(..., method="rk4")` -- ground truth. Fixed-step RK4 at an
   oversampled rate chosen so the (Hertz-estimated) contact time spans >= 40
   steps. RK4 runs only while the striker is near the surface; after
   separation the modal free decay is continued analytically (exact), so the
   render length is unlimited at no cost.

2. `simulate_impact(..., method="implicit")` -- audio-rate scheme in the
   spirit of Avanzini & Rocchesso's K-method. Striker and modes are
   discretized with the trapezoidal (bilinear) rule, which has direct
   feedthrough: the compression at sample i depends on the force at sample i,
   creating the delay-free loop the K-method addresses. Both x and xdot are
   affine in the unknown force,

        x[i]    = P  - G  f[i]
        xdot[i] = Pd - Gd f[i]      (G, Gd > 0 constants; P, Pd from state)

   so each sample requires solving the scalar nonlinear equation

        f = HC(P - G f, Pd - Gd f),  f >= 0

   (this is where the implicit nonlinear equation arises). HC is monotone
   decreasing in f here, so the root is unique; we solve it with bisection
   via scipy's brentq. This is the shape a real-time C++ port would take
   (Newton with a couple of iterations instead of brentq).

3. `force_pulse_rigid` + `ModalBank.process` -- open-loop fallback kept per
   spec: the force pulse is precomputed against a rigid wall and fed to the
   modal bank as a plain input signal.
"""
from __future__ import annotations

import numpy as np
from scipy.optimize import brentq

from .modal_bank import ModalBank, Mode, ring_out


def contact_force(x, xdot, k: float, alpha: float, lam: float):
    """Hunt-Crossley force, elementwise; clamped to f >= 0 (no adhesion)."""
    x = np.asarray(x, dtype=float)
    xdot = np.asarray(xdot, dtype=float)
    xa = np.where(x > 0.0, x, 0.0) ** alpha
    f = k * xa + lam * xa * xdot
    return np.maximum(f, 0.0)


def _hc_scalar(x: float, xdot: float, k: float, alpha: float, lam: float) -> float:
    if x <= 0.0:
        return 0.0
    xa = x ** alpha
    return max(0.0, k * xa + lam * xa * xdot)


def _contact_stats(x_hist: np.ndarray, h: float):
    """Contact metrics from the compression history.

    contact_time = duration of the FIRST contiguous x>0 segment (this is the
    quantity Avanzini & Rocchesso's trends refer to). With a compliant
    resonator and strong dissipation the surface can chase the barely-
    rebounding striker and re-collide ("micro-bounces"); those extra
    segments are reported separately as n_contacts / contact_span.
    """
    idx = np.nonzero(x_hist > 0.0)[0]
    if len(idx) == 0:
        return 0.0, 0, 0.0
    gaps = np.nonzero(np.diff(idx) > 1)[0]
    first_len = (gaps[0] + 1) if len(gaps) else len(idx)
    n_contacts = len(gaps) + 1
    span = (idx[-1] - idx[0] + 1) * h
    return first_len * h, n_contacts, span


def hertz_contact_time(m: float, k: float, v: float) -> float:
    """Analytic contact-time estimate for the lossless Hertz case alpha=1.5.

    tau ~= 2.87 (m^2 / (k^2 v))^(1/5). Used only to pick the sim step."""
    return 2.87 * (m * m / (k * k * max(v, 1e-3))) ** 0.2


def simulate_impact(striker_mass: float, v_in: float, k: float, alpha: float,
                    lam: float, modes: list[Mode], fs: int,
                    dur: float = 1.0, method: str = "rk4",
                    t_contact_max: float = 0.05) -> tuple[np.ndarray, dict]:
    """Strike the modal resonator; return (audio, info).

    info keys: contact_time, f_max, force (pulse at sim rate), force_t,
    stable, v_out, fs_sim, method.
    """
    if method == "rk4":
        return _simulate_rk4(striker_mass, v_in, k, alpha, lam, modes, fs,
                             dur, t_contact_max)
    elif method == "implicit":
        return _simulate_implicit(striker_mass, v_in, k, alpha, lam, modes, fs,
                                  dur, t_contact_max)
    raise ValueError(f"unknown method {method!r}")


# ---------------------------------------------------------------- RK4 path

def _simulate_rk4(m_s, v_in, k, alpha, lam, modes, fs, dur, t_contact_max):
    bank = ModalBank(modes, fs)
    N = len(modes)
    w0sq = bank.w0**2
    twod = 2.0 * bank.decays
    m_n = bank.masses

    # step size: >= 40 steps per (estimated) contact, at least 8x oversampling
    tau_est = hertz_contact_time(m_s, k, v_in)
    os_ = int(np.clip(np.ceil(40.0 / (tau_est * fs)), 8, 4096))
    h = 1.0 / (fs * os_)

    def deriv(y):
        s, vs = y[0], y[1]
        q = y[2:2 + N]
        v = y[2 + N:]
        x = s - q.sum()
        xd = vs - v.sum()
        f = _hc_scalar(x, xd, k, alpha, lam)
        dy = np.empty_like(y)
        dy[0] = vs
        dy[1] = -f / m_s
        dy[2:2 + N] = v
        dy[2 + N:] = f / m_n - w0sq * q - twod * v
        return dy, f

    y = np.zeros(2 + 2 * N)
    y[1] = v_in
    n_max = int(t_contact_max / h)
    f_hist = np.zeros(n_max)
    x_hist = np.zeros(n_max)
    q_hist = np.zeros((n_max, N))
    touched = False
    n_steps = 0
    for i in range(n_max):
        k1, f_now = deriv(y)
        k2, _ = deriv(y + 0.5 * h * k1)
        k3, _ = deriv(y + 0.5 * h * k2)
        k4, _ = deriv(y + h * k3)
        y = y + (h / 6.0) * (k1 + 2 * k2 + 2 * k3 + k4)
        f_hist[i] = f_now
        q_hist[i] = y[2:2 + N]
        x = y[0] - y[2:2 + N].sum()
        x_hist[i] = x
        n_steps = i + 1
        if not np.all(np.isfinite(y)):
            break
        if f_now > 0.0:
            touched = True
        # separation: past contact, gap opening, striker receding
        if touched and f_now == 0.0 and x < 0.0 and y[1] < 0.0:
            break

    stable = bool(np.all(np.isfinite(y)))
    f_hist = f_hist[:n_steps]
    x_hist = x_hist[:n_steps]
    q_hist = q_hist[:n_steps]

    contact_time, n_contacts, contact_span = _contact_stats(x_hist, h)
    f_max = float(f_hist.max()) if n_steps else 0.0

    # audio: decimate sim segment to fs grid, then analytic ring-out
    n_total = int(round(dur * fs))
    part1 = bank.gains @ q_hist[::os_].T if stable else np.zeros(0)
    n1 = min(len(part1), n_total)
    audio = np.zeros(n_total)
    audio[:n1] = part1[:n1]
    if stable and n1 < n_total:
        t_end = n_steps * h
        taus = np.arange(n1, n_total) / fs - t_end
        q0 = y[2:2 + N].copy()
        v0 = y[2 + N:].copy()
        audio[n1:] = ring_out(q0, v0, bank, taus)

    info = dict(contact_time=contact_time, n_contacts=n_contacts,
                contact_span=contact_span, f_max=f_max, force=f_hist,
                force_t=np.arange(n_steps) * h, stable=stable,
                v_out=float(y[1]), fs_sim=fs * os_, method="rk4")
    return audio, info


# ----------------------------------------------------- implicit audio-rate

def _simulate_implicit(m_s, v_in, k, alpha, lam, modes, fs, dur, t_contact_max):
    bank = ModalBank(modes, fs)
    N = len(modes)
    w0sq = bank.w0**2
    d = bank.decays
    m_n = bank.masses
    h = 1.0 / fs

    D = 1.0 + h * d + (h * h / 4.0) * w0sq          # per-mode trapezoid denom
    G = h * h / (4.0 * m_s) + np.sum(h * h / (4.0 * m_n * D))
    Gd = h / (2.0 * m_s) + np.sum(h / (2.0 * m_n * D))

    s, vs = 0.0, v_in
    q = np.zeros(N)
    v = np.zeros(N)
    f_prev = 0.0

    n_win = int(t_contact_max * fs)
    f_hist = np.zeros(n_win)
    x_hist = np.zeros(n_win)
    q_hist = np.zeros((n_win, N))
    touched = False
    n_steps = 0
    stable = True
    for i in range(n_win):
        a_prev = -w0sq * q - 2.0 * d * v + f_prev / m_n
        Cv = v + 0.5 * h * a_prev - 0.5 * h * w0sq * (q + 0.5 * h * v)
        # free (f=0) predictions
        v_free = Cv / D
        q_free = q + 0.5 * h * (v + v_free)
        s_free = s + h * vs - (h * h / (4.0 * m_s)) * f_prev
        vs_free = vs - (h / (2.0 * m_s)) * f_prev
        P = s_free - q_free.sum()
        Pd = vs_free - v_free.sum()

        if P <= 0.0:
            f = 0.0
        else:
            def g(fi):
                return fi - _hc_scalar(P - G * fi, Pd - Gd * fi, k, alpha, lam)
            if g(0.0) >= 0.0:
                f = 0.0
            else:
                hi = max(1.0, f_prev * 2.0)
                while g(hi) < 0.0 and hi < 1e15:
                    hi *= 4.0
                f = brentq(g, 0.0, hi, xtol=1e-9, rtol=1e-12)

        v_new = v_free + (0.5 * h / (m_n * D)) * f
        q = q + 0.5 * h * (v + v_new)      # trapezoid: q_prev + h/2 (v_prev + v_new)
        v = v_new
        s = s_free - (h * h / (4.0 * m_s)) * f
        vs = vs_free - (h / (2.0 * m_s)) * f
        f_prev = f

        f_hist[i] = f
        x_hist[i] = s - q.sum()
        q_hist[i] = q
        n_steps = i + 1
        if not np.isfinite(f) or not np.all(np.isfinite(q)):
            stable = False
            break
        if f > 0.0:
            touched = True
        if touched and f == 0.0 and (s - q.sum()) < 0.0 and vs < 0.0:
            break

    f_hist = f_hist[:n_steps]
    x_hist = x_hist[:n_steps]
    q_hist = q_hist[:n_steps]
    contact_time, n_contacts, contact_span = _contact_stats(x_hist, h)
    f_max = float(f_hist.max()) if n_steps else 0.0

    n_total = int(round(dur * fs))
    audio = np.zeros(n_total)
    n1 = min(n_steps, n_total)
    audio[:n1] = (bank.gains @ q_hist[:n1].T)
    if stable and n1 < n_total:
        taus = np.arange(1, n_total - n1 + 1) * h
        audio[n1:] = ring_out(q.copy(), v.copy(), bank, taus)

    info = dict(contact_time=contact_time, n_contacts=n_contacts,
                contact_span=contact_span, f_max=f_max, force=f_hist,
                force_t=np.arange(n_steps) * h, stable=stable,
                v_out=float(vs), fs_sim=fs, method="implicit")
    return audio, info


# ------------------------------------------------------ open-loop fallback

def force_pulse_rigid(striker_mass: float, v_in: float, k: float, alpha: float,
                      lam: float, fs: int, oversample: int = 64,
                      t_max: float = 0.05) -> np.ndarray:
    """Force pulse of the striker against a RIGID wall (resonator immobile),
    integrated with RK4 and decimated to fs. Feed this open-loop into a
    ModalBank via .process() -- the cheap decoupled path kept as fallback.
    """
    h = 1.0 / (fs * oversample)
    x, v = 0.0, v_in

    def acc(x_, v_):
        return -_hc_scalar(x_, v_, k, alpha, lam) / striker_mass

    n_max = int(t_max / h)
    f_hist = np.zeros(n_max)
    n_steps = 0
    for i in range(n_max):
        f_hist[i] = _hc_scalar(x, v, k, alpha, lam)
        k1x, k1v = v, acc(x, v)
        k2x, k2v = v + 0.5 * h * k1v, acc(x + 0.5 * h * k1x, v + 0.5 * h * k1v)
        k3x, k3v = v + 0.5 * h * k2v, acc(x + 0.5 * h * k2x, v + 0.5 * h * k2v)
        k4x, k4v = v + h * k3v, acc(x + h * k3x, v + h * k3v)
        x += (h / 6.0) * (k1x + 2 * k2x + 2 * k3x + k4x)
        v += (h / 6.0) * (k1v + 2 * k2v + 2 * k3v + k4v)
        n_steps = i + 1
        if x < 0.0 and v < 0.0:
            break
    return f_hist[:n_steps:oversample].copy()
