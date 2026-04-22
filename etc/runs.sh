#!/usr/bin/env bash
# Usage: ./etc/runs.sh [N] [JOBS]
# Random acquire runs. Parallel via temp files.

FILES=($(find "$HOME/gits/moot/optimize" -name "*.csv" -type f))
N=${#FILES[@]}
TMP=$(mktemp -d)
echo "$TMP" >&2
trap "cat $TMP/*; rm -rf $TMP" EXIT

for i in $(seq 1 ${1:-10000}); do
  F=${FILES[$(( RANDOM % N ))]}
  B=$(( RANDOM % 141 + 10 ))
  C=$(( RANDOM % 10 + 1 ))
  ( printf ":budget %d :check %d " "$B" "$C"
    python3 -B ezeg.py --learn.budget $B --learn.check $C --acquire "$F" | tr -d '\n'
    printf " :file %s\n" "$(basename "$F")"
  ) > "$TMP/$(printf '%05d' $i)" &
  (( i % ${2:-10} == 0 )) && wait
done
wait
# /var/folders/78/8f0j3pln705clvktr3m1w8jc0000gp/T/tmp.01hwI6sdlJ
