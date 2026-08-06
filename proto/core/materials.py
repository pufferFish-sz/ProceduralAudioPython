"""Material model: frequency-dependent damping from a single scalar.

Reference: Klatzky, Pai & Krotkov, "Perception of Material from Contact
Sounds" (Presence 9(4), 2000).

Key result implemented here: each mode's decay rate scales with its own
frequency through one material constant, the internal-friction coefficient
tan(phi):

    d_n   = pi * f_n * tan_phi          [1/s]
    tau_n = 1 / (pi * f_n * tan_phi)    [s]

so ONE scalar (tan_phi) changes the perceived material while the mode
frequency set (the "shape") stays fixed. Klatzky et al. found this decay
parameter dominates material identification -- more than absolute frequency.

The tan_phi values below are order-of-magnitude presets consistent with the
ranges discussed in that literature (glass/metal very small, wood mid,
plastic/rubber large); they are meant as starting points for ear tuning,
not measured constants.
"""
from __future__ import annotations

import numpy as np

from .modal_bank import Mode

# material -> tan_phi (internal friction). Small = long ring.
MATERIALS: dict[str, float] = {
    "metal":   0.0002,
    "glass":   0.0008,
    "wood":    0.012,
    "plastic": 0.05,
    "rubber":  0.15,
}

# A few "shapes": mode frequency sets + relative gains. Frequencies define
# perceived size/geometry; they stay fixed while material (tan_phi) swaps.
SHAPES: dict[str, dict] = {
    # generic small struck object, spread partials, well separated (good for
    # decay-fit verification)
    "generic": {
        "freqs": [420.0, 990.0, 1730.0, 2650.0, 3800.0, 5200.0],
        "gains": [1.0, 0.70, 0.55, 0.40, 0.30, 0.22],
    },
    "wood_block": {
        "freqs": [523.0, 1180.0, 1980.0, 3120.0, 4560.0],
        "gains": [1.0, 0.6, 0.45, 0.3, 0.2],
    },
    "ceramic_mug": {
        "freqs": [1150.0, 2210.0, 3900.0, 6300.0, 8100.0],
        "gains": [1.0, 0.7, 0.5, 0.35, 0.2],
    },
    "metal_pot": {
        "freqs": [640.0, 1480.0, 2380.0, 3440.0, 4820.0, 6900.0, 9200.0],
        "gains": [1.0, 0.8, 0.65, 0.5, 0.4, 0.3, 0.2],
    },
}


def material_damping(freqs: np.ndarray | list[float], tan_phi: float) -> np.ndarray:
    """Per-mode decay rates d_n = pi * f_n * tan_phi (1/s)."""
    return np.pi * np.asarray(freqs, dtype=float) * tan_phi


def make_modes(shape: str | dict, material: str | float,
               mass: float = 0.05) -> list[Mode]:
    """Build a Mode list from a shape preset (or dict) and a material
    (name from MATERIALS, or a raw tan_phi float)."""
    spec = SHAPES[shape] if isinstance(shape, str) else shape
    tan_phi = MATERIALS[material] if isinstance(material, str) else float(material)
    decays = material_damping(spec["freqs"], tan_phi)
    return [Mode(freq=f, decay=d, gain=g, mass=mass)
            for f, d, g in zip(spec["freqs"], decays, spec["gains"])]
