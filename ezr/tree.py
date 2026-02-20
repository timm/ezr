#!/usr/bin/env python3 -B
from ez2 import (BIG,DATA,NUM,Sym,the,
  add,adds,csv,clone,disty,main,o,sd,shuffle, filename)

def treeSelects(rows, at, fn):
  left, right = [], []
  for r in rows:
    if (v := r[at]) != "?": (left if fn(v) else right).append(r)
  return ((left,right) if len(left)>=the.leaf and len(right)>=the.leaf
          else (None, None))

def treeSplits(col, rows):
  at = col.at
  if Sym is col.it:
    for v in set(r[at] for r in rows if r[at] != "?"):
      left, right = treeSelects(rows, at, lambda x: x == v)
      if left: yield v, left, right
  else:
    vals = sorted(r[at] for r in rows if r[at] != "?")
    if len(vals) >= 2:
      med = vals[len(vals) // 2]
      left, right = treeSelects(rows, at, lambda x: x <= med)
      if left: yield med, left, right

def TREE(data, rows):
  center = mids(clone(data,rows))
  tree = Thing(mids={col.txt:center[col.at] for col in data.cols.y},
             y = adds(disty(data, r) for r in rows))
  if len(rows) >= 2 * the.leaf:
    best, bestW = None, BIG
    for c in data.cols.x:
      for cut, left, right in treeSplits(c, rows):
        w = sum(len(s)*spread(adds(disty(data,r) for r in s))
                for s in [left,right])
        if w < bestW:
          best, bestW = (c, cut, left, right), w
    if best:
      c, cut, left, right = best
      tree.update(col=c, cut=cut, left=TREE(data, left),
                                  right=TREE(data, right))
  return tree

def treeLeaf(tree, row):
  if "col" in tree:
    v = row[tree.col.at]
    if v == "?": return treeLeaf(tree.left, row)
    kid = (tree.left if (v == tree.cut
                         if Sym is tree.col.it
                         else v <= tree.cut) else tree.right)
    return treeLeaf(kid, row)
  return tree

def treeUsed(tree):
  return {n.col.txt for n,_,_ in treeNodes(tree) if "col" in n}

def treeNodes(tree, lvl=0, pre=""):
  if tree:
    yield tree, lvl, pre
    if "col" in tree:
      op = '==' if Sym is tree.col.it else '<='
      no = '!=' if Sym is tree.col.it else '>'
      for kid, txt in sorted([(tree.left, op), (tree.right, no)],
                              key=lambda p: mid(p[0].y)):
        yield from treeNodes(kid, lvl+1,
                             f"{tree.col.txt} {txt} {say(tree.cut)}")

def treeShow(tree):
  for n, lvl, pre in treeNodes(tree):
    s = f"{'|   '*(lvl-1)}{pre}" if pre else ""
    print(f"{s:{the.Show}} {say(mid(n.y)):>6} ({n.y.n:>3})",say(n.mids))

#-------------------------------------------------
def eg__tree(f: filename):
  "treeing"
  data = DATA(csv(f))
  data1 = clone(data,
                shuffle(data.rows)[:the.Budget])
  treeShow(tree(data1, data1.rows))

def eg__test(f: filename):
  "testing"
  data = DATA(csv(f))
  half = len(data.rows)//2
  Y = lambda r: disty(data,r)
  b4 = sorted(Y(r) for r in data.rows)
  win = lambda r: int(
    100*(1-(Y(r)-b4[0])/(b4[half]-b4[0]+1E-6)))
  wins = NUM()
  for _ in range(60):
    rows = shuffle(data.rows)
    test = rows[half:]
    train = rows[:half][:the.Budget]
    t = tree(clone(data,train), train)
    test.sort(key=lambda r: treeLeaf(t,r).y.mu)
    add(wins, win(min(test[:the.Check], key=Y)))
  print(f"{round(wins.mu)}"
        f" ,sd {round(sd(wins))}"
        f" ,b4 {say(b4[half])}"
        f" ,lo {say(b4[0])}"
        f" ,B {the.Budget}",
    *[f"{s} {len(a)}" for s,a in
      dict(x=data.cols.x, y=data.cols.y,
           r=data.rows).items()],
    *f.split("/")[-2:], sep=" ,")

if __name__=="__main__": main(the,globals())
