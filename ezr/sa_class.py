#!/usr/bin/env python3 -B
"""sa.py: simulated annealing
(c) 2026 Tim Menzies timm@ieee.org, MIT license"""
import sys,random
from math import exp
choices,rand = random.choices,random.random
from ez_class import Data,csv,says,shuffle,choice,eg_s,eg_h,main,filename

def oneplus1(d:Data, mutator:callable, accept:callable, b=1000, restart=0):
  def score(r):
    near = d.nearest(r, d.rows)
    for at in d.cols.y: r[at] = near[at]
    return d.disty(r)

  h, best, best_e =  0, None, 1E32
  s,e,last_improvement = choice(d.rows)[:], 1E32, 0 # START
  while True:
    if h >= b: return
    for sn in mutator(s):
      h += 1
      en = score(sn)
      if accept(e, en, h, b): s, e = sn, en
      if en < best_e:
        best, best_e = sn[:], en
        last_improvement = h
        yield h, best_e, best
      if restart and h - last_improvement > restart: 
        s,e,last_improvement = choice(d.rows)[:], 1E32, 0 #RESTART  
        break               

def sa(d:Data, restarts=0, m=0.5, b=1000):
  def accept(e,en,h,b):
    return en<e or rand() < exp((e - en)/(1 - h/b + 1E-32))
  def mutate(s):
    sn = s[:]
    xs = list(d.cols.x.items())
    for at,c in choices(xs, k=max(1,int(m*len(xs)))):
       sn[at] = c.pick(sn[at])
    yield sn
  return oneplus1(d, mutate, accept, b, restarts)

def eg__data(f:filename):
  d0 = Data(csv(f))
  d1 = Data([d0.cols.names] + shuffle(d0.rows)[:50])
  says(["Evals","Energy"] + d1.cols.names, 8)
  for h,e,row in sa(d1):
    says([h,e] + row, 8)

if __name__ == "__main__": main(globals())
