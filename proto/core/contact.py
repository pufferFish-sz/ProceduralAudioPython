"""Unified two-body contact: one force pulse, every body contributes.

There is no "is the other thing the ground?" branch. A contact is between
the dropped/thrown OBJECT and whatever it hits; the other body's sound
model decides what it adds:

    k      = Hertz(object material, surface material, edge radius)
    f(t)   = Hunt-Crossley pulse (object rigid mass = striker, surface =
             rigid wall in the contact solve)
    object = modal ring (contact-point acceleration, radiated by obj_area)
           + contact click: rigid-body acceleration f(t)/M radiated by
             obj_area -- the "acceleration noise" of Chadwick, Zheng &
             James 2012, reduced to its simplest form
    surface= surface_response(f(t)) -- floor modes with a physical modal
             mass, same pressure units (core/ground.py)

All three are in the same pressure-proxy units (core/radiation.py), so the
balance between object and floor is no longer a hand-set gain: a soft
object makes a long, dull pulse that excites the floor's low modes; a
massive concrete slab barely moves; a light plank floor thumps.
"""
from __future__ import annotations

import numpy as np

from .ground import GROUND_PRESETS, surface_response
from .impact import hertz_stiffness, simulate_impact
from .modal_bank import Mode
from .radiation import pressure_from_accel, pressure_from_displacement


def force_at_rate(info: dict, fs: int) -> np.ndarray:
    """Contact force from simulate_impact info, resampled to fs.

    The RK4 path runs oversampled; block-averaging preserves the impulse
    (integral of f), which is what drives the low floor modes."""
    f = info["force"]
    os_ = int(round(info["fs_sim"] / fs))
    if os_ <= 1:
        return f.copy()
    n = int(np.ceil(len(f) / os_))
    f = np.pad(f, (0, n * os_ - len(f)))
    return f.reshape(n, os_).mean(axis=1)


def render_contact(obj_modes: list[Mode], obj_mass: float, obj_area: float,
                   obj_material: str | dict, v_in: float,
                   surface: str | dict, fs: int, dur: float,
                   edge_radius: float = 0.003, alpha: float = 1.5,
                   mu: float = 0.6, k: float | None = None) -> dict:
    """Render one object-on-surface impact; returns components + info.

    keys: object, click, surface, mix (all Pa @ 1 m), force (N @ fs), k,
    info (simulate_impact info). Pass k to override the Hertz value.
    """
    p = GROUND_PRESETS[surface] if isinstance(surface, str) else surface
    if k is None:
        k = hertz_stiffness(obj_material, p["material"], edge_radius)
    disp, info = simulate_impact(obj_mass, v_in, k, alpha, mu * k, obj_modes,
                                 fs, dur=dur)
    n = len(disp)
    force = force_at_rate(info, fs)
    f = np.zeros(n)
    f[:min(len(force), n)] = force[:n]

    # one sign convention for all bodies: + = direction of the object's
    # incoming motion. Modes and floor are pushed along +, the object's
    # rigid body is decelerated (-f/M).
    obj = pressure_from_displacement(disp, fs, obj_area)
    click = pressure_from_accel(-f / obj_mass, obj_area)
    srf = surface_response(f, fs, p, dur)[:n]
    return dict(object=obj, click=click, surface=srf,
                mix=obj + click + srf, force=f, k=k, info=info)
