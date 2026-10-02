#!/usr/bin/env python3
"""
Rotate the 'up' (+z) 310 mm notional-nozzle holder STL so the nozzle hole
points along -x, keeping the jet emergence point at (0, 0, 7).

Transform: rigid -90 deg rotation about the y-axis through the point (0,0,7).
    (x, y, z) -> (7 - z, y, x + 7)
    exit-cap normal (0,0,1) -> (-1,0,0)   (fires in -x)

Original holder  (bunkering_nozzle_up_310mm_m.stl):
    outer box   x,y in [-0.25, 0.25]   z in [6.5, 7.0]
    opening     +z face at z = 7.0,  inner square +/-0.155
    exit cap    recessed horizontal face at z = 6.69  (normal +z)

Rotated holder (this script's output):
    outer box   x in [0.0, 0.5]   y in [-0.25, 0.25]   z in [6.75, 7.25]
    opening     -x face at x = 0.0,  inner square y in [-0.155,0.155] z in [6.845,7.155]
    exit cap    recessed vertical face at x = 0.31  (normal -x)
    jet emerges into the domain at (0, 0, 7) heading -x
"""
import sys

SRC = "../CAD_geo/bunkering_nozzle_up_310mm_m.stl"
DST = "../CAD_geo/bunkering_nozzle_xneg_310mm_m.stl"


def tf_point(x, y, z):
    return (7.0 - z, y, x + 7.0)


def tf_normal(nx, ny, nz):
    # same rotation applied to the direction vector
    return (-nz, ny, nx)


def fmt(v):
    # trim floating point noise from the exact 0.5 / 0.155 / 6.845 ... values
    return " ".join(f"{round(c, 6):g}" for c in v)


def main():
    out = []
    with open(SRC) as f:
        for line in f:
            s = line.split()
            if len(s) == 5 and s[0] == "facet" and s[1] == "normal":
                n = tf_normal(*(float(c) for c in s[2:5]))
                out.append(f" facet normal {fmt(n)}\n")
            elif len(s) == 4 and s[0] == "vertex":
                p = tf_point(*(float(c) for c in s[1:4]))
                out.append(f"   vertex {fmt(p)}\n")
            else:
                out.append(line)
    with open(DST, "w") as f:
        f.writelines(out)
    print(f"wrote {DST}")


if __name__ == "__main__":
    sys.exit(main())
