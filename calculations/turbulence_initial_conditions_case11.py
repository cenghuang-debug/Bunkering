"""Turbulence initial/boundary conditions (k, epsilon, nut, alphat) for
Bunkering_11 (10% rupture, 46mm nozzle, southwest wind case, larger quay).

Reuses the k_epsilon/nut_alphat formulas from turbulence_initial_conditions.py
(Bunkering_07) unchanged. Nozzle parameters (46mm, 800 m/s) are also unchanged
from Bunkering_07 -- Bunkering_11 keeps the same 10% rupture source, so there
is no nozzle-size mismatch to fix (unlike Bunkering_10, which moved to the
978mm 100% rupture nozzle).

Only the background (domain internalField + open boundaries) changes, for
the same reason documented in turbulence_initial_conditions_case10.py:

- Background velocity: Bunkering_07's U_AMBIENT=0.01 m/s was explicitly a
  numerical placeholder for a domain starting at rest. Bunkering_11 adds a
  persistent 7 m/s southwest ambient wind (a system boundary condition, not
  a placeholder), so background k/eps should scale off the real wind speed.

- Background turbulence intensity: Bunkering_07's I_AMBIENT=1% was also just
  "small and finite", not physical. Use I_AMBIENT=5%, the same typical
  open-water/marine atmospheric TI value used for Bunkering_10.
"""

from hydrogen_properties import R_H2, R_AIR, P_ATM
from turbulence_initial_conditions import (
    CMU, PRT, L_AMBIENT, T_AMB, I_NOZZLE, NOZZLE_SIDE, D_NOZZLE, L_NOZZLE,
    V_NOZZLE, T_GAS, k_epsilon, nut_alphat,
)

# ---- background (domain internalField + open boundaries) ----
U_AMBIENT = 7.0          # m/s -- SW wind speed (Vx=4.95, Vy=-4.95, Vz=0), not a
                          # near-rest placeholder like Bunkering_07's 0.01 m/s.
I_AMBIENT = 0.05          # 5% -- typical atmospheric TI over open water; Bunkering_07's
                          # 1% was a "small and finite" placeholder, not physical.

# nozzle inlet: unchanged from Bunkering_07 (46mm, 800 m/s, 10% rupture)


if __name__ == "__main__":
    rho_air = P_ATM / (R_AIR * T_AMB)
    rho_h2 = P_ATM / (R_H2 * T_GAS)

    k_amb, eps_amb = k_epsilon(U_AMBIENT, I_AMBIENT, L_AMBIENT)
    nut_amb, alphat_amb = nut_alphat(k_amb, eps_amb, rho_air)

    k_noz, eps_noz = k_epsilon(V_NOZZLE, I_NOZZLE, L_NOZZLE)
    nut_noz, alphat_noz = nut_alphat(k_noz, eps_noz, rho_h2)

    print(f"Background (domain internalField + open boundaries), I = {I_AMBIENT:.0%}")
    print(f"  U_ambient   = {U_AMBIENT} m/s, L_ambient = {L_AMBIENT} m")
    print(f"  rho_air     = {rho_air:.4f} kg/m^3 (T_amb = {T_AMB:.2f} K)")
    print(f"  k           = {k_amb:.4e} m^2/s^2")
    print(f"  epsilon     = {eps_amb:.4e} m^2/s^3")
    print(f"  nut         = {nut_amb:.4e} m^2/s")
    print(f"  alphat      = {alphat_amb:.4e} kg/(m s)")

    print("\nNozzle inlet (unchanged from Bunkering_07), I = 5%, l = 0.07*D, D = 46mm")
    print(f"  D_nozzle    = {D_NOZZLE * 1e3:.1f} mm (square side, hydraulic diameter)")
    print(f"  l           = {L_NOZZLE * 1e3:.2f} mm")
    print(f"  V_nozzle    = {V_NOZZLE:.0f} m/s (current ramp target)")
    print(f"  rho_H2      = {rho_h2:.4f} kg/m^3 (T_gas = {T_GAS:.2f} K)")
    print(f"  k           = {k_noz:.4e} m^2/s^2")
    print(f"  epsilon     = {eps_noz:.4e} m^2/s^3")
    print(f"  nut         = {nut_noz:.4e} m^2/s")
    print(f"  alphat      = {alphat_noz:.4e} kg/(m s)")
