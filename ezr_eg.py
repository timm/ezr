#!/usr/bin/env python3 -B
"""
ezr_eg.py: more demos for ezr.py (clustering, optimizers)
(c) 2026 Tim Menzies <timm@ieee.org> MIT license

Options: see ezr.py (all settings live in one place).
"""
import random, sys
from ezr import *


#-- cluster -----------------------------------------------

# Group rows by x-distance, no labels needed. kmeans [1]
# loops: send each row to its nearest centroid, then recompute
# centroids. kpp [2] picks better starting seeds: each new
# seed is chosen with probability proportional to its distance
# from the seeds picked so far. nearest [3] is 1-nn lookup.
def kmeans(tbl, rows): # [1]
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

def kpp(tbl, rows, k=None, few=256): # [2] kmeans++ seeds
  rows = random.sample(rows, min(few, len(rows)))
  out = [random.choice(rows)]
  while len(out) < (k or the.K):
    ws = [min(xdist(tbl, r, c)**2 for c in out) for r in rows]
    out.append(random.choices(rows, weights=ws)[0])
  return out

def nearest(tbl, row, rows): # [3]
  return min(rows, key=lambda r: xdist(tbl, r, row))


#-- optimize ----------------------------------------------

# Search for good rows without labelling everything. pick [1]
# samples a plausible value for one column. oneplus1 [2] is
# the 1+1 evolution strategy: mutate the current solution,
# keep the mutant if accepted, remember the best ever seen.
# Two customizations: ls [3] accepts only improvements (and
# restarts when stuck); sa [4] is simulated annealing, which
# sometimes accepts worse solutions, less so as time runs out.
# de [6] is differential evolution: build a candidate by
# interpolating [5] between three population members (per
# column, a + f*(b-c), applied with probability cr); keep the
# candidate if it beats the member it challenges.
def pick(col, v=None): # [1] sample a plausible value
  if type(col) is Sym:
    return random.choices(list(col), col.values())[0]
  mu = col[1] if v is None or v == "?" else v
  lo, hi = col[1] - 3*sd(col), col[1] + 3*sd(col)
  new = mu + sd(col)*2*(random.random() + random.random()
                        + random.random() - 1.5)
  return lo + (new - lo) % (hi - lo + 1e-32)

def oneplus1(tbl, mutate, accept, oracle, restart=0): # [2]
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

def ls(tbl, oracle, p=0.5, tries=20): # [3] local search
  def mutate(s):
    at = random.choice(tbl.x)
    for _ in range(tries):
      s2 = list(s); s2[at] = pick(tbl.cols[at], s[at])
      yield tuple(s2)
  return oneplus1(tbl, mutate, lambda en, e, *_: en < e,
                  oracle, the.restart)

def sa(tbl, oracle, m=0.5): # [4] 1983 simulated annealing
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

def interpolate(col, a, b, c, f=0.5): # [5] DE crossover term
  if type(col) is Sym or "?" in (a, b, c):
    return random.choice([a, b, c])
  return a + f*(b - c)

def de(tbl, oracle, np=20, cr=0.9): # [6] storn+price 1997
  pop = random.sample(tbl.rows, np)
  es = [oracle(s) for s in pop]
  h = np
  while h < the.budget:
    for i, s in enumerate(pop):
      if h >= the.budget: break
      a, b, c = random.sample(pop, 3)
      sn = list(s)
      for at in tbl.x:
        if random.random() < cr:
          sn[at] = interpolate(tbl.cols[at], a[at], b[at], c[at])
      en = oracle(tuple(sn)); h += 1
      if en < es[i]: pop[i], es[i] = tuple(sn), en
  return pop[es.index(min(es))]


#-- bayes -------------------------------------------------

# Naive Bayes, used two ways: to pick which row to label next
# (bayes [4], acquireBayes [5]) and to classify (next
# section). like [1] scores one value against one column;
# likes [2] adds the logs of those scores across a row's x
# columns; liked [3] asks several tables "who most likes this
# row?".
def like(col, v, prior=0): # [1] P(v | col)
  if type(col) is Sym:
    return ((col.get(v, 0) + the.m * prior)
            / (size(col) + the.m + 1e-32))
  s = sd(col) + 1e-32
  return exp(-(v-col[1])**2 / (2*s*s)) / sqrt(2*pi*s*s)

def likes(tbl, row, nall, nh): # [2] log P(tbl|row), unscaled
  prior = (len(tbl.rows) + the.k) / (nall + the.k * nh)
  return log(prior) + sum(
    log(1e-32 + like(tbl.cols[at], v, prior))
    for at in tbl.x if (v := row[at]) != "?")

def liked(tbls, row): # [3] most likely of several tables
  n = sum(len(t.rows) for t in tbls.values())
  return max(tbls, key=lambda k:likes(tbls[k],row,n,len(tbls)))

def bayes(tbl, best, rest): # [4] most likely best
  n = len(best.rows) + len(rest.rows)
  return lambda z: likes(best, z, n, 2) - likes(rest, z, n, 2)

def acquireBayes(tbl, cap=None): # [5] label most-likely-best
  return acquire(tbl, cap, bayes)


#-- classify ----------------------------------------------

# The optimizer's parts, reused for classification. confuse
# [1] turns (got, want) pairs into per-class accuracy, recall
# (pd), false alarm (pf) and precision. fitTree [2] and
# fitBayes [3] are rival classifiers built from ezr.py's trees
# and this file's bayes. _klass [4] races fits over the same
# train/test splits, printing one confusion report per fit.
def confuse(pairs): # [1] (got, want)s --> per-klass scores
  out = {}
  for got, want in pairs:
    for x in [got, want]:
      out[x] = out.get(x) or o(l=x, tp=0, fp=0, fn=0)
    if got == want: out[want].tp += 1
    else:           out[want].fn += 1; out[got].fp += 1
  for c in out.values():
    c.tn   = len(pairs) - c.tp - c.fn - c.fp
    c.acc  = (c.tp + c.tn) / len(pairs)
    c.pd   = c.tp / (c.tp + c.fn + 1e-32)
    c.pf   = c.fp / (c.fp + c.tn + 1e-32)
    c.prec = c.tp / (c.tp + c.fp + 1e-32)
  return out

def fitTree(tbl, rows, y): # [2] sqrt-sized leaves
  the.Leaf = int(sqrt(len(rows)))
  tt = tree(clone(tbl, rows), rows, y=y)
  return lambda r: leaf(tt, r)[2]

def fitBayes(tbl, rows, y): # [3] one table per class
  tbls = {}
  for r in rows:
    if y(r) not in tbls: tbls[y(r)] = clone(tbl)
    addRow(tbls[y(r)], r)
  return lambda r: liked(tbls, r)

def _klass(*fits): # [4] each fit(tbl, rows, y) --> predictor
  tbl = Tbl(csv(the.Klass))
  y = lambda r: r[tbl.klass]
  n = len(tbl.rows) // 2
  splits = [random.sample(tbl.rows, len(tbl.rows))
            for _ in range(the.Repeats)] # same splits, all fits
  def one(fit):
    accs, pairs = [], []
    for rows in splits:
      got = fit(tbl, rows[:n], y)
      now = [(got(r), y(r)) for r in rows[n:]]
      pairs += now
      accs += [sum(g == w for g, w in now) / len(now)]
    for c in confuse(pairs).values():
      pc = lambda v: round(100 * v)
      print(f"{fit.__name__:<10} {pc(c.acc):>3} {pc(c.pd):>3}"
            f" {pc(c.pf):>3} {pc(c.prec):>4}"
            f" {tbl.cols[tbl.klass].get(c.l, 0):>6}  {c.l}")
    return accs
  print(f"{'rx':<10} {'acc':>3} {'pd':>3} {'pf':>3}"
        f" {'prec':>4} {'n':>6}  class")
  return [one(fit) for fit in fits]


#-- start-up ----------------------------------------------

# Demos, run from the shell: "ezr_eg --kmeans", or "--all"
# for everything. "-Key val" flags (from the options above or
# ezr.py's) may precede any demo; settings reset after each.
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
  for what in [sa, ls, de]:
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

def test_klass():
  "Tree vs bayes, same splits: confusions, then same?"
  a, b = _klass(fitTree, fitBayes)
  x, z = adds(a), adds(b)
  print(f"\nfitTree {round(100*x[1])} ({round(100*sd(x))})"
        f" fitBayes {round(100*z[1])} ({round(100*sd(z))})"
        f" delta {round(100*abs(x[1] - z[1]))}"
        f" : {'same' if same(a, b, eps=0.01) else 'different'}")

def test_all():
  "Run every demo; exit code counts the crashes"
  sys.exit(sum(print(f"\n# {k[5:]}") or run(f)
               for k, f in list(globals().items())
               if k[:5] == "test_" and f is not test_all))

def main(): # pip entry point
  cli(the, globals(), sys.argv[1:] or ["--help"])

if __name__ == "__main__": main()
