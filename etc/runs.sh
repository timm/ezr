#!/usr/bin/env bash
# Usage: ./etc/runs.sh [N] [JOBS]
# Saturated parallel pool: keeps JOBS workers busy via `wait -n`.

FILES=($(find "$HOME/gits/moot/optimize" -name "*.csv" -type f))
NF=${#FILES[@]}
JOBS=${2:-10}

for i in $(seq 1 ${1:-100000}); do
  while (( $(jobs -rp | wc -l) >= JOBS )); do wait -n; done
  F=${FILES[$(( RANDOM % NF ))]}
  B=$(( RANDOM % 141 + 10 ))
  C=$(( RANDOM % 10 + 1 ))
  ( out=$(python3 -B cli.py --learn.budget=$B --learn.check=$C acquire "$F" | tr -d '\n')
    printf '%s :file %s\n' "$out" "$(basename "$F")"
  ) &
done
wait
