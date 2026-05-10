#!/usr/bin/env bash
# Usage: ./stats.sh /path/to/csv/dir
TARGET_DIR=${1:-$HOME/gits/moot/optimize}
gawk -F, '
  FNR==1 {
    nx=0; ny=0
    for(i=1;i<=NF;i++) {
      if      ($i ~ /[+-]$/) ny++
      else if ($i ~ /X$/)    continue
      else                   nx++
    }
  }
  ENDFILE { print nx, ny, FNR-1, FILENAME }
' "$TARGET_DIR"/*/*.csv | \
  sort -k1,1n -k2,2n -k3,3n | \
  column -t

