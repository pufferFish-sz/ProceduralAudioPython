"""Scene family: a small wooden stick strikes three bars of identical size
made of wood, steel and stone.

Same stick, same 2 m/s swing, same bar size and strike point; only the bar
material changes. Material enters three ways at once: pitch (sqrt(E/rho)),
ring time (tan_phi) and contact hardness (Hertz, E and nu).

Gate: bar fundamentals follow sqrt(E/rho) exactly (same geometry).
Run:  python -m proto.scenes.stick_strike
"""
import numpy as np

from ..core.bodies import bar_body, wood_stick
from ..core.materials import PHYSICAL
from .common import strike_scene, write_family

V = 2.0
BARS = [("wood", "wood"), ("metal", "steel"), ("stone", "stone")]


def main():
    stick = wood_stick()
    scenes = []
    for mat, word in BARS:
        target = bar_body(mat, word)
        s = strike_scene(stick, target, V)
        s.name = f"strike_{stick.slug}_at-{V:g}mps_on_{target.slug}"
        s.what = (f"a wooden stick hits a {word} bar (30 x 4 x 2 cm) once at "
                  f"{V:g} m/s; the bar rings and the stick adds a short "
                  "wooden tick")
        scenes.append(s)
        print(f"  {s.name}")
        for f in s.facts:
            print(f"      {f}")
    out = write_family(
        "stick_strike", "Wooden stick strikes bars: wood / steel / stone",
        "One 2 m/s hit with the same stick on bars of identical size. Only "
        "the bar material changes.", scenes)

    f1 = {w: bar_body(m, w).modes[0].freq for m, w in BARS}
    c = {w: np.sqrt(PHYSICAL[m]["E"] / PHYSICAL[m]["rho"]) for m, w in BARS}
    ok = all(abs(f1[w] / f1["wood"] - c[w] / c["wood"]) < 1e-9 for w in f1)
    print(f"stick_strike gate f1 ~ sqrt(E/rho): {'PASS' if ok else 'FAIL'} "
          f"({', '.join(f'{w} {f:.0f} Hz' for w, f in f1.items())})")
    print(f"stick_strike: {len(scenes)} scenes -> {out}")
    return ok


if __name__ == "__main__":
    main()
