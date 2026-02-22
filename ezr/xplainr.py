#!/usr/bin/env python3 -B
"""xplainr.py: rule generation from top signals
Options:
  -B Bpc=2         best bins per column
  -M Maxr=5        max rule size
  -S Support=10    min rows matching a rule
  -T Top=8         top columns by signal"""
import re
from ez import (Data, Num, Row, csv, disty, adds,
                 the, cast, main, O, shuffle, clone)
from xplain import xplanTrain, signal, rowBin, colsDict

cfg = O(**{k: cast(v) for k, v in re.findall(r"(\S+)=(\S+)", __doc__)})

def ruleMatch(cols:dict, rule:dict, row:Row) -> bool:
  return all(row[at] != "?" and rowBin(cols[at], row[at]) == b
             for at, b in rule.items())

def ruleScore(d:Data, cols:dict, rule:dict, rows:list) -> Num|None:
  if (ys := adds( disty(d,r) for r in rows
                  if ruleMatch(cols, rule, r))).n >= cfg.Support:
    return ys

def ruleStr(cols:dict, rule:dict) -> str:
  parts = []
  for at, b in sorted(rule.items()):
    col, s = cols[at], cols[at].bins[b]
    parts.append(f"{col.txt}={b}" if not hasattr(s, 'lo') else
      f"{col.txt}={round(s.lo,the.decs)}..{round(s.hi,the.decs)}")
  return " and ".join(parts)

def rules(d:Data, cols:dict, train:list):
  seen = set()
  n    = 0

  def score(rule):
    k = tuple(sorted(rule.items()))
    if k not in seen:
      seen.add(k)
      if ys := ruleScore(d, cols, rule, train):
        return ys.mu

  spans = [(x.at, b, s, (n:=n+1))
           for x in sorted(d.cols.x,
                           key=signal, reverse=True)[:cfg.Top]
           for b in sorted(x.bins,
                           key=lambda b: x.bins[b].y.mu)[:cfg.Bpc]
           if (s := score({x.at: b})) is not None]

  beam = sorted((s, i, {at:b}) for at,b,s,i in spans)[:cfg.Top]
  for s, _, rule in beam: yield s, _, rule

  for _ in range(2, cfg.Maxr+1):
    beam = sorted(
      [(s, (n:=n+1), new) for _,_, rule in beam
                          for at, b, *_ in spans if at not in rule
                          if (s := score(new := {**rule, at: b}))
                          is not None])[:cfg.Top]
    if not beam: break
    for s, _, rule in beam: yield s, _, rule

def report(d:Data):
  rows = shuffle(d.rows[:])
  mid  = len(rows) // 2
  train, test = rows[:mid], rows[mid:]
  d_train = clone(d, train)
  xplanTrain(d_train)
  cols = colsDict(d_train)
  print(f"{'train':>6}  {'test':>6}  {'n':>4}  rule")
  for score, _, rule in sorted(rules(d_train, cols, train))[:cfg.Top]:
    if not (t := ruleScore(d_train, cols, rule, test)): continue
    print(f"{score:>6.2f}  {t.mu:>6.2f}"
          f"  {t.n:>4}  {ruleStr(cols, rule)}")
   
def eg_h():            print(__doc__)
def eg__report(f:str): report(Data(csv(f)))
def eg_B(n:int): cfg.Bpc     = n
def eg_M(n:int): cfg.Maxr    = n
def eg_S(n:int): cfg.Support = n
def eg_T(n:int): cfg.Top     = n

if __name__ == "__main__": main(globals())
