"""Ramp-up strategy for the full-bore (100% area) 500 bar notional nozzle:
lower inlet velocities (800/600/400/200 m/s) considered two ways.

(A) Mass-conserving equivalent nozzle: a uniform top-hat inlet at the
    reduced velocity, enlarged so the SAME total mass flow rate passes
    through it as the real notional nozzle (same method used in the
    V_house ramp-up notebook, cells 32126155).

(B) Virtual downstream source: instead of resizing the source, look
    further downstream in the real (full-velocity) notional jet for the
    station x at which the natural turbulent centerline velocity has
    already decayed to the target value, using the standard variable-
    density round-jet decay law (Chen & Rodi 1980 form, also used by
    Houf & Schefer for H2 jets):

        U_c(x) / V_n = K_u * sqrt(rho_n / rho_amb) * (D_n / x)

    with K_u ~ 5.4 (literature range ~5.0-6.2) and D_n the notional
    nozzle's equivalent diameter. The jet's own physical half-width at
    that station is estimated from the standard linear round-jet
    spreading law b(x) ~= S * x, S ~ 0.094 (Rajaratnam-type constant for
    the velocity half-width). Both constants carry engineering-level
    uncertainty (+/-15-20%) -- treat these as order-of-magnitude
    estimates, not a substitute for resolving the near-field jet in CFD.

Both methods start from the same 500 bar, 50.8 mm hose, 100% open area,
Birch 1987 notional nozzle as the reference source.
"""

import math

from hydrogen_properties import R_AIR
from notional_nozzle_birch import notional_nozzle

P0 = 500e5           # storage pressure, 500 bar [Pa]
T0 = 12 + 273.15      # storage gas temperature, 12 degC [K]
T_AMB = 20 + 273.15   # ambient temperature, 20 degC [K]
D = 50.8e-3           # hose inner diameter [m]

K_U = 5.4             # centerline velocity decay constant (Chen & Rodi form)
SPREAD_RATE = 0.094   # round-jet velocity half-width spreading rate, b(x) ~= SPREAD_RATE * x

TARGET_VELOCITIES = [800.0, 600.0, 400.0, 200.0]  # m/s


def mass_conserving_nozzle(mdot, rho_n, velocity):
    area = mdot / (rho_n * velocity)
    side = math.sqrt(area)
    return area, side


def decay_distance(v_n, d_n, rho_n, rho_amb, u_target, k_u=K_U):
    return k_u * math.sqrt(rho_n / rho_amb) * d_n * v_n / u_target


def jet_half_width(x, spread_rate=SPREAD_RATE):
    return spread_rate * x


if __name__ == "__main__":
    ref = notional_nozzle(P0, T0, D, T_AMB, area_fraction=1.0)
    mdot = ref["mdot"]
    v_n = ref["v_n"]
    d_n = ref["diameter_n"]          # circular-equivalent diameter of full notional nozzle
    rho_n = ref["rho_n"]             # H2 density at notional-nozzle (ambient) conditions
    rho_amb = 101325.0 / (R_AIR * T_AMB)  # ambient air density [kg/m^3]

    print("Reference: full-bore (100% area) Birch 1987 notional nozzle")
    print(f"  mdot = {mdot:.2f} kg/s, V_n = {v_n:.1f} m/s, "
          f"D_n (equiv. circular) = {d_n * 1e3:.1f} mm, "
          f"D_n (square side) = {math.sqrt(ref['area_n']) * 1e3:.1f} mm")
    print(f"  rho_n (H2 @ ambient) = {rho_n:.4f} kg/m^3, "
          f"rho_amb (air @ {T_AMB:.1f} K) = {rho_amb:.4f} kg/m^3")

    print("\n(A) Mass-conserving equivalent nozzle at reduced velocity")
    print("-" * 70)
    print(f"{'V [m/s]':>10} {'A [m^2]':>10} {'square side [mm]':>18} {'vs. full-bore D_n':>20}")
    print("-" * 70)
    for v in TARGET_VELOCITIES:
        area, side = mass_conserving_nozzle(mdot, rho_n, v)
        print(f"{v:>10.0f} {area:>10.4f} {side * 1e3:>18.1f} {side / math.sqrt(ref['area_n']):>19.2f}x")

    print("\n(B) Virtual downstream source in the real full-velocity jet")
    print("-" * 70)
    print(f"{'V [m/s]':>10} {'x downstream [m]':>18} {'x/D_n':>8} {'jet half-width b(x) [mm]':>26}")
    print("-" * 70)
    for v in TARGET_VELOCITIES:
        x = decay_distance(v_n, d_n, rho_n, rho_amb, v)
        b = jet_half_width(x)
        print(f"{v:>10.0f} {x:>18.2f} {x / d_n:>8.1f} {b * 1e3:>26.1f}")
