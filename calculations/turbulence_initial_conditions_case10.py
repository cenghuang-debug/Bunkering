"""Turbulence initial/boundary conditions (k, epsilon, nut, alphat) for
Bunkering_10 (978mm nozzle, 100% rupture domain, southwest wind case).

Reuses the k_epsilon/nut_alphat formulas from turbulence_initial_conditions.py
(Bunkering_07) unchanged.

Three differences from the Bunkering_07 script:

- Nozzle inlet: Bunkering_10 uses the 978mm square nozzle
  (system/topoSetDict box +/-0.489m) rather than Bunkering_07's 46mm
  nozzle, at the same reduced 800 m/s ramp target currently in 0.orig/U --
  Bunkering_10's own 0.orig/{k,epsilon} nozzle entries were carried over
  from a 07-based case (mixingLength comment still said "D=46mm"), stale
  for the 978mm nozzle.

- Background velocity (domain internalField + open boundaries):
  Bunkering_07's U_AMBIENT=0.01 m/s was explicitly a numerical placeholder
  because that domain starts at rest with no physical mean velocity to
  scale I off of (see turbulence_initial_conditions.py docstring).
  Bunkering_10 adds a persistent 7 m/s southwest ambient wind (a system
  boundary condition, not a placeholder), so that reasoning no longer
  applies -- background k/eps should scale off the real 7 m/s wind speed
  instead.

- Background turbulence intensity: for the same reason, Bunkering_07's
  I_AMBIENT=1% (also just "small and finite", not physical) is too low to
  carry over as a real atmospheric value. Typical turbulence intensity for
  wind over open water/marine surroundings (low surface roughness) is
  roughly 5-8%, well below onshore/rough-terrain values (10-20%+); use
  I_AMBIENT=5% as a reasonable, defensible mid-range choice for this
  quayside/open-water site. L_AMBIENT (nominal ambient length scale) is
  kept unchanged.
"""

from hydrogen_properties import R_H2, R_AIR, P_ATM
from turbulence_initial_conditions import (
    CMU, PRT, L_AMBIENT, T_AMB, I_NOZZLE, T_GAS,
    k_epsilon, nut_alphat,
)

# ---- background (domain internalField + open boundaries) ----
U_AMBIENT = 7.0          # m/s -- SW wind speed (Vx=4.95, Vy=-4.95, Vz=0), not a
                          # near-rest placeholder like Bunkering_07's 0.01 m/s.
I_AMBIENT = 0.05          # 5% -- typical atmospheric TI over open water; Bunkering_07's
                          # 1% was a "small and finite" placeholder, not physical.

# ---- nozzle inlet (Bunkering_10: 978mm square nozzle) ----
NOZZLE_SIDE = 978e-3     # m, square nozzle side (system/topoSetDict box +/-0.489m)
D_NOZZLE = NOZZLE_SIDE   # hydraulic diameter of a square duct = its side length
L_NOZZLE = 0.07 * D_NOZZLE
V_NOZZLE = 800.0         # m/s -- current ramp target (Bunkering_10/0.orig/U)


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

    print("\nNozzle inlet, I = 5%, l = 0.07*D, D = 978mm")
    print(f"  D_nozzle    = {D_NOZZLE * 1e3:.1f} mm (square side, hydraulic diameter)")
    print(f"  l           = {L_NOZZLE * 1e3:.2f} mm")
    print(f"  V_nozzle    = {V_NOZZLE:.0f} m/s (current ramp target)")
    print(f"  rho_H2      = {rho_h2:.4f} kg/m^3 (T_gas = {T_GAS:.2f} K)")
    print(f"  k           = {k_noz:.4e} m^2/s^2")
    print(f"  epsilon     = {eps_noz:.4e} m^2/s^3")
    print(f"  nut         = {nut_noz:.4e} m^2/s")
    print(f"  alphat      = {alphat_noz:.4e} kg/(m s)")
