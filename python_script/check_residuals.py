"""
check_residuals.py — Plot solver residuals (initial) vs time for a given Bunkering case.

Adapted from the H2Vent project (python_script/check_residuals.py)
for the Bunkering directory layout (Bunkering_<NN>/ at the run root, no
volume/nozzle subfolder naming).

Stitches postProcessing/myResiduals subfolders across restarts automatically.
Auto-detects available fields (and whether the pressure field is p or p_rgh,
since older cases use reactingFoam and newer ones rhoReactingBuoyantFoam) by
reading the solverInfo.dat header directly.

Reads system/fvSolution residualControl tolerances; annotates each field's
line with its tolerance (dotted reference line, same colour) and prints a
per-field convergence summary table.

Usage:
    python3 check_residuals.py <case_number>
    e.g.: python3 check_residuals.py 7
          python3 check_residuals.py 06
"""

import os
import re
import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BASE_DIR = os.path.join(os.path.dirname(__file__), "..")

GOLDEN_WIDTH, GOLDEN_HEIGHT = 9.0, 5.5
LW = 2.2

FIELD_COLORS = {
    "p_rgh": "#ff7f00", "p": "#ff7f00", "U": "#377eb8",
    "H2": "#4daf4a", "O2": "#e41a1c", "H2O": "#377eb8", "N2": "#ffff33",
    "k": "#984ea3", "epsilon": "#a65628", "omega": "#f781bf", "h": "#999999",
}


def apply_style():
    plt.rcParams.update({
        "font.size": 12,
        "axes.grid": True,
        "grid.alpha": 0.3,
        "figure.autolayout": True,
    })


def save_figure(fig, out_base):
    fig.savefig(out_base + ".png", dpi=200)
    fig.savefig(out_base + ".pdf")
    print(f"Saved: {out_base}.png / .pdf")


def find_case_dir(case_num):
    for name in (f"Bunkering_{case_num:02d}", f"Bunkering_{case_num}"):
        d = os.path.join(BASE_DIR, name)
        if os.path.isdir(d):
            return d
    return None


def load_residuals(case_dir):
    """Stitch all myResiduals subfolders; return (header_list, float_array) sorted by time."""
    res_base = os.path.join(case_dir, "postProcessing", "myResiduals")
    if not os.path.isdir(res_base):
        print(f"ERROR: postProcessing/myResiduals not found in {case_dir}")
        print("Hint: run ./scp_postProcessing.sh <case_num> first to pull it from Dardel.")
        sys.exit(1)

    segments = sorted(os.listdir(res_base), key=lambda x: float(x))
    header = None
    blocks = []

    for seg in segments:
        fpath = os.path.join(res_base, seg, "solverInfo.dat")
        if not os.path.isfile(fpath):
            continue
        rows = []
        with open(fpath) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                if line.startswith("#"):
                    if header is None and "Time" in line:
                        header = line.lstrip("# ").split()
                    continue
                rows.append(line.split())
        if rows:
            blocks.append(rows)

    if not blocks or header is None:
        print("ERROR: no data or header found in myResiduals")
        sys.exit(1)

    all_rows = [r for block in blocks for r in block]
    n_cols = len(header)
    all_rows = [r for r in all_rows if len(r) == n_cols]

    arr = np.array(all_rows)
    times = arr[:, 0].astype(float)
    order = np.argsort(times)
    return header, arr[order]


def get_col(header, arr, name):
    if name in header:
        return arr[:, header.index(name)].astype(float)
    return None


def parse_fvsolution_tolerances(case_dir):
    """Return {field_pattern: tolerance} from PIMPLE residualControl in system/fvSolution."""
    fvsol_path = os.path.join(case_dir, "system", "fvSolution")
    if not os.path.isfile(fvsol_path):
        return {}
    with open(fvsol_path) as f:
        content = f.read()

    rc_match = re.search(r'residualControl\s*\{', content)
    if not rc_match:
        return {}

    start = rc_match.end() - 1
    depth, end = 0, start
    for i, ch in enumerate(content[start:], start):
        if ch == '{':
            depth += 1
        elif ch == '}':
            depth -= 1
            if depth == 0:
                end = i
                break

    rc_block = content[start + 1:end]
    tolerances = {}
    for m in re.finditer(r'"?([^"\s{]+)"?\s*\{([^}]*)\}', rc_block, re.DOTALL):
        field_name = m.group(1)
        tol_m = re.search(r'tolerance\s+([\d.e+\-]+)', m.group(2))
        if tol_m:
            tolerances[field_name] = float(tol_m.group(1))
    return tolerances


def lookup_tolerance(tolerances, rc_field):
    """Exact match first, then treat dict keys as regex patterns (e.g. '(H2|O2|H2O|N2)')."""
    if rc_field is None or not tolerances:
        return None
    if rc_field in tolerances:
        return tolerances[rc_field]
    for pattern, tol in tolerances.items():
        try:
            if re.fullmatch(pattern, rc_field):
                return tol
        except re.error:
            pass
    return None


def build_field_specs(header):
    """Auto-detect which fields are present in the solverInfo header and build
    (label, [columns to max-reduce], color, residualControl field) specs."""
    specs = []

    # Pressure field: rhoReactingBuoyantFoam -> p_rgh, reactingFoam -> p
    if "p_rgh_final" in header:
        specs.append(("p_rgh", ["p_rgh_final"], FIELD_COLORS["p_rgh"], "p_rgh"))
    elif "p_final" in header:
        specs.append(("p", ["p_final"], FIELD_COLORS["p"], "p"))

    if "Ux_initial" in header:
        specs.append(("U", ["Ux_initial", "Uy_initial", "Uz_initial"], FIELD_COLORS["U"], "U"))

    for field in ("H2", "O2", "H2O", "N2", "k", "epsilon", "omega", "h"):
        col = f"{field}_initial"
        if col in header:
            specs.append((field, [col], FIELD_COLORS.get(field, "#333333"), field))

    return specs


def main():
    case_num = int(sys.argv[1]) if len(sys.argv) > 1 else 7

    case_dir = find_case_dir(case_num)
    if case_dir is None:
        print(f"ERROR: no case directory found for case {case_num}")
        sys.exit(1)

    print(f"Case {case_num}: {case_dir}")

    header, data = load_residuals(case_dir)
    t = data[:, 0].astype(float)
    tolerances = parse_fvsolution_tolerances(case_dir)

    if tolerances:
        print("residualControl tolerances read from system/fvSolution:")
        for field, tol in tolerances.items():
            print(f"  {field}: {tol:.1e}")
    else:
        print("WARNING: could not parse residualControl from system/fvSolution")

    field_specs = build_field_specs(header)
    if not field_specs:
        print("ERROR: no recognised residual columns found in solverInfo.dat header")
        sys.exit(1)

    apply_style()
    fig, ax = plt.subplots(figsize=(GOLDEN_WIDTH, GOLDEN_HEIGHT))

    plotted_fields = []
    for label, candidates, color, rc_field in field_specs:
        cols = [get_col(header, data, c) for c in candidates if c in header]
        if not cols:
            continue
        values = np.maximum.reduce(cols) if len(cols) > 1 else cols[0]
        tol = lookup_tolerance(tolerances, rc_field)
        tol_str = f"{tol:.0e}" if tol is not None else "—"
        ax.semilogy(t, values, label=f"{label}  [tol={tol_str}]", color=color, linewidth=LW - 1)
        if tol is not None:
            ax.axhline(tol, color=color, linestyle=":", linewidth=1.4, alpha=0.75)
        plotted_fields.append((label, rc_field, color, tol, values))

    case_label = os.path.basename(case_dir)
    ax.set_xlabel("Time [s]")
    ax.set_ylabel("Residual")
    ax.set_title(f"{case_label} — Solver residuals\n(dotted lines = PIMPLE residualControl tolerance)")
    ax.legend(loc="upper right", fontsize=10, ncol=2)
    ax.set_xlim(left=0)

    # ── Convergence summary table ────────────────────────────────────────────
    last_t = t[-1]
    n_avg = min(50, len(t))
    pressure_label = field_specs[0][0] if field_specs and field_specs[0][0] in ("p", "p_rgh") else None
    print(f"\nConvergence summary  (last {n_avg}-step average,  t_end = {last_t:.4g} s):")
    print(f"  {'Field':<10} {'RC Tolerance':>14} {'Avg Residual':>14} {'Status':>10}")
    print(f"  {'-'*10} {'-'*14} {'-'*14} {'-'*10}")
    for label, rc_field, color, tol, values in plotted_fields:
        avg_val = float(np.mean(values[-n_avg:]))
        if label == pressure_label:
            # <field>_final (plotted) is the linear-solver exit residual (~1e-7).
            # PIMPLE residualControl checks the Initial residual of the first
            # pressure solve per outer iteration — not stored in solverInfo.dat.
            print(f"  {label:<10} {tol:>14.1e} {avg_val:>14.3e} {'(see note)':>10}")
        elif tol is not None:
            status = "CONVERGED" if avg_val <= tol else "NOT CONV"
            print(f"  {label:<10} {tol:>14.1e} {avg_val:>14.3e} {status:>10}")
        else:
            print(f"  {label:<10} {'(no RC tol)':>14} {avg_val:>14.3e} {'N/A':>10}")
    print("  Notes:")
    print("  * solverInfo.dat records residuals from the FIRST outer iteration only.")
    print("    PIMPLE residualControl checks residuals after the LAST outer iteration,")
    print("    by which point they are much lower — 'NOT CONV' here does not mean the")
    print("    simulation is diverging; it means outer-iter-1 residuals exceed tolerance.")
    if pressure_label:
        print(f"  * {pressure_label}: solverInfo stores {pressure_label}_final (linear-solver exit")
        print("    residual, typically ~1e-7). PIMPLE checks the Initial residual of the")
        print("    first pressure solve per outer iteration; not in solverInfo.dat —")
        print("    parse the solver log directly to verify PIMPLE-level convergence.")

    out = os.path.join(os.path.dirname(__file__), f"residuals_case{case_num:02d}")
    save_figure(fig, out)
    plt.close(fig)


if __name__ == "__main__":
    main()
