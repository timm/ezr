#!/usr/bin/env python3 -B
"""frugal1.py: one dataset's row of etc/frugal56.tsv.

`attic.py --fft` prints a table per file; this reads the d=5 line
and the tree0 line out of it, so `make frugal` can fan the whole
of moot/regression over the cores and sort the rows at the end.

  ./etc/frugal1.py FILE.csv     # one tab-separated row, or nothing
"""
import os, re, subprocess, sys
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D5   = re.compile(r"\s*5\s+(\d+) \|\s+([\d.]+)\s+[\d.]+ \|\s+([\d.]+)")
T0   = re.compile(r"tree0, every leaf \|\s+([\d.]+)\s+([\d.]+)")

def row(f):
  "The (variants, frugal train, frugal test, tree0 train, test) of F."
  try:
    out = subprocess.run([sys.executable, f"{HERE}/attic.py", "-File", f,
                          "--fft"], capture_output=True, text=True,
                         timeout=900).stdout
  except Exception:                  # a file this rig cannot read is
    return None                      # not a result, it is a skip
  a = b = None
  for ln in out.splitlines():
    if m := D5.match(ln): a = m.groups()
    if m := T0.search(ln): b = m.groups()
  return (os.path.basename(f)[:-4], *a, *b) if a and b else None

if __name__ == "__main__":
  for path in sys.argv[1:]:
    one = row(path)
    if one: print("\t".join(one))
