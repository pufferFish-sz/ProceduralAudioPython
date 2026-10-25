"""Shared scene machinery: render "mover hits target", name files by what
happens, write a manifest that says exactly what each file contains.

File-name grammar (one scene = one mix file):
    <action>_<mover>_<how>_<onto|on>_<target>.wav
    e.g. drop_rubber-ball-small-r15mm_from-1m_onto_wood-floor.wav
Stems (what each body contributes) go to stems/ as
    <same name>__ONLY-<body>.wav
All files of one scene family share ONE gain, so loudness differences
between files are real (physics), not normalization -- except families
built from non-physical layers (footsteps), whose manifest says so.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from ..analysis.spectro import spectrogram_db
from ..core.bodies import (Body, body_sound, calibrate_mu, contact_pulse,
                           mode_summary)
from ..util import FIG_DIR, FS, SCENE_DIR, _write_wav_file, db_to_lin

G = 9.81
FADE = 0.03        # s, raised-cosine fade at file end (no cut-off click)


@dataclass
class Scene:
    name: str                      # mix file stem
    what: str                      # one sentence: what you hear
    mover: Body | None             # None for non-modal scenes (footsteps)
    target: Body | None
    stems: dict[str, np.ndarray]   # body slug -> pressure proxy
    facts: list[str] = field(default_factory=list)

    @property
    def mix(self) -> np.ndarray:
        return sum(self.stems.values())


def _place(F: np.ndarray, pulse: np.ndarray, i0: int) -> None:
    n = min(len(pulse), len(F) - i0)
    if n > 0:
        F[i0:i0 + n] += pulse[:n]


def bounce_scene(ball: Body, floor: Body, h0: float, fs: int = FS,
                 tail: float = 1.0, v_min: float = 0.15,
                 max_bounces: int = 30, t_max: float = 8.0) -> Scene:
    """Drop `ball` from h0 onto `floor` and let it bounce to rest. Every
    bounce uses the rebound speed the contact solve actually produced."""
    v = np.sqrt(2 * G * h0)
    t = np.sqrt(2 * h0 / G)
    v0 = v
    mu0 = calibrate_mu(ball, floor, v0, fs)
    hits = []
    while True:
        # mu * v held constant -> (near) constant restitution per bounce, the
        # classic bouncing-ball model; fixed mu would make slow bounces almost
        # perfectly elastic and the ball would never settle.
        mu = mu0 * v0 / v
        pulse, info = contact_pulse(ball, floor, v, fs, mu)
        hits.append((t, v, pulse, info))
        v_reb = info["rebound"]
        if v_reb < v_min or len(hits) >= max_bounces:
            break
        t += info["contact_time"] + 2 * v_reb / G
        if t > t_max:
            break
        v = v_reb
    F = np.zeros(int((hits[-1][0] + tail) * fs))
    for t_i, _, pulse, _ in hits:
        _place(F, pulse, int(t_i * fs))
    stems = {ball.slug: body_sound(ball, F, fs, -1.0)["mix"],
             floor.slug: body_sound(floor, F, fs, +1.0)["mix"]}
    first = hits[0][3]
    imp_err = max(abs(p.sum() / fs - ball.mass * (vi + inf["rebound"]))
                  / (ball.mass * (vi + inf["rebound"])) for _, vi, p, inf in hits)
    facts = [
        f"drop height {h0:g} m -> first impact {hits[0][1]:.2f} m/s; "
        f"{len(hits)} bounces over {hits[-1][0]:.2f} s",
        f"contact stiffness k = {first['k']:.2e} N/m^1.5 (Hertz, "
        f"{ball.material} on {floor.material}); first contact "
        f"{first['contact_time']*1e3:.2f} ms",
        f"restitution {hits[0][3]['rebound']/hits[0][1]:.2f} on the first bounce "
        f"(calibrated, mu * v = {mu0 * v0:.3f}), "
        f"{hits[-1][3]['rebound']/hits[-1][1]:.2f} on the last",
        f"impulse check: max error {100*imp_err:.2f} % vs m (v_in + v_out)",
    ]
    return Scene(name="", what="", mover=ball, target=floor, stems=stems,
                 facts=facts)


def strike_scene(stick: Body, target: Body, v: float, fs: int = FS,
                 dur: float = 6.0) -> Scene:
    """One hit of `stick` on a free (suspended) `target` at speed v."""
    mu = calibrate_mu(stick, target, v, fs)
    pulse, info = contact_pulse(stick, target, v, fs, mu)
    F = np.zeros(int(dur * fs))
    _place(F, pulse, int(0.1 * fs))
    stems = {stick.slug: body_sound(stick, F, fs, -1.0)["mix"],
             target.slug: body_sound(target, F, fs, +1.0)["mix"]}
    facts = [
        f"strike speed {v:g} m/s; contact stiffness k = {info['k']:.2e} "
        f"N/m^1.5 (Hertz, {stick.material} tip on {target.material})",
        f"contact time {info['contact_time']*1e3:.3f} ms, "
        f"{info['n_contacts']} contact(s) (micro-bounces), stick rebound "
        f"{info['rebound']:.2f} m/s (calibrated mu = {mu:.3f} s/m)",
        f"effective mass in contact {info['m_eff']*1e3:.1f} g "
        "(stick tip vs free bar, reduced mass)",
    ]
    return Scene(name="", what="", mover=stick, target=target, stems=stems,
                 facts=facts)


# ---------------------------------------------------------------- output

def _fade(y: np.ndarray, fs: int) -> np.ndarray:
    n = int(FADE * fs)
    y = y.copy()
    y[-n:] *= 0.5 * (1 + np.cos(np.linspace(0, np.pi, n)))
    return y


def _energy_share(scene: Scene) -> dict[str, float]:
    e = {k: float(np.sum(v**2)) for k, v in scene.stems.items()}
    tot = sum(e.values()) or 1.0
    return {k: 100 * v / tot for k, v in e.items()}


def write_family(family: str, title: str, intro: str, scenes: list[Scene],
                 fs: int = FS, peak_db: float = -3.0,
                 level_note: str | None = None) -> Path:
    """Write mixes + stems with one shared gain, a README manifest and a
    spectrogram figure. Returns the family directory."""
    out = SCENE_DIR / family
    (out / "stems").mkdir(parents=True, exist_ok=True)
    for old in list(out.glob("*.wav")) + list((out / "stems").glob("*.wav")):
        old.unlink()
    peak = max(float(np.max(np.abs(s.mix))) for s in scenes) or 1.0
    g = db_to_lin(peak_db) / peak

    lines = [f"# {title}", "", intro, "",
             level_note or ("All files in this folder share one gain: louder "
                            "here = louder in the physics."),
             "Stems in `stems/` are each sound source on its own (same gain).",
             ""]
    for s in scenes:
        _write_wav_file(out / f"{s.name}.wav", _fade(s.mix, fs) * g, fs)
        if len(s.stems) > 1:              # a single stem == the mix
            for slug, y in s.stems.items():
                _write_wav_file(out / "stems" / f"{s.name}__ONLY-{slug}.wav",
                                _fade(y, fs) * g, fs)
        share = _energy_share(s)
        bodies = [b for b in (s.mover, s.target) if b is not None]
        lines += [f"## `{s.name}.wav`", "", f"**What you hear:** {s.what}", ""]
        if s.mover is not None:
            lines.append(f"- **Mover:** {s.mover.description}. Audible "
                         f"modes: {mode_summary(s.mover)}.")
        if s.target is not None:
            lines.append(f"- **Target:** {s.target.description}. Lowest "
                         f"modes: {mode_summary(s.target)} "
                         f"({len(s.target.modes)} modes used).")
        lines += [*[f"- {f}" for f in s.facts],
                  "- Energy share: " + ", ".join(
                      f"{k} {v:.0f} %" for k, v in share.items()),
                  *[f"- Note: {n}" for b in bodies for n in b.notes],
                  ""]
    (out / "README.md").write_text("\n".join(lines), encoding="utf-8")

    ncol = min(3, len(scenes))
    nrow = int(np.ceil(len(scenes) / ncol))
    fig, axes = plt.subplots(nrow, ncol, figsize=(5 * ncol, 3.6 * nrow),
                             squeeze=False, sharey=True)
    for ax, s in zip(axes.flat, scenes):
        f, ts, S = spectrogram_db(s.mix, fs)
        ax.pcolormesh(ts, f, S, shading="gouraud", cmap="magma",
                      vmin=-90, vmax=0)
        ax.set_ylim(0, 8000)
        ax.set_title(s.name.replace("_", " "), fontsize=8)
        ax.set_xlabel("time (s)")
    for ax in axes[:, 0]:
        ax.set_ylabel("frequency (Hz)")
    for ax in list(axes.flat)[len(scenes):]:
        ax.axis("off")
    fig.suptitle(title)
    fig.tight_layout()
    fig.savefig(FIG_DIR / f"scenes_{family}.png", dpi=110)
    plt.close(fig)
    return out
