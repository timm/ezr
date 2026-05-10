#!/usr/bin/env python3 -B
"""classify.py: incremental Naive Bayes (test then train)."""
from ezr import *

def _dinc(k1, k2, b4=None):
  """Increment nested dict counter."""
  b4 = b4 or {}; b4[k1] = b4.get(k1) or {}
  b4[k1][k2] = b4[k1].get(k2, 0) + 1
  return b4

def classify(src, wait=10):
  """Test then train: classify before update."""
  src = iter(src)
  h, cf, all = {}, None, Data([next(src)])
  for n, row in enumerate(src):
    want = row[all.cols.klass.at]
    if n >= wait:
      cf = _dinc(want,
                 max(h, key=lambda kl: likes(h[kl], row, len(all.rows), len(h))),
                 cf)
    if want not in h: h[want] = clone(all)
    add(all, add(h[want], row))
  return cf

def cli(argv):
  """Run incremental NB on FILE; print final confusion matrix raw counts."""
  if not argv: print("usage: ezr classify FILE [--key=val ...]"); return
  cf = classify(csv(argv[0])) or {}
  for want in sorted(cf):
    for got in sorted(cf[want]):
      print(f"  want={want:<24} got={got:<24} n={cf[want][got]}")

if __name__ == "__main__":
  cli(sys.argv[1:])
