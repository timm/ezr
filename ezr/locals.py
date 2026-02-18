#!/usr/bin/env python3 -B
"""ls.py: local search + comparison with sa
(c) 2026 Tim Menzies timm@ieee.org, MIT license"""
import sys
import random
choice,rand = random.choice,random.random
from ez1 import (nearby,csv,say,Data,shuffle)
from sa import sa, oneplus1

def ls(d, p=0.5, n=20, b=4000):
  def accept(e,en,*_):
    return en<e
  def mutate(s):
    i = choice(list(d.cols.x))
    for _ in range(n if rand() < p else 1):
      sn = s[:]; sn[i] = nearby(d.cols.x[i], sn[i]); yield sn
  return oneplus1(d, mutate, accept, b)

if __name__ == "__main__":
  seed,file = sys.argv[1:]
  random.seed(float(seed))
  d0 = Data(csv(file))
  seen={sa:[],ls:[]}
  for _ in range(20):
    d1 = Data([d0.cols.names] + shuffle(d0.rows)[:50])
    for algo in [sa,ls]:
      print(f"\n--- {algo.__name__} ---")
      for h,e,row in algo(d1):
        print(h, say(e), [say(v) for v in row])
      seen[algo] += [100*e]
  print("")
  for algo,lst in seen.items():
    print(algo.__name__, *sorted(map(int,lst)))
