#!/usr/bin/env python3 -B
"""stats.py: KS test, Cliff's delta, confusion matrix utilities."""
from ezr import *

def same(xs, ys, eps):
  """Are two lists statistically same?"""
  xs, ys = sorted(xs), sorted(ys)
  n, m = len(xs), len(ys)
  if abs(xs[n//2] - ys[m//2]) <= eps: return True
  gt = sum(bisect.bisect_left(ys, a) for a in xs)
  lt = sum(m - bisect.bisect_right(ys, a) for a in xs)
  if abs(gt - lt) / (n*m) > the.stats.cliffs:
    return False
  ks = lambda v: abs(bisect.bisect_right(xs, v)/n
                     - bisect.bisect_right(ys, v)/m)
  return max(max(map(ks, xs)), max(map(ks, ys))) <= \
         the.stats.conf * ((n+m)/(n*m))**.5

def bestRanks(d):
  """Group treatments tied for best."""
  items = sorted(d.items(), key=lambda kv:
                 sorted(kv[1])[len(kv[1])//2])
  k0, lst0 = items[0]
  best = {k0: adds(lst0, Num(k0))}
  for k, lst in items[1:]:
    if same(lst0, lst, spread(best[k0]) * the.stats.eps):
      best[k] = adds(lst, Num(k))
    else: break
  return best

def confused(cf):
  """Confusion stats per class. All metrics as int %."""
  klasses = sorted(set(cf.keys()).union(
    {g for w in cf.values() for g in w.keys()}))
  total = sum(cf[w][g] for w in cf for g in cf[w])
  p = lambda y, z: int(100 * y / (z or 1e-32))
  out = []
  for c in klasses:
    tp = cf.get(c, {}).get(c, 0)
    fn = sum(cf.get(c, {}).values()) - tp
    fp = sum(cf.get(w, {}).get(c, 0) for w in cf if w != c)
    tn = total - tp - fn - fp
    pd, pr = p(tp, tp+fn), p(tp, fp+tp)
    sp = p(tn, tn+fp)
    out.append(S(tp=tp, fn=fn, fp=fp, tn=tn,
                 pd=pd, pr=pr,
                 f1=int(2*pd*pr/(pd+pr+1e-32)),
                 g=int(2*pd*sp/(pd+sp+1e-32)),
                 acc=p(tp+tn, total), label="  "+c))
  return out

def cli(argv):
  print("stats.py: library only. See tests/test_stats.py for examples.")

if __name__ == "__main__":
  cli(sys.argv[1:])
