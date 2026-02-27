#!/usr/bin/env python3 -B
"""locals.py: local search + comparison with sa
(c) 2026 Tim Menzies timm@ieee.org, MIT license"""
import sys,random
choice,rand = random.choice,random.random
from ez import (nearby,csv,says,Data,shuffle)
from sa import sa, oneplus1

def lsRminus(d,**args):  return ls(d,restarts=0,  **args)
def saRplus(d, **args):  return sa(d,restarts=100,**args)

def ls(d, restarts=100, p=0.5, n=20, b=1000):
  def accept(e, en, *_): return en < e
  def mutate(s):
    for _ in range(n if rand() < p else 1): yield d.pick(s, n=1)
  return oneplus1(d, mutate, accept, b, restarts)
 
if __name__ == "__main__":
  print("usage: python3 -B mutate.py SEED CSV")
  random.seed(float(sys.argv[1]))
  d0   = Data(csv(sys.argv[2]))
  seen = {sa:[], ls:[], lsRminus:[], saRplus:[]}
  for _ in range(20):
    d1 = Data([d0.cols.names] + shuffle(d0.rows)[:50])
    for algo in [sa,ls,lsRminus,saRplus]:
      print(f"\n--- {algo.__name__} ---")
      says(["evals","energy"] + d1.cols.names,w=8)
      for h,e,row in algo(d1):
        says([h,e]+row, w=8)
      seen[algo] += [100*e]
  print("")
  for algo,lst in seen.items():
    says(sorted(map(int,lst)) + [algo.__name__],3)
