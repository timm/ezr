#!/usr/bin/env python3 -B
import sys,random
rand=random.random

class It(dict):
  __getattr__,__setattr__ = dict.__getitem__,dict.__setitem__
  __repr__= lambda self: o(self)

the = It(Keep=256, seed=1)
random.seed(the.seed)

from typing import Iterable,Any
Qty  = int | float
Row  = list[Qty | str]
Rows = list[Row]

Num,Sym,isa = list,dict,isinstance

def Col(s:str) -> Num | Sym: 
  return (Num if s[0].isupper() else Sym)()

def mid(col:Col) -> Any:
  return col[len(col)//2] if isa(col,Num) else max(col, key=col.get)

def sd(n:Num) -> float: 
  i = len(n)//10; return (n[9*i] - n[i]) / 2.56

def ent(d:Sym) -> float: 
  N = sum(d.values())
  return -sum(p*log(p,2) for n in d.values() if (p:=n/N)>0)

def norm(c:Col,v) -> float:
  if v=="?" or isa(c,Sym): return v
  lo,hi = c[0],c[-1]
  return (v - lo) / (hi - lo + 1E-32)

def keep(l:Num, v:Any, seen:int):
  if len(l) < the.Keep: 
    l += [v]
  elif rand() < the.Keep / seen:
    l[int(rand() * the.Keep)] = v

#--------------------------------------------------------------------
def Data(items:Iterable):
  d = It(rows=[], cols=None, mids=None)
  for row in items: adds(d,row)
  return d

def adds(d:Data, row:Row):
  if not d.cols: # reading row0 with column names
    cols   = {i:Col(s) for i,s in enumerate(row)}
    x      = {i:col for i,col in cols.items() if row[i][-1] not in "-+!X"}
    y      = {i:col for i,col in cols.items() if row[i][-1]     in "-+!" }
    w      = {i:row[i][-1] != "!" for i in y}
    d.cols = It(names=row, all=cols, x=x, y=y, w=w)
  else: # reading remaining rows
    d.mid = None
    d.rows.append(row)
    for i, col in d.cols.all.items(): add(col, row[i], len(d.rows))

def add(c:Col, v:Any, seen=0):
  if v != "?":
    if isa(c,Sym): c[v] = 1 + c.get(v, 0)
    else: keep(c,v,seen)
  return v

def ok(data):
  if not data.mids:
    [col.sort() for col in data.cols.all.values() if isa(col,Num)]
    data.mids = [mid(col) for col in data.cols.all.values()]
  return data

#--------------------------------------------------------------------
def minkowski(items):
  n,d = 0,0
  for item in items: n, d = n+1, d+item ** the.p
  return 0 if n==0 else (d / n) ** (1 / the.p)

def disty(data, row):
  return minkowski((norm(y, row[n]) - data.ok().cols.w[n]) 
                   for n,y in data.cols.y.items())

def o(t):
  match t:
    case dict(): return "{" + " ".join(f":{k} {o(t[k])}" for k in t) + "}"
    case float(): return f"{int(t)}" if int(t) == t else f"{t:.{the.decs}f}"
    case _: return str(t)

CASTS = [int,float,lambda s: {"true":1,"false":0}.get(s.lower(),s)]

def cast(s):
  for f in CASTS:
    try: return f(s)
    except ValueError: ...

def csv(f):
  with open(f,encoding="utf-8") as file:
    for s in file:
      if s:=s.partition("#")[0].strip(): 
        yield [cast(x.strip()) for x in s.split(",")]

#-----------------------------------------------------
def eg_h(): print(__doc__)

def eg_s(n:int): the.seed=n; random.seed(the.seed)
def eg_K(n:int): the.Keep=n

def eg__the(): print(the)

def eg__keep(): 
  the.Keep,lst = 32,[]
  for i in range(10**3): keep(lst,i,i)
  print(sorted(lst))

def eg__csv(f:str):
  for row in csv(f): print(row)

def eg__data(f:str):
  d = ok(Data(csv(f)))
  for row in d.rows: print(row)
  print("mid",ok(d).mids)

#-----------------------------------------------------

def main(settings,funs):
  args = iter(sys.argv[1:])
  for s in args:
    if f := funs.get(f"eg_{s[1:].replace('-','_')}"):
      f(*[cast(next(args)) for t in f.__annotations__.values()])

if __name__ == "__main__": main(the,globals())
