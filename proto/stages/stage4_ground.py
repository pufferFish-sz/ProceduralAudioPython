"""Stage 4: ground layer -- legacy hand-mixed vs unified two-body contact.

Legacy (v1): object ring and a momentum-driven ground layer, each
peak-normalized and mixed with a hand-set gain.
Unified (v2, core/contact.py): one Hunt-Crossley force pulse (k from
Hertz(object, floor)) drives the object's modes, the object's rigid-body
"click" and the floor's modes; all in the same pressure-proxy units, so the
object/floor balance comes from the floor's modal mass, not a mix knob.

Gates:
- impulse check: integral of the resampled force = m (v_in - v_out), < 1 %;
- floor matters: the wood-floor layer is >= 20 dB stronger than concrete's
  for the same drop (massive slab barely moves).
Renders share one gain within the unified group, so wood floor vs concrete
loudness is comparable by ear. Add real floor-drop recordings to
recordings/ (*floor*.wav) for the full comparison.
Run:  python -m proto.stages.stage4_ground
"""
import numpy as np

from ..analysis.spectro import plot_spec_compare
from ..core.contact import render_contact
from ..core.ground import ground_layer
from ..core.impact import simulate_impact
from ..core.materials import make_modes
from ..util import FS, PROTO_DIR, write_wav_group

REC_DIR = PROTO_DIR / "recordings"

V, MASS = 2.2, 0.25          # wood block dropped ~25 cm
AREA = 0.012                 # m^2, radiating face of the block
DUR = 1.2


def legacy():
    k = 4e8
    obj, _ = simulate_impact(MASS, V, k, 1.5, 0.6 * k,
                             make_modes("wood_block", "wood", mass=0.05),
                             FS, dur=DUR)
    obj = obj / (np.max(np.abs(obj)) or 1.0)
    gnd = ground_layer(V, MASS, "wood_floor", FS, dur=DUR)
    gnd = np.pad(gnd, (0, len(obj) - len(gnd)))
    gnd = gnd / (np.max(np.abs(gnd)) or 1.0)
    return obj, gnd, obj + 0.9 * gnd


def rms_db(x):
    return 20 * np.log10(np.sqrt(np.mean(x**2)) + 1e-12)


def main():
    _, gnd_old, mix_old = legacy()
    write_wav_group({
        "stage4_legacy_drop_with_ground.wav": mix_old,
        "stage4_legacy_ground_layer_solo.wav": gnd_old,
    })

    res = {s: render_contact(make_modes("wood_block", "wood", mass=0.05),
                             MASS, AREA, "wood", V, s, FS, DUR)
           for s in ("wood_floor", "concrete")}
    obj_only = res["wood_floor"]["object"] + res["wood_floor"]["click"]
    write_wav_group({
        "stage4_drop_object_only.wav": obj_only,
        "stage4_drop_wood_floor.wav": res["wood_floor"]["mix"],
        "stage4_drop_concrete.wav": res["concrete"]["mix"],
        "stage4_floor_solo_wood_floor.wav": res["wood_floor"]["surface"],
        "stage4_floor_solo_concrete.wav": res["concrete"]["surface"],
    })

    print(f"stage4: wood block {MASS} kg at {V} m/s, unified contact")
    ok = True
    for s, r in res.items():
        info = r["info"]
        imp = r["force"].sum() / FS
        imp_exp = MASS * (V - info["v_out"])
        e_imp = abs(imp - imp_exp) / imp_exp
        ok &= e_imp < 0.01
        print(f"  {s:10s} k={r['k']:.2e}  contact {info['contact_time']*1e3:.2f} ms"
              f"  impulse {imp:.4f} vs m*dv {imp_exp:.4f} N s (err {100*e_imp:.2f} %)"
              f"  RMS dB: object {rms_db(r['object']):6.1f}"
              f"  click {rms_db(r['click']):6.1f}  floor {rms_db(r['surface']):6.1f}")
    gap = rms_db(res["wood_floor"]["surface"]) - rms_db(res["concrete"]["surface"])
    g2 = gap >= 20.0
    print(f"stage4 gate impulse conserved (<1 %):           {'PASS' if ok else 'FAIL'}")
    print(f"stage4 gate wood floor >= 20 dB over concrete:  "
          f"{'PASS' if g2 else 'FAIL'} ({gap:.1f} dB)")

    signals = [("unified: object only", obj_only, FS),
               ("legacy: object + ground layer", mix_old, FS),
               ("unified: on wood floor", res["wood_floor"]["mix"], FS),
               ("unified: on concrete", res["concrete"]["mix"], FS)]
    # pull in real floor-drop recordings if the user has added any
    for rec in sorted(REC_DIR.glob("*floor*.wav"))[:1]:
        try:
            import soundfile as sf
            y, fs_r = sf.read(rec)
            if y.ndim > 1:
                y = y.mean(axis=1)
            signals.append((f"real: {rec.name}", y, fs_r))
        except Exception as e:
            print(f"  (skip {rec.name}: {e})")
    plot_spec_compare(signals, "stage4_ground_ab.png",
                      "Stage 4: floor drop -- legacy hand-mix vs unified "
                      "two-body contact", fmax=6000)
    print("stage4: A/B renders + comparison figure written")
    if not REC_DIR.exists() or not any(REC_DIR.glob("*.wav")):
        print(f"  NOTE: put real floor-drop recordings in {REC_DIR} "
              "(any *floor*.wav is auto-included in the figure)")
    return ok and g2


if __name__ == "__main__":
    main()
