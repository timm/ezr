from lib import of
from obj import obj
from data import Data

def _aha(col,u,v):
  "Distance between numeric or symbolic atoms."
  if u=="?" and v=="?": return 1 
  if col.it is Sym: return u!=v  #1=different, 0=same 
  u = norm(col,u)
  v = norm(col,v)
  u = u if u != "?" else (0 if v > .5 else 1)
  v = v if v != "?" else (0 if u > .5 else 1)
  return abs(u - v) 

def _dist(vs):
  "Minkowski distance." 
  n, s = 0, 0
  for x in vs:
    n += 1
    s += abs(x)**the.p
  return (s / n)**(1/the.p)

@of("Distance between independent attributes.")
def xdist(i:Data, row1, row2):  
  return dist(_aha(c, row1[c.at], row2[c.at]) for c in i.cols.x)

@of("Return all rows, sorted by xdist to row1.")
def xdists(i:Data, row1, rows=None):
  return sorted(rows or o._rows, 
                key=lambda row2: i.xdist(row1,row2))

@of("Distance to goal (1 for maximize, 0 for minimze)")
def ydist(i:Data, row): 
  return _dist(abs(c.norm(row[c.at]) - c.heaven) for c in i.cols.y)

@of("Return all rows, sorted by ydist to goals.")
def ydists(i:Data, rows=None):
  return sorted(rows or i._rows, key=lambda row: i.ydist(row))

@of("Find k centroids d**2 away from existing centoids.")
def kpp(i:Data, k=None, rows=None):
  row, *rows = shuffle(rows or i._rows)[:the.Few]
  out = [row]
  while len(out) < (k or the.Build):
     ws = [min(i.xdist(r, c)**2 for c in out) for r in rows]
     out.append(random.choices(rows, weights=ws)[0])
  return out


