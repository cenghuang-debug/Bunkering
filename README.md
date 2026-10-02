# Bunkering — H2 hose rupture during ship bunkering (OpenFOAM v2406)

Archived OpenFOAM case setups (the project is finished). The scenario is a hydrogen supply hose that ruptures while a ferry is bunkering at a quay:

- The ferry is 130 m long and 12 m above sea level, moored 1 m from the quay. The quay deck is 5 m above sea level.
- The release point is 1 m from the ship side, 7 m above sea level, at the model position (0, 0, 7) m.
- The high-pressure exit is replaced by a notional nozzle (Birch 1987).
- Chemistry and combustion are off: only the dispersion of H2 in air is modelled. Turbulence is k-ε RANS and endTime is 2 s.

Each case directory contains only the **setup**: `0.orig/`, `constant/` (without `polyMesh`), `system/`, `Allrun`/`Allclean` and the Slurm script. Meshes, time directories, logs and post-processing output are not included. To rebuild a case, run `./Allrun` in its directory.

## Cases

| Case | Solver | Nozzle | Jet | Inlet U | Wind | Notes |
|---|---|---|---|---|---|---|
| 01 | rhoReactingBuoyantFoam | 46 mm | +z | 1630 m/s step | – | first attempt, unstable |
| 02 | reactingFoam | 46 mm | +z | 0→100 m/s over 0.01 s | – | BC / scheme debugging |
| 03 | reactingFoam | 46 mm | +z | 0→800 m/s over 0.01 s | – | debugging |
| 04 | reactingFoam | 46 mm | +z | 0→800 m/s over 0.2 s | – | stable reduced-source reference |
| 05 | reactingFoam | 46 mm | +z | 0→1630 m/s over 0.2 s | – | full notional velocity, diverged |
| 06 | reactingFoam | 46 mm | +z | 0→1630 m/s over 0.2 s | – | waveTransmissive outer BCs |
| **07** | rhoReactingBuoyantFoam | 310 mm (10 % rupture) | +z | 0→800 m/s over 0.2 s | none | report matrix |
| 08 | rhoReactingBuoyantFoam | 196 mm | +z | 0→2001.8 m/s over 0.5 s | none | negative result (T below the JANAF limit) |
| **09** | rhoReactingBuoyantFoam | 978 mm (100 % full-bore) | +z | 0→800 m/s over 0.2 s | none | report matrix |
| **10** | rhoReactingBuoyantFoam | 978 mm (100 %) | +z | 0→800 m/s over 0.2 s | SW 7 m/s | report matrix |
| **11** | rhoReactingBuoyantFoam | 310 mm (10 %) | +z | 0→800 m/s over 0.2 s | SW 7 m/s | report matrix |
| 12 | rhoReactingBuoyantFoam | 310 mm (10 %) | −x | 0→800 m/s over 0.2 s | none | horizontal-jet variant of 07 |
| 13 | rhoReactingBuoyantFoam | 978 mm (100 %) | −x | 0→800 m/s over 0.2 s | none | horizontal-jet variant of 09 |

The final results come from cases 07, 09, 10 and 11, which form the {no wind, SW wind} × {10 %, 100 % rupture} matrix. They use a reduced-velocity notional nozzle at 800 m/s. Its area is sized to conserve the mass flow, but not the momentum.

## Supporting material

- `CAD_geo/`: STL geometry for the quay, ship and nozzles, including the rotated −x nozzles.
- `calculations/`: Python scripts for the notional nozzle (Birch), choked flow, the reduced-velocity ramp and the turbulence inlet/initial values.
- `python_script/`: the nozzle STL rotation scripts and the residual checker.
- `paraview_script/`: pvpython rendering scripts for H2 volume fraction slices.
- `create_new_case.sh`, `scp_*.sh`: case-copy and HPC transfer helpers. Before using them, set your own cluster user, host and paths.
