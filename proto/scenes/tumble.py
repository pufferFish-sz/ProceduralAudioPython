"""Scene family: a small block thrown onto the floor, tumbling to rest.

Objects are 20 x 5 x 2 cm pieces (wood or steel); floors as in ball_drop.
What makes a tumble sound like a tumble, and how it is generated:
- every landing hits a DIFFERENT point (random position along the length),
  so each hit excites a different mix of the same modes -- the object's
  pitch stays, its colour changes from hit to hit;
- corners/edges land first (contact radius 3 mm);
- with 50 % chance a landing on an edge is followed 10-40 ms later by the
  other end slapping down ("clack-clack"), at 30-70 % of the landing speed;
- the block is thrown with vertical AND sideways speed. Rebound speed comes
  from the contact solve (restitution calibrated once, mu * v held constant
  as in ball_drop); a random 40-90 % of it stays vertical (the rest goes
  into spin). Each landing also catches an edge and turns part of the
  sideways speed into a new hop (35 % x U(0.2, 1)), while the sideways
  speed drops by 25-50 %. This is a heuristic stand-in for rigid-body
  rotation, not a rigid-body simulation;
- it stops when the landing speed falls below 0.15 m/s.
Linear superposition: each hit drives the object's modes with its own
contact-point coupling; the floor sees the summed force at one point.

Gate: momentum check on every contact (< 1 %).
Run:  python -m proto.scenes.tumble
"""
import numpy as np

from ..core.bodies import body_sound, calibrate_mu, contact_pulse, floor, plank
from ..util import FS
from .common import G, Scene, write_family

V0 = 2.5           # vertical speed at first landing (m/s)
U0 = 3.0           # sideways throw speed (m/s)
EDGE_R = 0.003
DIMS = (0.20, 0.05, 0.02)
CASES = [("wood", "wood", "block", "wood-floor"),
         ("wood", "wood", "block", "concrete-slab"),
         ("metal", "steel", "bar", "concrete-slab")]
FLOOR_WORDS = {"concrete-slab": "a concrete slab",
               "wood-floor": "a wooden plank floor"}


def piece(material, word, kind, strike):
    return plank(*DIMS, material, word, kind, strike=strike,
                 contact_radius=EDGE_R, situation="tumbling, lands on edges")


def tumble_scene(material, word, kind, flr, seed=5, tail=1.0):
    rng = np.random.default_rng(seed)
    first = piece(material, word, kind, 0.5)
    mu0 = calibrate_mu(first, flr, V0, FS)
    t, v, u = 0.3, V0, U0
    hits = []                      # (t, strike pos, pulse, info, v_in)

    def hit(t_, pos, v_):
        body = piece(material, word, kind, pos)
        pulse, info = contact_pulse(body, flr, v_, FS, mu0 * V0 / v_)
        hits.append((t_, body, pulse, info, v_))
        return info

    while v >= 0.15 and len(hits) < 40:
        pos = rng.uniform(0.05, 0.95)
        info = hit(t, pos, v)
        if rng.random() < 0.5:     # other end slaps down
            hit(t + rng.uniform(0.010, 0.040), 1.0 - pos,
                v * rng.uniform(0.3, 0.7))
        hop = 0.35 * u * rng.uniform(0.2, 1.0)     # edge catch: sideways -> up
        u *= rng.uniform(0.5, 0.75)
        v = info["rebound"] * rng.uniform(0.4, 0.9) + hop
        t += info["contact_time"] + 2 * v / G
    n = int((hits[-1][0] + tail) * FS)
    F_total = np.zeros(n)
    obj = np.zeros(n)
    for t_i, body, pulse, _, _ in hits:
        F = np.zeros(n)
        i0 = int(t_i * FS)
        m = min(len(pulse), n - i0)
        F[i0:i0 + m] = pulse[:m]
        F_total += F
        obj += body_sound(body, F, FS, -1.0)["mix"]
    stems = {first.slug: obj, flr.slug: body_sound(flr, F_total, FS, +1.0)["mix"]}
    imp_err = max(abs(p.sum() / FS - b.mass * (vi + inf["rebound"]))
                  / (b.mass * (vi + inf["rebound"])) for _, b, p, inf, vi in hits)
    k = hits[0][3]["k"]
    facts = [f"thrown {U0:g} m/s sideways, first landing {V0:g} m/s "
             f"vertical; {len(hits)} contacts over {hits[-1][0] - 0.3:.2f} s",
             f"contact stiffness k = {k:.2e} N/m^1.5 (Hertz, {material} edge "
             f"r = {EDGE_R*1e3:.0f} mm on {flr.material})",
             f"contact points vary along the length (5-95 %), so each hit "
             f"colours the same modes differently",
             f"impulse check: max error {100*imp_err:.2f} % vs m (v_in + v_out)"]
    sc = Scene(name="", what="", mover=first, target=flr, stems=stems,
               facts=facts)
    sc.imp_err = imp_err
    return sc


def main():
    scenes = []
    for material, word, kind, fslug in CASES:
        flr = floor(fslug)
        s = tumble_scene(material, word, kind, flr)
        s.name = (f"tumble_{s.mover.slug}_thrown-{U0:g}mps_onto_{fslug}")
        s.what = (f"a small {word} {kind} is thrown onto {FLOOR_WORDS[fslug]} "
                  "and tumbles to rest: irregular clacks, getting softer")
        scenes.append(s)
        print(f"  {s.name}")
        for f in s.facts:
            print(f"      {f}")
    out = write_family(
        "tumble", "Small block tumbling to rest",
        "20 x 5 x 2 cm pieces thrown sideways at 3 m/s. Two wood-block files differ "
        "only in the floor; the steel file differs from the second only in "
        "the object's material. Same random seed for all three.", scenes)
    ok = all(s.imp_err < 0.01 for s in scenes)
    print(f"tumble gate impulse conserved every contact: {'PASS' if ok else 'FAIL'}")
    print(f"tumble: {len(scenes)} scenes -> {out}")
    return ok


if __name__ == "__main__":
    main()
