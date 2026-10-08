#!/usr/bin/env python3 -B
# vim: set et sw=2 ts=2 sts=2 cc=75 :
"""
ezr0_cmp.py: two planners, same labels, same rows, same judge.

  inst  ezr0_plan.py: per-label walks, borrowed by the nearest label
  fmap  ezr0_plan.py's clusters: fastmap leaves of ~Few labels; same
        free walk (steps, bisect), centroid to a better centroid
  bins  ezr1.py: binned rows, columns ranked by b^2/(b+r), bin jumps
        (bins = Cut 10, bins50 = Cut 50)
  tree  ezr.py's tree, grown on the same labels. Plans go leaf to a
        better leaf and touch only columns tested on that leaf's
        path; each failed test is mended with the target leaf's
        value closest to the row's. Picked per leaf (from the leaf's
        centroid, by most dy/dx) and cached before any row is seen.

Per holdout row, per planner, in wins (100 = best row, 0 = average):
  win0  the row, as the judge sees it
  win1  the changed row, as the judge sees it
        judge = nearest of Judge rows, held out before the split:
        labelled, but never seen by either planner
  dx    xdist(row, changed row)
  k     columns changed;  gain/k = total gain / total k
  cover share of rows with k > 0

Usage: ./ezr0_cmp.py [-Option value].. [--rank file.csv..]

Options:
   -Repeats=20  seeds
   -Test=100    holdout rows planned, per seed (sampled)
   -Judge=64    rows held out for the judge, per seed
"""
import os, random, sys, time
import ezr as E
import ezr1 as B
from ezr0_plan import *

the.Repeats, the.Test, the.Judge = 20, 100, 64

def paths(node, conds=()): # (leaf, [(at, go, wanted)]) for each leaf
  if not node.kids: yield node, list(conds); return
  for kid, want in zip(node.kids, (True, False)):
    yield from paths(kid, conds + ((node.at, node.go, want),))

def mend(tbl, row, leaf, conds): # least edit that lands ROW in LEAF
  new = row.copy()
  for at in {at for at, go, want in conds if go(row) != want}:
    col = tbl.cols[at]
    vs  = [r[at] for r in leaf.rows if r[at] != "?"] or ["?"]
    new[at] = min(vs, key=lambda v: gap(col, row[at], v))
  return new

def Trees(tbl, m): # grow, then cache one target per leaf
  node = E.tree(lab := E.clone(E.Tbl([tbl.names]), m.lab.rows),
                lab.rows)
  ps   = list(paths(node))
  mu   = {id(l): sum(ydist(m.lab, r) for r in l.rows)/len(l.rows)
          for l, _ in ps}
  plan = {}
  for src, _ in ps:
    c, top = mids(clone(tbl, src.rows)), None
    for dst, conds in ps:
      if mu[id(dst)] >= mu[id(src)]: continue
      new = mend(tbl, c, dst, conds)
      if E.leaf(node, new) is not dst: continue
      r = (mu[id(src)] - mu[id(dst)]) / (xdist(tbl, c, new) + 1e-32)
      if top is None or r > top[0]: top = (r, dst, conds)
    plan[id(src)] = top and top[1:]
  return o(node=node, mu=mu, plan=plan)

def treeAdvise(tbl, T, row):
  here = E.leaf(T.node, row)
  if not (p := T.plan[id(here)]): return row[:], here
  new = mend(tbl, row, *p)
  return new, E.leaf(T.node, new)

def binsAdvise(t1, m1, cache, r1): # a bins plan, back in raw cells
  nu = B.apply(r1.bins, cache[id(B.near(t1, m1, r1.bins))].changes)
  return [v if nu[at] == r1.bins[at] else B.rebin(t1.cols[at], nu[at])
          for at, v in enumerate(r1.raw)]

KEYS = ("tree", "bins_base", "bins_cuts50")   # add "inst", "fmap" too

def one(t, t1, w, seed): # one split: per-row wins, and secs, per planner
  random.seed(seed); the.Seed = seed
  idx   = random.sample(range(len(t.rows)), len(t.rows))
  rows, rows1 = [t.rows[i] for i in idx], [t1.rows[i] for i in idx]
  pool, rows  = rows[:the.Judge], rows[the.Judge:]  # judge, then 50:50
  rows1 = rows1[the.Judge:]
  n     = len(rows)//2
  m     = model(t, rows[:n])
  judge = lambda r: w(min(pool, key=lambda z: xdist(t, r, z)))
  test  = list(zip(rows[n:], rows1[n:]))[:the.Test]
  B.the.Stop, B.the.Check = the.Stop, the.Check   # same label budget
  def bins(cut):
    def build():
      B.the.Cut = cut; m1 = B.model(t1, rows1[:n])
      cache = {id(r): B.plan1(t1, m1, r) for r in m1.lab.rows}
      return lambda r, r1: binsAdvise(t1, m1, cache, r1)
    return build
  def inst():
    cache = plans(t, m); return lambda r, _: advise(t, m, cache, r).row
  def fmap():
    C = Clusters(t, m); return lambda r, _: clusterAdvise(t, C, r)
  def tree():
    T = Trees(t, m); return lambda r, _: treeAdvise(t, T, r)[0]
  make = dict(inst=inst, fmap=fmap, tree=tree,
              bins_base=bins(10), bins_cuts50=bins(50))
  out, secs = o(), o()
  for k in KEYS:                          # secs = build + plan Test rows
    t0  = time.perf_counter()
    adv = make[k](); nus = [adv(r, r1) for r, r1 in test]
    secs[k] = time.perf_counter() - t0
    out[k] = [o(win0=judge(r), win1=judge(nu), dx=xdist(t, r, nu),
                k=sum(r[c.at] != nu[c.at] for c in t.x))
              for (r, _), nu in zip(test, nus)]
  return out, secs

def report(R):
  med = lambda xs: sorted(xs)[len(xs)//2]
  f   = lambda a: f"{sum(a)/len(a):7.1f}{med(a):6.1f}"
  g   = lambda a: f"{sum(a)/len(a):7.3f}{med(a):6.3f}"
  print(f"{'':12}{'win0':>13}{'win1':>13}{'gain':>13}{'dx':>13}"
        f"{'k':>6}{'gain/k':>8}{'cover':>7}   (mean, median)")
  for k, ss in R.items():
    print(f"{k:12}{f([s.win0 for s in ss])}{f([s.win1 for s in ss])}"
          f"{f([s.win1 - s.win0 for s in ss])}{g([s.dx for s in ss])}"
          f"{sum(s.k for s in ss)/len(ss):6.2f}"
          f"{sum(s.win1-s.win0 for s in ss)/(sum(s.k for s in ss)+1e-32):8.1f}"
          f"{sum(s.k > 0 for s in ss)/len(ss):7.0%}")
  print("  + = ties the best mean, by ezr.same (cliffs and ks)")
  for x, sign in (("win1", 1), ("gain", 1), ("k", -1)):
    print(f"  {x:<5}", "  ".join(f"{k}{m}" for k, m in marks(R, x, sign)))

def get(s, x): return s.win1 - s.win0 if x == "gain" else s[x]

def marks(R, x, sign): # (treatment, '+' if it ties the best mean)
  v   = {k: [get(s, x) for s in ss] for k, ss in R.items()}
  top = max(v, key=lambda k: sign * sum(v[k]) / len(v[k]))
  return [(k, "+" if k == top or E.same(v[k], v[top]) else " ")
          for k in v]

def rank1(f): # one data file: per-row results, and secs, per planner
  the.File = f
  t, t1 = Tbl(csv(f)), B.Tbl(csv(f))
  w, R, S = wins(t), o({k: [] for k in KEYS}), o({k: 0 for k in KEYS})
  for s in range(1, the.Repeats + 1):
    out, secs = one(t, t1, w, s)
    for k in KEYS: R[k] += out[k]; S[k] += secs[k]
  return R, S

def rank(files): # csv: data,,tree,,..; "!" = ranks first (or ties it)
  from concurrent.futures import ProcessPoolExecutor
  with ProcessPoolExecutor() as ex: RS = list(ex.map(rank1, files))
  for x, sign, fmt in (("gain", 1, "{:.1f}"), ("win1", 1, "{:.1f}"),
                       ("k", -1, "{:.2f}")):
    print(f"\n# {x}: mean; ! = ranks first, or ties it by ezr.same")
    print("data,," + ",,".join(KEYS))
    firsts = o({k: 0 for k in KEYS})
    for f, (R, _) in zip(files, RS):
      ms, cells = dict(marks(R, x, sign)), []
      for k in KEYS:
        bang = "!" if ms[k] == "+" else ""; firsts[k] += bool(bang)
        cells += [bang, fmt.format(sum(get(s, x) for s in R[k])/len(R[k]))]
      print(",".join([os.path.basename(f)[:-4]] + cells))
    print(",".join(["firsts"] + [c for k in KEYS for c in ("", str(firsts[k]))]))
    print(",".join(["secs"] + [c for k in KEYS
                     for c in ("", f"{sum(S[k] for _, S in RS):.2f}")]))

if __name__ == "__main__":
  if "-h" in sys.argv: print(__doc__); sys.exit()
  for _k, _v in zip(sys.argv[1:], sys.argv[2:]):
    if _k[1:] in the: the[_k[1:]] = atom(_v)
  if "--rank" in sys.argv:          # ./ezr0_cmp.py [-Opt v].. --rank f..
    rank(sys.argv[sys.argv.index("--rank") + 1:]); sys.exit()
  _R, _ = rank1(the.File)
  print(f"{the.File}  seeds={the.Repeats}  rows={len(_R.tree)}")
  report(_R)
