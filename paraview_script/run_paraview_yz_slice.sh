#!/bin/bash
# Run render_yz_slice.py for one or more Bunkering cases.
#
# Usage:
#   bash run_paraview_yz_slice.sh <case_num> [<case_num> ...] [--x0 0.0] [--debug] [--cmax VALUE] [--zmax VALUE]
#   e.g.:
#   bash run_paraview_yz_slice.sh 07
#   bash run_paraview_yz_slice.sh 07 09 --debug
#   bash run_paraview_yz_slice.sh 09 --x0 0.0 --cmax 1.0

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PV_SCRIPT="${SCRIPT_DIR}/render_yz_slice.py"

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
    echo "Usage: $0 <case_num> [<case_num> ...] [--x0 0.0] [--debug] [--cmax VALUE] [--zmax VALUE]"
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
