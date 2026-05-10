#!/usr/bin/env python3 -B
"""cluster.py: kmeans, kmeans++, recursive halving."""
from ezr import *

def kmeans(d, rs=None, k=10, n=10, cents=None) -> Datas:
  """Cluster rows into k groups."""
  rs, out = rs or d.rows, []
  cents = cents or choices(rs, k=k)
  for _ in range(n):
    out = [clone(d) for _ in cents]
    for r in rs:
      add(out[min(range(len(cents)),
                  key=lambda j: distx(d, cents[j], r))], r)
    cents = [mids(kid) for kid in out if kid.rows]
  return out

def kpp(d, rs=None, k=10, few=256) -> Rows:
  """k-means++ centroid selection."""
  rs = rs or d.rows
  out = [choice(rs)]
  while len(out) < k:
    t = sample(rs, min(few, len(rs)))
    ws = {i: min(distx(d, t[i], c)**2 for c in out)
          for i in range(len(t))}
    out.append(t[pick(ws)])
  return out

def half(d, rs, few=20) -> tuple:
  """Divide rows by two extreme points."""
  t = sample(rs, min(few, len(rs)))
  gap, east, west = max(
    ((distx(d, r1, r2), r1, r2)
     for r1 in t for r2 in t),
    key=lambda z: z[0])
  proj = lambda r: (
    distx(d, r, east)**2 + gap**2 -
    distx(d, r, west)**2) / (2*gap + 1e-32)
  rs = sorted(rs, key=proj)
  n = len(rs) // 2
  return (rs[:n], rs[n:], east, west, gap, proj(rs[n]))

def rhalf(d, rs=None, k=10, stop=None, few=20) -> Datas:
  """Recursively halve into clusters."""
  rs = rs if rs is not None else d.rows
  stop = stop or 20
  if len(rs) <= 2*stop:
    return [clone(d, rs)]
  l, r, east, west, gap, cut = half(d, rs, few)
  return rhalf(d, l, k, stop, few) + rhalf(d, r, k, stop, few)

def neighbors(d, r1, ds, near=1, fast=False) -> Rows:
  """Find nearest rows or centroid."""
  c = min(ds, key=lambda c: distx(d, r1, mids(c)))
  return ([mids(c)] if fast
          else sorted(c.rows, key=lambda r2: distx(d, r1, r2))[:near])

def cli(argv):
  """Cluster FILE via kmeans++ and print one row per cluster."""
  if not argv: print("usage: ezr cluster FILE [--k=10]"); return
  d = Data(csv(argv[0]))
  cents = kpp(d, k=10)
  ds = kmeans(d, k=10, cents=cents)
  for c in ds:
    print(f"  n={len(c.rows):>4}  centroid={o(mids(c))}")

if __name__ == "__main__":
  cli(sys.argv[1:])
