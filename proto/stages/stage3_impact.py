"""Stage 3: Hunt-Crossley impact exciter (Avanzini & Rocchesso 2001).

Gates:
- contact time DECREASES with k and with v_in (trend plots);
- spectral centroid RISES with k ("harder = brighter");
- stability sweep across k orders of magnitude at fs=44100, failures logged;
- renders: 5 velocities x 3 stiffnesses = 15 WAVs;
- cross-check: RK4 (ground truth) vs audio-rate implicit (K-method style)
  vs open-loop rigid-wall force pulse.
Run:  python -m proto.stages.stage3_impact
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from ..analysis.spectro import plot_wave_spec, spectral_centroid
from ..core.impact import force_pulse_rigid, simulate_impact
from ..core.materials import make_modes
from ..core.modal_bank import ModalBank
from ..util import FIG_DIR, FS, write_wav_group

M_S = 0.008          # striker mass (kg), small mallet head
ALPHA = 1.5          # Hertzian sphere contact
MU = 0.6             # lambda = MU * k  (dissipation, s/m)
VELS = [0.25, 0.5, 1.0, 2.0, 4.0]
KS = [1e7, 1e8, 1e9]                 # soft / medium / hard (N/m^alpha)
K_SWEEP = np.logspace(5, 12, 15)     # stability sweep range


def modes():
    """Object used for the audible renders."""
    return make_modes("generic", "wood", mass=0.05)


def trend_modes():
    """Heavy resonator (modal mass >> striker mass) for the trend gates --
    matches the hammer-vs-massive-resonator setup the paper's contact-time
    observations refer to. With a LIGHT resonator the surface is pushed away
    and chases the striker, lengthening contact and causing micro-bounces
    (n_contacts > 1 in info) -- physically real, but a different regime."""
    return make_modes("generic", "wood", mass=0.5)


def main():
    # ---- 15 renders: 5 velocities x 3 stiffnesses -------------------------
    renders = {}
    for k in KS:
        for v in VELS:
            audio, info = simulate_impact(M_S, v, k, ALPHA, MU * k, modes(),
                                          FS, dur=1.5)
            renders[f"stage3_impact_k{k:.0e}_v{v:.2f}.wav"] = audio
    write_wav_group(renders)
    plot_wave_spec(renders[f"stage3_impact_k{KS[-1]:.0e}_v1.00.wav"], FS,
                   "stage3_example_render.png",
                   f"Stage 3: impact render (k={KS[-1]:.0e}, v=1 m/s)")

    # ---- trend: contact time & centroid vs k (v=1) ------------------------
    k_axis = np.logspace(6, 11, 11)
    ct_k, cen_k = [], []
    for k in k_axis:
        audio, info = simulate_impact(M_S, 1.0, k, ALPHA, MU * k,
                                      trend_modes(), FS, dur=1.0)
        ct_k.append(info["contact_time"])
        cen_k.append(spectral_centroid(audio, FS))

    # ---- trend: contact time vs v (k=1e8) ---------------------------------
    v_axis = np.linspace(0.25, 4.0, 9)
    ct_v, cen_v = [], []
    for v in v_axis:
        audio, info = simulate_impact(M_S, v, 1e8, ALPHA, MU * 1e8,
                                      trend_modes(), FS, dur=1.0)
        ct_v.append(info["contact_time"])
        cen_v.append(spectral_centroid(audio, FS))

    fig, axes = plt.subplots(2, 2, figsize=(11, 8))
    axes[0, 0].loglog(k_axis, ct_k, "o-")
    axes[0, 0].set_xlabel("stiffness k (N/m^alpha)")
    axes[0, 0].set_ylabel("contact time (s)")
    axes[0, 0].set_title("contact time vs k (v=1 m/s) -- expect decreasing")
    axes[0, 1].semilogx(k_axis, cen_k, "o-")
    axes[0, 1].set_xlabel("stiffness k")
    axes[0, 1].set_ylabel("spectral centroid (Hz)")
    axes[0, 1].set_title("centroid vs k -- expect rising (harder=brighter)")
    axes[1, 0].plot(v_axis, ct_v, "o-")
    axes[1, 0].set_xlabel("impact velocity (m/s)")
    axes[1, 0].set_ylabel("contact time (s)")
    axes[1, 0].set_title("contact time vs v (k=1e8) -- expect decreasing")
    axes[1, 1].plot(v_axis, cen_v, "o-")
    axes[1, 1].set_xlabel("impact velocity (m/s)")
    axes[1, 1].set_ylabel("spectral centroid (Hz)")
    axes[1, 1].set_title("centroid vs v")
    for ax in axes.flat:
        ax.grid(alpha=0.3, which="both")
    fig.suptitle("Stage 3: Hunt-Crossley trends (RK4 reference integrator)")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "stage3_trends.png", dpi=130)
    plt.close(fig)

    ct_k = np.array(ct_k); cen_k = np.array(cen_k); ct_v = np.array(ct_v)
    g1 = bool(np.all(np.diff(ct_k) < 0))
    g2 = bool(cen_k[-1] > cen_k[0] and
              np.polyfit(np.log10(k_axis), cen_k, 1)[0] > 0)
    # non-strict: contact time is quantized to the sim step (plateaus of
    # 1-2 steps between neighboring v values are measurement resolution)
    g3 = bool(np.all(np.diff(ct_v) <= 0) and ct_v[-1] < ct_v[0])
    print(f"stage3 gate contact-time falls with k: {'PASS' if g1 else 'FAIL'}")
    print(f"stage3 gate centroid rises with k:     {'PASS' if g2 else 'FAIL'}")
    print(f"stage3 gate contact-time falls with v: {'PASS' if g3 else 'FAIL'}")

    # ---- stability sweep --------------------------------------------------
    print("stage3 stability sweep (v=1 m/s), fs=44100:")
    for k in K_SWEEP:
        for method in ("rk4", "implicit"):
            audio, info = simulate_impact(M_S, 1.0, k, ALPHA, MU * k, modes(),
                                          FS, dur=0.3, method=method)
            ok = info["stable"] and np.all(np.isfinite(audio))
            if not ok:
                print(f"  UNSTABLE: k={k:.1e} method={method}")
    print("  (no lines above = all stable)")

    # ---- integrator cross-check ------------------------------------------
    k = 1e8
    a_rk4, i_rk4 = simulate_impact(M_S, 1.0, k, ALPHA, MU * k, modes(), FS,
                                   dur=1.0, method="rk4")
    a_imp, i_imp = simulate_impact(M_S, 1.0, k, ALPHA, MU * k, modes(), FS,
                                   dur=1.0, method="implicit")
    pulse = force_pulse_rigid(M_S, 1.0, k, ALPHA, MU * k, FS)
    bank = ModalBank(modes(), FS)
    a_ol = bank.process(np.pad(pulse, (0, FS - len(pulse))))

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))
    axes[0].plot(i_rk4["force_t"] * 1e3, i_rk4["force"] / 1e3,
                 label=f"RK4 (fs_sim={i_rk4['fs_sim']/1e3:.0f} kHz)")
    axes[0].plot(i_imp["force_t"] * 1e3, i_imp["force"] / 1e3, "s--",
                 label="implicit @ 44.1 kHz")
    axes[0].set_xlabel("time (ms)")
    axes[0].set_ylabel("contact force (kN)")
    axes[0].set_title(f"force pulse, k={k:.0e}, v=1 m/s")
    axes[0].legend(); axes[0].grid(alpha=0.3)
    for label, sig in [("RK4", a_rk4), ("implicit", a_imp),
                       ("open-loop rigid pulse", a_ol)]:
        Y = np.abs(np.fft.rfft(sig / (np.max(np.abs(sig)) or 1)))
        f = np.fft.rfftfreq(len(sig), 1 / FS)
        axes[1].semilogy(f, np.maximum(Y / Y.max(), 1e-5), label=label, lw=0.8)
    axes[1].set_xlim(0, 8000)
    axes[1].set_xlabel("frequency (Hz)")
    axes[1].set_ylabel("normalized |Y(f)|")
    axes[1].set_title("output spectra: 3 integration paths")
    axes[1].legend(); axes[1].grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "stage3_integrators.png", dpi=130)
    plt.close(fig)
    print(f"stage3 integrator check: contact_time rk4={i_rk4['contact_time']*1e3:.3f} ms"
          f" implicit={i_imp['contact_time']*1e3:.3f} ms"
          f"  centroid rk4={spectral_centroid(a_rk4, FS):.0f} Hz"
          f" implicit={spectral_centroid(a_imp, FS):.0f} Hz")
    return g1 and g2 and g3


if __name__ == "__main__":
    main()
