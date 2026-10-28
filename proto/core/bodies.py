"""Fully specified sounding bodies + two-body contact between them.

Every scene is "MOVER hits TARGET at v". Both are Bodies: a named object
with stated size and material whose modes come from core/shapes.py, so the
file name, the description and the physics all describe the same thing.

Contact (one force pulse, both bodies respond):
- k     = Hertz(E, nu of both; 1/R = 1/R_mover + 1/R_target)
- mass  = mover mass if the target is fixed (floor), else the reduced mass
          m1 m2 / (m1 + m2) (free target, e.g. a suspended bar)
- modes = mover modes + target modes inside ONE coupled Hunt-Crossley
          solve. Both sets are pushed back by the same force, so the
          compression is x = s - sum(q_mover) - sum(q_target): this is the
          two-body coupled model, not an approximation of it.
- sound = each body's modes driven by the force timeline (pressure proxy,
          core/radiation.py) + rigid-body "click" of each FREE body
          (acceleration f/M radiated by its area). Fixed bodies have none.

Because the same Body keeps ringing across repeated contacts (one modal
bank per body for the whole scene), a bouncing ball re-excites a floor that
is still moving -- the persistent-voice model planned for the plugin.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from .contact import force_at_rate
from .impact import hertz_stiffness, simulate_impact
from .modal_bank import ModalBank, Mode
from .radiation import (accel_to_pressure, coincidence_freq, sigma_of,
                        velocity_to_pressure)
from .materials import PHYSICAL
from .shapes import bar, plate_ss, sphere

ALPHA = 1.5        # Hertzian sphere-on-flat exponent
FLAT = np.inf      # contact radius of a flat surface


@dataclass
class Body:
    slug: str                 # file-name part, e.g. "rubber-ball-small-r15mm"
    description: str          # one human sentence for manifests
    material: str             # materials.PHYSICAL key (contact hardness)
    modes: list[Mode]
    mass: float               # kg; for a held stick: effective mass at the tip
    area: float               # m^2 radiating area (pressure proxy)
    contact_radius: float     # m, curvature where it touches (FLAT for planes)
    fixed: bool = False       # True = immovable (floors): no rigid click
    # radiation-efficiency model (core/radiation.py): compact dipole, or
    # {"kind": "plate", a, b, h, phys} for Maidanik plate radiation
    radiator: dict = field(default_factory=lambda: {"kind": "compact"})
    notes: list[str] = field(default_factory=list)


def contact_pulse(mover: Body, target: Body, v_in: float, fs: int,
                  mu: float) -> tuple[np.ndarray, dict]:
    """Coupled contact of mover into target; returns (force at fs, info)."""
    inv_r = 1.0 / mover.contact_radius + 1.0 / target.contact_radius
    k = hertz_stiffness(mover.material, target.material, 1.0 / inv_r)
    m = mover.mass if target.fixed else \
        mover.mass * target.mass / (mover.mass + target.mass)
    _, info = simulate_impact(m, v_in, k, ALPHA, mu * k,
                              mover.modes + target.modes, fs, dur=0.01)
    info.update(k=k, m_eff=m, rebound=max(0.0, -info["v_out"]))
    return force_at_rate(info, fs), info


# Coefficient of restitution of the MOVER's material against a hard surface
# at the scene's impact speed. Presets for plausibility (bouncy ball ~0.8-0.9,
# wooden stick on a hard bar ~0.5-0.7), not measurements.
RESTITUTION = {"rubber": 0.80, "wood": 0.60, "metal": 0.70, "glass": 0.75,
               "plastic": 0.60, "stone": 0.50}


def calibrate_mu(mover: Body, target: Body, v_in: float, fs: int,
                 e_target: float | None = None) -> float:
    """Hunt-Crossley mu (s/m) that gives restitution e_target at v_in.

    Calibrated once per scene at the first (fastest) impact and then held
    fixed, so slower later bounces come out MORE elastic -- the
    Hunt-Crossley trend, and what real balls do."""
    e_t = RESTITUTION[mover.material] if e_target is None else e_target

    def err(mu):
        _, info = contact_pulse(mover, target, v_in, fs, mu)
        return info["rebound"] / v_in - e_t

    lo, hi = 0.0, 0.05
    if err(lo) <= 0.0:          # losses into the modes alone already exceed it
        return 0.0
    while err(hi) > 0.0 and hi < 50.0:
        hi *= 2.0
    from scipy.optimize import brentq
    return brentq(err, lo, hi, xtol=1e-4)


def body_sound(body: Body, force: np.ndarray, fs: int, sign: float) -> dict:
    """Radiated pressure (Pa @ 1 m) of one body driven by a force timeline.

    Modes: each mode's spatial-rms velocity (contact-point velocity *
    sqrt(m_n / M), since phi_n(x_s)^2 = M / m_n) times
    rho c sqrt(sigma(f_n) S / 2 pi) / r -- folded into the modal output gains.
    Click (free bodies only): rigid-body acceleration -/+ f/M through the
    same sigma(f) (core/radiation.py).
    sign: +1 if the force pushes the body along +, -1 for the mover."""
    out = {"modes": np.zeros(len(force)), "click": np.zeros(len(force))}
    if body.modes:
        f_n = np.array([m.freq for m in body.modes])
        w = velocity_to_pressure(sigma_of(body.radiator, body.area, f_n),
                                 body.area)
        weighted = [Mode(freq=m.freq, decay=m.decay, mass=m.mass,
                         gain=float(wn * np.sqrt(m.mass / body.mass)))
                    for m, wn in zip(body.modes, w)]
        y = ModalBank(weighted, fs).process(force)
        out["modes"] = np.diff(y, prepend=0.0) * fs      # displacement -> velocity
    if not body.fixed:
        # rigid-body motion of the WHOLE object radiates as a compact dipole
        # even when its bending modes radiate like a plate: Maidanik's plate
        # efficiency does not fall to 0 at low f, and through the 1/(i w)
        # of accel_to_pressure it blows up near DC (a free 0.2 kg box)
        out["click"] = accel_to_pressure(sign * force / body.mass, fs,
                                         {"kind": "compact"}, body.area)
    out["mix"] = out["modes"] + out["click"]
    return out


def with_contact_damping(body: Body, loss: float, why: str) -> Body:
    """Copy of `body` whose modes also lose energy into a contact: decay
    d_n += pi f_n * loss (a loss factor added to tan phi). An object lying
    on its face is held along that face, so its bending modes ring far
    shorter than when it hangs free (contact damping, Zheng & James 2011)."""
    from dataclasses import replace
    modes = [replace(m, decay=m.decay + np.pi * m.freq * loss)
             for m in body.modes]
    return replace(body, modes=modes,
                   notes=body.notes + [f"contact damping: loss factor +{loss:g} "
                                       f"while in contact ({why})"])


def mode_summary(body: Body, n: int = 4) -> str:
    if not body.modes:
        return "none audible (all modes > 16 kHz)"
    return ", ".join(f"{m.freq:.0f}" for m in body.modes[:n]) + " Hz"


# ------------------------------------------------------------- catalog

def rubber_ball(radius: float, size_word: str) -> Body:
    modes, M = sphere(radius, "rubber")
    return Body(slug=f"rubber-ball-{size_word}-r{radius*1e3:.0f}mm",
                description=(f"solid rubber ball, radius {radius*100:.1f} cm, "
                             f"{M*1e3:.0f} g (bouncy-ball type)"),
                material="rubber", modes=modes, mass=M,
                area=np.pi * radius**2, contact_radius=radius,
                notes=["solid, not air-filled: a hollow playground ball adds "
                       "an air-cavity resonance this model does not have"])


FLOOR_SPECS = {
    # slug: (description, material, a, b, thickness, installed tan_phi)
    "concrete-slab": ("concrete slab on ground, 4 x 4 m, 15 cm thick",
                      "concrete", 4.0, 4.0, 0.15, 0.05),
    "wood-floor": ("wooden plank floor bay, 2.4 x 1.2 m, 22 mm boards",
                   "wood", 2.4, 1.2, 0.022, 0.03),
    "steel-plate-floor": ("steel deck plate walkway, 1 x 1 m, 6 mm",
                          "metal", 1.0, 1.0, 0.006, 0.005),
}


def floor(slug: str) -> Body:
    desc, mat, a, b, h, loss = FLOOR_SPECS[slug]
    modes, M = plate_ss(a, b, h, mat, tan_phi=loss, f_max=10000.0)
    fc = coincidence_freq(h, PHYSICAL[mat])
    return Body(slug=slug, description=f"{desc}, installed loss {loss}",
                material=mat, modes=modes, mass=M, area=a * b,
                contact_radius=FLAT, fixed=True,
                radiator=dict(kind="plate", a=a, b=b, h=h, phys=PHYSICAL[mat]),
                notes=[f"simply supported plate; radiates per Maidanik, "
                       f"coincidence {fc:.0f} Hz (inefficient below)"])


def wood_stick() -> Body:
    """Drumstick-like wooden stick, 30 cm x 12 mm, swung from the hand.
    Effective tip mass of a rod pivoting about its end = M/3.

    Rigid striker: NO modes of its own. A free-free rod hit at its tip is
    very light in bending (every mode has tip mass M/4); in the coupled
    solve it absorbs 80-95 % of the impact energy (rebound 5-18 % of the
    swing), and driven open-loop it gains more energy than the swing had.
    Neither matches a hand-held stick, whose grip damps and loads it. Until
    a grip model exists the stick contributes only its contact click."""
    L, r = 0.30, 0.006
    M = PHYSICAL["wood"]["rho"] * np.pi * r**2 * L
    return Body(slug="wood-stick-30cm", description=(
                    f"wooden stick 30 cm long, 12 mm diameter, {M*1e3:.0f} g, "
                    "swung from one end (tip effective mass M/3), rounded "
                    "6 mm tip"),
                material="wood", modes=[], mass=M / 3.0,
                area=2 * r * L, contact_radius=r,
                notes=["stick = rigid striker: you hear its contact click, "
                       "not its own ring (no hand-grip model yet)"])


BAR_DIMS = (0.30, 0.04, 0.02)      # length, width, thickness (m)


def plank(L: float, w: float, t: float, material: str, word: str,
          kind: str, strike: float = 0.3, contact_radius: float = FLAT,
          situation: str = "free-free") -> Body:
    """Slender rectangular object (bar, plank, block piece): beam modes from
    shapes.bar, contacted at `strike` (fraction of length)."""
    modes, M = bar(L, w, t, material, strike=strike, n_modes=8)
    dims = f"{L*100:g}x{w*100:g}x{t*100:g}cm"
    return Body(slug=f"{word}-{kind}-{dims}",
                description=(f"{word} {kind} {dims.replace('x', ' x ')}, "
                             f"{M:.2f} kg, {situation}, contact at "
                             f"{strike*100:.0f} % of its length"),
                material=material, modes=modes, mass=M, area=L * w,
                contact_radius=contact_radius)


def bar_body(material: str, word: str) -> Body:
    L, w, t = BAR_DIMS
    return plank(L, w, t, material, word, "bar",
                 situation="resting on soft supports (free-free)")
