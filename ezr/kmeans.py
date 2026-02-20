#!/usr/bin/env python3 -B 
import sys, random
from ez2 import Data, add, csv, distx, align,say,mids
choice=random.choice

def kmeans(d:Data, rows=None, k=10, n=10, cents=None):
  rows  = rows or d.rows
  cents = cents or random.choices(rows, k=k)
  for _ in range(n):
    kids = [Data([d.cols.names]) for _ in cents]
    err  = 0
    for r in rows:
      i    = min(range(len(cents)), key=lambda j: distx(d,cents[j],r))
      err += distx(d, cents[i], r)
      add(kids[i], r)
    yield err/len(rows), kids
    cents = [random.choice(c.rows) for c in kids if c.rows]

if __name__ == "__main__":
  random.seed(float(sys.argv[1]))
  d = Data(csv(sys.argv[2]))
  last = 1e32
  for err, kids in kmeans(d):
    print(f"err={err:.3f}")
    if abs(last - err) <= 0.01: break
    last = err
  align([mids(k) for k in kids])
