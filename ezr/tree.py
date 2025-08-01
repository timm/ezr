#!/usr/bin/env python3 -B
from data import *
from dist import *

#--------------------------------------------------------------------
treeOps = {'<=' : lambda x,y: x <= y, 
           '==' : lambda x,y:x == y, 
           '>'  : lambda x,y:x > y}

def treeSelects(row,op,at,y): 
  "Have we selected this row?"
  return (x := row[at]) == "?" or treeOps[op](x, y)

def Tree(data, Klass=Num, Y=None, how=None):
  "Create regression tree."
  Y = Y or (lambda row: disty(data, row))
  data.kids, data.how = [], how
  data.ys = adds(Y(row) for row in data.rows)
  if len(data.rows) >= the.leaf:
    hows = [how for col in data.cols.x 
            if (how := treeCuts(col,data.rows,Y,Klass))]
    if hows:
      for how1 in min(hows, key=lambda c: c.div).hows:
        rows1 = [r for r in data.rows if treeSelects(r, *how1)]
        if the.leaf <= len(rows1) < len(data.rows):
          data.kids += [Tree(clone(data,rows1), Klass, Y, how1)]
  return data

def treeCuts(col, rows, Y, Klass):
  "Divide a col into ranges."
  def _sym(sym):
    d, n = {}, 0
    for row in rows:
      if (x := row[col.at]) != "?":
        n += 1
        d[x] = d.get(x) or Klass()
        add(d[x], Y(row))
    return o(div = sum(c.n/n * div(c) for c in d.values()),
             hows = [("==",col.at,x) for x in d])
  def _num(num):
    out, b4, lhs, rhs = None, None, Klass(), Klass()
    xys = [(row[col.at], add(rhs, Y(row))) # add returns the "y" value
           for row in rows if row[col.at] != "?"]
    for x, y in sorted(xys, key=lambda z: z[0]):
      if x != b4 and the.leaf <= lhs.n <= len(xys) - the.leaf:
        now = (lhs.n * lhs.sd + rhs.n * rhs.sd) / len(xys)
        if not out or now < out.div:
          out = o(div=now, hows=[("<=",col.at,b4), (">",col.at,b4)])
      add(lhs, sub(rhs, y))
      b4 = x
    return out
  return (_sym if col.it is Sym else _num)(col)

#--------------------------------------------------------------------
def treeNodes(data, lvl=0, key=None):
  "iterate over all treeNodes"
  yield lvl, data
  for j in sorted(data.kids, key=key) if key else data.kids:
    yield from treeNodes(j,lvl + 1, key)

def treeLeaf(data, row):
  "Select a matching leaf"
  for j in data.kids or []:
    if treeSelects(row, *j.how): return treeLeaf(j,row)
  return data

def treeShow(data, key=lambda d: d.ys.mu):
  "Display tree with #rows and win% columns"
  ats = {}
  print(f"{'#rows':>6} {'win':>4}")
  for lvl, d in treeNodes(data, key=key):
    if lvl == 0: continue
    op, at, y = d.how
    name = data.cols.names[at]
    indent = '|  ' * (lvl - 1)
    expl = f"if {name} {op} {y}"
    score = int(100 * (1 - (d.ys.mu - data.ys.lo) /
             (data.ys.mu - data.ys.lo + 1e-32)))
    leaf = ";" if not d.kids else ""
    print(f"{d.ys.n:6} {score:4}    {indent}{expl}{leaf}")
    ats[at] = 1
  used = [data.cols.names[at] for at in sorted(ats)]
  print(len(data.cols.x), len(used), ', '.join(used))

#--------------------------------------------------------------------
def eg__tree():
  "generate and print a tree"
  data1 = Data(csv(the.file))
  data2 = clone(data1, random.choices(data1.rows, k=32))
  treeShow(Tree(data2))

def eg__all()  : mainAll(globals())
def eg__list() : mainList(globals())
def eg_h()     : print(helpstring)
if __name__ == "__main__": main(globals())
