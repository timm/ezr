#!/usr/bin/env python3 -B 
from types import SimpleNamespace as o
from typing import Any,List
import random,  math, sys, re

the=o(acq="klass", 
      Any=4,      
      Build=24, 
      Check=5,  
      Few=128,
      bins=7,  
      p=2,
      seed=1234567891,
      file="../../moot/optimize/misc/auto93.csv")

#--------------------------------------------------------------------
big = 1e32

def Num(i) return o(it=Num, i=i, n=0, hi=-big, lo=big)
def Sym(i) return o(it=Sym, i=i, n=0, has={})

def Cols(names) -> o:
  all, x, y, klass = [],[],[],None
  for c,s in enumerate(names):
    all += [(Num if s[0].isupper() else Sym)(c)]
    if s[-1] == "X": continue
    (y if s[-1] in "!-+" else x).append(all[-1])
  return o(it=Cols, names=names, all=all, x=x, y=y)

def Data(src) -> o:
  src = iter(src)
  return adds(src, o(it=Data, n=0, mid=None, 
             rows=[], cols= Cols(next(src))))

def Cols(names: List[str]) -> o:
  all, x, y, klass = [],[],[],None
  for c,s in enumerate(names):
    all += [(Num if s[0].isupper() else Sym)(c,s)]
    if s[-1] == "X": continue
    if s[-1] == "!": klass = all[-1]
    (y if s[-1] in "!-+" else x).append(all[-1])
  return o(it=Cols, names=names, all=all, x=x, y=y, klass=klass)

def clone(data:Data, rows=None) -> o:
  return adds(rows or [], Data([data.cols.names]))

#--------------------------------------------------------------------
def adds(src, it=None) -> o:
  for x in src:
     it = it or (Num if isinstance(x,(int,float)) else Sym)()
     add(it, x)
  return it

def sub(x:o, v:Any, zap=False) -> Any: 
  return add(x,v,-1,zap)

def add(x: o, v:Any, inc=1, zap=False) -> Any:
  if v == "?": return v
  if x.it is Sym: x.has[v] = inc + x.has.get(v,0)
  elif x.it is Num:
    x.n += inc
    x.lo, x.hi = min(v, x.lo), max(v, x.hi)
    if inc < 0 and x.n < 2:
      x.mu = x.n = 0
    else:
      d     = v - x.mu
      x.mu += inc * (d / x.n)
  elif x.it is Data:
    x.n += inc
    if inc > 0: x.rows += [v]
    elif zap: x.rows.remove(v) # slow for long rows
    [add(col, v[col.at],inc) for col in x.cols.all]
  return v

#--------------------------------------------------------------------
def norm(num:Num, v:float) -> float:  # 0..1
  return  (v - num.lo) / (num.hi - num.lo + 1E-32)

def mids(data):
  return [mid(col) for col in data.cols.all]

def mid(col):
  return max(col.has, key=col.has.get) if col.it is Sym else col.mu

#--------------------------------------------------------------------
def atom(s):
  for fn in [int,float]:
    try: return fn(s)
    except Exception as _: pass
  s = s.strip()
  return {'True':True,'False':False}.get(s,s)

def csv(file):
  with open(file,encoding="utf-8") as f:
    for line in f:
      if (line := line.split("%")[0]):
        yield [atom(s.strip()) for s in line.split(",")]


#--------------------------------------------------------------------
def dist(src) -> float:
  "general distance function"
  d,n = 0,0
  for v in src: n,d = n+1, d + v**the.p;
  return (d/n) ** (1/the.p)

def disty(data:Data, row:Row) -> float:
  "distance of row to best goal values"
  return dist(abs(norm(c, row[c.at]) - c.more) for c in data.cols.y)

def distysort(data:Data,rows=None) -> List[Row]:
  "sort rows by distance to best goal values"
  return sorted(rows or data.rows, key=lambda r: disty(data,r))

def distx(data, row1, row2):
  "Distance between independent values of two rows."
  def _aha(col, a,b):
    if a==b=="?": return 1
    if col.it is Sym: return a != b
    a,b = norm(col,a), norm(col,b)
    a = a if a != "?" else (0 if b>0.5 else 1)
    b = b if b != "?" else (0 if a>0.5 else 1)
    return abs(a - b)
  return dist(_aha(col, row1[col.at], row2[col.at])  
              for col in data.cols.x)

#--------------------------------------------------------------------
print(Data(csv(the.file)))
def likely(data):
  rows = rows or data.rows
  x = clone(data, shuffle(rows[:]))
  xy,best,rest = clone(data), clone(data), clone(data)
  for _ in range(the.Any): add(xy, sub(x, x.rows.pop()))
  xy.dist = distysort(xy)
  n = round(the.Any**.5)
  adds
