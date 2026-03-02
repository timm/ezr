#!/usr/bin/env python3 -B 
import sys
from ez import Data, csv, align,say, choice, eg_s, main, filename
from random import choices

def kmeans(d:Data, rows=None, k=10, n=10, cents=None):
  rows  = rows or d.rows
  cents = cents or choices(rows, k=k)
  for _ in range(n):
    kids = [Data([d.cols.names]) for _ in cents]
    err  = 0
    for r in rows:
      i    = min(range(len(cents)), key=lambda j: d.distx(cents[j],r))
      err += d.distx(cents[i], r)
      kids[i].add(r)
    yield err/len(rows), kids
    cents = [choice(c.rows) for c in kids if c.rows]

def eg__data(s:filename):
  d = Data(csv(s))
  last = 1e32
  for err, kids in kmeans(d):
    print(f"err={err:.3f}")
    if abs(last - err) <= 0.01: break
    last = err
  align([k.mid() for k in kids])

if __name__ == "__main__": main(globals())
 
