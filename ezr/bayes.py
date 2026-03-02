#!/usr/bin/env python3 -B
"""bayes.py: incremental naive Bayes classifier
(c) 2026 Tim Menzies timm@ieee.org, MIT license"""
from ez import Data,csv,says,main,align,Iterable,filename
from stats import Confuse, confuse, confused

def nbayes(src:Iterable, warmup:int=10) -> Confuse:
  rows = iter(src)
  d    = Data([next(rows)])
  every, ks, cf = Data([d.cols.names]), {}, Confuse()
  def best(k):
    return ks[k].like( r, len(every.rows), len(ks))
  for r in rows:
    k = r[d.cols.klass]
    if k not in ks: ks[k] = Data([d.cols.names])
    if len(every.rows) >= warmup:
      confuse(cf, str(k), str(max(ks, key=best)))
    ks[k].add(every.add(r))
  return cf

def eg__data(f:filename):
  rows = [["label","n","pd","pf","prec","acc"]]
  for c in confused(nbayes(csv(f))):
    rows.append([c.label, c.fn+c.tp, c.pd, c.pf, c.prec, c.acc])
  align(rows)

if __name__ == "__main__": main(globals())
