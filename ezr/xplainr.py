#!/usr/bin/env python3 -B
"""xplainr.py: rule generation from top signals"""
import sys
from ez2 import BIG, Data, Num, Sym, Row, csv, disty, adds, the
from xplain import xplanTrain, signal, bnum

TOP  = 8
MAXR = 5

def combos(lst:list, n:int):
  if n:
    for i, x in enumerate(lst):
      for rest in combos(lst[i+1:], n-1):
        yield (x, *rest)
  else: yield ()

def ruleMatch(d:Data, rule:dict, row:Row) -> bool:
  return all(row[at] != "?" and
             (row[at] if Sym is d.cols.all[at].it 
                      else bnum(d.cols.all[at], row[at])) == b
             for at, b in rule.items())

def ruleScore(d:Data, rule:dict) -> float:
  ys = adds(disty(d, r) for r in d.rows if ruleMatch(d, rule, r))
  return ys.mu if ys.n else BIG

def ruleStr(d:Data, rule:dict) -> str:
  parts = []
  for at, b in rule.items():
    col = d.cols.all[at]
    if Sym is col.it:
      parts.append(f"{col.txt}={b}")
    else:
      s = col.bins[b]
      parts.append(
        f"{col.txt}={round(s.lo, the.decs)}..{round(s.hi, the.decs)}")
  return " and ".join(parts)

def rules(d:Data, ys:Num, top=TOP, maxr=MAXR):
  spans = sorted([(x, b) for x in d.cols.x
                         for b in x.bins],
                 key=lambda t: signal(t[0]), reverse=True)[:top]
  n = 0
  for size in range(1, maxr+1):
    for combo in combos(spans, size):
      rule = {x.at: b for x, b in combo}
      if len(rule) == size:
        yield ruleScore(d, rule), size, (n := n+1), rule

def report(d:Data, ys:Num, top=TOP, maxr=MAXR):
  print(f"{'score':>6}  {'n':>5}  rule")
  for score, size, _, rule in sorted(rules(d, ys, top, maxr))[:top]:
    fx =sum(ruleMatch(d,rule,r) for r in d.rows)
    print(f"{score:>6.2f}  {fx:>5}  {ruleStr(d, rule)}")

if __name__ == "__main__":
  d = Data(csv(sys.argv[-1]))
  report(d, *xplanTrain(d)[1:])

