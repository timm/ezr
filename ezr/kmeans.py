#!/usr/bin/env -B python3
from ez1 import *

def distKpp(data, rows=None, k=20, few=256):
  "Return key centroids usually separated by distance D^2."
  if k==0: return rows
  rows = rows or data.rows
  out = [rows[0]]
  while len(out) < k:
    tmp = random.sample(rows, few)
    ws  = [min(distx(data, r, c)**2 for c in out) for r in tmp]
    p   = sum(ws) * random.random()
    out += [pick(ws)]
  return out

def distKmeans(data, rows=None, n=10, out=None, err=1, **key):
  "Return key centroids within data."
  rows = rows or data.rows
  centroids = [mids(d) for d in out] if out else distKpp(data,rows,**key)
  tmp,err1 = {},0
  for row in rows:
    col = min(centroids, key=lambda crow: distx(data,crow,row))
    err1 += distx(data,col,row) / len(rows)
    tmp[id(col)] = tmp.get(id(col)) or Data([data.cols.names])
    adds(tmp[id(col)],row)
  print(f'err={err1:.3f}')
  return (out if (n==1 or abs(err - err1) <= 0.01) else
          distKmeans(data, rows, n-1, d.values(), err=err1,**key))

