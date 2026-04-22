#!/usr/bin/env bash
# Usage: ./etc/runs.sh
# 1000 random runs: random file, random budget (10..150), random check (1..10)

FILES=($(find "$HOME/gits/moot/optimize" -name "*.csv" -type f))
N=${#FILES[@]}

for i in $(seq 1 10000); do
  F=${FILES[$(( RANDOM % N ))]}
  B=$(( RANDOM % 141 + 10 ))
  C=$(( RANDOM % 10 + 1 ))
  echo -n ":i $i :budget $B :check $C "
  echo -n "$(python3 -B ezeg.py --learn.budget $B --learn.check $C --acquire "$F")"
  echo " :file $(basename $F)"
done
