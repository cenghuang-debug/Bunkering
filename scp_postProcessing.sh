#!/bin/bash

# Check if case number is provided
if [ $# -ne 1 ]; then
    echo "Usage: $0 <case_number>"
    exit 1
fi

CASE_NUM=$1
BASE_DIR="Bunkering_${CASE_NUM}"
REMOTE="<cluster-host>:~/<your-project-dir>/OpenFOAM/<user>-v2406/run/Bunkering/${BASE_DIR}/postProcessing"

# Download using scp
scp -r "$REMOTE" "$BASE_DIR"
