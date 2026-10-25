"""Scene family: a solid rubber ball (small / large) dropped from 1 m onto
three floors, bouncing until it rests.

Only two things change between files: ball size and floor. The ball is
the same material (rubber), the drop height is the same, and the contact
hardness comes from Hertz theory for each ball/floor pair.

Gates:
- every bounce conserves momentum: integral of f = m (v_in + v_out), < 1 %;
- the large ball's modes are lower by exactly r_small / r_large (same
  material, geometrically similar).
Run:  python -m proto.scenes.ball_drop
"""
from ..core.bodies import FLOOR_SPECS, floor, rubber_ball
from .common import bounce_scene, write_family

H0 = 1.0
BALLS = [(0.015, "small"), (0.040, "large")]
FLOOR_WORDS = {"concrete-slab": "a concrete slab",
               "wood-floor": "a wooden plank floor",
               "steel-plate-floor": "a steel deck plate"}


def main():
    scenes = []
    for r, size in BALLS:
        ball = rubber_ball(r, size)
        for slug in FLOOR_SPECS:
            s = bounce_scene(ball, floor(slug), H0)
            s.name = f"drop_{ball.slug}_from-{H0:g}m_onto_{slug}"
            s.what = (f"a {size} solid rubber ball (r = {r*100:.1f} cm) falls "
                      f"{H0:g} m onto {FLOOR_WORDS[slug]} and bounces until it "
                      "rests; both the ball and the floor sound")
            scenes.append(s)
            print(f"  {s.name}")
            for f in s.facts:
                print(f"      {f}")
    out = write_family(
        "ball_drop", "Rubber ball drop: 2 sizes x 3 floors",
        "Solid rubber balls dropped from 1 m. Same material and height "
        "everywhere; only ball size and floor change.", scenes)

    ok_imp = all(float(s.facts[3].split("max error ")[1].split(" %")[0]) < 1.0
                 for s in scenes)
    small, large = rubber_ball(*BALLS[0]), rubber_ball(*BALLS[1])
    ratio = large.modes[0].freq / small.modes[0].freq
    ok_pitch = abs(ratio - BALLS[0][0] / BALLS[1][0]) < 1e-6
    print(f"ball_drop gate impulse conserved every bounce: "
          f"{'PASS' if ok_imp else 'FAIL'}")
    print(f"ball_drop gate pitch scales 1/r ({ratio:.4f}): "
          f"{'PASS' if ok_pitch else 'FAIL'}")
    print(f"ball_drop: {len(scenes)} scenes -> {out}")
    return ok_imp and ok_pitch


if __name__ == "__main__":
    main()
