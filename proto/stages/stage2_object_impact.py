"""Stage 2: the struck object -- shape x material, excited by an impact.

Merges the former stage 2 (materials) and stage 3 (impact). They are one
layer: the IMPACT does not add a new resonator, it only computes the
contact force pulse f(t) that drives the object's modal bank. So

    object  = shape (mode frequencies) x material (tan_phi -> decay)
    impact  = Hunt-Crossley contact (striker mass, velocity v, hardness k,
              alpha, mu) -> force pulse -> same modal bank

Impulse excitation (part A) is the k -> infinity limit of part B: an
infinitely short pulse excites every mode equally, isolating material cues.
Part C closes the loop with physically derived parameters: mode sets from
geometry + E/rho (core/shapes.py) and k from the two materials (Hertz),
striker = the object's own rigid-body mass dropped onto a concrete floor.

Gates:
A  measured decay matches analytic tau = 1/(pi f tan_phi), 5 materials;
B  contact time DECREASES with k and with v_in; centroid RISES with k;
   stability across k = 1e5..1e12 for both integrators; RK4 vs implicit
   vs open-loop cross-check;
C  analytic primitive sanity: beam ratio f2/f1 = 2.757, hollow-tube vs
   solid-rod pitch ratio = sqrt(Ro^2 + Ri^2) / Ro.
Run:  python -m proto.stages.stage2_object_impact
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from ..analysis.decay_fit import measure_decay_times
from ..analysis.spectro import plot_wave_spec, spectral_centroid, spectrogram_db
from ..core.impact import force_pulse_rigid, hertz_stiffness, simulate_impact
from ..core.materials import MATERIALS, SHAPES, make_modes
from ..core.modal_bank import ModalBank
from ..core.shapes import bar, disc, tube
from ..util import FIG_DIR, FS, write_wav_group

ORDER = ["metal", "glass", "wood", "plastic", "rubber"]
M_S = 0.008          # striker mass (kg), small mallet head
ALPHA = 1.5          # Hertzian sphere contact
MU = 0.6             # lambda = MU * k  (dissipation, s/m)
VELS = [0.25, 0.5, 1.0, 2.0, 4.0]
KS = [1e7, 1e8, 1e9]                 # soft / medium / hard (N/m^alpha)
K_SWEEP = np.logspace(5, 12, 15)     # stability sweep range


def modes():
    """Object used for the audible impact renders."""
    return make_modes("generic", "wood", mass=0.05)


def trend_modes():
    """Heavy resonator (modal mass >> striker mass) for the trend gates --
    matches the hammer-vs-massive-resonator setup the paper's contact-time
    observations refer to. With a LIGHT resonator the surface is pushed away
    and chases the striker, lengthening contact and causing micro-bounces
    (n_contacts > 1 in info) -- physically real, but a different regime."""
    return make_modes("generic", "wood", mass=0.5)


# ------------------------------------------------------------ A: material

def part_a_materials():
    freqs = np.array(SHAPES["generic"]["freqs"])
    renders = {}
    for mat in ORDER:
        bank = ModalBank(make_modes("generic", mat), FS)
        renders[f"stage2_material_{mat}.wav"] = bank.impulse_response(2.5)
    write_wav_group(renders)

    fig, axes = plt.subplots(1, len(ORDER), figsize=(3.2 * len(ORDER), 4.2),
                             sharey=True)
    print("stage2A: same shape, tan_phi swap; decay check @ first mode "
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
    fig.suptitle("Stage 2A: one shape, five materials (single tan_phi scalar)")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "stage2_materials.png", dpi=130)
    plt.close(fig)
    print(f"stage2A gate decay matches tan_phi:     {'PASS' if ok else 'CHECK'}")
    return ok


# -------------------------------------------------------------- B: impact

def part_b_impact():
    # ---- 15 renders: 5 velocities x 3 stiffnesses -------------------------
    renders = {}
    for k in KS:
        for v in VELS:
            audio, info = simulate_impact(M_S, v, k, ALPHA, MU * k, modes(),
                                          FS, dur=1.5)
            renders[f"stage2_impact_k{k:.0e}_v{v:.2f}.wav"] = audio
    write_wav_group(renders)
    plot_wave_spec(renders[f"stage2_impact_k{KS[-1]:.0e}_v1.00.wav"], FS,
                   "stage2_impact_example.png",
                   f"Stage 2B: impact render (k={KS[-1]:.0e}, v=1 m/s)")

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
    fig.suptitle("Stage 2B: Hunt-Crossley trends (RK4 reference integrator)")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "stage2_impact_trends.png", dpi=130)
    plt.close(fig)

    ct_k = np.array(ct_k); cen_k = np.array(cen_k); ct_v = np.array(ct_v)
    g1 = bool(np.all(np.diff(ct_k) < 0))
    g2 = bool(cen_k[-1] > cen_k[0] and
              np.polyfit(np.log10(k_axis), cen_k, 1)[0] > 0)
    # non-strict: contact time is quantized to the sim step (plateaus of
    # 1-2 steps between neighboring v values are measurement resolution)
    g3 = bool(np.all(np.diff(ct_v) <= 0) and ct_v[-1] < ct_v[0])
    print(f"stage2B gate contact-time falls with k: {'PASS' if g1 else 'FAIL'}")
    print(f"stage2B gate centroid rises with k:     {'PASS' if g2 else 'FAIL'}")
    print(f"stage2B gate contact-time falls with v: {'PASS' if g3 else 'FAIL'}")

    # ---- stability sweep --------------------------------------------------
    print("stage2B stability sweep (v=1 m/s), fs=44100:")
    stable_all = True
    for k in K_SWEEP:
        for method in ("rk4", "implicit"):
            audio, info = simulate_impact(M_S, 1.0, k, ALPHA, MU * k, modes(),
                                          FS, dur=0.3, method=method)
            ok = info["stable"] and np.all(np.isfinite(audio))
            stable_all &= bool(ok)
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
    fig.savefig(FIG_DIR / "stage2_integrators.png", dpi=130)
    plt.close(fig)
    print(f"stage2B integrator check: contact_time rk4={i_rk4['contact_time']*1e3:.3f} ms"
          f" implicit={i_imp['contact_time']*1e3:.3f} ms"
          f"  centroid rk4={spectral_centroid(a_rk4, FS):.0f} Hz"
          f" implicit={spectral_centroid(a_imp, FS):.0f} Hz")
    return g1 and g2 and g3 and stable_all


# ------------------------------------------------- C: physical primitives

V_DROP = 2.0         # m/s, ~20 cm drop
EDGE_R = 0.003       # m, radius of the corner/edge that touches the floor
FLOOR = "concrete"

PRIMITIVES = {
    # name: (builder, kwargs, material)
    "wood_plank":  (bar,  dict(length=0.40, width=0.08, thickness=0.02), "wood"),
    "plastic_bar": (bar,  dict(length=0.25, width=0.03, thickness=0.01), "plastic"),
    "steel_rod":   (tube, dict(length=0.50, outer_radius=0.015, wall=None), "metal"),
    "steel_pipe":  (tube, dict(length=0.50, outer_radius=0.015, wall=0.0015), "metal"),
    "glass_disc":  (disc, dict(radius=0.12, thickness=0.004), "glass"),
}


def part_c_primitives():
    print(f"stage2C: primitives dropped on {FLOOR} at {V_DROP} m/s (striker = "
          f"object mass, k = Hertz(material, {FLOOR}, r={EDGE_R*1e3:.0f} mm))")
    renders, tables = {}, {}
    for name, (builder, kw, mat) in PRIMITIVES.items():
        mds, M = builder(material=mat, **kw)
        k = hertz_stiffness(mat, FLOOR, EDGE_R)
        audio, info = simulate_impact(M, V_DROP, k, ALPHA, MU * k, mds, FS,
                                      dur=2.0)
        renders[f"stage2_primitive_{name}.wav"] = audio
        tables[name] = [m.freq for m in mds]
        print(f"  {name:12s} {mat:8s} M={M:6.3f} kg  k={k:8.2e}  "
              f"contact {info['contact_time']*1e3:6.3f} ms  "
              f"modes(Hz) {', '.join(f'{m.freq:.0f}' for m in mds[:5])}")
    write_wav_group(renders)

    fig, ax = plt.subplots(figsize=(9, 4.2))
    for i, fr in enumerate(tables.values()):
        ax.scatter(fr, [i] * len(fr), marker="|", s=300)
    ax.set_yticks(range(len(tables)), list(tables))
    ax.set_xscale("log")
    ax.set_xlabel("mode frequency (Hz)")
    ax.set_title("Stage 2C: analytic primitive mode sets (geometry + E/rho)")
    ax.grid(alpha=0.3, which="both")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "stage2_primitives.png", dpi=130)
    plt.close(fig)

    r = tables["wood_plank"][1] / tables["wood_plank"][0]
    ro, ri = 0.015, 0.0135
    pr = tables["steel_pipe"][0] / tables["steel_rod"][0]
    pr_expect = np.sqrt(ro**2 + ri**2) / ro
    g1 = abs(r - 2.7565) < 0.01
    g2 = abs(pr - pr_expect) < 1e-3
    print(f"stage2C gate beam f2/f1 = {r:.4f} (2.7565): {'PASS' if g1 else 'FAIL'}")
    print(f"stage2C gate pipe/rod f1 = {pr:.4f} ({pr_expect:.4f}): "
          f"{'PASS' if g2 else 'FAIL'}")
    return g1 and g2


def main():
    a = part_a_materials()
    b = part_b_impact()
    c = part_c_primitives()
    ok = a and b and c
    print(f"stage2 gate: {'PASS' if ok else 'FAIL'} + listen to the WAVs")
    return ok


if __name__ == "__main__":
    main()
