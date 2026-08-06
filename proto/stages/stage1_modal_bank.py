"""Stage 1: modal bank alone, impulse-excited.

Gate: analytic tau_n vs. decay-fit measured tau_n must match (tol 15%).
Outputs: renders/stage1_*.wav, figures/stage1_*.png
Run:  python -m proto.stages.stage1_modal_bank
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from ..analysis.decay_fit import measure_decay_times
from ..analysis.spectro import plot_wave_spec
from ..core.materials import SHAPES, make_modes
from ..core.modal_bank import ModalBank
from ..util import FIG_DIR, FS, write_wav

TOL = 0.15


def main():
    tan_phi = 0.008          # wood-ish, rings long enough to fit cleanly
    modes = make_modes("generic", tan_phi)
    bank = ModalBank(modes, FS)
    y = bank.impulse_response(dur=2.0)
    write_wav("stage1_modal_impulse.wav", y)
    plot_wave_spec(y, FS, "stage1_modal_impulse.png",
                   f"Stage 1: modal bank impulse response (tan_phi={tan_phi})")

    freqs = np.array(SHAPES["generic"]["freqs"])
    tau_analytic = 1.0 / (np.pi * freqs * tan_phi)
    tau_meas = measure_decay_times(y, FS, freqs)
    err = np.abs(tau_meas - tau_analytic) / tau_analytic

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.plot(freqs, tau_analytic, "o-", label="analytic tau = 1/(pi f tan_phi)")
    ax.plot(freqs, tau_meas, "s--", label="measured tau (band env fit)")
    ax.set_xlabel("mode frequency (Hz)")
    ax.set_ylabel("decay time constant tau (s)")
    ax.set_title("Stage 1 gate: analytic vs measured decay")
    ax.legend()
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "stage1_decay_gate.png", dpi=130)
    plt.close(fig)

    print("stage1: analytic vs measured tau per mode")
    ok = True
    for f0, ta, tm, e in zip(freqs, tau_analytic, tau_meas, err):
        flag = "OK " if e < TOL else "FAIL"
        ok &= e < TOL
        print(f"  {f0:7.1f} Hz  analytic {ta:7.4f} s  measured {tm:7.4f} s"
              f"  err {100*e:5.1f} %  {flag}")
    print(f"stage1 gate: {'PASS' if ok else 'FAIL'} (tol {TOL:.0%})")
    return ok


if __name__ == "__main__":
    main()
