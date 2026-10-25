"""Analytic shape primitives: mode sets from geometry + material constants.

Unlike the hand-authored materials.SHAPES, every frequency here follows
from dimensions (m) and the material's E, rho, nu (materials.PHYSICAL);
damping still comes from tan_phi (Klatzky et al.), so one call gives a
complete Mode list for "a <size> <shape> made of <material>".

Primitives and the theory behind them:

- bar(...)   slender free-free Euler-Bernoulli beam, rectangular section,
             bending in the thin direction. Standard result:
                 f_n = (beta_n L)^2 / (2 pi L^2) * sqrt(E I / (rho A))
             beta_n L = 4.7300, 7.8532, 10.9956, ... (ratios 1 : 2.757 :
             5.404 : 8.933 ...). Valid while L >> thickness.
- tube(...)  same beam theory with an annular section, I/A = (Ro^2+Ri^2)/4,
             so solid rods (Ri=0) and hollow pipes share one code path.
             Hollow tubes additionally get circumferential "ring" modes
             (inextensional ring / long thin shell approximation):
                 w_n = (h / R^2) sqrt(E / (12 rho (1-nu^2)))
                       * n (n^2-1) / sqrt(n^2+1),  n = 2, 3, ...
             -- for thin walls these are what make a pipe or can "clang".
- disc(...)  free-edge circular plate (Kirchhoff), f = lambda^2/(2 pi a^2)
             * sqrt(D / (rho h)), D = E h^3 / (12 (1-nu^2)); lambda^2 for
             nu = 0.3 from the Malison & Sompornjaroensuk (2015) benchmark
             table (consistent with Leissa, NASA SP-160, 1969).

Contact coupling: for the beam primitives the strike position x_s enters
through the exact free-free mode shape phi_n(x_s) (normalized so that
mean(phi^2) = 1 over the length). With modal mass = total mass M, the
contact-point coordinate q_n = phi_n(x_s) eta_n obeys
    q_n'' + ... = phi_n(x_s)^2 f / M     ->  Mode.mass = M / phi_n(x_s)^2
which is exactly the form ModalBank / simulate_impact expect (output and
contact displacement = sum of q_n). Striking near a node silences that
mode. Ring and plate modes use a heuristic 1/sqrt(order) coupling.

- sphere(...) solid sphere, spheroidal modes from Lamb's (1882) frequency
             equation, solved numerically with spherical Bessel functions
             (form as written in the nanoparticle-vibration literature, e.g.
             Saviot & Murray). eta = w a / c_T; validated: l=2 gives
             eta = 2.640 for nu = 0.25 (the classic value). Only the
             axisymmetric modes seen from the contact pole are used.
- plate_ss(...) simply supported rectangular plate (floors, decks, slabs):
                 f_mn = (pi/2) sqrt(D/(rho h)) ((m/a)^2 + (n/b)^2)
             phi_mn = 2 sin(m pi x/a) sin(n pi y/b) (mean phi^2 = 1).
             Standard Kirchhoff plate result (Leissa 1969).

Not covered analytically (no closed form): cubes/blocks, bowls, irregular
meshes -> FEM precompute (see docs/plan_and_brainstorm.md).
"""
from __future__ import annotations

import numpy as np
from scipy.optimize import brentq
from scipy.special import spherical_jn

from .materials import MATERIALS, PHYSICAL, material_damping
from .modal_bank import Mode

BEAM_BETA_L = np.array([4.730041, 7.853205, 10.995608, 14.137165,
                        17.278760, 20.420352, 23.561945, 26.703538])

# free-edge circular plate, nu = 0.3: (nodal diameters, nodal circles, lambda^2)
# Malison & Sompornjaroensuk, Engineering Transactions 18(1), 2015 (FEM
# benchmark, first 80 coefficients); repeated degenerate pairs listed once.
DISC_LAMBDA2 = [(2, 0, 5.359), (0, 1, 9.005), (3, 0, 12.441),
                (1, 1, 20.489), (4, 0, 21.840), (5, 0, 33.511),
                (2, 1, 35.293)]

F_MAX = 16000.0     # drop modes above this (inaudible/aliasing-prone)


def _props(material: str | dict):
    phys = PHYSICAL[material] if isinstance(material, str) else material
    tan_phi = MATERIALS[material] if isinstance(material, str) \
        else material["tan_phi"]
    return phys, tan_phi


def beam_mode_shape(n: int, x_frac: float) -> float:
    """Free-free beam mode shape phi_n at x = x_frac * L, mean(phi^2) = 1."""
    bl = BEAM_BETA_L[n]
    bx = bl * x_frac
    sigma = (np.cosh(bl) - np.cos(bl)) / (np.sinh(bl) - np.sin(bl))
    return float(np.cosh(bx) + np.cos(bx) - sigma * (np.sinh(bx) + np.sin(bx)))


def _beam_modes(L, I_over_A, area, material, strike, n_modes):
    phys, tan_phi = _props(material)
    M = phys["rho"] * area * L
    c = np.sqrt(phys["E"] / phys["rho"])
    freqs = BEAM_BETA_L[:n_modes] ** 2 / (2 * np.pi * L**2) * c * np.sqrt(I_over_A)
    modes = []
    for n, f in enumerate(freqs):
        phi2 = beam_mode_shape(n, strike) ** 2
        if f > F_MAX or phi2 < 1e-4:          # above range, or struck on a node
            continue
        d = material_damping([f], tan_phi)[0]
        modes.append(Mode(freq=float(f), decay=float(d), gain=1.0, mass=M / phi2))
    return modes, M


def bar(length: float, width: float, thickness: float, material: str | dict,
        strike: float = 0.1, n_modes: int = 6) -> tuple[list[Mode], float]:
    """Rectangular bar/plank/stick. Returns (modes, total mass kg).
    strike = contact position as a fraction of length (0 = end)."""
    area = width * thickness
    return _beam_modes(length, thickness**2 / 12.0, area, material, strike,
                       n_modes)


def tube(length: float, outer_radius: float, wall: float | None,
         material: str | dict, strike: float = 0.1, n_modes: int = 6,
         n_ring: int = 4) -> tuple[list[Mode], float]:
    """Circular rod (wall=None -> solid) or pipe. Returns (modes, mass)."""
    ro = outer_radius
    ri = 0.0 if wall is None else max(ro - wall, 0.0)
    area = np.pi * (ro**2 - ri**2)
    modes, M = _beam_modes(length, (ro**2 + ri**2) / 4.0, area, material,
                           strike, n_modes)
    if ri > 0.0:
        phys, tan_phi = _props(material)
        h, R = ro - ri, 0.5 * (ro + ri)
        w_scale = h / R**2 * np.sqrt(phys["E"] / (12 * phys["rho"] *
                                                  (1 - phys["nu"]**2)))
        for i, n in enumerate(range(2, 2 + n_ring)):
            f = w_scale * n * (n * n - 1) / np.sqrt(n * n + 1) / (2 * np.pi)
            if f > F_MAX:
                break
            d = material_damping([f], tan_phi)[0]
            modes.append(Mode(freq=float(f), decay=float(d), gain=1.0,
                              mass=M * np.sqrt(i + 1)))
    modes.sort(key=lambda m: m.freq)
    return modes, M


def disc(radius: float, thickness: float, material: str | dict,
         n_modes: int = 8) -> tuple[list[Mode], float]:
    """Free-edge circular plate (plate, lid, cymbal-ish). Returns (modes, mass)."""
    phys, tan_phi = _props(material)
    M = phys["rho"] * np.pi * radius**2 * thickness
    D = phys["E"] * thickness**3 / (12 * (1 - phys["nu"]**2))
    scale = np.sqrt(D / (phys["rho"] * thickness)) / (2 * np.pi * radius**2)
    modes = []
    for i, (_, _, lam2) in enumerate(DISC_LAMBDA2[:n_modes]):
        f = lam2 * scale
        if f > F_MAX:
            break
        d = material_damping([f], tan_phi)[0]
        modes.append(Mode(freq=float(f), decay=float(d), gain=1.0,
                          mass=M * np.sqrt(i + 1)))
    return modes, M


def _lamb_spheroidal(eta: float, l: int, beta: float) -> float:
    """Lamb's free-sphere spheroidal equation, multiplied through by
    j_l(eta) j_l(xi) so it has no poles. beta = c_T / c_L, xi = beta eta."""
    xi = beta * eta
    jl, jl1 = spherical_jn(l, eta), spherical_jn(l + 1, eta)
    xl, xl1 = spherical_jn(l, xi), spherical_jn(l + 1, xi)
    return (2 * (eta**2 * jl + (l - 1) * (l + 2) * (eta * jl1 - (l + 1) * jl))
            * xi * xl1
            + (-eta**4 / 2 + (l - 1) * (2 * l + 1) * eta**2) * jl * xl
            + (eta**2 - 2 * l * (l - 1) * (l + 2)) * eta * jl1 * xl)


def sphere_eta(l: int, nu: float, n_roots: int = 1) -> list[float]:
    """Lowest dimensionless spheroidal roots eta = w a / c_T for degree l."""
    beta = np.sqrt((1 - 2 * nu) / (2 * (1 - nu)))
    x = np.linspace(0.2, 30.0, 6000)
    g = _lamb_spheroidal(x, l, beta)
    roots = []
    for i in np.nonzero(np.sign(g[:-1]) != np.sign(g[1:]))[0]:
        roots.append(brentq(_lamb_spheroidal, x[i], x[i + 1], args=(l, beta)))
        if len(roots) >= n_roots:
            break
    return roots


def sphere(radius: float, material: str | dict, l_max: int = 5,
           overtones: int = 2) -> tuple[list[Mode], float]:
    """Solid ball (marble, bouncy ball, steel ball bearing). Returns
    (modes, mass). Struck at a pole, only axisymmetric modes respond; their
    radial amplitude at the pole is P_l(1) = 1 for every l. Coupling mass:
    heuristic M * sqrt(order) (no closed-form modal mass used here).
    Small hard balls ring far above hearing (F_MAX culls them) -- a glass
    marble's sound is its contact click + the floor."""
    phys, tan_phi = _props(material)
    M = phys["rho"] * 4.0 / 3.0 * np.pi * radius**3
    c_t = np.sqrt(phys["E"] / (2 * (1 + phys["nu"])) / phys["rho"])
    freqs = []
    for l in range(2, l_max + 1):
        for eta in sphere_eta(l, phys["nu"], overtones):
            freqs.append(eta * c_t / (2 * np.pi * radius))
    modes = []
    for i, f in enumerate(sorted(freqs)):
        if f > F_MAX:
            break
        d = material_damping([f], tan_phi)[0]
        modes.append(Mode(freq=float(f), decay=float(d), gain=1.0,
                          mass=M * np.sqrt(i + 1)))
    return modes, M


def plate_ss(a: float, b: float, thickness: float, material: str | dict,
             tan_phi: float, x: float = 0.37, y: float = 0.43,
             f_max: float = 4000.0) -> tuple[list[Mode], float]:
    """Simply supported rectangular plate a x b (m), struck at (x*a, y*b).

    tan_phi here is the INSTALLED loss factor (material + supports + what
    the plate rests on), not the bare material value: a bolted steel deck
    or a slab on soil loses far more energy than a free sample.
    Returns (modes, mass); coupling mass = M / phi_mn(x, y)^2."""
    phys = PHYSICAL[material] if isinstance(material, str) else material
    M = phys["rho"] * a * b * thickness
    D = phys["E"] * thickness**3 / (12 * (1 - phys["nu"]**2))
    scale = np.pi / 2 * np.sqrt(D / (phys["rho"] * thickness))
    modes = []
    m_max = int(np.sqrt(f_max / scale) * a) + 1
    n_max = int(np.sqrt(f_max / scale) * b) + 1
    for m in range(1, m_max + 1):
        for n in range(1, n_max + 1):
            f = scale * ((m / a)**2 + (n / b)**2)
            if f > f_max:
                continue
            phi2 = (2 * np.sin(m * np.pi * x) * np.sin(n * np.pi * y))**2
            if phi2 < 1e-3:
                continue
            d = material_damping([f], tan_phi)[0]
            modes.append(Mode(freq=float(f), decay=float(d), gain=1.0,
                              mass=M / phi2))
    modes.sort(key=lambda md: md.freq)
    return modes, M
