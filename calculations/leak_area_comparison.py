"""Compare full-bore vs. partial-area hose failure at 500 bar.

A 10% open area models a partial rupture / crack rather than a full
guillotine break of the 50.8 mm hose. V_n from Birch 1987 depends only
on P0, T0 and gamma (not on area), so it is identical in both cases;
mass flow rate and notional nozzle size scale linearly / as sqrt(area)
with the open-area fraction.
"""

from notional_nozzle_birch import notional_nozzle

P0 = 500e5          # storage pressure, 500 bar [Pa]
T0 = 12 + 273.15     # storage gas temperature, 12 degC [K]
T_AMB = 20 + 273.15  # ambient temperature, 20 degC [K]
D = 50.8e-3          # hose inner diameter [m]

AREA_FRACTIONS = [1.0, 0.10]

print("500 bar H2 release, 50.8 mm hose, T_gas = 12 degC, T_amb = 20 degC")
print("=" * 90)
print(f"{'Open area':>10} {'A0 [mm^2]':>10} {'V_throat [m/s]':>15} {'mdot [kg/s]':>12} "
      f"{'V_n [m/s]':>10} {'A_n [mm^2]':>12} {'square side [mm]':>18}")
print("-" * 90)

for frac in AREA_FRACTIONS:
    state = notional_nozzle(P0, T0, D, T_AMB, area_fraction=frac)
    square_side = state["area_n"] ** 0.5
    print(f"{frac * 100:>9.0f}% {state['area'] * 1e6:>10.1f} {state['v_star']:>15.1f} "
          f"{state['mdot']:>12.3f} {state['v_n']:>10.1f} {state['area_n'] * 1e6:>12.1f} "
          f"{square_side * 1e3:>18.1f}")

print("=" * 90)
print("\nNote: V_n is area-independent (throat state only). mdot scales linearly with")
print("open area; A_n scales linearly with mdot at fixed V_n, so D_n scales as sqrt(area).")
