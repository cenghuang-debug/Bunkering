#!/bin/bash

# Usage: ./create_new_case.sh <old_number> <new_number>
# Example: ./create_new_case.sh 08 09

if [ $# -ne 2 ]; then
    echo "Error: Please provide old and new case numbers."
    echo "Usage: $0 <old_number> <new_number>"
    echo "Example: $0 08 09"
    exit 1
fi

OLD=$1
NEW=$2

BASE_NAME="Bunkering"
OLD_CASE="${BASE_NAME}_${OLD}"
NEW_CASE="${BASE_NAME}_${NEW}"

# Check if we're in the correct directory
if [[ ! "$(basename $(pwd))" == "Bunkering" ]]; then
    echo "Warning: This script should be run from inside the H2Vent directory."
    echo "Current directory: $(pwd)"
fi

echo "Creating new case: $NEW_CASE (from $OLD_CASE)"

# Create and enter the new case directory
mkdir -p "$NEW_CASE" || { echo "Failed to create $NEW_CASE"; exit 1; }
cd "$NEW_CASE" || { echo "Failed to cd into $NEW_CASE"; exit 1; }

# Copy the required folders and files from the old case
cp -r "../${OLD_CASE}/0.orig" .          || echo "Warning: 0.orig not copied"
cp -r "../${OLD_CASE}/constant" .        || echo "Warning: constant not copied"
cp -r "../${OLD_CASE}/system" .          || echo "Warning: system not copied"
cp -r "../${OLD_CASE}/All"* . 2>/dev/null || echo "Warning: All* files not copied"
cp -r "../${OLD_CASE}/open.foam" . 2>/dev/null || echo "Warning: open.foam file not copied"

# <<< CHANGED: Copy the monitor script instead of test script >>>
cp -r "../${OLD_CASE}/sbatch_OF_dardel_monitor" . || { echo "Error: sbatch_OF_dardel_monitor not found in $OLD_CASE!"; exit 1; }

# <<< CHANGED: Update the new script (replace old number with new) >>>
sed -i "s/_${OLD}/_${NEW}/g" sbatch_OF_dardel_monitor

echo "Success! New case $NEW_CASE created and ready."
echo "You are now in: $(pwd)"
