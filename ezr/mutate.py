#!/usr/bin/env python3 -B
"""oneplusone.py: (1+1) optimizers: sa, ls
(c) 2026 Tim Menzies timm@ieee.org, MIT license"""
import sys
from math import exp
import random
choice,choices,rand = random.choice,random.choices,random.random
from ez1 import (nearest,disty,gauss,pick,csv,say,
                 Sym,Col,Any,isa,mid,sd,Data,ok,shuffle,cast)

# -- mutators --------------------------------------------------
def mutation(c:Col, v:Any) -> Any:
  if isa(c,Sym): return pick(c)
  lo,hi = c[0],c[-1]
  v = v if v != "?" else mid(c)
  return lo + (v + choice(c) - choice(c) - lo) % (hi-lo+1E-32)

def mutations(d:Data, s:list, m=0.5, **_):
  sn = s[:]
  for i in choices(list(d.cols.x), k=max(1,int(m*len(d.cols.x)))):
    sn[i] = mutation(d.cols.x[i], sn[i])
  yield sn

def walk(d:Data, s:list, p=0.5, n=20, **_):
  i = choice(list(d.cols.x))
  for _ in range(n if rand() < p else 1):
    sn = s[:]; sn[i] = mutation(d.cols.x[i], sn[i]); yield sn

# -- engine ----------------------------------------------------
def oneplus1(d:Data, mutator, accept, b=4000, **kw):
  def score(r):
    near = nearest(d, r, d.rows)
    for i in d.cols.y: r[i] = near[i]
    return disty(d, r)

  h,s,e = 0, choice(d.rows)[:], 1E32
  best, best_e = s[:], e
  while True:  
    for sn in mutator(d, s, **kw):
      if h >= b: return  
      en = score(sn)
      if accept(e, en, h, b): s, e = sn, en
      if en < best_e:
        best, best_e = sn[:], en
        yield h, best_e, best
      h += 1
     
# -- algorithms ------------------------------------------------
def sa(d, m=0.5, b=4000, **kw): 
  return oneplus1(d, mutator=mutations, accept=anneal, m=m, b=b, **kw)

def ls(d, p=0.5, n=20, b=4000, **kw): 
  return oneplus1(d, mutator=walk, accept=greedy, p=p, n=n, b=b, **kw)

def anneal(e,en,h,b): return en<e or rand() < exp((e - en)/(1 - h/b))
def greedy(e,en,*_): return en<e

# -- demo ------------------------------------------------------
if __name__ == "__main__":
  seed,file = sys.argv[1:]
  random.seed(cast(seed))
  d0 = Data(csv(file))
  seen={sa:[],ls:[]}
  for _ in range(20):
    d1 = ok(Data([d0.cols.names] + shuffle(d0.rows)[:50]))
    for algo in [sa,ls]:
      print(f"\n--- {algo.__name__} ---")
      for h,e,row in algo(d1):
        print(h,say(e),[say(v) for v in row])
      seen[algo] += [100*e]
  for algo,lst in seen.items():
    print(algo.__name__, *sorted(map(int,lst)))
