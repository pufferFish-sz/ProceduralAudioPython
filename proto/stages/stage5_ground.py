"""Stage 5: simplified ground layer (Qu & James 2019, heavily reduced).

Gate: A/B renders of an object impact with and without the ground layer;
spectrogram comparison figure (add real floor-drop recordings to
recordings/ for the full comparison).
Run:  python -m proto.stages.stage5_ground
"""
from pathlib import Path

import numpy as np

from ..analysis.spectro import plot_spec_compare
from ..core.ground import ground_layer
from ..core.impact import simulate_impact
from ..core.materials import make_modes
from ..util import FS, PROTO_DIR, write_wav_group

REC_DIR = PROTO_DIR / "recordings"


def main():
    v, mass = 2.2, 0.25          # object dropped on floor
    k = 4e8
    obj, _ = simulate_impact(0.25, v, k, 1.5, 0.6 * k,
                             make_modes("wood_block", "wood", mass=0.05),
                             FS, dur=1.2)
    obj = obj / (np.max(np.abs(obj)) or 1.0)
    gnd = ground_layer(v, mass, "wood_floor", FS, dur=1.2)
    gnd = np.pad(gnd, (0, len(obj) - len(gnd)))
    gnd = gnd / (np.max(np.abs(gnd)) or 1.0)
    with_ground = obj + 0.9 * gnd
    write_wav_group({
        "stage5_drop_object_only.wav": obj,
        "stage5_drop_with_ground.wav": with_ground,
        "stage5_ground_layer_solo.wav": gnd,
    })

    signals = [("object only", obj, FS), ("object + ground layer", with_ground, FS)]
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
    plot_spec_compare(signals, "stage5_ground_ab.png",
                      "Stage 5: floor drop A/B (ground layer adds LF thump + contact noise)",
                      fmax=6000)
    print("stage5: A/B renders + comparison figure written")
    if not REC_DIR.exists() or not any(REC_DIR.glob("*.wav")):
        print(f"  NOTE: put real floor-drop recordings in {REC_DIR} "
              "(any *floor*.wav is auto-included in the figure)")
    return True


if __name__ == "__main__":
    main()
