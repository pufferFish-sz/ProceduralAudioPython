"""Stage 2: one shape x five materials -- a single scalar (tan_phi) swap.

Gate: renders traverse glass -> metal -> wood -> plastic -> rubber by ear;
measured decay still matches analytic for each material.
Run:  python -m proto.stages.stage2_materials
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from ..analysis.decay_fit import measure_decay_times
from ..analysis.spectro import spectrogram_db
from ..core.materials import MATERIALS, SHAPES, make_modes
from ..core.modal_bank import ModalBank
from ..util import FIG_DIR, FS, write_wav_group

ORDER = ["metal", "glass", "wood", "plastic", "rubber"]


def main():
    freqs = np.array(SHAPES["generic"]["freqs"])
    renders = {}
    for mat in ORDER:
        bank = ModalBank(make_modes("generic", mat), FS)
        renders[f"stage2_material_{mat}.wav"] = bank.impulse_response(2.5)
    write_wav_group(renders)

    fig, axes = plt.subplots(1, len(ORDER), figsize=(3.2 * len(ORDER), 4.2),
                             sharey=True)
    print("stage2: same shape, tan_phi swap; decay check @ first mode "
          f"({freqs[0]:.0f} Hz)")
    ok = True
    for ax, mat in zip(axes, ORDER):
        y = renders[f"stage2_material_{mat}.wav"]
        f, ts, S_db = spectrogram_db(y, FS)
        ax.pcolormesh(ts, f, S_db, shading="gouraud", cmap="magma",
                      vmin=-90, vmax=0)
        ax.set_ylim(0, 8000)
        ax.set_xlim(0, 1.2)
        ax.set_title(f"{mat}\ntan_phi={MATERIALS[mat]}")
        ax.set_xlabel("t (s)")
        tau_a = 1.0 / (np.pi * freqs[0] * MATERIALS[mat])
        tau_m = measure_decay_times(y, FS, [freqs[0]])[0]
        e = abs(tau_m - tau_a) / tau_a if np.isfinite(tau_m) else np.inf
        flag = "OK " if e < 0.2 else "WARN"
        ok &= e < 0.2
        print(f"  {mat:8s} tau analytic {tau_a:8.4f} s  measured "
              f"{tau_m:8.4f} s  err {100*e:5.1f} %  {flag}")
    axes[0].set_ylabel("frequency (Hz)")
    fig.suptitle("Stage 2: one shape, five materials (single tan_phi scalar)")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "stage2_materials.png", dpi=130)
    plt.close(fig)
    print(f"stage2 gate: {'PASS' if ok else 'CHECK'} + listen to the 5 WAVs")
    return ok


if __name__ == "__main__":
    main()
