"""Birch (1987) notional-nozzle model: replaces the real, underexpanded
choked hose exit with an equivalent nozzle discharging at ambient
pressure, conserving mass flow rate and momentum flux (energy is not
conserved -- standard for the notional-nozzle approach).

The notional-nozzle temperature is taken equal to ambient temperature,
Tn = T_amb, rather than the real-throat temperature T* (the other common
variant of the model). This is why an ambient temperature is needed as an
explicit input alongside the storage gas temperature.
"""

import math

from hydrogen_properties import R_H2, P_ATM
from hose_exit_choked_flow import choked_flow_exit


def notional_nozzle(p0, t0, diameter, t_amb, p_amb=P_ATM, area_fraction=1.0):
    """Notional-nozzle state, extending the real choked-flow state.

    p0, t0, diameter: as in choked_flow_exit()
    t_amb: ambient temperature [K], used for the notional-nozzle density
    p_amb: ambient pressure [Pa]
    area_fraction: fraction of the full hose bore open to flow (see
        choked_flow_exit). V_n is independent of this; ṁ, A_n, D_n
        scale down with it.
    """
    state = choked_flow_exit(p0, t0, diameter, area_fraction)
    mdot = state["mdot"]

    v_n = state["v_star"] + (state["p_star"] - p_amb) * state["area"] / mdot
    rho_n = p_amb / (R_H2 * t_amb)
    area_n = mdot / (rho_n * v_n)
    diameter_n = math.sqrt(4.0 * area_n / math.pi)

    state.update(v_n=v_n, rho_n=rho_n, area_n=area_n, diameter_n=diameter_n)
    return state


if __name__ == "__main__":
    P0 = 500e5          # storage pressure, 500 bar [Pa]
    T0 = 12 + 273.15     # storage gas temperature, 12 degC [K]
    T_AMB = 20 + 273.15  # ambient temperature, 20 degC [K]
    D = 50.8e-3          # hose inner diameter [m]

    AREA_FRACTION = 1.0  # 1.0 = full-bore rupture; e.g. 0.1 = 10% open area

    state = notional_nozzle(P0, T0, D, T_AMB, area_fraction=AREA_FRACTION)

    print(f"Birch (1987) notional nozzle -- 500 bar H2, T_gas = 12 degC, "
          f"T_amb = 20 degC, {AREA_FRACTION * 100:.0f}% area open")
    print(f"  real hose-exit velocity : {state['v_star']:.1f} m/s")
    print(f"  real hose-exit mdot     : {state['mdot']:.2f} kg/s")
    print(f"  notional exit velocity  : {state['v_n']:.1f} m/s")
    print(f"  notional exit area      : {state['area_n'] * 1e6:.1f} mm^2")
    print(f"  notional exit diameter  : {state['diameter_n'] * 1e3:.1f} mm")
