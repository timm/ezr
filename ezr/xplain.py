#!/usr/bin/env python3 -B
"""xplain.py: which attribute bins predict low distance-to-heaven"""
import sys
from ez import BIG,Data,Num,Sym,O,Qty,csv,norm,disty,add,adds,sd,the

WIDTH = 15

def Span(lo=BIG, hi=-BIG): return O(lo=lo, hi=hi, y=Num())

def spanAdd(s, x:Qty, y:float):
  s.lo = min(s.lo, x)
  s.hi = max(s.hi, x)
  add(s.y, y)

def rowBin(col, v):
  return v if Sym is col.it else min(the.bins, max(1, int(the.bins * norm(col, v))))

def spanShow(s, ys) -> str:
  blocks = " ▁▂▃▄▅▆▇█"
  reset  = "\033[0m"
  score  = max(1, rowBin(ys, s.y.mu))
  c = "\033[1;32m" if score <= the.bins//3 else \
      "\033[1;31m" if score >= 2*the.bins//3 else "\033[2;37m"
  return f"{c}{blocks[min(score,len(blocks)-1)]}{reset}"

def xplanTrain(d):
  for x in d.cols.x: x.bins = {}
  ys = Num()
  for r in d.rows:
    y = add(ys, disty(d, r))
    for x in d.cols.x:
      if (v := r[x.at]) != "?":
        b = rowBin(x, v)
        x.bins[b] = x.bins.get(b) or Span(lo=v, hi=v)
        spanAdd(x.bins[b], v, y)
  return d, ys

def signal(x): return sd(adds(s.y.mu for s in x.bins.values()))

def colsDict(d): return {x.at: x for x in d.cols.x}

def report1(x, ys) -> str:
  lo, hi = x.bins[min(x.bins)].lo, x.bins[max(x.bins)].hi
  if Num is x.it: lo, hi = round(lo, the.decs), round(hi, the.decs)
  spark = "".join(spanShow(x.bins[k], ys) if k in x.bins else "░"
                  for k in range(the.bins+1))
  return f"  {x.txt[:WIDTH]:<{WIDTH}} | {str(lo):>6} {str(hi):>6} | {spark}"

def report(d, ys):
  print(f"\n  {'NAME':<{WIDTH}} | {'lo':>6} {'hi':>6} | {'░'*(the.bins+1)}")
  print(f"  {'-'*WIDTH}-+-{'-'*6}-{'-'*6}-+-{'-'*(the.bins+1)}")
  for x in sorted(d.cols.x, key=signal, reverse=True):
    print(report1(x, ys))
  print(" ")

if __name__ == "__main__": report(*xplanTrain(Data(csv(sys.argv[-1]))))
