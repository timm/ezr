#!/usr/bin/env python3 -B
"""cluster.py: k-means++ seeding vs vanilla k-means comparison
(c) 2026 Tim Menzies timm@ieee.org, MIT license"""
import random
from ez    import Data, csv, pick, shuffle, says, main, filename,choice
from kmeans import kmeans
sample = random.sample

def kpp(d:Data, rows=None, k=10, few=256):
  rows = rows or d.rows
  out  = [choice(rows)]
  while len(out) < k:
    tmp  = sample(rows, min(few, len(rows)))
    out += [tmp[pick({i: min(d.distx(r,c)**2 for c in out)
                      for i,r in enumerate(tmp)})]]
  return out

def kmeansp(data, k=10, **kw):
  return kmeans(data, k=k, cents=kpp(data, k=k), **kw)

def eg__data(f:filename):
  "compare vanilla kmeans vs kmeans++ seeding"
  d0   = Data(csv(f))
  seen = {kmeans: [], kmeansp: []}
  for _ in range(20):
    d1 = Data([d0.cols.names] + shuffle(d0.rows)[:50])
    for algo in seen:
      last = 1e32
      for err,_ in algo(d1):
        if abs(last - err) <= 0.01: break
        last = err
      seen[algo] += [int(100*err)]
  for algo, errs in seen.items():
    says(sorted(errs) + [sum(errs)/len(errs), algo.__name__], w=3)

if __name__ == "__main__": main(globals())
