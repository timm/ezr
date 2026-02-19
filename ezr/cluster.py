#!/usr/bin/env python3 -B
import sys, random
from ez1 import Data, choice, csv, distx, furthest, ok, pick, shuffle
from kmeans import kmeans

def kpp(data, rows=None, k=20, few=256):
  rows = rows or data.rows
  out  = [choice(rows)]
  while len(out) < k:
    tmp  = random.sample(rows, min(few, len(rows)))
    out += [tmp[pick({i: min(distx(data,r,c)**2 for c in out)
                      for i,r in enumerate(tmp)})]]
  return out

def kmeans_kpp(data, k=20, **kw):
  return kmeans(data, k=k, cents=kpp(data, k=k), **kw)

if __name__ == "__main__":
  random.seed(float(sys.argv[1]))
  d0   = Data(csv(sys.argv[2]))
  seen = {kmeans: [], kmeans_kpp: []} 
  for _ in range(20):
    d1 = Data([d0.cols.names] + shuffle(d0.rows)[:50])
    for algo in seen:
      last = 1e32
      for err,_ in algo(d1):
        if abs(last-err) <= 0.01: break
        last = err
      seen[algo] += [err]
  print(f"\n{'algo':<14} {'mean':>6}  sorted runs")
  fmt = lambda e: f"{e:.2f}".lstrip("0")
  for algo,errs in seen.items():
     print(f"{algo.__name__:<14} {fmt(sum(errs)/len(errs)):>5}",
          " ".join(fmt(e) for e in sorted(errs)))
