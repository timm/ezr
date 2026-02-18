#!/usr/bin/env python3 -B
"""sa.py: simulated annealing
(c) 2026 Tim Menzies timm@ieee.org, MIT license"""
import sys,random
from math import exp
choice,choices,rand = random.choice,random.choices,random.random
from ez1 import (nearest,disty,nearby,csv,say,Data,shuffle)

def oneplus1(d:Data, mutator, accept, b=4000):
  def score(r):
    near = nearest(d, r, d.rows)
    for i in d.cols.y: r[i] = near[i]
    return disty(d, r)

  h,s,e = 0, choice(d.rows)[:], 1E32
  best, best_e = s[:], e
  while True:
    for sn in mutator(s):
      if h >= b: return
      en = score(sn)
      if accept(e, en, h, b): s, e = sn, en
      if en < best_e:
        best, best_e = sn[:], en
        yield h, best_e, best
      h += 1

def sa(d, m=0.5, b=4000):
  def accept(e,en,h,b):
    return en<e or rand() < exp((e - en)/(1 - h/b))
  def mutate(s):
    sn = s[:]
    for i in choices(list(d.cols.x), k=max(1,int(m*len(d.cols.x)))):
      sn[i] = nearby(d.cols.x[i], sn[i])
    yield sn
  return oneplus1(d, mutate, accept, b)

if __name__ == "__main__":
  seed,file = sys.argv[1:]
  random.seed(float(seed))
  d0 = Data(csv(file))
  d1 = Data([d0.cols.names] + shuffle(d0.rows)[:50])
  for h,e,row in sa(d1):
    print(h, say(e), [say(v) for v in row])
