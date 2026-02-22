#!/usr/bin/env python3 -B
"""xplainr.py: rule generation from top signals

Options:
  -M Maxr=5        max rule size
  -S Support=10    min rows matching a rule
  -T Top=8         top columns by signal"""
import sys, re
from ez2 import BIG, Data, Num, Sym, Row, csv, disty, adds, the, cast, main, O, shuffle, clone
from xplain import xplanTrain, signal, bnum

BPC = 2
cfg = O(**{k: cast(v) for k, v in re.findall(r"(\S+)=(\S+)", __doc__)})

def ruleMatch(d:Data, rule:dict, row:Row) -> bool:
  return all(row[at] != "?" and
             (row[at] if Sym is d.cols.all[at].it else bnum(d.cols.all[at], row[at])) == b
             for at, b in rule.items())

def ruleScore(d:Data, rule:dict, rows:list):
  matched = [r for r in rows if ruleMatch(d, rule, r)]
  if len(matched) < cfg.Support: return BIG, 0
  ys = adds(disty(d, r) for r in matched)
  return ys.mu, ys.n

def ruleStr(d:Data, rule:dict) -> str:
  parts = []
  for at, b in sorted(rule.items()):
    col = d.cols.all[at]
    if Sym is col.it:
      parts.append(f"{col.txt}={b}")
    else:
      s = col.bins[b]
      parts.append(f"{col.txt}={round(s.lo,the.decs)}..{round(s.hi,the.decs)}")
  return " and ".join(parts)

def rules(d:Data, ys:Num, train:list):
  spans = [(x, b)
           for x in sorted(d.cols.x, key=signal, reverse=True)[:cfg.Top]
           for b in sorted(x.bins, key=lambda b: x.bins[b].y.mu)[:BPC]]

  seen = set()
  def fresh(rule):
    k = frozenset(rule.items())
    if k in seen: return False
    seen.add(k); return True

  beam = []
  for x, b in spans:
    rule = {x.at: b}
    score, n = ruleScore(d, rule, train)
    if score < BIG and fresh(rule):
      beam.append((score, rule))
  beam = sorted(beam)[:cfg.Top]
  for score, rule in beam: yield score, len(rule), rule

  for _ in range(2, cfg.Maxr+1):
    candidates = []
    for _, rule in beam:
      for x, b in spans:
        if x.at not in rule:
          new = {**rule, x.at: b}
          score, n = ruleScore(d, new, train)
          if score < BIG and fresh(new):
            candidates.append((score, new))
    if not candidates: break
    beam = sorted(candidates)[:cfg.Top]
    for score, rule in beam: yield score, len(rule), rule

def report(d:Data, ys:Num):
  rows  = shuffle(d.rows[:])
  mid   = len(rows) // 2
  train, test = rows[:mid], rows[mid:]
  d_train = clone(d, train)
  xplanTrain(d_train)

  found = sorted(rules(d_train, ys, train))[:cfg.Top]
  print(f"{'train':>6}  {'test':>6}  {'n':>4}  rule")
  for score, size, rule in found:
    test_score, _ = ruleScore(d_train, rule, test)
    if test_score == BIG: continue          # no test support, skip
    n_train = sum(ruleMatch(d_train, rule, r) for r in train)
    print(f"{score:>6.2f}  {test_score:>6.2f}  {n_train:>4}  {ruleStr(d_train, rule)}")
   
def eg__report(f:str):
  d = Data(csv(f))
  _, ys = xplanTrain(d)
  report(d, ys)

def eg_M(n:int): cfg.Maxr    = n
def eg_S(n:int): cfg.Support = n
def eg_T(n:int): cfg.Top     = n

if __name__ == "__main__": main(globals())
