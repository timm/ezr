#-- tree --------------------------------------------------
# Node = [edge, n, ymu, ymids, go, kid, kid]
def xpect(a, b): # sizes are >= the.Leaf, so no zero guard
  return ((div(a)*size(a) + div(b)*size(b))/(size(a) + size(b)))

def cutNum(xy, acc): # (left, right, x) per value boundary
  xy.sort()
  here, there = acc(), adds((y for _, y in xy), acc())
  for i, (x, y) in enumerate(xy[:-1]):
    here, there = add(here, y), add(there, y, -1)
    if x != xy[i+1][0]: yield here, there, x

def cutSym(xy, acc): # (in, out, sym), one per symbol
  for v in sorted({x for x, _ in xy}):
    yield (adds((y for x, y in xy if x == v), acc()),
           adds((y for x, y in xy if x != v), acc()), v)

def cut(tbl, rows, ys, acc): # best (col, val) split
  best = (1e30, None, None)
  for at in tbl.x:
    xy = [(x, y) for r,y in zip(rows, ys) if (x := r[at]) != "?"]
    what = cutSym if type(tbl.cols[at]) is Sym else cutNum
    for here, there, v in what(xy, acc):
      if the.Leaf <= size(here) <= len(xy) - the.Leaf:
        if (s := xpect(here, there)) < best[0]:
          best = (s, at, v)
  if best[1] is not None: return best[1:]

def routing(tbl, at, v):
  s, c = tbl.names[at], tbl.cols[at]
  if type(c) is not Sym:
    return (f"{s} <= {round(v,2)}", f"{s} > {round(v,2)}",
            lambda r: (c[1] if r[at] == "?" else r[at]) <= v)
  return (f"{s} = {v}", f"{s} != {v}",
          lambda r: (mid(c) if r[at] == "?" else r[at]) == v)

def tree(tbl, rows, edge="", y=None):
  y    = y or (lambda r: ydist(tbl, r))
  ys   = [y(r) for r in rows]
  acc  = Sym if isinstance(ys[0],str) else Num
  node = [edge, len(rows), mid(adds(ys,acc())), ymids(tbl,rows)]
  if (len(rows) > the.Leaf and (best := cut(tbl, rows, ys,acc))):
    e1, e2, go = routing(tbl, *best)
    yes, no = [], []
    for r in rows:
      (yes if go(r) else no).append(r)
    if yes and no:
      node += [go, tree(tbl, yes, e1, y), tree(tbl, no, e2, y)]
  return node

def kids(n): return n[5:]

def leaf(tr, row):
  while kids(tr): tr = tr[5] if tr[4](row) else tr[6]
  return tr

