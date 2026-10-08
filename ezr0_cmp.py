#!/usr/bin/env python3 -B
# vim: set et sw=2 ts=2 sts=2 cc=75 :
"""
ezr0_cmp.py: two planners, same labels, same rows, same judge.

  inst  ezr0_plan.py: per-label walks, borrowed by the nearest label
  tree  ezr.py's tree, grown on the same labels. Plans go leaf to a
        better leaf and touch only columns tested on that leaf's
        path; each failed test is mended with the target leaf's
        value closest to the row's. Picked per leaf (from the leaf's
        centroid, by most dy/dx) and cached before any row is seen.

Per holdout row, per planner:
  own   dy as the planner's own model sees it (labels only)
          inst: y(near label of row) - y(near label of new row)
          tree: mu(leaf of row)      - mu(leaf of new row)
  judge dy by one shared judge: nearest row of the WHOLE table
        (benchmark only; it reads every label, as `wins` does)
  dx    xdist(row, new row)
  k     columns changed;  cover = share of rows with k > 0

Options:
   -Repeats=20  seeds
   -Test=100    holdout rows planned, per seed (sampled)
"""
import random, sys
import ezr as E
from ezr0_plan import *

the.Repeats, the.Test = 20, 100

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

def one(seed): # one split: per-row stats for both planners
  t = Tbl(csv(the.File)); random.seed(seed); the.Seed = seed
  rows = random.sample(t.rows, len(t.rows)); n = len(rows)//2
  m, judge = model(t, rows[:n]), lambda r: ydist(t, min(
                 t.rows, key=lambda z: xdist(t, r, z)))
  cache, T, yl = plans(t, m), Trees(t, m), lambda r: ydist(m.lab, r)
  out = o(inst=[], tree=[])
  for r in rows[n:][:the.Test]:              # rows is shuffled already
    a = advise(t, m, cache, r)
    new, lf = treeAdvise(t, T, r)
    for k, nu, own in (
        ("inst", a.row, yl(near(t, m, r)) - yl(a.witness)),
        ("tree", new,   T.mu[id(E.leaf(T.node, r))] - T.mu[id(lf)])):
      out[k] += [o(own=own, judge=ydist(t, r) - judge(nu),
                   dx=xdist(t, r, nu),
                   k=sum(r[c.at] != nu[c.at] for c in t.x))]
  return out

def report(R):
  med  = lambda xs: sorted(xs)[len(xs)//2]
  print(f"{'':6}{'own dy':>14}{'judge dy':>14}{'dx':>14}"
        f"{'k':>6}{'cover':>7}   (mean/median)")
  for k, ss in R.items():
    f = lambda a: f"{sum(a)/len(a):7.3f}{med(a):7.3f}"
    print(f"{k:6}{f([s.own for s in ss])}{f([s.judge for s in ss])}"
          f"{f([s.dx for s in ss])}{sum(s.k for s in ss)/len(ss):6.2f}"
          f"{sum(s.k > 0 for s in ss)/len(ss):7.0%}")
  for x in ("judge", "dx"):
    a, b = [s[x] for s in R["inst"]], [s[x] for s in R["tree"]]
    print(f"  {x:<6} same by cliffs? {E.cliffs(a, b)}")

if __name__ == "__main__":
  if "-h" in sys.argv: print(__doc__); sys.exit()
  for _k, _v in zip(sys.argv[1:], sys.argv[2:]):
    if _k[1:] in the: the[_k[1:]] = atom(_v)
  _R = o(inst=[], tree=[])
  for _s in range(1, the.Repeats + 1):
    _o = one(_s)
    for _k in _R: _R[_k] += _o[_k]
  print(f"{the.File}  seeds={the.Repeats}  rows={len(_R.inst)}")
  report(_R)
