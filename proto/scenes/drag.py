"""Scene family: objects dragged back and forth by hand, each matched to a
real recording in proto/recordings/Sliding/.

What the sliding recordings show (docs/rolling_sliding_vs_recordings.md):
smooth broadband texture (>1 kHz kurtosis 4-9, i.e. nearly Gaussian, ~0-3
clicks/s), level riding on hand strokes at ~1.5-2.8 Hz (15-25 dB deep), and
broad spectral humps -- almost no narrow resonances (0-1 peaks > 6 dB).
The old renders (scenes/slide.py) are the opposite on the last point: the
plank's bending modes stand out as lines (Q = 1/tan phi ~ 80), because the
plank rings as if it hung free while it actually lies on its face.

Models compared (same gesture, same floor):
  A  noise exciter (core/friction.py), baseline
  B  surface-profile exciter as before: 1x rate, no contact damping
  C  B + 4x oversampled contact + cubic profile read (no aliasing / no
     v/DX line) + contact damping on the slider while it lies on the floor
     + the face rides on N_TRACKS independent asperity tracks (sum ->
     near-Gaussian, as measured), each averaged at its own asperity scale
     in SIGMA_C (one scale = a brightness hump at v / (2 pi sigma); a
     spread of sizes = the flat spectrum of the recordings)

Gesture: v = v_pk tanh(3 s) / tanh(3), s = sin(pi f_s t), with
stroke-to-stroke amplitude variation, f_s = 1.7 strokes/s (the
recordings' modulation peak), signed: strokes go back and forth over the
same patch of floor. The tanh gives a hand's quick but smooth reversals
(the recordings dip ~15-20 dB between strokes; a plain sine dwells near
zero and goes silent; sign(s)|s|^0.4 had infinite acceleration at each
reversal and at the start, heard as a bump).

Run:  python -m proto.scenes.drag            (renders)
      python -m proto.scenes.drag sweep      (contact-damping sweep only)
      python -m proto.scenes.drag boxes      (cardboard/steel boxes, one long pull)
"""
import sys
from pathlib import Path

import numpy as np

from ..analysis.texture_stats import (compare_line, load, ltas_distance,
                                      pair_figure, stats)
from ..core.bodies import Body, body_sound, floor, plank, with_contact_damping
from ..core.friction import friction_exciter
from ..core.radiation import coincidence_freq
from ..core.materials import PHYSICAL
from ..core.shapes import plate_ss
from ..core.slide_profile import SURFACE_PROFILES, profile_slide_force
from ..util import FIG_DIR, FS
from .common import G, Scene, write_family

REC_DIR = Path(__file__).resolve().parents[1] / "recordings" / "Sliding"
DUR = 6.0
STROKES_HZ = 1.7
V_PK = 0.8           # m/s peak hand speed -> ~0.3 m strokes
M_CONTACT = 0.010    # model B/C contact mass (kg), preset as in slide.py
WOBBLE = 0.25        # hand pressure varies more than a free slide
CONTACT_LOSS = 0.10  # model C: chosen by `sweep` (see docstring)
N_TRACKS = 6         # model C: asperity contact tracks under the face
# model C: asperity contact sizes (m), one per track, log-spaced. Chosen
# per floor by a sweep against the matched recordings (doc section 3):
# sanded wood 20-150 um, broom-finish concrete 60-200 um
SIGMA_C = {"wood-floor": (20e-6, 150e-6), "concrete-slab": (60e-6, 200e-6)}
MU_K = {"wood-floor": 0.35, "concrete-slab": 0.60, "steel-plate-floor": 0.30}
ROUGH_A = {"wood-floor": (0.10, 9000.0), "concrete-slab": (0.25, 2500.0)}


def hand_strokes(seed: int = 0) -> np.ndarray:
    """Signed hand velocity: back-and-forth strokes, varied amplitude."""
    rng = np.random.default_rng(seed)
    t = np.arange(int(DUR * FS)) / FS
    n_str = int(np.ceil(DUR * STROKES_HZ)) + 1
    amp = 1.0 + 0.2 * rng.standard_normal(n_str)
    k = np.clip(((t - 0.1) * STROKES_HZ).astype(int), 0, n_str - 1)
    sn = np.sin(np.pi * STROKES_HZ * (t - 0.1))     # first stroke starts at 0.1 s
    # quick but smooth reversals: tanh(3 s) has a finite slope at s = 0
    # (sign(s)|s|^0.4 did not: infinite acceleration at every reversal and
    # at the start, an acceleration impulse z' dv delta(t) in the force)
    v = V_PK * amp[k] * np.tanh(3.0 * sn) / np.tanh(3.0)
    v[t < 0.1] = 0.0
    v *= 0.5 - 0.5 * np.cos(np.pi * np.clip((t - 0.1) / 0.15, 0.0, 1.0))
    fade = np.clip((DUR - 0.3 - t) / 0.2, 0.0, 1.0)     # hand stops at the end
    return v * fade


PULL_DUR = 8.0       # s, one long pull (box listening set)
PULL_V = 0.5         # m/s mean pull speed
PULL_RAMP = 0.6      # s, raised-cosine start and stop


def steady_pull(seed: int = 0) -> np.ndarray:
    """One long, one-way pull: smooth raised-cosine start and stop (zero
    acceleration at both ends -- a speed step gives the profile force an
    acceleration impulse z' dv delta(t), heard as a bump), and a slow
    +-12 % hand variation (< 1.5 Hz) in between."""
    from scipy.signal import butter, sosfiltfilt
    rng = np.random.default_rng(seed)
    t = np.arange(int(PULL_DUR * FS)) / FS
    w = sosfiltfilt(butter(2, 1.5, fs=FS, output="sos"),
                    rng.standard_normal(len(t)))
    w /= np.std(w) or 1.0
    t0, t1 = 0.1, PULL_DUR - 0.4
    up = np.clip((t - t0) / PULL_RAMP, 0.0, 1.0)
    dn = np.clip((t1 - t) / PULL_RAMP, 0.0, 1.0)
    env = (0.5 - 0.5 * np.cos(np.pi * up)) * (0.5 - 0.5 * np.cos(np.pi * dn))
    return PULL_V * env * (1.0 + 0.12 * w)


def box(a: float, b: float, c: float, material: str, wall: float,
        loss: float, word: str, joint: str, contact=(0.37, 0.43)) -> Body:
    """Empty box a x b x c (m), walls `wall` thick, sliding on its a x b
    bottom: the bottom panel (simply supported by the walls) is what the
    floor rubs and what rings. loss = installed loss factor of the panel.
    contact = where the floor rubs the panel (fractions of a, b). A sheet-
    metal box rests on its folded bottom rim: contact ~3 % from an edge,
    where the low panel modes hardly move (phi ~ m pi x / a), so the
    50-500 Hz roar of an interior contact drops away."""
    phys = PHYSICAL[material]
    M = phys["rho"] * wall * 2 * (a * b + a * c + b * c)
    modes, _ = plate_ss(a, b, wall, material, tan_phi=loss, x=contact[0],
                        y=contact[1], f_max=10000.0)
    fc = coincidence_freq(wall, phys)
    dims = f"{a*100:g}x{b*100:g}x{c*100:g}cm"
    return Body(slug=f"{word.replace(' ', '-')}-box-{dims}",
                description=(f"{word} box {dims.replace('x', ' x ')}, "
                             f"{wall*1e3:g} mm walls, {M:.2f} kg, empty, "
                             "sliding on its bottom panel"),
                material=material, modes=modes, mass=M, area=a * b,
                contact_radius=np.inf,
                radiator=dict(kind="plate", a=a, b=b, h=wall, phys=phys),
                notes=[f"bottom panel modes (simply supported, {joint} "
                       f"loss {loss:g}); coincidence {fc:.0f} Hz",
                       f"floor rubs the panel at ({contact[0]:.0%}, "
                       f"{contact[1]:.0%}) of its sides"])


def steel_box() -> Body:
    return box(0.40, 0.30, 0.25, "metal", 0.0008, 0.002, "sheet-steel",
               "welded box")


def wood_plank() -> Body:
    return plank(0.40, 0.08, 0.02, "wood", "wood", "plank",
                 situation="lying flat on its broad face")


def contact_mass(slider: Body) -> float:
    """Model B/C contact mass. Plate-like sliders (box bottoms): from the
    panel's point impedance Z = 8 sqrt(D rho h) (infinite-plate result) at
    the texture band, m_p = Z / (2 pi 1 kHz) -- 9.7 g for 0.8 mm steel, 3 g
    for 4 mm cardboard. Other sliders: the M_CONTACT preset."""
    r = slider.radiator
    if r.get("kind") != "plate":
        return M_CONTACT
    ph, h = r["phys"], r["h"]
    D = ph["E"] * h**3 / (12 * (1 - ph["nu"]**2))
    return 8 * np.sqrt(D * ph["rho"] * h) / (2 * np.pi * 1000.0)


def drag_force(model: str, slider: Body, flr_slug: str, v: np.ndarray):
    N0 = slider.mass * G
    mu_k = MU_K[flr_slug]
    if model == "A":
        rough, cut = ROUGH_A[flr_slug]
        x = friction_exciter(np.abs(v), FS, cut_per_v=cut, v_ref=0.5)
        ref = friction_exciter(np.full(FS, 0.5), FS, cut_per_v=cut, v_ref=0.5)
        return x / np.sqrt(np.mean(ref**2)) * rough * mu_k * N0, {}
    extra = dict(oversample=4, n_tracks=N_TRACKS,
                 sigma_c=SIGMA_C[flr_slug]) if model == "C" else {}
    return profile_slide_force(v, FS, SURFACE_PROFILES[flr_slug], N0,
                               contact_mass(slider), slider.material,
                               floor(flr_slug).material, wobble=WOBBLE,
                               **extra)


def render(model: str, slider: Body, flr_slug: str, loss: float | None = None,
           gesture=hand_strokes):
    v = gesture()
    F, info = drag_force(model, slider, flr_slug, v)
    flr = floor(flr_slug)
    if model == "C":
        loss = CONTACT_LOSS if loss is None else loss
        slider = with_contact_damping(slider, loss, "dragged flat on the floor")
    stems = {slider.slug: body_sound(slider, F, FS, -1.0)["mix"],
             flr.slug: body_sound(flr, F, FS, +1.0)["mix"]}
    return slider, flr, stems, info, v


# (slider factory, floor slug, matching recording)
CASES = [
    (wood_plank, "wood-floor", "479718-Sliding_Chess_Pieces_04.wav"),
    (wood_plank, "concrete-slab",
     "50124-FOLEY_WOOD_BOX_DRAG_ON_CEMENT_FAST_STUTTER_01.wav"),
    (steel_box, "concrete-slab",
     "331763-Slide_Metal_Box_Big_Quick_Smooth_Calm_Close.wav"),
]
FLOOR_WORDS = {"wood-floor": "a wooden plank floor",
               "concrete-slab": "a concrete slab"}


def sweep():
    """Pick the contact loss: narrow-peak count and LTAS distance vs the
    matched recording, model C, for each case."""
    for make, flr_slug, rec in CASES:
        s_rec = stats(*load(REC_DIR / rec))
        for loss in (0.0, 0.03, 0.1, 0.3):
            _, _, stems, _, _ = render("C", make(), flr_slug, loss)
            s = stats(sum(stems.values()), FS)
            print(f"  {make().slug[:22]:22s} on {flr_slug:14s} loss {loss:<4g}: "
                  f"narrow peaks {len(s['tonal'])} (real {len(s_rec['tonal'])}), "
                  f"LTAS dist {ltas_distance(s, s_rec):.1f} dB, "
                  f">300 Hz {ltas_distance(s, s_rec, lo=300.0):.1f} dB")


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "sweep":
        return sweep()
    if len(sys.argv) > 1 and sys.argv[1] == "boxes":
        return boxes()
    scenes, pairs = [], []
    variants = [(CASES[0], m) for m in ("A", "B", "C")] + \
               [(CASES[1], "C"), (CASES[2], "B"), (CASES[2], "C")]
    tags = {"A": "A-noise-model", "B": "B-profile-model",
            "C": "C-profile-damped-oversampled"}
    for (make, flr_slug, rec), model in variants:
        y_rec, fs_rec = load(REC_DIR / rec)
        s_rec = stats(y_rec, fs_rec)
        slider, flr, stems, info, v = render(model, make(), flr_slug)
        sc = Scene(name=f"drag_{slider.slug}_by-hand-{STROKES_HZ:g}-strokes-per-s"
                        f"_on_{flr_slug}_{tags[model]}",
                   what=(f"a {slider.description.split(',')[0]} is dragged back "
                         f"and forth by hand on {FLOOR_WORDS[flr_slug]} "
                         f"(match: {rec})"),
                   mover=slider, target=flr, stems=stems)
        sc.facts = [f"hand strokes: {STROKES_HZ:g} per second, peak speed "
                    f"{V_PK:g} m/s +-20 % per stroke, back and forth over the "
                    f"same ~{0.8 * V_PK / STROKES_HZ:.2f} m of floor, quick reversals"]
        if info:
            tracks = info.get("n_tracks", 1)
            sc.facts.append(
                f"profile contact: {tracks:g} track(s)"
                + (f" at asperity scales {SIGMA_C[flr.slug][0]*1e6:g}-"
                   f"{SIGMA_C[flr.slug][1]*1e6:g} um"
                   if tracks > 1 else
                   " at patch scale 100 um")
                + f"; airborne {info['lift_off_fraction']:.0%} per track, "
                f"{info['landings_per_s']:.0f} micro-impacts/s per track, "
                f"force kurtosis {info['kurtosis']:.0f}, normal-force wobble "
                f"+-{WOBBLE:.0%}")
        s_r = stats(sc.mix, FS)
        sc.facts.append(compare_line(s_r, s_rec))
        scenes.append(sc)
        pairs.append((sc.name, sc.mix, FS, y_rec, fs_rec, s_r, s_rec, rec))
        print(f"  {sc.name}\n    {sc.facts[-1]}")
    out = write_family(
        "drag", "Objects dragged by hand, matched to real recordings",
        "A wooden plank and a sheet-steel box dragged back and forth on wood "
        "and concrete. A = noise exciter, B = surface-profile exciter as in "
        "scenes/slide.py, C = B with oversampled contact, cubic profile read "
        "and contact damping on the slider. Each entry ends with render-vs-"
        "real texture statistics.", scenes)
    pair_figure(pairs, FIG_DIR / "drag_vs_recordings.png",
                "Hand drag: render vs real recording")
    print(f"drag: {len(scenes)} scenes -> {out}")


# --------------------------------------------- listening set: boxes

BOXES = [
    (lambda: box(0.30, 0.20, 0.20, "cardboard", 0.004, 0.05, "cardboard",
                 "glued/taped corrugated board"), "small"),
    (lambda: box(0.60, 0.40, 0.40, "cardboard", 0.004, 0.05, "cardboard",
                 "glued/taped corrugated board"), "large"),
    (lambda: box(0.30, 0.20, 0.20, "metal", 0.0008, 0.002, "sheet-steel",
                 "welded box", contact=RIM), "small"),
    (lambda: box(0.60, 0.40, 0.40, "metal", 0.001, 0.002, "sheet-steel",
                 "welded box", contact=RIM), "large"),
]
BOX_FLOOR = "concrete-slab"
# sheet-metal boxes ride on their folded bottom rim (3 % in from an edge)
RIM = (0.03, 0.5)
# designer level trims (dB, applied after the shared gain), by box material.
# Cardboard came out 10-14 dB louder than steel and was judged too loud by
# ear (2026-10-28); the model has no soft-liner contact compliance yet
BOX_TRIM_DB = {"cardboard": -6.0}


def boxes():
    """Small/large cardboard and sheet-steel boxes dragged by hand on the
    same concrete floor with model C, one shared gain."""
    scenes = []
    for make, size in BOXES:
        slider, flr, stems, info, v = render("C", make(), BOX_FLOOR,
                                             gesture=steady_pull)
        dist = np.sum(v) / FS
        sc = Scene(name=f"drag_{slider.slug}_pulled-{dist:.1f}m-at-"
                        f"{PULL_V:g}mps_on_{BOX_FLOOR}",
                   what=(f"a {size} empty {slider.description.split(' box')[0]} "
                         f"box is pulled in one long drag across "
                         f"{FLOOR_WORDS[BOX_FLOOR]}"),
                   mover=slider, target=flr, stems=stems)
        sc.facts = [f"one pull: {PULL_V:g} m/s +-12 % (slow hand variation), "
                    f"{dist:.1f} m in {PULL_DUR - 0.5:.1f} s, smooth "
                    f"{PULL_RAMP:g} s start and stop; normal force = box "
                    f"weight {slider.mass * G:.1f} N (+-{WOBBLE:.0%})",
                    f"contact mass {contact_mass(slider)*1e3:.1f} g (bottom "
                    f"panel point impedance at 1 kHz)",
                    f"model C: {info['n_tracks']:g} asperity tracks, scales "
                    f"{SIGMA_C[BOX_FLOOR][0]*1e6:g}-{SIGMA_C[BOX_FLOOR][1]*1e6:g} "
                    f"um, force kurtosis {info['kurtosis']:.0f}"]
        sc.trim_db = BOX_TRIM_DB.get(slider.material, 0.0)
        scenes.append(sc)
        print(f"  {sc.name}")
    out = write_family(
        "drag_boxes", "Cardboard and steel boxes pulled across concrete",
        "Small (30 x 20 x 20 cm) and large (60 x 40 x 40 cm) empty boxes of "
        "corrugated cardboard and sheet steel, each pulled in one long drag "
        "across the same concrete slab with model C (scenes/drag.py). One "
        "shared gain for all four files.", scenes)
    print(f"drag_boxes: {len(scenes)} scenes -> {out}")


if __name__ == "__main__":
    main()
