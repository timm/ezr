#!/usr/bin/env python3 -B
"""ls.py: local search + comparison with sa
(c) 2026 Tim Menzies timm@ieee.org, MIT license"""
import sys,random
choice,rand = random.choice,random.random
from ez2 import (nearby,csv,says,Data,shuffle)
from sa import sa, oneplus1

def ls(d, p=0.5, n=20, b=4000):
  def accept(e,en,*_):
    return en<e
  def mutate(s):
    x = choice(list(d.cols.x))
    for _ in range(n if rand() < p else 1):
      sn = s[:]; sn[x.at] = nearby(x, sn[x.at]); yield sn
  return oneplus1(d, mutate, accept, b,RESTARTS)

if __name__ == "__main__":
  print("usage: python3 -B mutate.py SEED, RESTART, CSV")
  seed,restarts,file = sys.argv[1:]
  random.seed(float(seed))
  RESTARTS=float(restarts)
  d0 = Data(csv(file))
  seen={sa:[],ls:[]}
  for _ in range(20):
    d1 = Data([d0.cols.names] + shuffle(d0.rows)[:50])
    for algo in [sa,ls]:
      print(f"\n--- {algo.__name__} ---")
      says(["evals","energy"] + d1.cols.names,w=10)
      for h,e,row in algo(d1):
        says([h,e]+row, w=10)
      seen[algo] += [100*e]
  print("")
  for algo,lst in seen.items():
    says([algo.__name__] +  sorted(map(int,lst)),2)
