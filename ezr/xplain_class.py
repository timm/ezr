#!/usr/bin/env python3 -B
"""xplain.py: which attribute bins predict low distance-to-heaven
(c) 2026 Tim Menzies timm@ieee.org, MIT license"""
from bisect import bisect_left
from types import SimpleNamespace as o
from ez_class import BIG, Data, Num, Sym, Qty, csv, adds, main, filename, the

WIDTH = 15

def Span(lo=BIG, hi=-BIG): return o(lo=lo, hi=hi, y=Num())

def spanAdd(s, x:Qty, y:float):
  s.lo = min(s.lo, x)
  s.hi = max(s.hi, x)
  s.y.add(y)

def spanShow(s, ys) -> str:
  blocks = " ▁▂▃▄▅▆▇█"
  reset  = "\033[0m"
  lo, hi = ys[0], ys[-1]
  v      = s.y.mid()
  norm   = 0 if lo==hi else max(0, min(1, (v-lo)/(hi-lo)))
  score  = max(1, min(the.bins, int(the.bins * norm) + 1))
  c = "\033[1;32m" if score <= the.bins//3 else \
      "\033[1;31m" if score >= 2*the.bins//3 else "\033[2;37m"
  return f"{c}{blocks[min(score,len(blocks)-1)]}{reset}"

def rowBin(col, v):
  return v if isinstance(col, Sym) else min(the.bins, max(1, int(the.bins * col.norm(v))))

def xplanTrain(d:Data):
  for at,x in d.cols.x.items(): x.bins = {}
  ys = Num()
  for r in d.rows:
    y = ys.add(d.disty(r))
    for at,x in d.cols.x.items():
      if (v := r[at]) != "?":
        b = rowBin(x, v)
        x.bins[b] = x.bins.get(b) or Span(lo=v, hi=v)
        spanAdd(x.bins[b], v, y)
  return d, ys

def signal(x) -> float:
  return adds(s.y.mid() for s in x.bins.values()).spread()

def report1(d:Data, at:int, x, ys, signals:Num) -> str:
  name = d.cols.names[at]
  lo, hi = x.bins[min(x.bins)].lo, x.bins[max(x.bins)].hi
  if isinstance(x, Num): lo, hi = round(lo, the.decs), round(hi, the.decs)
  spark = "".join(spanShow(x.bins[k], ys) if k in x.bins else "░"
                  for k in range(the.bins+1))
  s= signals.norm(signal(x))
  bars= "+" * int(20*s)
  return f"  {name[:WIDTH]:<{WIDTH}} | {str(lo):>6} {str(hi):>6} | {spark} {bars} [{int(100*s)}]"

def report(d:Data, ys):
  print(f"\n  {'NAME':<{WIDTH}} | {'lo':>6} {'hi':>6} | {'░'*(the.bins+1)}")
  print(f"  {'-'*WIDTH}-+-{'-'*6}-{'-'*6}-+-{'-'*(the.bins+1)}")
  signals=Num()
  for at,x in sorted(d.cols.x.items(), key=lambda kv: signals.add(signal(kv[1])), reverse=True):
    print(report1(d, at, x, ys, signals))
  print(" ")

def eg__data(f:filename):
  "show which bins predict low distance-to-heaven"
  report(*xplanTrain(Data(csv(f))))

if __name__ == "__main__": main(globals())
