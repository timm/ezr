#!/usr/bin/env bash
# Usage: ./runs.sh

for i in $(seq 1 100); do
  C=$(( RANDOM % 4 + 3 ))
  B=$(( RANDOM % 76 + 25 ))
  
  # Note: This explicitly calls 'make', so it relies on the Makefile
  # being present in the current working directory.
  num=$(make -B C=$C B=$B ~/tmp/ez_test.log | grep OUT)
  
  echo "$C $B $num"
done
