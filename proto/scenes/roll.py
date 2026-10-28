"""Scene family: round objects rolling across floors, each matched to a real
recording in proto/recordings/Rolling/ (same object kind, same floor).

Rolling speed is not a guess: in every recording the strongest envelope
modulation is the revolution rate (or seams per revolution x rate), so
v = mod_peak / bumps_per_rev * 2 pi R (see docs/rolling_sliding_vs_recordings.md).

Physics: core/rolling.py -- the object rides the circle-dilated surface
profile (+ its own out-of-round rim profile) on a Hunt-Crossley contact
(point contact for balls, line contact for cylinders). The fluctuating
normal force drives the object's modes and rigid "click" and the floor's
modes (core/bodies.body_sound). All files share one gain.

Run:  python -m proto.scenes.roll            (matched to recordings)
      python -m proto.scenes.roll spheres    (wood/steel balls, small/large)
"""
from dataclasses import replace
from pathlib import Path

import numpy as np

from ..analysis.texture_stats import compare_line, load, pair_figure, stats
from ..core.bodies import Body, body_sound, floor
from ..core.rolling import contact_law, roll_force
from ..core.shapes import sphere, tube
from ..core.slide_profile import SURFACE_PROFILES
from ..util import FIG_DIR, FS
from .common import G, Scene, write_family

REC_DIR = Path(__file__).resolve().parents[1] / "recordings" / "Rolling"
DUR = 6.0
RAMP = 0.3           # s, smooth start of the roll

# floor slug -> (contact damping ratio zeta, rolling resistance c_rr);
# presets. zeta sets the micro-landing restitution e = exp(-pi zeta /
# sqrt(1 - zeta^2)): wood 0.5, tile 0.6, rug 0.1
CONTACT = {"wood-floor": (0.22, 0.003),
           "varnished-wood-floor": (0.22, 0.003),
           "varnished-wood-floor-tight": (0.22, 0.003), "tile-floor": (0.16, 0.002),
           "rug": (0.59, 0.005), "tile-on-timber": (0.16, 0.002)}
# floor slug -> surface profile (SURFACE_PROFILES key)
PROFILE_OF = {"tile-on-timber": "tile-floor"}
FLOOR_WORDS = {"wood-floor": "a wooden plank floor",
               "tile-floor": "a ceramic tile floor",
               "rug": "a cut-pile rug on a wooden floor",
               "tile-on-timber": "ceramic tiles on a timber floor",
               "varnished-wood-floor": "a varnished wooden plank floor",
               "varnished-wood-floor-tight":
                   "a varnished wooden plank floor with tight joints"}


def rolling_floor(slug: str) -> Body:
    """Floors for rolling: tile = concrete slab with a ceramic surface; rug
    = wooden floor under a soft pile (the pile sets the contact, the boards
    still ring)."""
    if slug == "tile-floor":
        b = floor("concrete-slab")
        return replace(b, slug=slug, material="ceramic",
                       description="ceramic tiles bonded to a " + b.description)
    if slug == "tile-on-timber":
        b = floor("wood-floor")
        return replace(b, slug=slug, material="ceramic",
                       description="ceramic tiles bonded to a " + b.description)
    if slug in ("varnished-wood-floor", "varnished-wood-floor-tight"):
        b = floor("wood-floor")
        return replace(b, slug=slug,
                       description="varnished " + b.description)
    if slug == "rug":
        b = floor("wood-floor")
        return replace(b, slug=slug, material="carpet",
                       description="cut-pile rug over a " + b.description)
    return floor(slug)


def baseball() -> Body:
    R, M = 0.0366, 0.145
    mat = dict(E=0.1e9, rho=M / (4 / 3 * np.pi * R**3), nu=0.45, tan_phi=0.10)
    modes, _ = sphere(R, mat)
    return Body(slug="baseball-r37mm",
                description=("baseball, radius 3.7 cm, 145 g (cork/yarn core, "
                             "leather cover: soft, heavily damped)"),
                material=mat, modes=modes, mass=M, area=np.pi * R**2,
                contact_radius=R,
                notes=["two raised seam crossings per revolution "
                       "(0.12 mm, 6 mm wide) + 30 um lumpiness",
                       "stitches: 12 ridges (40 um, 1.5 mm) around each seam crossing "
                       "where the track runs along the stitched seam -- "
                       "count set to the recording's ~57 clicks/s",
                       "pebbled leather: 10 um rms surface texture"])


def soda_can_full() -> Body:
    R, L, M = 0.033, 0.122, 0.37
    mat = dict(E=69e9, rho=2700.0, nu=0.33, tan_phi=0.03)
    modes, m_wall = tube(L, R, 1e-4, mat)
    # the liquid moves with the wall: modal masses scaled by full/empty mass
    modes = [replace(md, mass=md.mass * M / m_wall) for md in modes]
    return Body(slug="soda-can-full",
                description=("full 330 ml aluminium soda can, radius 3.3 cm, "
                             "12.2 cm long, 370 g, rolling on its side"),
                material=mat, modes=modes, mass=M, area=2 * R * L,
                contact_radius=R,
                notes=["shell ring modes, mass-loaded and damped by the "
                       "liquid (modal mass x full/empty, tan phi 0.03)",
                       "rim: 50 um eccentricity + one 0.5 mm, 6 mm wide dent "
                       "(a used can; sized so the can just lifts off once "
                       "per revolution, the recording's 17 dB swell)",
                       "painted aluminium: 1 um rms surface texture"])


def aa_battery() -> Body:
    R, L, M = 0.00725, 0.0505, 0.023
    mat = dict(E=200e9, rho=M / (np.pi * R**2 * L), nu=0.29, tan_phi=0.01)
    modes, _ = tube(L, R, None, mat)
    return Body(slug="aa-battery",
                description="AA battery, radius 7.3 mm, 5 cm long, 23 g, "
                            "steel can, rolling on its side",
                material=mat, modes=modes, mass=M, area=2 * R * L,
                contact_radius=R,
                notes=["no audible modes (all above 16 kHz): you hear its "
                       "rigid click and the floor",
                       "rim: 10 um eccentricity + a 30 um label seam",
                       "plastic label: 2 um rms surface texture"])


# (body factory, shape, rim profile spec, bumps per revolution, recording,
#  floor slug)
ROLLERS = [
    (baseball, "sphere",
     dict(bumps=[(0.0, 0.12e-3, 6e-3), (0.5, 0.12e-3, 6e-3)]
          + [(c - 0.1 + 0.2 * j / 11, 40e-6, 1.5e-3)
             for c in (0.0, 0.5) for j in range(12)], lumps=30e-6,
          rough=dict(h_rms=10e-6, gamma=2.2)), 2,
     "520792-FLY_PROP_Baseball_Rolling_on_Hardwood_Floor_Loop_2.wav",
     "wood-floor"),
    (soda_can_full, "cylinder",
     dict(ecc=50e-6, bumps=[(0.3, -0.5e-3, 6e-3)],
          rough=dict(h_rms=1e-6, gamma=2.4)), 1,
     "522505-ROLL_FULL_SODA_CAN_ON_HARDWOOD_FLOOR_LOOP.wav", "wood-floor"),
    (soda_can_full, "cylinder",
     dict(ecc=50e-6, bumps=[(0.3, -0.5e-3, 6e-3)],
          rough=dict(h_rms=1e-6, gamma=2.4)), 1,
     "522506-ROLL_FULL_SODA_CAN_ON_RUG_LOOP.wav", "rug"),
    (aa_battery, "cylinder",
     dict(ecc=10e-6, bumps=[(0.0, 30e-6, 2e-3)],
          rough=dict(h_rms=2e-6, gamma=2.2)), 1,
     "520951-ROLL_BATTERY_TILE_LOOP.wav", "tile-floor"),
    (aa_battery, "cylinder",
     dict(ecc=10e-6, bumps=[(0.0, 30e-6, 2e-3)],
          rough=dict(h_rms=2e-6, gamma=2.2)), 1,
     "520951-ROLL_BATTERY_TILE_LOOP.wav", "tile-on-timber"),
]


def roll_scene(obj: Body, shape: str, rim: dict, v_rec: float,
               speed_note: str, flr: Body):
    """Roll obj across flr; mid-render speed v_rec (m/s)."""
    zeta, c_rr = CONTACT[flr.slug]
    R = obj.contact_radius
    length = obj.area / (2 * R) if shape == "cylinder" else 0.0
    v0 = v_rec + c_rr * G * (DUR - 0.1) / 2     # mid-render speed = v_rec
    t = np.arange(int(DUR * FS)) / FS
    i0 = int(0.1 * FS)
    # raised-cosine start over 0.3 s: a speed step gives the profile force
    # an acceleration impulse (z' dv delta(t)), heard as a bump at the start
    ramp = 0.5 - 0.5 * np.cos(np.pi * np.clip((t - 0.1) / RAMP, 0.0, 1.0))
    speed = ramp * np.maximum(v0 - c_rr * G * (t - 0.1), 0.0)
    k, alpha = contact_law(shape, R, length, obj.material, flr.material)
    spec = SURFACE_PROFILES[PROFILE_OF.get(flr.slug, flr.slug)]
    F, info = roll_force(speed, FS, spec, R, obj.mass,
                         k, alpha, zeta, obj_spec=rim, track_width=length)
    F[:i0] = 0.0
    stems = {obj.slug: body_sound(obj, F, FS, -1.0)["mix"],
             flr.slug: body_sound(flr, F, FS, +1.0)["mix"]}
    softened = info["f_contact_used"] < info["f_contact"] - 1.0
    facts = [
        f"rolling speed {v0:.2f} -> {speed[-1]:.2f} m/s (rolling resistance "
        f"c_rr {c_rr}); mid-render {v_rec:.2f} m/s{speed_note}",
        f"surface: {spec['note']}",
        f"contact: {'Hertz point' if shape == 'sphere' else 'Hertz line'} law, "
        f"k = {k:.2e}, alpha {alpha}; static penetration {info['delta0']*1e6:.3f} um, "
        f"contact resonance {info['f_contact']:.0f} Hz"
        + (f" (solved softened to {info['f_contact_used']:.0f} Hz, still above "
           "hearing)" if softened else "")
        + f", damping ratio {zeta} (micro-landing restitution "
        f"{info['restitution']:.2f}); random roughness seen "
        f"{info['h_rms_seen']*1e6:.1f} um rms"
        + (" (averaged along the line contact)" if length else ""),
        f"airborne {info['airborne']:.1%} of the time, {info['landings_per_s']:.0f} "
        f"landings/s, revolution rate {info['rev_hz']:.2f} Hz",
    ]
    sc = Scene(name="", what="", mover=obj, target=flr, stems=stems, facts=facts)
    return sc, v0


def main():
    scenes, pairs = [], []
    for make, shape, rim, bpr, rec, flr_slug in ROLLERS:
        y_rec, fs_rec = load(REC_DIR / rec)
        s_rec = stats(y_rec, fs_rec)
        obj, flr = make(), rolling_floor(flr_slug)
        R = obj.contact_radius
        v_rec = s_rec["mod_peak_hz"] / bpr * 2 * np.pi * R
        sc, v0 = roll_scene(obj, shape, rim, v_rec,
                            f" = the recording's {s_rec['mod_peak_hz']:.1f} Hz "
                            f"modulation peak / {bpr} bump(s) per revolution",
                            flr)
        sc.name = f"roll_{obj.slug}_from-{v0:.2f}mps_on_{flr_slug}"
        sc.what = (f"a {obj.description.split(',')[0]} rolls from {v0:.2f} m/s "
                   f"across {FLOOR_WORDS[flr_slug]} (match: {rec})")
        s_r = stats(sc.mix, FS)
        sc.facts.append(compare_line(s_r, s_rec))
        scenes.append(sc)
        pairs.append((sc.name, sc.mix, FS, y_rec, fs_rec, s_r, s_rec, rec))
        print(f"  {sc.name}\n    {sc.facts[-1]}")
    out = write_family(
        "roll", "Rolling objects, each matched to a real recording",
        "Four rolling objects on the floor of their matching recording in "
        "proto/recordings/Rolling/. Speeds come from the recordings' "
        "revolution-rate modulation. Each entry ends with render-vs-real "
        "texture statistics (proto/analysis/texture_stats.py).",
        scenes)
    pair_figure(pairs, FIG_DIR / "roll_vs_recordings.png",
                "Rolling: render vs real recording")
    print(f"roll: {len(scenes)} scenes -> {out}")
    return scenes


# ------------------------------------------------ listening set: spheres

def solid_ball(radius: float, material: str, word: str, size_word: str,
               finish: str) -> Body:
    """Solid ball of a PHYSICAL/MATERIALS material (wood, metal)."""
    modes, M = sphere(radius, material)
    note = ("no audible modes (lowest sphere mode above 16 kHz): you hear "
            "its rigid click and the floor" if not modes else
            f"{len(modes)} audible sphere modes")
    return Body(slug=f"{word}-ball-{size_word}-r{radius*1e3:.0f}mm",
                description=(f"solid {word} ball, radius {radius*100:.1f} cm, "
                             f"{M*1e3:.0f} g, {finish}"),
                material=material, modes=modes, mass=M, area=np.pi * radius**2,
                contact_radius=radius, notes=[note])


# (radius m, material, word, size word, finish, rim profile)
BALLS = [
    (0.020, "wood", "wooden", "small", "turned hardwood",
     dict(ecc=20e-6, rough=dict(h_rms=3e-6, gamma=2.2))),
    (0.050, "wood", "wooden", "large", "turned hardwood",
     dict(ecc=40e-6, rough=dict(h_rms=3e-6, gamma=2.2))),
    (0.010, "metal", "steel", "small", "polished (ball bearing)",
     dict(ecc=1e-6, rough=dict(h_rms=0.1e-6, gamma=2.4))),
    (0.030, "metal", "steel", "large", "polished (ball bearing)",
     dict(ecc=2e-6, rough=dict(h_rms=0.1e-6, gamma=2.4))),
]
V_BALL = 0.5          # m/s mid-render, same for every ball
# varnished, not the sanded "wood-floor" preset: on that one the small
# balls hop every 1.7 mm grain ripple (~250 landings/s, heard as static)
BALL_FLOOR = "varnished-wood-floor"
# A/B for the small balls: same floor with tight flush joints (their
# loudest ticks are hops out of the 1.5 mm board joints)
TIGHT_FLOOR = "varnished-wood-floor-tight"


def spheres():
    """Four solid balls rolled across the same wooden floor at the same
    speed, one shared gain: differences are size and material only."""
    scenes = []
    runs = [(ball, BALL_FLOOR) for ball in BALLS] +            [(ball, TIGHT_FLOOR) for ball in BALLS if ball[3] == "small"]
    for (R, mat, word, size, finish, rim), flr_slug in runs:
        flr = rolling_floor(flr_slug)
        obj = solid_ball(R, mat, word, size, finish)
        sc, v0 = roll_scene(obj, "sphere", rim, V_BALL,
                            " (same for all balls)", flr)
        sc.name = f"roll_{obj.slug}_from-{v0:.2f}mps_on_{flr_slug}"
        sc.what = (f"a {obj.description.split(',')[0]} ({finish}) rolls "
                   f"across {FLOOR_WORDS[flr_slug]}")
        sc.facts.append(f"rim: {rim.get('ecc', 0)*1e6:g} um out of round, "
                        f"surface texture {rim['rough']['h_rms']*1e6:g} um rms")
        scenes.append(sc)
        print(f"  {sc.name}")
    out = write_family(
        "roll_spheres", "Solid wooden and steel balls rolling on a varnished wooden floor",
        "Small and large solid balls of wood and steel, rolled at the same "
        f"{V_BALL:g} m/s across the same varnished wooden floor "
        "(core/rolling.py); the last two files repeat the small balls on "
        "the same floor with tight flush board joints. "
        "One shared gain for all files.", scenes)
    print(f"roll_spheres: {len(scenes)} scenes -> {out}")
    return scenes


if __name__ == "__main__":
    import sys
    spheres() if sys.argv[1:] == ["spheres"] else main()
