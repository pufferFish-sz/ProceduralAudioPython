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
    # granite-like stone; ear-plausible preset (lithophones ring for a while)
    "stone":   0.004,
}

# Elastic constants per material: Young's modulus E (Pa), density rho
# (kg/m^3), Poisson ratio nu. Rounded engineering reference values (steel,
# soda-lime glass, hardwood along the grain, ABS-type plastic, natural
# rubber), for intuition and order-of-magnitude pitch/hardness -- not
# citation-grade measurements. Used by core/shapes.py (E/rho -> mode
# frequencies) and core/impact.hertz_stiffness (E, nu -> contact k).
# Wood is strongly anisotropic; the along-grain E sets pitch, while contact
# (Hertz indentation) uses E_contact: impacts load wood ACROSS the grain,
# ~10x softer (hardwood radial/tangential E ~0.5-1.5 GPa, rounded).
PHYSICAL: dict[str, dict] = {
    "metal":   dict(E=200e9, rho=7850.0, nu=0.29),
    "glass":   dict(E=70e9,  rho=2500.0, nu=0.22),
    "wood":    dict(E=11e9,  rho=650.0,  nu=0.30, E_contact=1.0e9),
    "plastic": dict(E=2.5e9, rho=1100.0, nu=0.37),
    "rubber":  dict(E=0.01e9, rho=1100.0, nu=0.49),
    "stone":   dict(E=50e9, rho=2700.0, nu=0.25),
    # corrugated cardboard, 4 mm board treated as a homogeneous plate:
    # EFFECTIVE E and rho chosen so that bending stiffness D ~ 10 N m and
    # mass ~ 0.55 kg/m^2 (typical single-wall board), not liner properties
    "cardboard": dict(E=1.7e9, rho=140.0, nu=0.30),
    # surface-only entries (floors): no tan_phi preset, never a resonator here
    "concrete": dict(E=30e9, rho=2400.0, nu=0.20),
    # glazed ceramic floor tile (porcelain E ~ 50-70 GPa, rounded)
    "ceramic": dict(E=60e9, rho=2300.0, nu=0.22),
    # cut-pile rug: EFFECTIVE compressive modulus of the pile under a small
    # object (order of magnitude, ~0.2 MPa: a can sinks ~0.2 mm), not a
    # fibre property
    "carpet": dict(E=0.2e6, rho=200.0, nu=0.30),
}

# Hand-authored "shapes": mode frequency sets + relative gains. These are NOT
# derived from any geometry -- they are ear-plausible partial sets chosen
# for listening/decay-fit tests (none matches the ratio series of a bar,
# plate or shell). Frequencies stay fixed while material (tan_phi) swaps.
# For mode sets derived from real geometry + material constants, see
# core/shapes.py.
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
