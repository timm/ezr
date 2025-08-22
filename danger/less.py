from types import SimpleNamespace as o
from typing import Any,List,Iterator
import random, math, sys, re

the=o(Any=4, Build=24, 
      Few=int(math.log(1-.95) / math.log(1-.2/6)),
      p=2,
      seed=1234567891,
      file="../../moot/optimize/misc/auto93.csv")

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

def Data(src=None):
  i = o(rows=[], mid=None, cols=None)
  [add(data,row) for row in src or []]
  return i 

def add(data,row):
  if data.cols:
    mids=None
    data.rows += [row]
    for c,(lo,hi) in data.cols.nums.items(): 
      if (v := rows[c]) != "?":
        data.cols.nums[c] = (min(v,lo), max(v,hi)) 
  else:
    data.cols = o(names = row, 
      x = [c for c,s in enumerate(row) if s not in "X+-"],
      y = {c:(0 if s[-1]=="-" else 1) for c,s in enumerate(row) if s[-1] in "+-"},
      nums={c:(big,-big) for c,s in enumerate(row) if s[0].isupper()})
  return row

def mid(data):
  def mid1(i,s):
    vs = [v for row in data.rows if (v := row[i]) != "?"]
    if i in data.cols.nums: return sorted(vs)[len(vs)//2]
    d = {}
    for x in vs: d[x] = d.get(x, 0) + 1 
    return min(d, key=d.get)
  data.mid = data.mid or [mid1(i,s) for i,s in enumerate(data.names)]
  return data.mid
              
def norm(v,lo,hi) : return (v - lo) / (hi - lo + 1e-32)

def distx(data:Data, row1:Row, row2:Row) -> float:
  def _aha(c, a,b):
    if a==b=="?": return 1
    if c not in data.cols.num: return a != b
    a,b = norm(data.cols.nums[c],a), norm(data.cols.nums[c],b)
    a = a if a != "?" else (0 if b>0.5 else 1)
    b = b if b != "?" else (0 if a>0.5 else 1)
    return abs(a - b)
  return dist(_aha(c, row1[x], row2[x]) for c,v in data.cols.x)

def disty(data, row):
  return dist(abs(norm(row[y],*data.cols.nums[y]) - w) 
              for y,w in data.cols.y.items())

def distysort(data,rows):
  return sorted(rows or data.rows, key=lambda r: disty(data,r))

def dist(src):
  d,n = 0,0
  for v in src: n,d = n+1, d + v**the.p;
  return (d/n) ** (1/the.p)
