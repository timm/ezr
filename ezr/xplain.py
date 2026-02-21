#!/usr/bin/env python3 -B
"""xplan.py: which attribute bins predict low distance-to-heaven"""
import sys
from ez2 import Data, Num, Sym, csv, norm, disty, add, adds, sd

W, B = 15, 9
BLOCKS = " ▁▂▃▄▅▆▇█"
RESET  = "\033[0m"

def bnum(col, v): return min(B, max(1, int(B * norm(col, v))))

def color(s):
  if s <= 3: return "\033[1;32m"  # bright green = good
  if s >= 7: return "\033[1;31m"  # bright red   = bad
  return "\033[2;37m"             # dim gray      = middle

def discretize(col, v):
  if v == "?": return v
  b    = v if Sym is col.it else bnum(col, v)
  bins = col.setdefault('bins', {})
  if b not in bins: bins[b] = Num(lo=v, hi=v) if Num is col.it else Num()
  elif Num is col.it:
    bins[b].lo = min(bins[b].lo, v)
    bins[b].hi = max(bins[b].hi, v)
  return b

def xplanTrain(d):
  ys = Num()
  for r in d.rows:
    y = add(ys, disty(d, r))
    for x in d.cols.x:
      if (v := r[x.at]) != "?":
        b = discretize(x, v)
        add(x.bins[b], y)
  return d, ys

def signal(x, ys):
  return sd(adds(bnum(ys, b.mu) for b in x.bins.values()))

def xplanReport(d, ys):
  sep = f"{'-'*W}-+-{'-'*6}-{'-'*6}-+-{'-'*(B+1)}"
  print(f"{'NAME':<{W}} | {'lo':>6} {'hi':>6} | {'░'*(B+1)}")
  print(sep)
  for x in sorted(d.cols.x, key=lambda x: signal(x, ys), reverse=True):
    def cell(k):
      b = x.bins.get(k)
      if not b: return "░"
      s = max(1, bnum(ys, b.mu))
      return f"{color(s)}{BLOCKS[s]}{RESET}"
    lo = round(x.bins[min(x.bins)].lo, 2) if Num is x.it else min(x.bins)
    hi = round(x.bins[max(x.bins)].hi, 2) if Num is x.it else max(x.bins)
    print(f"{x.txt[:W]:<{W}} | {str(lo):>6} {str(hi):>6} | "
          f"{''.join(cell(k) for k in range(B+1))}")

if __name__ == "__main__":
  xplanReport(
     *xplanTrain(
        Data(csv(sys.argv[-1]))))
