#!/usr/bin/env python3 -B
"""
ezr_eg.py: more demos for ezr.py (clustering, optimizers)
(c) 2026 Tim Menzies <timm@ieee.org> MIT license

Options:

  -budget=1000  optimize: max oracle calls
  -restart=100  ls: retry after this many no-improvements
  -K=10         kmeans: clusters
  -N=10         kmeans: iterations
"""
import random, re, sys
from ezr import *

for k, v in re.findall(r"(\w+)=(\S+)", __doc__ or ""):
  the[k] = the._defaults[k] = atom(v)


#-- cluster -----------------------------------------------
def kmeans(tbl, rows):
  cents = random.sample(rows, the.K)
  for _ in range(the.N):
    ds = [clone(tbl) for _ in cents]
    for r in rows:
      j = min(range(len(cents)),
              key=lambda i: xdist(tbl, r, cents[i]))
      addRow(ds[j], r)
    ds = [d for d in ds if d.rows]
    cents = [mids(d) for d in ds]
  return ds

def kpp(tbl, rows, k=None, few=256): # kmeans++ seeds
  rows = random.sample(rows, min(few, len(rows)))
  out = [random.choice(rows)]
  while len(out) < (k or the.K):
    ws = [min(xdist(tbl, r, c)**2 for c in out) for r in rows]
    out.append(random.choices(rows, weights=ws)[0])
  return out

def nearest(tbl, row, rows):
  return min(rows, key=lambda r: xdist(tbl, r, row))


#-- optimize ----------------------------------------------
def pick(col, v=None): # sample a plausible value
  if type(col) is Sym:
    return random.choices(list(col), col.values())[0]
  mu = col[1] if v is None or v == "?" else v
  lo, hi = col[1] - 3*sd(col), col[1] + 3*sd(col)
  new = mu + sd(col)*2*(random.random() + random.random()
                        + random.random() - 1.5)
  return lo + (new - lo) % (hi - lo + 1e-32)

def oneplus1(tbl, mutate, accept, oracle, restart=0):
  s, e, h, imp, best, be = None, 1e32, 0, 0, None, 1e32
  s = random.choice(tbl.rows)
  while h < the.budget:
    for sn in mutate(s):
      h += 1
      en = oracle(sn)
      if accept(en, e, h, the.budget): s, e = sn, en
      if en < be: best, be, imp = sn, en, h
      if restart and h - imp > restart:
        s, e = random.choice(tbl.rows), 1e32
      if h >= the.budget: break
  return best

def ls(tbl, oracle, p=0.5, tries=20): # local search
  def mutate(s):
    at = random.choice(tbl.x)
    for _ in range(tries):
      s2 = list(s); s2[at] = pick(tbl.cols[at], s[at])
      yield tuple(s2)
  return oneplus1(tbl, mutate, lambda en, e, *_: en < e,
                  oracle, the.restart)

def sa(tbl, oracle, m=0.5): # 1983 simulated annealing
  def accept(en, e, h, b):
    return en < e or random.random() < exp(
      (e - en) / (1 - h/b + 1e-32))
  def mutate(s):
    s2 = list(s)
    for at in tbl.x:
      if random.random() < m:
        s2[at] = pick(tbl.cols[at], s2[at])
    yield tuple(s2)
  return oneplus1(tbl, mutate, accept, oracle)


#-- acquire, bayesian -------------------------------------
def bayes(tbl, best, rest): # most likely best
  n = len(best.rows) + len(rest.rows)
  return lambda z: likes(best, z, n, 2) - likes(rest, z, n, 2)

def acquireBayes(tbl, cap=None): # label most-likely-best
  return acquire(tbl, cap, bayes)


#-- start-up ----------------------------------------------
def test_help():
  "Show usage, settings, demos"
  print(__doc__, "Demos:\n",
        *[f"  --{k[5:]:<10} {f.__doc__}"
          for k, f in globals().items() if k[:5] == "test_"],
        sep="\n")

def test_kmeans():
  "Cluster the.File; per cluster: n rows, mean ydist"
  tbl = Tbl(csv(the.File))
  for d in sorted(kmeans(tbl, tbl.rows),
                  key=lambda d: ymu(tbl, d.rows)):
    print(f"{len(d.rows):>4} {round(ymu(tbl, d.rows), 2)}")

def test_kpp():
  "kmeans++ seeds spread wider than random picks"
  tbl = Tbl(csv(the.File))
  far = lambda cents: round(sum(
    xdist(tbl, a, b) for a in cents for b in cents), 1)
  print(f"random {far(random.sample(tbl.rows, the.K))}"
        f" kpp {far(kpp(tbl, tbl.rows))}")

def test_optimize():
  "SA vs local search, nearest-neighbor oracle, wins"
  tbl = Tbl(csv(the.File))
  win = wins(tbl)
  known = clone(tbl, random.sample(tbl.rows, 50))
  def oracle(r):
    return ydist(tbl, nearest(tbl, r, known.rows))
  for what in [sa, ls]:
    random.seed(the.Seed)
    got = nearest(tbl, what(tbl, oracle), known.rows)
    print(f"{what.__name__:<3} win {round(win(got))}")

def test_acquires():
  "Centroid vs bayes acquisition: 20 holdouts each"
  tbl = Tbl(csv(the.File))
  win = wins(tbl)
  for fn in [acquire, acquireBayes]:
    random.seed(the.Seed)
    mu = 0
    for _ in range(20):
      rows = random.sample(tbl.rows, len(tbl.rows))
      n = len(rows) // 2
      tr = clone(tbl, rows[:n][:the.Few])
      tt = tree(tr, fn(tr, the.Stop - the.Check))
      top = sorted(rows[n:],
                   key=lambda r: leaf(tt, r)[2])[:the.Check]
      mu += win(min(top, key=lambda r: ydist(tr, r)))
    print(f"{fn.__name__:<13} win {round(mu/20)}")

def test_all():
  "Run every demo; exit code counts the crashes"
  sys.exit(sum(print(f"\n# {k[5:]}") or run(f)
               for k, f in list(globals().items())
               if k[:5] == "test_" and f is not test_all))

def main(): # pip entry point
  cli(the, globals(), sys.argv[1:] or ["--help"])

if __name__ == "__main__": main()
