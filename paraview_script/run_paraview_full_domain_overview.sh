#!/bin/bash
# Run render_full_domain_overview.py (H2 vol concentration, x-z nozzle-plane
# slice at y=0, framed to the FULL computational domain) for one or more
# Bunkering cases.
#
# Usage:
#   bash run_paraview_full_domain_overview.sh <case_num> [<case_num> ...] [--debug] [--cmax VALUE]
#   e.g.:
#   bash run_paraview_full_domain_overview.sh 10
#   bash run_paraview_full_domain_overview.sh 10 11 --debug
#   bash run_paraview_full_domain_overview.sh 10 --cmax 1.0

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PV_SCRIPT="${SCRIPT_DIR}/render_full_domain_overview.py"

CASES=()
EXTRA_ARGS=()
for arg in "$@"; do
    if [[ "$arg" =~ ^[0-9]+$ ]]; then
        CASES+=("$arg")
    else
        EXTRA_ARGS+=("$arg")
    fi
done

if [[ ${#CASES[@]} -eq 0 ]]; then
    echo "Usage: $0 <case_num> [<case_num> ...] [--debug] [--cmax VALUE]"
    exit 1
fi

for CASE in "${CASES[@]}"; do
    CASE_NAME="Bunkering_$(printf '%02d' "$CASE")"
    echo "========================================"
    echo "Case: ${CASE_NAME}"
    echo "========================================"
    PYTHONPATH=/usr/lib/python3/dist-packages \
    LIBGL_ALWAYS_SOFTWARE=1 MESA_GL_VERSION_OVERRIDE=4.5 \
    pvpython "${PV_SCRIPT}" "${CASE_NAME}" "${EXTRA_ARGS[@]}"
    if [[ $? -ne 0 ]]; then
        echo "[ERROR] pvpython failed for ${CASE_NAME}"
    else
        echo "[OK] Done: ${CASE_NAME}"
    fi
    echo ""
done

echo "All done."
