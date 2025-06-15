from lib import o,isa
import random
from Sym import Sym

the = o(p=2, k=20, Few=128)

def dist(vs):
  "Minkowski distance." 
  n, s = 0, 0
  for x in vs:
    n += 1
    s += abs(x)**the.p
  return (s / n)**(1/the.p)

def ydist(data, row): 
  "Distance to goal (1 for maximize, 0 for minimze)"
  return dist(abs(c.norm(row[c.at]) - c.heaven) for c in data.cols.y)

def ydists(data, rows=None):
  "Return all rows, sorted by ydis tto goals."
  return sorted(rows or data._rows, key=lambda row: ydist(data,row))

def xdists(data, row1, rows=None):
  "Return all rows, sorted by xdist to row1."
  return sorted(rows or data._rows, 
                key=lambda row2: xdist(data,row1,row2))
  
def xdist(data, row1, row2):  
  "Distance between independent attributes."
  return dist(_xdist(c, row1[c.at], row2[c.at]) for c in data.cols.x)

def _xdist(col,u,v):
  "Distance between numeric or symbolic atoms."
  if u=="?" and v=="?": return 1 
  if isa(col, Sym): return u!=v  #1=different, 0=same 
  u = col.norm(u)
  v = col.norm(v)
  u = u if u != "?" else (0 if v > .5 else 1)
  v = v if v != "?" else (0 if u > .5 else 1)
  return abs(u - v) 

#XXX
def knn(data,k,combine):
  seen=[]
  rows = shuffle[data._rows)
  for n,row in enumerate(rows[1:]): 
    combine(xdists(data,row, rows)[:n]),
            the.k, lambda r: ydist(data,r))

def uniform(lst,k,fn):
  "Return average."
  return sum(fn(x) for x in lst[:k])/ len(lst)

def triangle(lst,k,fn):
 "Sort by d, take first k, return weighted v scores ranks."
 wts = [k - i for i in range(k)]
 return sum(w*fn(x) for x,w in zip(lst[:k],wts)) / sum(wts)

def kpp(data, k=None, rows=None):
  "Find k centroids d**2 away from existing centoids."
  row, *rows = shuffle(rows or data._rows)[:the.Few]
  out = [row]
  while len(out) < (k or the.Build):
     ws = [min(xdist(data, r, c)**2 for c in out) for r in rows]
     out.append(random.choices(rows, weights=ws)[0])
  return out, memo 
