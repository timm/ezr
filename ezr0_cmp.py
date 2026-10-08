#!/usr/bin/env python3 -B
# vim: set et sw=2 ts=2 sts=2 cc=75 :
"""
ezr0_cmp.py: two planners, same labels, same rows, same judge.

  inst  ezr0_plan.py: per-label walks, borrowed by the nearest label
  fmap  ezr0_plan.py's clusters: fastmap leaves of ~Few labels; same
        free walk (steps, bisect), centroid to a better centroid
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

Options:
   -Repeats=20  seeds
   -Test=100    holdout rows planned, per seed (sampled)
   -Judge=64    rows held out for the judge, per seed
"""
import random, sys
import ezr as E
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

def one(t, w, seed): # one split: per-row wins for both planners
  random.seed(seed); the.Seed = seed
  rows  = random.sample(t.rows, len(t.rows))
  pool, rows = rows[:the.Judge], rows[the.Judge:]   # judge, then 50:50
  n     = len(rows)//2
  m     = model(t, rows[:n])
  judge = lambda r: w(min(pool, key=lambda z: xdist(t, r, z)))
  cache, C, T = plans(t, m), Clusters(t, m), Trees(t, m)
  out = o(inst=[], fmap=[], tree=[])
  for r in rows[n:][:the.Test]:              # rows is shuffled already
    for k, nu in (("inst", advise(t, m, cache, r).row),
                  ("fmap", clusterAdvise(t, C, r)),
                  ("tree", treeAdvise(t, T, r)[0])):
      out[k] += [o(win0=judge(r), win1=judge(nu), dx=xdist(t, r, nu),
                   k=sum(r[c.at] != nu[c.at] for c in t.x))]
  return out

def report(R):
  med = lambda xs: sorted(xs)[len(xs)//2]
  f   = lambda a: f"{sum(a)/len(a):7.1f}{med(a):6.1f}"
  g   = lambda a: f"{sum(a)/len(a):7.3f}{med(a):6.3f}"
  print(f"{'':6}{'win0':>13}{'win1':>13}{'gain':>13}{'dx':>13}"
        f"{'k':>6}{'gain/k':>8}{'cover':>7}   (mean, median)")
  for k, ss in R.items():
    print(f"{k:6}{f([s.win0 for s in ss])}{f([s.win1 for s in ss])}"
          f"{f([s.win1 - s.win0 for s in ss])}{g([s.dx for s in ss])}"
          f"{sum(s.k for s in ss)/len(ss):6.2f}"
          f"{sum(s.win1-s.win0 for s in ss)/(sum(s.k for s in ss)+1e-32):8.1f}"
          f"{sum(s.k > 0 for s in ss)/len(ss):7.0%}")
  for x in ("win1", "dx"):
    for p, q in (("inst", "tree"), ("fmap", "tree"), ("inst", "fmap")):
      a, b = [s[x] for s in R[p]], [s[x] for s in R[q]]
      print(f"  {x:<5} {p}, {q} same by cliffs? {E.cliffs(a, b)}")

if __name__ == "__main__":
  if "-h" in sys.argv: print(__doc__); sys.exit()
  for _k, _v in zip(sys.argv[1:], sys.argv[2:]):
    if _k[1:] in the: the[_k[1:]] = atom(_v)
  _t = Tbl(csv(the.File)); _w = wins(_t)  # load once
  _R = o(inst=[], fmap=[], tree=[])
  for _s in range(1, the.Repeats + 1):
    _o = one(_t, _w, _s)
    for _k in _R: _R[_k] += _o[_k]
  print(f"{the.File}  seeds={the.Repeats}  rows={len(_R.inst)}")
  report(_R)
