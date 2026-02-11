#!/usr/bin/env python3 -B
import ez
from ez import BIG, OBJ, DATA, NUM, SYM, the
from ez import add,adds,bucket,clone,csv,disty
from ez import main,mids,o,sd,shuffle,sub,filename

#---------------------------------------------------------------------
# Discretization
def CUT(at=0, b=0, score=BIG, lo=-BIG, hi=BIG):
  return OBJ(it=CUT, at=at, b=b, score=score, lo=lo, hi=hi)

def cutScore(n, mu, sd1):
  return BIG if n < the.leaf else sd1

def cutXys(col, pairs):
  xys, right = [], NUM()
  for row, y in pairs:
    if (x := row[col.at]) != "?":
      add(right, y) 
      xys.append((x, y, bucket(col, x)))
  return sorted(xys, key=lambda p: p[0]), right

def cutBest(data, rows):
  def who(col): return cutSym if SYM is col.it else cutNum
  pairs = [(row, disty(data, row)) for row in rows]
  return min((cut for c in data.cols.x 
                  for cut in who(c)(c, *cutXys(c, pairs))),
             key=lambda c: c.score, default=None)
 
def cutSym(col, xys, _):
  N, d = len(xys), {}
  if N: 
    for x, y, _ in xys: 
      if x not in d: d[x] = NUM()
      add(d[x], y)
    for b, num in d.items():
      yield CUT(col.at, b, cutScore(num.n, num.mu, sd(num)))

def cutNum(col, xys, right):
  N, left, cut = len(xys), NUM(), CUT(at=col.at, lo=-BIG, hi=-BIG)  
  if N > 1:
    x, y, last_b = xys[0]
    pre_x = x            
    add(left, sub(right, y))
    for x, y, b in xys[1:]:
      if b != last_b:
        cut.hi = pre_x    
        if left.n >= the.leaf and right.n >= the.leaf:
          score = cutScore(N,
                           (left.n * left.mu  + right.n * right.mu)  / N,
                           (left.n * sd(left) + right.n * sd(right)) / N)
          yield CUT(col.at, last_b, score, lo=cut.lo, hi=cut.hi)
        cut.lo = pre_x   
        last_b = b
      add(left, sub(right, y))
      pre_x = x
   
def cutSelects(cut, data, row):
  col = data.cols.all[cut.at]
  v = row[col.at]
  if v == "?": return False
  if SYM is col.it: return v == cut.b
  return v <= cut.hi

def cutShow(cut, data, yes):
  col = data.cols.all[cut.at]
  if SYM is col.it:
    return f"{col.txt} {'==' if yes else '!='} {cut.b}"
  return f"{col.txt} {'<=' if yes else '>'} {o(cut.hi)}"

#------------------------------------------------------------------------
# Tree Builder
def Tree(data, uses=None):
  uses = uses or set()
  def grow(rows):
    cut, kids = None, {}
    if len(rows) > the.leaf:
      if (cut := cutBest(data, rows)):
        yes, no = [], []
        for row in rows:
          (yes if cutSelects(cut, data, row) else no).append(row)
        if yes and no:
          if len(yes) >= the.leaf: kids[True] = grow(yes)
          if len(no)  >= the.leaf: kids[False] = grow(no)
          if kids: uses.add(cut.at)
    return OBJ(root=data, kids=kids, cut=cut,
               x=mids(clone(data, rows)),
               y=adds(disty(data, row) for row in rows))
  return grow(data.rows), uses

def treeLeaf(t, row):
  if not t or not t.kids: return t
  kid = t.kids.get(cutSelects(t.cut, t.root, row))
  return treeLeaf(kid, row) if kid else t

def treeShow(t):
  ys = [c for c in t.root.cols.y]
  head = "  ".join(f"{y.txt:>8}" for y in ys)
  def show(n, lvl, pre):
    if n:
      tree = f"{'|.. ' * (lvl - 1)}{pre or ''}"
      g = "  ".join(f"{o(n.x[c.at]):>8}" for c in ys)
      print(f"{tree:{the.Show}}  {o(n.y.mu):>6} ({n.y.n:>3})  {g}")
      if n.kids:
        show(n.kids.get(True), lvl + 1, cutShow(n.cut, n.root, True))
        show(n.kids.get(False), lvl + 1, cutShow(n.cut, n.root, False))
  print(f"{'':{the.Show}}  {'Score':>6} {'N':>5}  {head}")
  show(t, 0, None)

#------------------------------------------------------------------------
def eg__tree(f:filename):
  "treeing"
  data = DATA(csv(f))
  data1 = clone(data, shuffle(data.rows)[:the.Budget])
  tree,_ = Tree(data1)
  treeShow(tree)

def eg__test(f:filename):
  "testing"
  data = DATA(csv(f))
  half  = len(data.rows)//2
  Y    = lambda row: disty(data,row)
  b4   = sorted(Y(row) for row in data.rows)
  win  = lambda r: int(100 * (1 - (Y(r)-b4[0]) / (b4[half]-b4[0] + 1E-6)))
  wins = NUM()
  for _ in range(60):
    rows = shuffle(data.rows)
    test, train = rows[half:], rows[:half][:the.Budget]
    tree,_ = Tree(clone(data,train))
    test.sort(key=lambda row: treeLeaf(tree,row).y.mu)
    add(wins, win(min(test[:the.Check], key=Y)))
  print(f"{round(wins.mu)} ,sd {round(sd(wins))} ,b4 {o(b4[half])} ,lo {o(b4[0])}",
        f" B {the.Budget}",
        *[f"{s} {len(a)}" for s,a in
          dict(x=data.cols.x, y=data.cols.y, r=data.rows).items()],
        *f.split("/")[-2:], sep=" ,")


if __name__ == "__main__": main(the,globals())
