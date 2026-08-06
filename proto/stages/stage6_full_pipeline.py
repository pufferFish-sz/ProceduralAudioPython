"""Stage 6: full pipeline driven by simulated physics (sim/trajectories.py).

- bouncing ball: impact model per event; must sound like a ball settling
  (decreasing loudness/brightness, accelerating rhythm);
- sliding box: friction exciter driven by decaying speed;
- tumble: irregular event stream, stress-tests overlap.
Run:  python -m proto.stages.stage6_full_pipeline
"""
import numpy as np

from ..analysis.spectro import plot_wave_spec
from ..core.friction import friction_exciter
from ..core.ground import ground_layer
from ..core.impact import simulate_impact
from ..core.materials import make_modes
from ..core.modal_bank import ModalBank
from ..sim.trajectories import bouncing_ball, sliding_box, tumble
from ..util import FS, write_wav

M_S = 0.06        # ball / object mass as striker
ALPHA = 1.5
K = 3e8
MU = 0.6


def render_events(events, modes_fn, dur_tail=1.5, ground=None,
                  velocity_to_k=None):
    """Sum one impact render per (t, v) event into a single timeline."""
    t_end = max(t for t, _ in events) + dur_tail
    out = np.zeros(int(t_end * FS) + 1)
    for t, v in events:
        k = velocity_to_k(v) if velocity_to_k else K
        audio, _ = simulate_impact(M_S, v, k, ALPHA, MU * k, modes_fn(),
                                   FS, dur=min(dur_tail, t_end - t))
        if ground is not None:
            g = ground_layer(v, M_S, ground, FS, dur=0.4)
            gp = np.max(np.abs(g)) or 1.0
            ap = np.max(np.abs(audio)) or 1.0
            g = g * (ap / gp) * 0.7 * min(1.0, v / 2.0)
            audio[:len(g)] += g
        i0 = int(t * FS)
        n = min(len(audio), len(out) - i0)
        out[i0:i0 + n] += audio[:n]
    return out


def main():
    # ---- bouncing ball ----------------------------------------------------
    events = bouncing_ball(h0=1.0, restitution=0.72, mass=M_S)
    print(f"stage6: bouncing ball -> {len(events)} impacts over "
          f"{events[-1][0]:.2f} s, v from {events[0][1]:.2f} to "
          f"{events[-1][1]:.2f} m/s")
    ball = render_events(events, lambda: make_modes("ceramic_mug", "glass",
                                                    mass=0.03),
                         ground="wood_floor")
    write_wav("stage6_bouncing_ball.wav", ball)
    plot_wave_spec(ball, FS, "stage6_bouncing_ball.png",
                   "Stage 6: bouncing ball (impact model per simulated event)")

    # ---- sliding box ------------------------------------------------------
    speed = sliding_box(v0=2.0, friction_mu=0.4, fs=FS)
    exc = friction_exciter(speed, FS, roughness=1.0)
    bank = ModalBank(make_modes("wood_block", "wood", mass=0.02), FS)
    slide = bank.process(exc) + 0.3 * exc
    write_wav("stage6_sliding_box.wav", slide)
    plot_wave_spec(slide, FS, "stage6_sliding_box.png",
                   "Stage 6: sliding box (friction exciter, decaying speed)")

    # ---- tumble -----------------------------------------------------------
    events = tumble(seed=7, dur=3.0)
    print(f"stage6: tumble -> {len(events)} irregular impacts")
    tmb = render_events(events, lambda: make_modes("wood_block", "wood",
                                                   mass=0.04),
                        ground="wood_floor",
                        velocity_to_k=lambda v: K * (0.5 + v / 2.5))
    write_wav("stage6_tumble.wav", tmb)
    plot_wave_spec(tmb, FS, "stage6_tumble.png",
                   "Stage 6: tumble stress test (overlapping impacts)")
    print("stage6: renders written -- LISTEN: ball should settle naturally "
          "(quieter, duller, faster rhythm)")
    return True


if __name__ == "__main__":
    main()
