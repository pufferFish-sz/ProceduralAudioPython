"""Stage 3: friction (sliding) + aggregate (granular surface) exciters.

Gates:
- sliding render driven by a synthetic decaying speed ramp: level and
  brightness track speed smoothly, silence below threshold;
- gravel / dirt / grass parameter sets render with distinct textures
  (grass = layered v3; grass_v2 rendered alongside for A/B listening).
Run:  python -m proto.stages.stage3_friction_aggregate
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from ..analysis.spectro import plot_wave_spec, spectrogram_db
from ..core.aggregate import (AGGREGATE_PRESETS, AGGREGATE_PRESETS_V2_GRASS,
                              render_aggregate)
from ..core.friction import friction_exciter
from ..core.materials import make_modes
from ..core.modal_bank import ModalBank
from ..sim.trajectories import sliding_box
from ..util import FIG_DIR, FS, write_wav, write_wav_group


def main():
    # ---- sliding box: speed ramp -> friction exciter -> object modal bank -
    speed = sliding_box(v0=1.6, friction_mu=0.35, fs=FS)
    exc = friction_exciter(speed, FS, roughness=1.0, stick_slip=False)
    bank = ModalBank(make_modes("wood_block", "wood", mass=0.02), FS)
    slide = bank.process(exc) + 0.3 * exc          # modal color + direct noise
    write_wav("stage3_slide_wood.wav", slide)
    plot_wave_spec(slide, FS, "stage3_slide_wood.png",
                   "Stage 3: sliding box on wood (speed ramp 1.6 m/s -> 0)")

    squeak = friction_exciter(speed, FS, roughness=1.0, stick_slip=True)
    slide_sq = bank.process(squeak) + 0.3 * squeak
    write_wav("stage3_slide_squeak.wav", slide_sq)

    # gate: RMS level must track speed monotonically (windowed)
    win = FS // 10
    nwin = len(slide) // win
    rms = np.array([np.sqrt(np.mean(slide[i*win:(i+1)*win]**2))
                    for i in range(nwin)])
    v_win = np.array([speed[i*win:(i+1)*win].mean() for i in range(nwin)])
    moving = v_win > 0.05
    corr = np.corrcoef(v_win[moving], rms[moving])[0, 1]
    tail_quiet = rms[~moving].max() < 0.02 * rms.max() if np.any(~moving) else True
    print(f"stage3 slide gate: level~speed corr={corr:.3f} "
          f"({'PASS' if corr > 0.95 else 'FAIL'}), "
          f"silent after stop: {'PASS' if tail_quiet else 'FAIL'}")

    fig, ax1 = plt.subplots(figsize=(8, 4))
    tw = (np.arange(nwin) + 0.5) * win / FS
    ax1.plot(tw, v_win, "o-", color="#204060", label="slide speed (m/s)")
    ax1.set_xlabel("time (s)"); ax1.set_ylabel("speed (m/s)")
    ax2 = ax1.twinx()
    ax2.plot(tw, rms / rms.max(), "s--", color="#a04020",
             label="render RMS (norm)")
    ax2.set_ylabel("normalized RMS")
    ax1.set_title("Stage 3 gate: render level tracks slide speed")
    fig.legend(loc="upper right")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "stage3_slide_gate.png", dpi=130)
    plt.close(fig)

    # ---- aggregate surfaces ----------------------------------------------
    dur = 2.5
    t = np.arange(int(dur * FS)) / FS
    # footstep-ish energy envelope: two soft humps (heel, toe) then quiet
    env = (np.exp(-((t - 0.4) / 0.18) ** 2) + 0.8 * np.exp(-((t - 1.4) / 0.22) ** 2))
    surfaces = dict(AGGREGATE_PRESETS, grass_v2=AGGREGATE_PRESETS_V2_GRASS)
    renders = {f"stage3_aggregate_{name}.wav": render_aggregate(p, env, FS)
               for name, p in surfaces.items()}
    write_wav_group(renders)

    fig, axes = plt.subplots(1, len(surfaces), figsize=(4.3 * len(surfaces), 4.2),
                             sharey=True)
    for ax, name in zip(axes, surfaces):
        f, ts, S_db = spectrogram_db(renders[f"stage3_aggregate_{name}.wav"], FS)
        ax.pcolormesh(ts, f, S_db, shading="gouraud", cmap="magma",
                      vmin=-90, vmax=0)
        ax.set_ylim(0, 12000); ax.set_title(name); ax.set_xlabel("t (s)")
    axes[0].set_ylabel("frequency (Hz)")
    fig.suptitle("Stage 3: aggregate textures (PhISEM grain streams)")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "stage3_aggregate.png", dpi=130)
    plt.close(fig)
    print("stage3: aggregate renders written (compare textures vs real "
          "recordings in recordings/ when available)")
    return corr > 0.95 and tail_quiet


if __name__ == "__main__":
    main()
