#!/usr/bin/env python3 -B
"""bayes.py: incremental naive Bayes classifier
(c) 2026 Tim Menzies timm@ieee.org, MIT license"""
from ez2   import Data, add, clone, csv, likes, says, main,align
from stats import Confuse, confuse, confused

def nbayes(src, warmup=10):
  rows = iter(src)
  d    = Data([next(rows)])
  every, ks, cf = clone(d), {}, Confuse()
  def best(k):
    return likes(ks[k], r, every.n, len(ks))
  for r in rows:
    k = r[d.cols.klass.at]
    if k not in ks: ks[k] = clone(d)
    if every.n >= warmup:
      confuse(cf, str(k), str(max(ks, key=best)))
    add(ks[k], add(every, r))
  return cf

def eg__bayes(f:str):
  rows = [["label","n","pd","pf","prec","acc"]]
  for c in confused(nbayes(csv(f))):
    rows.append([c.label, c.fn+c.tp, c.pd, c.pf, c.prec, c.acc])
  align(rows)

if __name__ == "__main__": main(globals())
