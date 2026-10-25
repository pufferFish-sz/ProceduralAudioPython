"""Scene family: four walking footsteps on gravel, dirt and grass.

Same walker, same gait (one step every 0.55 s); only the surface changes.
The old grass preset (v2, stationary hiss) is rendered once more for A/B.

Step envelope (replaces stage 3's two slow Gaussians): each step is a
sharp HEEL strike (5 ms attack, 70 ms decay) followed 150 ms later by a
softer TOE push-off (smooth 60 ms hump, 60 % level); each step gets
+-10 % level and +-15 ms timing jitter (seeded). The envelope drives grain
density and grain energy of core/aggregate (PhISEM).

Levels: the aggregate layer is NOT in physical units -- each layer is
peak-normalized inside aggregate_exciter -- so loudness differences between
these files reflect the presets, not physics. Shoe-on-ground impact (heel
thud) is not modelled.
Run:  python -m proto.scenes.footsteps
"""
import numpy as np

from ..core.aggregate import (AGGREGATE_PRESETS, AGGREGATE_PRESETS_V2_GRASS,
                              render_aggregate)
from ..util import FS
from .common import Scene, write_family

N_STEPS, STEP_DT = 4, 0.55
DUR = 0.3 + N_STEPS * STEP_DT + 0.5


def step_envelope(seed: int = 3) -> np.ndarray:
    rng = np.random.default_rng(seed)
    t = np.arange(int(DUR * FS)) / FS
    env = np.zeros_like(t)
    for i in range(N_STEPS):
        t0 = 0.3 + i * STEP_DT + rng.uniform(-0.015, 0.015)
        g = rng.uniform(0.9, 1.1)
        dt = t - t0
        heel = np.where(dt >= 0, (1 - np.exp(-np.maximum(dt, 0) / 0.005))
                        * np.exp(-np.maximum(dt, 0) / 0.070), 0.0)
        toe = 0.6 * np.exp(-((dt - 0.15) / 0.06) ** 2)
        env += g * (heel + toe)
    return env / env.max()


SURFACES = {
    "gravel": ("loose gravel", AGGREGATE_PRESETS["gravel"],
               "every stone its own pitch (PhISEM v2)"),
    "dirt": ("packed dirt", AGGREGATE_PRESETS["dirt"],
             "low, dull, fast-dying grains + low rustle (PhISEM v2)"),
    "grass": ("grass", AGGREGATE_PRESETS["grass"],
              "layered v3: swishing blades + stem snaps + thin bed"),
    "grass-v2-old": ("grass, OLD v2 preset", AGGREGATE_PRESETS_V2_GRASS,
                     "v2: 80 % stationary 2.8-11 kHz hiss (kept for A/B)"),
}


def main():
    env = step_envelope()
    scenes = []
    for slug, (word, preset, how) in SURFACES.items():
        y = render_aggregate(preset, env, FS, seed=11)
        s = Scene(
            name=f"walk_{N_STEPS}-steps_every-{STEP_DT:g}s_on_{slug}",
            what=(f"four footsteps (heel then toe) on {word}; only the "
                  "surface texture is synthesized"),
            mover=None, target=None, stems={f"{slug}-texture": y},
            facts=[f"surface model: {how}",
                   f"gait: {N_STEPS} steps, {STEP_DT:g} s apart; heel 5 ms "
                   "attack / 70 ms decay, toe hump +150 ms at 60 %"])
        scenes.append(s)
        print(f"  {s.name}")
    out = write_family(
        "footsteps", "Footsteps on gravel / dirt / grass",
        "The same four-step walk on each surface. Only the aggregate "
        "texture preset changes.", scenes,
        level_note=("Levels here are NOT physical: the aggregate layer is "
                    "normalized per layer, so compare textures, not "
                    "loudness. All files share one gain."))
    print(f"footsteps: {len(scenes)} scenes -> {out}")
    return True


if __name__ == "__main__":
    main()
