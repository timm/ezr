#!/usr/bin/env python3 -B
"""tree.py: decision tree for multi-objective optimization
(c) 2026 Tim Menzies timm@ieee.org, MIT license"""
from types import SimpleNamespace as o
from ez_class import (BIG, Data, Num, Sym, the, eg_B,
  Row, csv, adds, say, shuffle, main, filename)

Row  = list
Rows = list[Row]

def clone(d:Data, rows:Rows=[]) -> Data:
  return Data([d.cols.names] + rows)

#---- tree construction -----------------------------------------------
def treeSelects(rows:Rows, at:int, fn:callable) -> tuple:
  left, right = [], []
  for r in rows:
    if (v := r[at]) != "?": (left if fn(v) else right).append(r)
  if len(left) >= the.leaf and len(right) >= the.leaf: return left, right
  return None, None

def treeSplits(at:int, col, rows:Rows):
  if isinstance(col, Sym):
    for v in set(r[at] for r in rows if r[at] != "?"):
      left, right = treeSelects(rows, at, lambda x: x == v)
      if left: yield v, left, right
  else:
    vals = sorted(r[at] for r in rows if r[at] != "?")
    if len(vals) >= 2:
      med = vals[len(vals) // 2]
      left, right = treeSelects(rows, at, lambda x: x <= med)
      if left: yield med, left, right

def Tree(d:Data, rows:Rows) -> o:
  mid    = clone(d, rows).mid()
  t      = o(mids={d.cols.names[at]: mid[at] for at in d.cols.y},
             y=adds(d.disty(r) for r in rows))
  if len(rows) >= 2 * the.leaf:
    best, bestW = None, BIG
    for at,col in d.cols.x.items():
      for cut, left, right in treeSplits(at, col, rows):
        w = sum(adds(d.disty(r) for r in s).spread() * len(s)
                for s in [left, right])
        if w < bestW:
          best, bestW = (at, col, cut, left, right), w
    if best:
      at, col, cut, left, right = best
      t.__dict__.update(at=at, col=col, cut=cut,
                        left=Tree(d, left), right=Tree(d, right))
  return t

#---- tree traversal --------------------------------------------------
def treeLeaf(t:o, row:Row) -> o:
  if hasattr(t, 'col'):
    v   = row[t.at]
    if v == "?": return treeLeaf(t.left, row)
    kid = (t.left if (v == t.cut if isinstance(t.col, Sym) else v <= t.cut)
                  else t.right)
    return treeLeaf(kid, row)
  return t

def treeUsed(t:o,d:Data) -> set:
  return {d.cols.names[n.at] for n,_,_ in treeNodes(t,d) if hasattr(n,'col')}

def treeNodes(t:o, d:Data, lvl=0, pre=""):
  if t:
    yield t, lvl, pre
    if hasattr(t, 'col'):
      op = '==' if isinstance(t.col, Sym) else '<='
      no = '!=' if isinstance(t.col, Sym) else '>'
      for kid, txt in sorted([(t.left, op), (t.right, no)],
                              key=lambda p: p[0].y.mid()):
        yield from treeNodes(kid, d, lvl+1,
                     f"{d.cols.names[t.at]} {txt} {say(t.cut)}")

def treeShow(d:Data, t:o):
  for n, lvl, pre in treeNodes(t,d):
    s = f"{'|   '*(lvl-1)}{pre}" if pre else ""
    print(f"{s:{the.Show}} {say(n.y.mid()):>6} ({n.y.seen:>3})", o(**n.mids))

#---- demos -----------------------------------------------------------
def eg__tree(f:filename):
  "show decision tree"
  d  = Data(csv(f))
  d1 = clone(d, shuffle(d.rows)[:the.Budget])
  treeShow(d1, Tree(d1, d1.rows))

def eg__test(f:filename):
  "test tree-guided optimization"
  d    = Data(csv(f))
  half = len(d.rows) // 2
  Y    = lambda r: d.disty(r)
  b4   = sorted(Y(r) for r in d.rows)
  win  = lambda r: int(100*(1-(Y(r)-b4[0])/(b4[half]-b4[0]+1E-3)))
  wins = Num()
  for _ in range(60):
    rows  = shuffle(d.rows)
    test  = rows[half:]
    train = rows[:half][:the.Budget]
    t     = Tree(clone(d, train), train)
    test.sort(key=lambda r: treeLeaf(t, r).y.mid())
    wins.add(win(min(test[:the.Check], key=Y)))
  print(f"{round(wins.mid())}"
        f" ,sd {round(wins.spread())}"
        f" ,b4 {say(b4[half])}"
        f" ,lo {say(b4[0])}"
        f" ,B {the.Budget}"
        f" ,C {the.Check}"
        f" ,U {len(treeUsed(t,d))}",
    *[f"{s} {len(a)}" for s,a in
      dict(x=d.cols.x, y=d.cols.y, r=d.rows).items()],
    *f.split("/")[-2:], sep=" ,")

if __name__ == "__main__": main(globals())
