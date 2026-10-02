"""Turbulence initial/boundary conditions (k, epsilon, nut, alphat) for
Bunkering_07, following the intensity/length-scale method used in the
H2Vent project (see H2Vent/python_script/calc_initial_k_epsilon.py and
H2Vent/CLAUDE.md "Turbulence Inlet BC Formulas"), citing Versteeg &
Malalasekera (2007), An Introduction to CFD: The Finite Volume Method:

    k       = 1.5 * (U * I)^2
    epsilon = Cmu^0.75 * k^1.5 / l

Two regions, per the documented methodology:

- Background (domain internalField + open boundaries): turbulence
  intensity I = 1%. The domain starts at rest, so there is no physical
  mean velocity to scale from; a small nominal reference velocity is
  used purely so k, epsilon are non-zero (avoids numerical errors from
  a zero-k initial field), matching this case's own 0.orig/U internal
  field (0.01 m/s) rather than borrowing H2Vent's room-scale numbers,
  which were tuned for a 1 m^3 enclosure, not Bunkering's open ~190x80x42 m
  outdoor domain. Background length scale L_AMBIENT is a nominal ambient
  eddy size, not a physically load-bearing choice -- these background
  values only need to be small and finite.

- Nozzle inlet: turbulence intensity I = 5%, length scale l = 0.07*D
  with D the (square) nozzle's hydraulic diameter. For a square duct of
  side s, D_h = 4*A/P = 4*s^2/(4*s) = s, so D = nozzle side length
  (46 mm, from system/topoSetDict: box +/-23mm).

nut and alphat are derived quantities (nut = Cmu*k^2/epsilon,
alphat = rho*nut/Prt) used only as initial "calculated"-type values;
the turbulence model recomputes them at runtime.
"""

from hydrogen_properties import R_H2, R_AIR, P_ATM

CMU = 0.09
PRT = 0.85

# ---- background (domain internalField + open boundaries) ----
U_AMBIENT = 0.01      # m/s -- matches 0.orig/U internalField (near-rest)
I_AMBIENT = 0.01       # 1%
L_AMBIENT = 1.0        # m -- nominal ambient eddy length scale (open outdoor domain)
T_AMB = 20 + 273.15    # ambient air temperature [K]

# ---- nozzle inlet ----
I_NOZZLE = 0.05         # 5%
NOZZLE_SIDE = 46e-3      # m, square nozzle side (system/topoSetDict box +/-23mm)
D_NOZZLE = NOZZLE_SIDE   # hydraulic diameter of a square duct = its side length
L_NOZZLE = 0.07 * D_NOZZLE
V_NOZZLE = 800.0         # m/s -- current ramp target (0.orig/U), Bunkering_07 reduced-velocity plan
T_GAS = 12 + 273.15      # H2 storage/inlet gas temperature [K]


def k_epsilon(u, intensity, length_scale):
    k = 1.5 * (u * intensity) ** 2
    epsilon = CMU ** 0.75 * k ** 1.5 / length_scale
    return k, epsilon


def nut_alphat(k, epsilon, rho, prt=PRT):
    nut = CMU * k ** 2 / epsilon
    alphat = rho * nut / prt
    return nut, alphat


if __name__ == "__main__":
    rho_air = P_ATM / (R_AIR * T_AMB)
    rho_h2 = P_ATM / (R_H2 * T_GAS)

    k_amb, eps_amb = k_epsilon(U_AMBIENT, I_AMBIENT, L_AMBIENT)
    nut_amb, alphat_amb = nut_alphat(k_amb, eps_amb, rho_air)

    k_noz, eps_noz = k_epsilon(V_NOZZLE, I_NOZZLE, L_NOZZLE)
    nut_noz, alphat_noz = nut_alphat(k_noz, eps_noz, rho_h2)

    print("Background (domain internalField + open boundaries), I = 1%")
    print(f"  U_ambient   = {U_AMBIENT} m/s, L_ambient = {L_AMBIENT} m")
    print(f"  rho_air     = {rho_air:.4f} kg/m^3 (T_amb = {T_AMB:.2f} K)")
    print(f"  k           = {k_amb:.4e} m^2/s^2")
    print(f"  epsilon     = {eps_amb:.4e} m^2/s^3")
    print(f"  nut         = {nut_amb:.4e} m^2/s")
    print(f"  alphat      = {alphat_amb:.4e} kg/(m s)")

    print("\nNozzle inlet, I = 5%, l = 0.07*D")
    print(f"  D_nozzle    = {D_NOZZLE * 1e3:.1f} mm (square side, hydraulic diameter)")
    print(f"  l           = {L_NOZZLE * 1e3:.2f} mm")
    print(f"  V_nozzle    = {V_NOZZLE:.0f} m/s (current ramp target)")
    print(f"  rho_H2      = {rho_h2:.4f} kg/m^3 (T_gas = {T_GAS:.2f} K)")
    print(f"  k           = {k_noz:.4e} m^2/s^2")
    print(f"  epsilon     = {eps_noz:.4e} m^2/s^3")
    print(f"  nut         = {nut_noz:.4e} m^2/s")
    print(f"  alphat      = {alphat_noz:.4e} kg/(m s)")
