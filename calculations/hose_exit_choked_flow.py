"""Choked (sonic) flow of hydrogen at the physical hose exit, expanding
from high-pressure storage down to the flow state at the orifice itself
-- NOT yet expanded to ambient pressure.

H2 releases from bar-level storage are essentially always choked: the
critical pressure ratio for H2 is P0/P_amb > (2/(gamma+1))**(-gamma/(gamma-1))
~= 1.9, trivially satisfied at 500 bar. Ideal-gas relations are used
throughout; at 500 bar H2 deviates non-trivially from ideal-gas behaviour
(compressibility factor Z > 1), so treat these numbers as an engineering
estimate rather than a high-accuracy result -- a real-gas EOS (Abel-Noble,
NIST REFPROP) would be needed for that.
"""

import math

from hydrogen_properties import GAMMA, R_H2


def choked_flow_exit(p0, t0, diameter, area_fraction=1.0):
    """Real-orifice choked-flow state.

    p0: storage (stagnation) pressure [Pa]
    t0: storage (stagnation) gas temperature [K]
    diameter: hose/pipe inner diameter [m]
    area_fraction: fraction of the full hose bore that is actually open
        to flow (1.0 = full-bore guillotine rupture, <1.0 = partial
        failure / crack releasing through a smaller effective area)
    """
    area = math.pi / 4.0 * diameter**2 * area_fraction

    t_star = t0 * 2.0 / (GAMMA + 1.0)
    p_star = p0 * (2.0 / (GAMMA + 1.0)) ** (GAMMA / (GAMMA - 1.0))
    rho0 = p0 / (R_H2 * t0)
    rho_star = rho0 * (2.0 / (GAMMA + 1.0)) ** (1.0 / (GAMMA - 1.0))
    v_star = math.sqrt(GAMMA * R_H2 * t_star)
    mdot = rho_star * area * v_star

    return {
        "area": area,
        "t_star": t_star,
        "p_star": p_star,
        "rho0": rho0,
        "rho_star": rho_star,
        "v_star": v_star,
        "mdot": mdot,
    }


if __name__ == "__main__":
    P0 = 500e5         # storage pressure, 500 bar [Pa]
    T0 = 12 + 273.15    # storage gas temperature, 12 degC [K]
    D = 50.8e-3         # hose inner diameter [m]
    AREA_FRACTION = 1.0  # 1.0 = full-bore rupture; e.g. 0.1 = 10% open area

    state = choked_flow_exit(P0, T0, D, AREA_FRACTION)

    print(f"Real hose-exit choked flow -- 500 bar H2, T_gas = 12 degC, "
          f"{AREA_FRACTION * 100:.0f}% area open")
    print(f"  hose ID               : {D * 1e3:.1f} mm  (open A = {state['area'] * 1e6:.1f} mm^2)")
    print(f"  exit (throat) temp    : {state['t_star']:.1f} K")
    print(f"  exit (throat) pressure: {state['p_star'] / 1e5:.1f} bar")
    print(f"  exit density          : {state['rho_star']:.2f} kg/m^3")
    print(f"  exit velocity (sonic) : {state['v_star']:.1f} m/s")
    print(f"  mass flow rate        : {state['mdot']:.2f} kg/s")
