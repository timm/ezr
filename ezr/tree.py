#!/usr/bin/env python3 -B
from ez import (BIG, Data, Num, Sym, the, Rows, Row, Col,
  add, adds, csv, clone, disty, main, sd, shuffle,
  mids, mid, say, spread, O)

def treeSelects(rows:Rows, at:int, fn:callable) -> (Rows,Rows):
  left, right = [], []
  for r in rows:
    if (v := r[at]) != "?": (left if fn(v) else right).append(r)
  if len(left) >= the.leaf and len(right) >= the.leaf: return (left,right)
  return (None, None)

def treeSplits(c:Col, rows:Rows) -> tuple[int,Rows,Rows]:
  if Sym is c.it:
    for v in set(r[c.at] for r in rows if r[c.at] != "?"):
      left, right = treeSelects(rows, c.at, lambda x: x == v)
      if left: yield v, left, right
  else:
    vals = sorted(r[c.at] for r in rows if r[c.at] != "?")
    if len(vals) >= 2:
      med = vals[len(vals) // 2]
      left, right = treeSelects(rows, c.at, lambda x: x <= med)
      if left: yield med, left, right

def Tree(d:Data, rows:Rows) -> O:
  center = mids(clone(d,rows))
  t = O(mids={col.txt:center[col.at] for col in d.cols.y},
               y = adds(disty(d, r) for r in rows))
  if len(rows) >= 2 * the.leaf:
    best, bestW = None, BIG
    for c in d.cols.x:
      for cut, left, right in treeSplits(c, rows):
        w = sum(len(s)*spread(adds(disty(d,r) for r in s))
                for s in [left,right])
        if w < bestW:
          best, bestW = (c, cut, left, right), w
    if best:
      c, cut, left, right = best
      t.update(col=c, cut=cut, left=Tree(d, left),
                               right=Tree(d, right))
  return t

def treeLeaf(t:Tree, row:Row) -> Tree:
  if "col" in t:
    v = row[t.col.at]
    if v == "?": return treeLeaf(t.left, row)
    kid = (t.left if (v == t.cut
                         if Sym is t.col.it
                         else v <= t.cut) else t.right)
    return treeLeaf(kid, row)
  return t

def treeUsed(t) -> set:
  return {n.col.txt for n,_,_ in treeNodes(t) if "col" in n}

def treeNodes(t, lvl=0, pre="") -> tuple[Tree,int,str]:
  if t:
    yield t, lvl, pre
    if "col" in t:
      op = '==' if Sym is t.col.it else '<='
      no = '!=' if Sym is t.col.it else '>'
      for kid, txt in sorted([(t.left, op), (t.right, no)],
                              key=lambda p: mid(p[0].y)):
        yield from treeNodes(kid, lvl+1,
                             f"{t.col.txt} {txt} {say(t.cut)}")

def treeShow(t:Tree):
  for n, lvl, pre in treeNodes(t):
    s = f"{'|   '*(lvl-1)}{pre}" if pre else ""
    print(f"{s:{the.Show}} {say(mid(n.y)):>6} ({n.y.n:>3})",O(**n.mids))

#-------------------------------------------------
def eg__tree(f: str):
  "treeing"
  data = Data(csv(f))
  data1 = clone(data,
                shuffle(data.rows)[:the.Budget])
  treeShow(Tree(data1, data1.rows))

def eg__test(f: str):
  "testing"
  data = Data(csv(f))
  half = len(data.rows)//2
  Y = lambda r: disty(data,r)
  b4 = sorted(Y(r) for r in data.rows)
  win = lambda r: int(
    100 * (1 - (Y(r) - b4[0])/(b4[half] - b4[0] + 1E-3)))
  wins = Num()
  for _ in range(60):
    rows = shuffle(data.rows)
    test = rows[half:]
    train = rows[:half][:the.Budget]
    t = Tree(clone(data,train), train)
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

if __name__=="__main__": main(globals())
