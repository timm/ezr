#!/usr/bin/env python3 -B
"""
attic.py: the regression rig for fast and frugal trees.

`frugals`, `exits` and `fleaf` now live in ezr.py.  What is left
here is the MAE experiment that first measured them.

A frugal tree exits on ONE side of every test, so it is a spine,
not a bush.  Which side, at each depth, is a different inductive
bias -- so one tree hides up to 3^Depth of them and we can shop.
Measured over moot/regression: the shopping never beat the plain
tree it collapsed, at any label budget.  What it buys is a tree
you can read in five questions, not a better one.
(c) 2026 Tim Menzies <timm@ieee.org> MIT license

Options, on top of ezr.py\'s:
      -Frugal=2        most collapses per node (1 or 2)
      -Depth=4         longest spine (so <= 3^Depth trees)
      -Hold=.25        labels kept back to pick the spine
"""
# pylint: disable=bad-indentation,multiple-statements
# pylint: disable=invalid-name,wildcard-import,unused-wildcard-import
# pylint: disable=no-member,assigning-non-slot  # `type()` structs
# pylint: disable=missing-function-docstring,redefined-outer-name
import os, sys, random        # pylint: disable=C0410
import ezr
from ezr import *

# Slots are fixed, so extra options mean a new Settings struct.
ezr.Settings = struct("Settings",
                      **(opts(ezr.__doc__) | opts(__doc__)))
the = ezr.the = ezr.Settings()

def nodes(z: NODE) -> Iterator[NODE]:
  "Every node of a tree, root first."
  yield z
  for k in z.kids: yield from nodes(k)

def fitv(root: NODE, Y: dict, rows: ROWS) -> NODE:
  """What the grown-in predictions cost on held-out ROWS, counted
  at every node a row passes through.  A variant\'s exits are
  disjoint and cover everything, so a row is counted once at
  whichever exit it reaches -- summing VERR over them is exact."""
  for z in nodes(root): z.verr = 0
  for r in rows:
    z = root
    while True:
      z.verr += abs(Y(r) - z.pred)
      if not z.kids: break
      z = z.kids[0 if z.go(r) else 1]
  return root

def frugal(tbl: TBL, rows: ROWS = None) -> list:
  """Of up to 3^Depth frugal trees, the one a held-out slice of
  the labels likes best.  Picking on the rows that grew the tree
  rewards the most elaborate spine, which is how it used to get
  WORSE as the budget rose."""
  rows = random.sample(rows or tbl.rows, len(rows or tbl.rows))
  n    = int((1 - the.Hold) * len(rows))
  grow, pick = (rows[:n], rows[n:]) if n < len(rows) else (rows, [])
  col, Y = target(tbl)
  root = fit(tree(tbl, grow, the.Depth), col, Y)
  cost = (lambda p: sum(x.err for x in exits(p)))     # no holdout
  if pick:
    fitv(root, Y, pick)
    cost = lambda p: sum(x.verr for x in exits(p))
  best, least = None, 1e30                # only ever two paths in
  for path in frugals(root, the.Frugal, the.Depth):   # hand: this
    if (err := cost(path)) < least: best, least = path[:], err
  return best, root

def fmae(path: list, tbl: TBL, rows: ROWS) -> float:
  "MAE, over how far the mean y sits above the best y."
  _, Y = target(tbl)
  vs = [Y(r) for r in rows]
  return (sum(abs(Y(r) - fleaf(path,r).pred) for r in rows) / len(rows)
          / (sum(vs)/len(vs) - min(vs) + 1E-32))

def eg_h() -> None:
  "Show the options and the demos."
  print(__doc__, "Demos:", *[f"  --{k[3:]:<9} {f.__doc__}"
        for k, f in globals().items() if k[:3] == "eg_"], sep="\n")

def eg_fft() -> None:
  """Frugal trees: one tree0, many biases, shop for the best."""
  random.seed(the.Seed)
  t      = Tbl(csv(the.File))
  rows   = random.sample(t.rows, len(t.rows)); n = len(rows)//2
  tr, te = clone(t, rows[:n]), clone(t, rows[n:])
  root   = fit(tree(tr, tr.rows), *target(tr))
  def base(f, tb, rs):       # same scale as fmae, for a reference
    _, Y = target(tb); vs = [Y(r) for r in rs]
    return (sum(abs(Y(r) - f(r)) for r in rs) / len(rs)
            / (sum(vs)/len(vs) - min(vs) + 1E-32))
  c   = t.cols.y          # name the target: a 0.2 on one of them
  tgt = c[0].txt if len(c)==1 else f"ydist of {len(c)} goals"
  print(f"{os.path.basename(the.File)}: {n} train,"     # is not a
        f" {len(te.rows)} test, Frugal={the.Frugal}"    # 0.2 on
        f"\ntarget: {tgt}, MAE over (mean - min)")       # another
  _, Y = target(tr); vs = [Y(r) for r in tr.rows]
  sc = n * (sum(vs)/len(vs) - min(vs))    # fmae's scale, precomputed
  print("  d     N |   best  worst |   test")
  for d in (1, 2, 3, 4, 5):
    best, least, most, N = None, 1e30, -1e30, 0
    for path in frugals(root, the.Frugal, d):
      e = sum(x.err for x in exits(path)) / sc; N += 1
      if e < least: best, least = path[:], e
      most = max(most, e)
    print(f"{d:3} {N:5} | {least:6.3f} {most:6.3f} |"
          f" {fmae(best,tr,te.rows):6.3f}")   # tr: train's scaler
  for txt, f in [("tree0, every leaf", lambda r: leaf(root,r).pred),
                 ("one leaf (the mean)", lambda r: root.pred)]:
    print(f"{txt:>25} | {base(f,tr,tr.rows):6.3f}"
          f" {base(f,tr,te.rows):6.3f}")

def eg_all() -> None:
  "Run every demo; exit code counts the crashes."
  sys.exit(sum(print(f"\n# {k[3:]}") or run(f)
                for k, f in list(globals().items())
                if k[:3] == "eg_" and f is not eg_all))

if __name__ == "__main__":
  main(sys.argv[1:] or ["--h"], globals())
