"""Scene family: a wooden plank shoved across three floors, sliding to a stop.
A/B of two sliding exciters, same plank, same 2.5 m/s shove, same floors.

Model A -- noise (core/friction.py): white noise whose level ~ v^1.2 and
lowpass cutoff ~ v, scaled so that at v_ref = 0.5 m/s the fluctuating force
rms = roughness * mu_k * M * g. Kept as the baseline ("sounds like static").

Model B -- surface profile (core/slide_profile.py): a fixed height profile
per floor read by POSITION (FoleyAutomatic), followed by a contact of
effective mass m_p pressed by a wobbling normal force; where the surface
drops faster than N/m_p allows, the contact lifts off and lands again
(physical curvature limit, after Agarwal et al. 2021), each landing a Hertz
micro-impact. See docs/sliding_sound_literature.md.

Shared physics: speed v(t) = v0 - mu_k g t; the steady Coulomb force is
silent; the force fluctuation (newtons) drives the plank's modes, the
floor's modes and the plank's rigid click via core/bodies.body_sound.
All files share one gain, so A vs B loudness is comparable.

Gates (every file): 100 ms RMS tracks slide speed (corr > 0.8) and is
silent after the stop.
Run:  python -m proto.scenes.slide
"""
import numpy as np

from ..core.bodies import body_sound, floor, plank
from ..core.friction import friction_exciter
from ..core.slide_profile import SURFACE_PROFILES, profile_slide_force
from ..sim.trajectories import sliding_box
from ..util import FS
from .common import G, Scene, write_family

V0 = 2.5
V_REF = 0.5
M_CONTACT = 0.010   # model B: effective contact mass (kg), preset
# floor slug: (mu_k wood-on-floor, roughness = fluct. rms / Coulomb force,
#              cut_per_v Hz per m/s ~ 1 / asperity spacing)  [model A]
SURFACES = {
    "wood-floor":        (0.35, 0.10, 9000.0),
    "concrete-slab":     (0.60, 0.25, 2500.0),
    "steel-plate-floor": (0.30, 0.05, 20000.0),
}
FLOOR_WORDS = {"concrete-slab": "a concrete slab",
               "wood-floor": "a wooden plank floor",
               "steel-plate-floor": "a steel deck plate"}


def friction_force(speed, M, mu_k, rough, cut_per_v, stick_slip=False):
    """Model A: fluctuating friction force (N) for a speed trajectory."""
    x = friction_exciter(speed, FS, cut_per_v=cut_per_v,
                         stick_slip=stick_slip, v_ref=V_REF)
    ref = friction_exciter(np.full(FS, V_REF), FS, cut_per_v=cut_per_v,
                           v_ref=V_REF)
    return x / np.sqrt(np.mean(ref**2)) * rough * mu_k * M * G


def slide_scene(slider, flr, model, stick_slip=False):
    mu_k, rough, cut_per_v = SURFACES[flr.slug]
    speed = sliding_box(v0=V0, friction_mu=mu_k, fs=FS, extra_time=1.0)
    i0 = int(0.2 * FS)
    F = np.zeros(len(speed) + i0)
    t_stop = V0 / (mu_k * G)
    facts = [f"shove speed {V0:g} m/s, kinetic friction mu_k = {mu_k} -> "
             f"slides {V0**2 / (2 * mu_k * G):.2f} m and stops after "
             f"{t_stop:.2f} s"]
    if model == "A":
        F[i0:] = friction_force(speed, slider.mass, mu_k, rough, cut_per_v,
                                stick_slip)
        facts.append(f"model A (noise): fluctuating force = {rough:.0%} of "
                     f"the Coulomb force {mu_k * slider.mass * G:.2f} N at "
                     f"{V_REF} m/s, brightness {cut_per_v:.0f} Hz per m/s")
        if stick_slip:
            facts.append("stick-slip on: the noise is chopped by a relaxation "
                         "oscillator whose rate follows speed (squeak)")
    else:
        spec = SURFACE_PROFILES[flr.slug]
        f, info = profile_slide_force(speed, FS, spec, slider.mass * G,
                                      M_CONTACT, slider.material,
                                      flr.material)
        F[i0:] = f
        feat = spec["features"]
        facts += [
            f"model B (surface profile): {spec['note']}; roughness "
            f"{spec['h_rms']*1e6:g} um rms, PSD ~ k^-{spec['gamma']:g}, "
            f"texture resonance {spec['k_r']:g} /m (heard at {spec['k_r']:g} "
            f"x v Hz, e.g. {spec['k_r'] * 1.0:.0f} Hz at 1 m/s)"
            + (f", meso feature every {feat['period']*100:g} cm "
               f"({'groove' if feat['height'] < 0 else 'bump'} "
               f"{abs(feat['height'])*1e3:g} mm)" if feat else ""),
            f"contact mass {M_CONTACT*1e3:g} g pressed by the plank weight "
            f"(+-15 % slow wobble): airborne {info['lift_off_fraction']:.0%} "
            f"of the slide, {info['landings_per_s']:.0f} micro-impacts per "
            f"second, force kurtosis {info['kurtosis']:.0f} (3 = Gaussian "
            "noise)"]
    stems = {slider.slug: body_sound(slider, F, FS, -1.0)["mix"],
             flr.slug: body_sound(flr, F, FS, +1.0)["mix"]}
    sc = Scene(name="", what="", mover=slider, target=flr, stems=stems,
               facts=facts)
    sc.speed = np.concatenate([np.zeros(i0), speed])
    return sc


def main():
    slider = plank(0.40, 0.08, 0.02, "wood", "wood", "plank",
                   situation="sliding flat on its broad face")
    scenes = []
    variants = [(s, m, False) for s in SURFACES for m in ("A", "B")]
    variants.append(("wood-floor", "A", True))
    for slug, model, squeak in variants:
        s = slide_scene(slider, floor(slug), model, squeak)
        tag = {"A": "A-noise-model", "B": "B-profile-model"}[model]
        s.name = (f"slide_{slider.slug}_shoved-{V0:g}mps_on_{slug}_{tag}"
                  + ("_squeaky" if squeak else ""))
        s.what = (f"a wooden plank is shoved at {V0:g} m/s across "
                  f"{FLOOR_WORDS[slug]} and slides to a stop -- "
                  + ("old noise exciter" if model == "A" else
                     "new surface-profile exciter")
                  + (", squeaking (stick-slip)" if squeak else ""))
        scenes.append(s)
        print(f"  {s.name}")

    ok = True
    for s in scenes:
        win = FS // 10
        y, v = s.mix, s.speed[:len(s.mix)]
        n = len(v) // win
        rms = np.array([np.sqrt(np.mean(y[i*win:(i+1)*win]**2)) for i in range(n)])
        vw = np.array([v[i*win:(i+1)*win].mean() for i in range(n)])
        moving = vw > 0.05
        corr = np.corrcoef(vw[moving], rms[moving])[0, 1]
        quiet = rms[n - 5:].max() < 0.05 * rms.max()
        s.facts.append(f"gate: level~speed corr {corr:.3f}, silent after stop "
                       f"{'yes' if quiet else 'NO'}")
        print(f"    {s.name[-40:]}: corr {corr:.3f} quiet {quiet}")
        ok &= corr > 0.8 and quiet
    out = write_family(
        "slide", "Wooden plank sliding to a stop: A (noise) vs B (surface profile)",
        "The same 40 x 8 x 2 cm wooden plank shoved at 2.5 m/s on three floors, "
        "rendered with the old noise exciter (A) and the new surface-profile "
        "exciter (B). Last file: A on the wood floor with stick-slip.",
        scenes)
    print(f"slide gate level tracks speed, silent after stop: "
          f"{'PASS' if ok else 'FAIL'}")
    print(f"slide: {len(scenes)} scenes -> {out}")
    return ok


if __name__ == "__main__":
    main()
