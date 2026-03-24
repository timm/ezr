#!/usr/bin/env bash
# Usage: ./run_tests.sh <output_file> <python_script> "<args>" "<files_glob>"

OUT_FILE=$1
SCRIPT=$2
ARGS=$3
# Default to the optimize csv files if no 4th argument is provided
FILES=${4:-$HOME/gits/moot/optimize/*/*.csv}

# Create the output directory automatically
if [ "$OUT_FILE" != "/dev/null" ]; then
  mkdir -p "$(dirname "$OUT_FILE")"
fi

# Run the parallel xargs pipeline
time ls -r $FILES | \
  xargs -P 24 -n 1 -I{} bash -c "python3 -B $SCRIPT $ARGS \"{}\"" | \
  tee "$OUT_FILE"
