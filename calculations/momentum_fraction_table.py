"""Mass-conserving reduced-velocity nozzle sizing (Method A) at a given
partial leak area, with the momentum and kinetic-energy flux fraction
retained relative to the rigorous Birch 1987 notional nozzle.

For a fixed mass flow rate mdot (set by the real orifice area and the
500 bar source state), enlarging the nozzle to hit a target velocity V
below the Birch notional velocity V_n conserves mass by construction,
but not momentum or kinetic energy:

    J(V)  / J_birch  = V / V_n          (momentum flux, J = mdot*V)
    Ek(V) / Ek_birch = (V / V_n)^2      (kinetic energy flux, Ek = 1/2 mdot V^2)

Both fractions are independent of leak area (mdot cancels), so they
apply equally at 100%, 10%, or any other open-area fraction.
"""

from notional_nozzle_birch import notional_nozzle
from hydrogen_properties import R_H2, P_ATM

P0 = 500e5           # storage pressure, 500 bar [Pa]
T0 = 12 + 273.15      # storage gas temperature, 12 degC [K]
T_AMB = 20 + 273.15   # ambient temperature, 20 degC [K]
D = 50.8e-3           # hose inner diameter [m]

AREA_FRACTION = 0.10                        # 10% open area (partial leak)
TARGET_VELOCITIES = [800.0, 600.0, 400.0, 200.0]  # m/s


def mass_conserving_table(area_fraction, velocities):
    ref = notional_nozzle(P0, T0, D, T_AMB, area_fraction=area_fraction)
    mdot = ref["mdot"]
    v_n = ref["v_n"]
    rho_n = P_ATM / (R_H2 * T_AMB)
    j_birch = mdot * v_n

    rows = []
    for v in velocities:
        area = mdot / (rho_n * v)
        side = area ** 0.5
        j = mdot * v
        j_frac = j / j_birch
        ek_frac = (v / v_n) ** 2
        rows.append({
            "v": v, "area": area, "side": side,
            "j": j, "j_frac": j_frac, "ek_frac": ek_frac,
        })
    return ref, rows


if __name__ == "__main__":
    ref, rows = mass_conserving_table(AREA_FRACTION, TARGET_VELOCITIES)

    print(f"{AREA_FRACTION * 100:.0f}% area release -- 500 bar H2, 50.8 mm hose, "
          f"T_gas = 12 degC, T_amb = 20 degC")
    print(f"  mdot = {ref['mdot']:.3f} kg/s, V_n (Birch) = {ref['v_n']:.1f} m/s, "
          f"J_birch = {ref['mdot'] * ref['v_n']:.1f} N")
    print()
    print(f"{'V [m/s]':>8} {'square side [mm]':>17} {'J [N]':>10} "
          f"{'J fraction':>11} {'Ek fraction':>12}")
    print("-" * 62)
    for row in rows:
        print(f"{row['v']:>8.0f} {row['side'] * 1e3:>17.1f} {row['j']:>10.1f} "
              f"{row['j_frac'] * 100:>10.1f}% {row['ek_frac'] * 100:>11.1f}%")
