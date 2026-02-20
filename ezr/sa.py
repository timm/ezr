#!/usr/bin/env python3 -B
"""sa.py: simulated annealing
(c) 2026 Tim Menzies timm@ieee.org, MIT license"""
import sys,random
from math import exp
choice,choices,rand = random.choice,random.choices,random.random
from ez2 import (nearest,disty,nearby,csv,says,Data,shuffle)

def oneplus1(d:Data, mutator, accept, b=1000, restart=0):
  def score(r):
    near = nearest(d, r, d.rows)
    for y in d.cols.y: r[y.at] = near[y.at]
    return disty(d, r)
  h, best, best_e =  0, None, 1E32
  s,e,last_improvement = choice(d.rows)[:], 1E32, 0 # START
  while True:
    if h >= b: return
    for sn in mutator(s):
      h += 1
      en = score(sn)
      if accept(e, en, h, b): s, e = sn, e
      if en < best_e:
        best, best_e = sn[:], en
        last_improvement = h
        yield h, best_e, best
      if restart and h - last_improvement > restart: 
        s,e,last_improvement = choice(d.rows)[:], 1E32, 0 #RESTART  
        break               

def sa(d, restarts=0, m=0.5, b=1000):
  def accept(e,en,h,b):
    return en<e or rand() < exp((e - en)/(1 - h/b))
  def mutate(s):
    sn = s[:]
    for x in choices(list(d.cols.x), k=max(1,int(m*len(d.cols.x)))):
      sn[x.at] = nearby(x,sn[x.at])
    yield sn
  return oneplus1(d, mutate, accept, b, restarts)

if __name__ == "__main__":
  seed,file = sys.argv[1:]
  random.seed(float(seed))
  d0 = Data(csv(file))
  d1 = Data([d0.cols.names] + shuffle(d0.rows)[:50])
  says(["Evals","Energy"] + d1.cols.names, 8)
  for h,e,row in sa(d1):
    says([h,e] + row, 8)
