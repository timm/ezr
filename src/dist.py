import random
from aux import big,shuffle
from about import the
from query import norm
from data import Sym

def minkowski(src):
  "Return pth root of the sum of the distances raises to p."
  d, n = 0, 1/big
  for x in src:
    n += 1
    d += x**the.p
  return (d / n)**(1 / the.p)

def ydist(data, row):  
  "Distance to heaven."
  return minkowski(abs(norm(c, row[c.at]) - c.heaven) for c in data.cols.y)

def ydists(data,rows=None):
  "Sort rows by distance to heaven."
  return sorted(rows or data._rows, key=lambda row: ydist(data,row))

def xdist(data, row1, row2):  
  "Distance between independent attributes."
  def _aha(col,u,v):
    if u=="?" and v=="?": return 1 
    if col.it is Sym: return u!=v  
    u = norm(col,u)
    v = norm(col,v)
    u = u if u != "?" else (0 if v > .5 else 1)
    v = v if v != "?" else (0 if u > .5 else 1)
    return abs(u - v) 
  #------------------
  return minkowski(_aha(c, row1[c.at], row2[c.at]) for c in data.cols.x)

def xdists(data, row, rows=None):
  "Sort rows by xdist"
  return sorted(rows or data._rows, key=lambda r:xdist(data,row,r))

def kpp(data, k=None, rows=None):
  "Retuen k points, usually D^2 distance from each other."
  k = k or the.Build
  row,  *rows = shuffle(rows or data._rows)
  some = rows[:the.Few]
  centroids   = [row]
  for _ in range(1, k):
    dists = [min(xdist(data,x,y)**2 for y in centroids) for x in some]
    r     = random.random() * sum(dists)
    for j, d in enumerate(dists):
      r -= d
      if r <= 0:
        centroids.append(some.pop(j))
        break
  return centroids
