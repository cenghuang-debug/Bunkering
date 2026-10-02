"""Generate the nozzle housing STL (bunkering-nozzle_up_m.stl) for a resized
notional nozzle, and print the matching system/topoSetDict box.

Context: Bunkering_07's original nozzle was 44mm x 44mm (meshed size; see
Bunkering_04/06/07 topoSetDict which targeted 46mm) at a recessed exit
z=6.95m, inside a 200mm x 200mm housing (z=6.8-7.0m). This script rebuilds
that housing STL as a plain flat-topped box (no recess) sized to the
reduced-velocity-ramp 10%-area / 800 m/s notional nozzle side length
(309.3 mm, see notional_nozzle_reduced_velocity_plan.md), with its top cap
flush at z=7.0m so the release height matches the documented 7 m above sea
level exactly (previously 6.95m, a 50mm discrepancy).

The "nozzle" and "nozzle_holder_wall" patches are not geometric holes in
this STL -- topoSetDict::boxToFace later subsets faces of the flat top cap
by location into the two patches (same convention as the original
geometry). So this script only needs to emit a closed box: 4 side walls +
bottom cap + a single flat (unsplit) top cap.

Housing footprint margin around the nozzle: kept at the same *absolute*
margin as the original design (100mm outer half-width - 22mm nozzle
half-width = 78mm), rounded to 80mm here for a clean number.
"""

NOZZLE_SIDE = 309.3e-3       # m, target square nozzle side (800 m/s, 10% area)
HOUSING_MARGIN = 80e-3        # m, per-side margin around the nozzle opening
Z_BASE = 6.8                  # m, housing bottom (unchanged from original)
Z_TOP = 7.0                   # m, housing top / nozzle exit -- release height

NOZZLE_HW = NOZZLE_SIDE / 2
HOUSING_HW = NOZZLE_HW + HOUSING_MARGIN

STL_PATH = "../Bunkering_07/constant/triSurface/bunkering-nozzle_up_m.stl"

# topoSetDict box: thin z-slab straddling Z_TOP (same +/-1.5mm convention as
# the original box, which was centred +/-1.5mm on its z=6950mm target)
TOPOSET_ZLO = Z_TOP - 1.5e-3
TOPOSET_ZHI = Z_TOP + 1.5e-3


def quad(v0, v1, v2, v3, normal):
    """Two triangles, CCW when viewed from outside along `normal`."""
    return [(normal, (v0, v1, v2)), (normal, (v0, v2, v3))]


def build_box(hw, zlo, zhi):
    tris = []
    # bottom cap, normal -z
    tris += quad((-hw, hw, zlo), (hw, hw, zlo), (hw, -hw, zlo), (-hw, -hw, zlo), (0, 0, -1))
    # top cap, normal +z
    tris += quad((-hw, -hw, zhi), (hw, -hw, zhi), (hw, hw, zhi), (-hw, hw, zhi), (0, 0, 1))
    # +x wall
    tris += quad((hw, -hw, zlo), (hw, hw, zlo), (hw, hw, zhi), (hw, -hw, zhi), (1, 0, 0))
    # -x wall
    tris += quad((-hw, hw, zlo), (-hw, -hw, zlo), (-hw, -hw, zhi), (-hw, hw, zhi), (-1, 0, 0))
    # +y wall
    tris += quad((hw, hw, zlo), (-hw, hw, zlo), (-hw, hw, zhi), (hw, hw, zhi), (0, 1, 0))
    # -y wall
    tris += quad((-hw, -hw, zlo), (hw, -hw, zlo), (hw, -hw, zhi), (-hw, -hw, zhi), (0, -1, 0))
    return tris


def write_stl(path, tris, solid_name="Mesh"):
    with open(path, "w") as f:
        f.write(f"solid {solid_name}\n")
        for normal, (v0, v1, v2) in tris:
            f.write(f" facet normal {normal[0]:g} {normal[1]:g} {normal[2]:g}\n")
            f.write("  outer loop\n")
            for v in (v0, v1, v2):
                f.write(f"   vertex {v[0]:.6f} {v[1]:.6f} {v[2]:.6f}\n")
            f.write("  endloop\n")
            f.write(" endfacet\n")
        f.write(f"endsolid {solid_name}\n")


if __name__ == "__main__":
    tris = build_box(HOUSING_HW, Z_BASE, Z_TOP)
    write_stl(STL_PATH, tris)

    print(f"Nozzle side       = {NOZZLE_SIDE*1e3:.1f} mm (half-width {NOZZLE_HW*1e3:.2f} mm)")
    print(f"Housing footprint = {2*HOUSING_HW*1e3:.1f} mm (half-width {HOUSING_HW*1e3:.2f} mm)")
    print(f"Housing z         = {Z_BASE} - {Z_TOP} m")
    print(f"Wrote {len(tris)} triangles to {STL_PATH}")
    print()
    print("system/topoSetDict box for 'nozzle' faceSet:")
    print(f"        box ({-NOZZLE_HW:.5f} {-NOZZLE_HW:.5f} {TOPOSET_ZLO:.5f})"
          f"({NOZZLE_HW:.5f} {NOZZLE_HW:.5f} {TOPOSET_ZHI:.5f});")
