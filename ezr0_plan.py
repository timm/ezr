#!/usr/bin/env python3 -B
# vim: set et sw=2 ts=2 sts=2 cc=75 :
"""
ezr0_plan.py: plan by least change, on top of ezr0.py.

For each labelled row: walk the x columns in power order (widest
best-to-rest gap first). On each column, try Steps moves toward two
targets (the best label's x, and mid(best)); keep the move with the
biggest dy/dx; bisect back to the least move that keeps that gain;
lock it in; go to the next column. Cache that plan.
To plan any other row, borrow the cached plan of its nearest label.

Clusters: fastmap the labels down to leaves of Few or so. Per leaf,
walk its centroid toward each better leaf's centroid (same walk;
witness = nearest leaf centroid, scored by the leaf's mean y); keep
the best dy/dx. A row borrows its nearest leaf's plan.

Stop a walk when the next column's power < Cut% of the top power,
or when the y gap left is within Enough% of the y gap at the start.

With Push=1, a column where no single step helps still moves (all
the way to mid(best)), since in many dimensions one column rarely
moves a labelled row off itself. The walk is then cut back to the
prefix with the most total dy (fewest changes, on ties).

Options:
   -Steps=4     moves tried, per target, per column
   -Bisect=6    halvings, to find the least move that still helps
   -Enough=10   stop once the y gap left is under this % of the start
   -Push=1      1 = move anyway when no step helps; 0 = skip the column
   -Kmax=0      most columns a plan may change; 0 = no cap
   -Few=3       clusters: fastmap leaves hold Few..2*Few-1 labels
"""
import random, sys
from ezr0 import *

the.Steps, the.Bisect, the.Enough = 4, 6, 10
the.Push, the.Kmax, the.Few = 1, 0, 3

def towards(col, a, b, f): # fraction F of the way from A to B
  if type(col) is Sym or a == "?" or b == "?": return b
  return a + (b - a) * f

def near(tbl, m, row): # nearest labelled row: what we know about ROW
  return min(m.lab.rows, key=lambda z: xdist(tbl, row, z))

def walk(tbl, r0, goals, gs, near, y, ylo): # the walk, any witnesses
  """From R0, over columns GS (power, at), toward GOALS. NEAR maps a
  row to its witness, Y scores a witness, YLO is the best Y."""
  w = near(r0); y0 = y(w)
  now, out, seen = r0.copy(), [], [(0, 0, r0.copy(), w)]
  for _, at in gs:
    if the.Kmax and len(out) >= the.Kmax: break        # change budget
    col, top = tbl.cols[at], None
    for g in goals:
      for k in range(1, the.Steps + 1):
        new = now.copy()
        new[at] = towards(col, now[at], g[at], k/the.Steps)
        if new[at] == now[at]: continue
        w2 = near(new)
        dy, dx = y(w) - y(w2), xdist(tbl, now, new)     # marginal
        if dy > 0 and (top is None or dy/dx > top[0]):
          top = (dy/dx, new, w2, g, k)
    if top is None:                           # no single step helps
      if not the.Push or now[at] == goals[-1][at]: continue
      new = now.copy(); new[at] = goals[-1][at]
      top = (0, new, near(new), goals[-1], the.Steps)
    _, new, w2, g, k = top
    lo, hi = (k-1)/the.Steps, k/the.Steps     # bisect: least move that
    for _ in range(the.Bisect):               # still reaches w2
      f = (lo + hi) / 2
      tmp = now.copy(); tmp[at] = towards(col, now[at], g[at], f)
      if tmp[at] != now[at] and near(tmp) is w2: hi, new = f, tmp
      else: lo = f
    now, w = new, w2                                        # lock it
    out += [o(at=at, was=r0[at], to=now[at])]
    seen += [(y0 - y(w), xdist(tbl, r0, now), now, w)]
    if y(w) - ylo <= the.Enough/100 * (y0 - ylo): break   # near enough
  i = max(range(len(seen)), key=lambda j: (seen[j][0], -j)) # most dy,
  if seen[i][0] <= 0: i = 0                 # then fewest changes
  return o(changes=out[:i], row=seen[i][2], witness=seen[i][3],
           dy=seen[i][0], dx=seen[i][1])

def strong(gs): # (power, at) pairs, strongest first, minus weak ones
  gs = sorted(gs, key=lambda z: -z[0])
  return [z for z in gs if z[0] >= the.Cut/100 * gs[0][0]]

def plan1(tbl, m, r0): # least change to labelled R0, most y per x
  y = lambda r: ydist(m.lab, r)
  return walk(tbl, r0, (m.lab.rows[0], mids(m.best)),   # row1, mid(best)
              strong((p, at) for p, at, _ in gaps(tbl, m)),
              lambda r: near(tbl, m, r), y, y(m.lab.rows[0]))

def plans(tbl, m): # one cached plan per labelled row
  return {id(r): plan1(tbl, m, r) for r in m.lab.rows}

def apply(tbl, row, changes): # numbers move by deltas; symbols get set
  new = row[:]
  for c in changes:
    col = tbl.cols[c.at]
    num = type(col) is Num and "?" not in (c.was, row[c.at])
    new[c.at] = row[c.at] + (c.to - c.was) if num else c.to
  return new

def advise(tbl, m, cache, row): # borrow the nearest label's plan
  p   = cache[id(near(tbl, m, row))]
  new = apply(tbl, row, p.changes)
  return o(row=new, changes=p.changes, witness=near(tbl, m, new))

#-- clusters: fastmap the labels into small leaves -------------
def halves(tbl, rows): # fastmap: two far points, split at the median
  far = lambda r: max(rows, key=lambda z: xdist(tbl, r, z))
  a = far(random.choice(rows)); b = far(a); c = xdist(tbl, a, b)
  x = lambda r: (xdist(tbl,r,a)**2 + c*c - xdist(tbl,r,b)**2)/(2*c+1e-32)
  rows = sorted(rows, key=x)
  return rows[:len(rows)//2], rows[len(rows)//2:]

def leaves(tbl, m, rows): # recurse until leaves hold Few..2*Few-1
  if len(rows) < 2 * the.Few:
    return [o(rows=rows, c=mids(clone(tbl, rows)),
              mu=sum(ydist(m.lab, r) for r in rows) / len(rows))]
  return [l for h in halves(tbl, rows) for l in leaves(tbl, m, h)]

def Clusters(tbl, m): # per leaf, walk its centroid to a better leaf
  L    = leaves(tbl, m, m.lab.rows)
  near = lambda r: min(L, key=lambda l: xdist(tbl, r, l.c))
  y, ylo, plan = (lambda l: l.mu), min(l.mu for l in L), {}
  for s in L:
    top = None
    for d in L:
      if d.mu >= s.mu: continue
      p = walk(tbl, s.c, (d.c,), strong(
             (gap(c, s.c[c.at], d.c[c.at]), c.at) for c in tbl.x),
             near, y, ylo)
      if p.dy > 0 and (top is None or p.dy/p.dx > top.dy/top.dx): top=p
    plan[id(s)] = top
  return o(leaves=L, near=near, plan=plan)

def clusterAdvise(tbl, C, row): # borrow the nearest leaf's plan
  p = C.plan[id(C.near(row))]
  return apply(tbl, row, p.changes if p else [])

#-- cli ----------------------------------------------------------
if __name__ == "__main__":
  if "-h" in sys.argv: print(__doc__); sys.exit()
  for _k, _v in zip(sys.argv[1:], sys.argv[2:]):
    if _k[1:] in the: the[_k[1:]] = atom(_v)
  _t = Tbl(csv(the.File))
  random.seed(the.Seed)
  _rows  = random.sample(_t.rows, len(_t.rows))
  _m     = model(_t, _rows[:len(_rows)//2])
  _cache = plans(_t, _m)
  _w     = wins(_t)                        # grader only: peeks at all
  _b4, _af, _ks = [], [], []
  for _r in _rows[len(_rows)//2:]:
    _a = advise(_t, _m, _cache, _r)
    _b4 += [_w(_r)]; _af += [_w(_a.witness)]; _ks += [len(_a.changes)]
  _n = len(_b4)
  print(f"rows={_n}  mean changes={sum(_ks)/_n:.1f}"
        f"  win before={sum(_b4)/_n:.0f}  after={sum(_af)/_n:.0f}")
  _r = max(_rows[len(_rows)//2:], key=_m.key)            # a rest row
  _a = advise(_t, _m, _cache, _r)
  print(f"eg: win {_w(_r):.0f} -> {_w(_a.witness):.0f} via",
        " and ".join(f"{_t.names[c.at]}:{say(_r[c.at])}"
                     f"->{say(_a.row[c.at])}" for c in _a.changes))
