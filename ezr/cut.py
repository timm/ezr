from ez import *

#-------------------------------------------------------------------------------
# Data Structures
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
  for x, y, _ in xys: # unpack 3-tuple, ignore bucket 'b'
    if x not in d: d[x] = NUM()
    add(d[x], y)
  for b, num in d.items():
    yield CUT(col.at, b, cutScore(num.n, num.mu, sd(num)))

def cutNum(col, xys, right):
  left, cut = NUM(), CUT(at=col.at, lo=-BIG, hi=-BIG)  
  x, y, last_b = xys[0]
  pre_x = x            # Track previous x to define split boundary
  add(left, sub(right, y))
  for x, y, b in xys[1:]:
    if b != last_b:
      cut.hi = pre_x    
      if left.n >= the.leaf and right.n >= the.leaf:
          yield CUT(col.at, last_b, cutScore(left.n, left.mu, sd(left)), 
                    lo=cut.lo, hi=cut.hi)
      last_b = b
    add(left, sub(right, y))
    pre_x = x          # Update tracker
  cut.hi = BIG

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

#-------------------------------------------------------------------------------
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
  def show(n, lvl, pre):
    if n:
      print(f"{'|.. ' * lvl}{pre or ''}", end="")
      if not n.kids:
        print(f" {o(n.y.mu)} ({n.y.n})")
      else:
        print(f" {o(n.y.mu)} ({n.y.n})")
        show(n.kids.get(True), lvl + 1, cutShow(n.cut, n.root, True))
        show(n.kids.get(False), lvl + 1, cutShow(n.cut, n.root, False))
  show(t, 0, None)
