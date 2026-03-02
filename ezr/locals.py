#!/usr/bin/env python3 -B
"""locals.py: local search + comparison with sa
(c) 2026 Tim Menzies timm@ieee.org, MIT license"""
import random
choice, rand = random.choice, random.random
from ez import csv, says, Data, shuffle, main, filename
from sa import sa, oneplus1

def lsRminus(d, **args): return ls(d, restarts=0,   **args)
def saRplus(d,  **args): return sa(d, restarts=100, **args)

def ls(d, restarts=100, p=0.5, n=20, b=1000):
  def accept(e, en, *_): return en < e
  def mutate(s):
    at, c = choice(list(d.cols.x.items()))  
    for _ in range(n if rand() < p else 1):
       s = s[:]; s[at] = c.pick(s[at]); yield s  
  return oneplus1(d, mutate, accept, b, restarts)
 
def eg__data(f:filename):
  "compare ls, sa, lsRminus, saRplus across 20 shuffled samples"
  d0   = Data(csv(f))
  seen = {sa: [], ls: [], lsRminus: [], saRplus: []}
  for _ in range(20):
    d1 = Data([d0.cols.names] + shuffle(d0.rows)[:50])
    for algo in seen:
      for h, e, row in algo(d1): pass
      seen[algo] += [int(100*e)]
  for algo, errs in seen.items():
    says(sorted(errs) + [sum(errs)/len(errs), algo.__name__], w=3)

if __name__ == "__main__": main(globals())
