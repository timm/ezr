#!/usr/bin/env python3 -B
"""tree.py: regression and classification trees, treeShow, treePlan."""
from ezr import *

class Tree:
  """Decision tree node."""
  def __init__(i, data, rows, klass=None, y=Num):
    klass = klass or (lambda r: disty(data, r))
    i.d = clone(data, rows)
    i.ynum = adds((klass(row) for row in rows), y())
    i.col, i.cut = None, 0
    i.left = i.right = None

def treeCuts(col, rows):
  """Possible split points for a column."""
  if Sym == type(col): return list(col.has.keys())
  vs = [row[col.at] for row in rows if row[col.at] != "?"]
  return [sorted(vs)[len(vs)//2]] if vs else []

def treeSplit(data, col, cut, rows, klass=None, y=Num):
  """Evaluate split on col at cut."""
  klass = klass or (lambda r: disty(data, r))
  l_rows, r_rows, l_y, r_y = [], [], y(), y()
  for row in rows:
    v = row[col.at]
    go = v == "?" or (v == cut if Sym == type(col) else v <= cut)
    (l_rows if go else r_rows).append(row)
    add(l_y if go else r_y, klass(row))
  s = l_y.n * spread(l_y) + r_y.n * spread(r_y)
  return s, col, cut, l_rows, r_rows

def treeGrow(data, rows, klass=None, y=Num):
  """Grow tree to minimize Y-variance (or entropy if y=Sym)."""
  tree = Tree(data, rows, klass, y)
  if len(rows) >= 2 * the.learn.leaf:
    splits = (treeSplit(data, col, cut, rows, klass, y)
              for col in tree.d.cols.xs
              for cut in treeCuts(col, rows))
    if valid := [s for s in splits
                 if min(len(s[3]), len(s[4])) >= the.learn.leaf]:
      _, tree.col, tree.cut, left, right = min(
        valid, key=lambda x: x[0])
      tree.left  = treeGrow(data, left,  klass, y)
      tree.right = treeGrow(data, right, klass, y)
  return tree

def treeLeaf(tree, row):
  """Find leaf node for row."""
  if not tree.left: return tree
  v = row[tree.col.at]
  go = v != "?" and (v <= tree.cut if Num == type(tree.col) else v == tree.cut)
  return treeLeaf(tree.left if go else tree.right, row)

def treeNodes(tree, lvl=0, col=None, op="", cut=None):
  """Yield all nodes (depth-first)."""
  yield tree, lvl, col, op, cut
  if tree.col:
    ops = ("<=", ">") if Num == type(tree.col) else ("==", "!=")
    kids = sorted([(tree.left, ops[0]), (tree.right, ops[1])],
                  key=lambda z: mid(z[0].ynum))
    for k, txt in kids:
      if k: yield from treeNodes(k, lvl+1, tree.col, txt, tree.cut)

def treeShow(tree):
  """Print tree structure."""
  for t1, lvl, col, op, cut in treeNodes(tree):
    p = f"{col.txt} {op} {o(cut)}" if col else ""
    if lvl > 0: p = "|   " * (lvl-1) + p
    g = {col.txt: mid(col) for col in t1.d.cols.ys}
    print(f"{p:<{the.show.show}}"
          f",{o(mid(t1.ynum)):>4}"
          f" ,({t1.ynum.n:3}), {o(g)}")

def treePlan(tree, here):
  """Plans to improve from current leaf."""
  eps = the.stats.eps * spread(tree.ynum)
  for there, _, _, _, _ in treeNodes(tree):
    if there.col is None and \
        (dy := mid(here.ynum) - mid(there.ynum)) > eps:
      diff = [f"{col.txt}={o(mid(col))}"
              for col, h in zip(there.d.cols.xs, here.d.cols.xs)
              if mid(col) != mid(h)]
      if diff:
        yield dy, mid(there.ynum), diff

def cli(argv):
  """Grow regression tree on FILE and show it."""
  if not argv: print("usage: ezr tree FILE"); return
  d = Data(csv(argv[0]))
  treeShow(treeGrow(d, d.rows))

if __name__ == "__main__":
  cli(sys.argv[1:])
