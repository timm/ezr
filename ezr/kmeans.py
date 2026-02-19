#!/usr/bin/env python3 -B 
#!/usr/bin/env python3 -B
import sys, random
from ez2 import Data, adds, csv, distx, align,say
choice=random.choice

def kmeans(data, rows=None, k=20, n=10, cents=None):
  rows  = rows or data.rows
  cents = cents or random.choices(rows, k=k)
  for _ in range(n):
    kids = [Data([data.cols.names]) for _ in cents]
    err  = 0
    for r in rows:
      i     = min(range(len(cents)), key=lambda j: distx(data,cents[j],r))
      err  += distx(data, cents[i], r)
      adds(kids[i], r)
    yield err/len(rows), kids
    cents = [random.choice(c.rows) for c in kids if c.rows]

if __name__ == "__main__":
  random.seed(float(sys.argv[1]))
  data = Data(csv(sys.argv[2]))
  last = 1e32
  for err, kids in kmeans(data, k=5, n=20):
    print(f"err={err:.3f}")
    if abs(last - err) <= 0.01: break
    last = err
  align([k.mids for k in kids])
