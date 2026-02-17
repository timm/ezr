#!/usr/bin/env python3 -B
import sys,random
rand=random.random

class It(dict):
  __getattr__,__setattr__ = dict.__getitem__,dict.__setitem__
  __repr__= lambda self: str({k:short(self[k]) for k in self})

the = It(Keep=256, seed=1, decs=2,p=2)
random.seed(the.seed)

from typing import Iterator,Iterable,Any
Qty  = int | float
Row  = list[Qty | str]
Rows = list[Row]
Data = It
Num,Sym,isa = list,dict,isinstance

def Col(s:str) -> Num | Sym: 
  return (Num if s[0].isupper() else Sym)()

def mid(c:Col) -> Any:
  return c[len(c)//2] if isa(c,Num) else max(c, key=c.get)

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
    l[1+int(rand() * (the.Keep -2))] = v

#--------------------------------------------------------------------
def Data(items:Iterable) -> Data:
  d = It(rows=[], cols=None, mids=None)
  for row in items: adds(d,row)
  return d

def adds(d:Data, row:Row):
  if not d.cols: # reading row0 with column names
    cols   = {i:Col(s) for i,s in enumerate(row)}
    x      = {i:c for i,c in cols.items() if row[i][-1] not in "-+!X"}
    y      = {i:c for i,c in cols.items() if row[i][-1]     in "-+!" }
    w      = {i:row[i][-1] != "-" for i in y}
    d.cols = It(names=row, all=cols, x=x, y=y, w=w)
  else: # reading remaining rows
    d.mid = None
    d.rows += [row]
    [add(c,v,len(d.rows)) for i, c in d.cols.all.items() 
                          if (v:=row[i]) != "?"]

def add(c:Col, v:Any, seen=0):
  if isa(c,Sym): c[v] = 1 + c.get(v, 0)
  else: keep(c,v,seen)

def ok(d:Data) -> Data:
  if not d.mids:
    [c.sort() for c in d.cols.all.values() if isa(c,Num)]
    d.mids = [mid(c) for c in d.cols.all.values()]
  return d

#--------------------------------------------------------------------
def minkowski(items: Iterable):
  n,d = 0,0
  for item in items: 
    n, d = n+1, d+item ** the.p
  return (d / n) ** (1 / the.p)

def disty(d:Data, row:Row):
  return minkowski((norm(y, row[n]) - d.cols.w[n]) 
                   for n,y in ok(d).cols.y.items())

def short(x:Any) -> Any:
  if isa(x,float): x= int(x) if int(x) == x else round(x,the.decs)
  return x

CASTS = [int,float,lambda s: {"true":1,"false":0}.get(s.lower(),s)]

def cast(s:str) -> int | float | str:
  for f in CASTS:
    try: return f(s)
    except ValueError: ...

def csv(f:str) -> Iterator[Row]:
  with open(f,encoding="utf-8") as file:
    for s in file:
      if s:=s.partition("#")[0].strip(): 
        yield [cast(x.strip()) for x in s.split(",")]

def align(m: list[list]):
  ws = [max(len(str(x)) for x in col) for col in zip(*m)]
  for l in m: print(", ".join(f"{str(v):>{w}}" for v, w in zip(l,ws)))

#-----------------------------------------------------
def eg_h(): print(__doc__)

def eg_s(n:int): the.seed=n; random.seed(the.seed)
def eg_K(n:int): the.Keep=n

def eg__the(): print(the)

def eg__keep(): 
  the.Keep,lst = 20,[]
  for i in range(10**4): keep(lst,i,i)
  print(sorted(lst))

def eg__csv(file:str):
  align(list(csv(file))[::30])

def eg__data(file:str):
  d = Data(csv(file))
  align([ok(d).mids] + [d.cols.names] + d.rows[::30])

def eg__disty(file:str):
  d = Data(csv(file))
  align([d.cols.names] + sorted(d.rows,key=lambda r:disty(d,r))[::30])

#-----------------------------------------------------

def cli(funs):
  args = iter(sys.argv[1:])
  for s in args:
    if f := funs.get(f"eg_{s[1:].replace('-','_')}"):
      f(*[make(next(args)) for make in f.__annotations__.values()])

if __name__ == "__main__": cli(globals())
