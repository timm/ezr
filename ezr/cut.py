def CUT(at=0, b=0, score=BIG, lo=-BIG, hi=BIG):
  return OBJ(it=CUT, at=at, b=b, score=score, lo=lo, hi=hi)

def cutScore(n, mu, sd1):
  return BIG if n < the.leaf else sd1

def cutXys(col, pairs):
  right = NUM()
  xys = sorted([(x, add(right, y)) for row, y in pairs
                 if (x := row[col.at]) != "?"])
  return xys, right

def cutBest(data, rows):
  def who(col): return cutSym if SYM is col.it else cutNum
  pairs = [(row, disty(data, row)) for row in rows]
  return min((cut for c in data.cols.x 
                  for cut in who(c)(c, *cutXys(c, pairs))),
             key=lambda c: c.score, default=None)
 
def cutSym(col, xys, _):
  N, d = len(xys), {}
  for x, y in xys:
    if x not in d: d[x] = NUM()
    add(d[x], y)
  for b, num in d.items():
    yield CUT(col.at, b, cutScore(num.n, num.mu, sd(num)))

def cutNum(col, xys, right):
  N = len(xys)
  left, cut = NUM(), CUT()
  old_b = bucket(col, xys[0][0])
  add(left, sub(right, xys[0][1]))
  for x, y in xys[1:]:
    if right.n > 0 and (b := bucket(col, x)) != old_b:
      cut.hi = x
      mu = (left.n*left.mu + right.n*right.mu) / N
      s  = (left.n*sd(left) + right.n*sd(right)) / N
      yield (cut := CUT(col.at, old_b, cutScore(N, mu, s), lo=x))
      old_b = b
    add(left, sub(right, y))
  cut.hi = BIG

def cutSelects(cut, data, row):
  col = data.cols.all[cut.at]
  v = row[col.at]
  if v == "?": return False
  return v == cut.b if SYM is col.it else bucket(col, v) <= cut.b

def cutShow(cut, data, yes):
  col = data.cols.all[cut.at]
  if SYM is col.it:
    return f"{col.txt} {'==' if yes else '!='} {cut.b}"
  return f"{col.txt} {'<' if yes else '>='} {o(cut.hi)}"

#-------------------------------------------------------------------------------
# tree
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
      g = [n.x[c.at] for c in n.root.cols.y]
      print(f"{('| '*(lvl-1)+pre):{the.Show}}: ", end="")
      print(f"{o(n.y.mu):6} : {n.y.n:4} : {o(g)}")
      if n.kids:
        for k in sorted(n.kids, key=lambda k: n.kids[k].y.mu):
          show(n.kids[k], lvl+1, cutShow(n.cut, n.root, k))
  ys = ', '.join([y.txt for y in t.root.cols.y])
  print(f"{'':{the.Show}}  Score       N   [{ys}]")
  show(t, 0, "")
