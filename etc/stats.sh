#!/usr/bin/env bash
# Usage: ./stats.sh /path/to/csv/dir

TARGET_DIR=${1:-$HOME/gits/moot/optimize}

gawk -F, 'ENDFILE {print NF, FNR, FILENAME}' "$TARGET_DIR"/*/*.csv | \
  sort -k1,1n -k2,2n | \
  column -t
