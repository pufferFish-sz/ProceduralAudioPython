"""Stage 5: full pipeline driven by simulated physics (sim/trajectories.py).

- bouncing ball: impact model per event; must sound like a ball settling
  (decreasing loudness/brightness, accelerating rhythm);
- sliding box: friction exciter driven by decaying speed;
- tumble: irregular event stream, stress-tests overlap.
Impact scenes render twice: unified two-body contact (core/contact.py; the
main file names) and the legacy hand-mixed ground layer (*_legacy.wav). The
ball is also rendered on concrete, sharing one gain with the wood-floor
version so the floor swap is audible as-is.
Run:  python -m proto.stages.stage5_full_pipeline
"""
import numpy as np

from ..analysis.spectro import plot_wave_spec
from ..core.contact import render_contact
from ..core.friction import friction_exciter
from ..core.ground import ground_layer
from ..core.impact import simulate_impact
from ..core.materials import make_modes
from ..core.modal_bank import ModalBank
from ..sim.trajectories import bouncing_ball, sliding_box, tumble
from ..util import FS, write_wav, write_wav_group

M_S = 0.06        # ball / object mass as striker
ALPHA = 1.5
K = 3e8           # legacy path only (unified path uses Hertz k)
MU = 0.6
BALL_AREA = 0.001     # m^2, ~cross-section of a 1.8 cm glass ball
BLOCK_AREA = 0.004    # m^2, small wooden block face


def render_events_unified(events, modes_fn, obj_mass, obj_area, material,
                          surface, edge_radius, dur_tail=1.5):
    """Unified two-body path (core/contact.py): every event's force pulse
    drives object + click + floor in shared pressure units -- no hand gains,
    and k comes from Hertz(material, floor) instead of a velocity hack."""
    t_end = max(t for t, _ in events) + dur_tail
    out = np.zeros(int(t_end * FS) + 1)
    for t, v in events:
        r = render_contact(modes_fn(), obj_mass, obj_area, material, v,
                           surface, FS, min(dur_tail, t_end - t),
                           edge_radius=edge_radius)
        i0 = int(t * FS)
        n = min(len(r["mix"]), len(out) - i0)
        out[i0:i0 + n] += r["mix"][:n]
    return out


def render_events(events, modes_fn, dur_tail=1.5, ground=None,
                  velocity_to_k=None):
    """LEGACY: sum one impact render per (t, v) event into a single
    timeline, ground layer peak-matched and mixed by hand."""
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
    print(f"stage5: bouncing ball -> {len(events)} impacts over "
          f"{events[-1][0]:.2f} s, v from {events[0][1]:.2f} to "
          f"{events[-1][1]:.2f} m/s")
    ball_modes = lambda: make_modes("ceramic_mug", "glass", mass=0.03)
    ball_old = render_events(events, ball_modes, ground="wood_floor")
    write_wav("stage5_bouncing_ball_legacy.wav", ball_old)
    # glass ball, r ~ 1.8 cm: contact curvature = ball radius
    balls = {s: render_events_unified(events, ball_modes, M_S, BALL_AREA,
                                      "glass", s, edge_radius=0.018)
             for s in ("wood_floor", "concrete")}
    write_wav_group({"stage5_bouncing_ball.wav": balls["wood_floor"],
                     "stage5_bouncing_ball_concrete.wav": balls["concrete"]})
    plot_wave_spec(balls["wood_floor"], FS, "stage5_bouncing_ball.png",
                   "Stage 5: bouncing ball on wood floor (unified contact)")

    # ---- sliding box ------------------------------------------------------
    speed = sliding_box(v0=2.0, friction_mu=0.4, fs=FS)
    exc = friction_exciter(speed, FS, roughness=1.0)
    bank = ModalBank(make_modes("wood_block", "wood", mass=0.02), FS)
    slide = bank.process(exc) + 0.3 * exc
    write_wav("stage5_sliding_box.wav", slide)
    plot_wave_spec(slide, FS, "stage5_sliding_box.png",
                   "Stage 5: sliding box (friction exciter, decaying speed)")

    # ---- tumble -----------------------------------------------------------
    events = tumble(seed=7, dur=3.0)
    print(f"stage5: tumble -> {len(events)} irregular impacts")
    block_modes = lambda: make_modes("wood_block", "wood", mass=0.04)
    tmb_old = render_events(events, block_modes, ground="wood_floor",
                            velocity_to_k=lambda v: K * (0.5 + v / 2.5))
    write_wav("stage5_tumble_legacy.wav", tmb_old)
    tmb = render_events_unified(events, block_modes, M_S, BLOCK_AREA, "wood",
                                "wood_floor", edge_radius=0.003)
    write_wav("stage5_tumble.wav", tmb)
    plot_wave_spec(tmb, FS, "stage5_tumble.png",
                   "Stage 5: tumble stress test on wood floor (unified contact)")
    print("stage5: renders written -- LISTEN: ball should settle naturally "
          "(quieter, duller, faster rhythm)")
    return True


if __name__ == "__main__":
    main()
