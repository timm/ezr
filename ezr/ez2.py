#!/usr/bin/env python3 -B
"""
ez1.py: lightweight incremental Bayes classifier with add/delete support
(c) 2026 Tim Menzies timm@ieee.org, MIT license

Options:
  -b bins=7          discretize numerics into this many bins
  -d decs=2          print floats to this many decimals
  -k k=1             for low value frequencies in Bayes
  -m m=2             for low class frequencies in Bayes
  -p p=2             Minkowski distance coefficient (2:Euclidean)
  -s seed=1          random number seed """
import random, sys, re
from math import sqrt, log, exp
from typing import Iterator, Iterable, Any
rand = random.random

#---- base object ----------------------------------------------------
class Thing(dict):
  __getattr__,__setattr__ = dict.__getitem__,dict.__setitem__
  __repr__ = lambda i: "{"+' '.join(f":{k} {say(i[k])}" for k in i)+"}"

BIG = 1E32
Qty = int | float
Val = Qty | str
Row = list[Val]
Rows = list[Row]
Col,Num,Sym,Data,Cols = Thing,Thing,Thing,Thing,Thing

#---- constructors ---------------------------------------------------
def Col(at=0,txt=" ") -> Col: 
  return (Num if txt[0].isupper() else Sym)(at=at,txt=txt, goal=txt[-1]!="-")

def Num(**d) -> Num: return Thing(it=Num, **d, n=0, mu=0, m2=0)
def Sym(**d) -> Num: return Thing(it=Sym, **d, n=0, has={})

def Data(items:Iterable[Row] = None) -> Data:
  return adds(items, Thing(it=Data, n=0, rows=[], cols=None, mids=None))

def Cols(names: list[str]) -> Cols:
  cols = [Col(i,s) for i,s in enumerate(names)]
  return Thing(it = Cols, names = names, all= cols,
               x = [c for c in cols if c.txt[-1] not in "-+!X"],
               y = [c for c in cols if c.txt[-1]     in "-+!" ])

def clone(data, rows=None): return Data([data.cols.names] + (rows or []))

#---- update ---------------------------------------------------------
def add(t:Thing, v:Val|Row, w=1) -> Any:
  if v != "?":
    t.n += w
    if Sym is t.it: 
      t.has[v] = w + t.has.get(v, 0)
    elif Num is t.it:
      if t.n <= 0: t.n,t.mu,t.m2 = 0,0,0
      else: d = v - t.mu; t.mu += w * d/t.n; t.m2 += w * d*(v - t.mu)
    elif Data is t.it:
      if not t.cols: t.cols = Cols(v)
      else:
        t.mids = None
        for col in t.cols.all: add(col, v[col.at], w)
        (t.rows.append if w > 0 else t.rows.remove)(v)
  return v

def sub(t:Thing, v:Any) -> Any: return add(t, v, w=-1)

def adds(items:Iterable[Row]=None, thing=None) -> Thing:
  thing = thing or Num()
  [add(thing, item) for item in (items or [])]
  return thing

def nearby(c:Col, v:Any) -> Val:
  return pick(c.has) if Sym is c.it else gauss(mid(c) if v=="?" else v,sd(c))

#---- query ----------------------------------------------------------
def mid(c:Col) -> Val:
  return c.mu if Num is c.it else  max(c.has, key=c.has.get)

def mids(d:Data) -> Row:
  d.mids = d.mids or [mid(c) for c in d.cols.all]
  return d.mids

def spread(c:Col) -> float: return ent(c) if Sym is c.it else sd(c)

def sd(num:Num) -> float:
  return 0 if num.n < 2 else sqrt(max(0, num.m2) / (num.n - 1))

def ent(sym:Sym) -> float:
  return -sum(p*log(p,2) for n in sym.has.values() if (p:=n/sym.n) > 0)

#---- normalization --------------------------------------------------
def z(num:Num, v:Qty) -> float:
  return max(-3, min(3, (v - num.mu) / (sd(num) + 1/BIG)))

def norm(c:Col, v:Val) -> Val:
  return v if v == "?" or Sym is c.it else 1 / (1 + exp(-1.7 * z(c, v)))

def bucket(c:Col, v:Any) -> Val:
  return v if (v == "?" or Sym is c.it) else int(the.bins * norm(c, v))

#---- distance -------------------------------------------------------
def minkowski(items: Iterable[Qty]) -> float:
  n, d = 0, 0
  for item in items: 
    n, d = n+1, d + item**the.p
  return 0 if n == 0 else (d / n) ** (1 / the.p)

def disty(d:Data, r:Row) -> float:
  return minkowski((norm(y, r[y.at]) - y.goal) for y in d.cols.y)

def distx(d:Data, r1:Row, r2:Row) -> float:
  return minkowski(aha(x, r1[x.at], r2[x.at]) for x in d.cols.x)

def aha(c:Col, u:Val, v:Val) -> float:
  if u == v == "?": return 1
  if Sym is c.it: return u != v
  u, v = norm(c, u), norm(c, v)
  u = u if u != "?" else (0 if v > 0.5 else 1)
  v = v if v != "?" else (0 if u > 0.5 else 1)
  return abs(u - v)

def furthest(*args) -> Row: return order(*args)[-1]
def nearest(*args)  -> Row: return order(*args)[0]

def order(d:Data, r1:Row, rows:Rows) -> Rows:
  return sorted(rows, key=lambda r2: distx(d, r1, r2))

#---- Bayes ----------------------------------------------------------
def like(c:Col, v:Any, prior=0) -> float:
  if Num is c.it:
    var = sd(c)**2 + 1/BIG
    return (1/sqrt(2*3.14159*var)) * exp(-((v - c.mu)**2) / (2*var))
  else:
    n = c.has.get(v, 0) + the.k * prior
    return max(1/BIG, n / (c.n + the.k))

def likes(d:Data, row:Row, n_all:int, n_h:int) -> float:
  prior = (len(d.rows) + the.m) / (n_all + the.m * n_h)
  likelihoods= (like(x,v,prior) 
                for x in d.cols.x if (v:=row[x.at])!="?")
  return log(prior) + sum(map(log,likelihoods))

#---- lib ------------------------------------------------------------
def says(lst:list,w=None): print(*[say(x,w) for x in lst])

def say(x, w=None):
  if type(x)==type(say): x= x.__name__ or '()'
  elif type(x)==float: x= str(int(x) if int(x)==x else f"{x:.{the.decs}f}")
  else: x= str(x)
  return f"{x:>{w}}" if w else x

def shuffle(lst:list) -> list: random.shuffle(lst); return lst

def pick(d:dict) -> Any:
  n = sum(d.values()) * rand()
  for k, v in d.items():
    if (n := n-v) <= 0: return k

def gauss(mu:float, s:float) -> float:
  return mu + 2 * s * (sum(rand() for _ in range(3)) - 1.5)

CASTS = [int, float, lambda s: {"true":1,"false":0}.get(s.lower(), s)]

def cast(s:str) -> Val:
  for f in CASTS:
    try: return f(s)
    except ValueError: ...

def csv(f):
  with open(f, encoding="utf-8") as file:
    for s in file:
      if s := s.partition("#")[0].strip():
        yield [cast(x.strip()) for x in s.split(",")]

def align(m:list[list]):
  m = [[say(x) for x in row] for row in m]
  ws = [max(len(str(x)) for x in col) for col in zip(*m)]
  for l in m: print(", ".join(f"{str(v):>{w}}" for v, w in zip(l, ws)))

#---- demos ----------------------------------------------------------
def eg_h():
  "show help"
  print(__doc__)
  for k, fun in globals().items():
    if k.startswith("eg__"):
      args = " ".join(fun.__annotations__)
      cmd  = f"{k[4:]} {args}".strip()
      print(f"  --{cmd:<16} {fun.__doc__ or ''}")

def eg_s(n:int): the.seed=n; random.seed(n)
def eg_d(n:int): the.decs=n
def eg_p(n:int): the.p=n

def eg__the():
  "show config"
  print(the)

def eg__csv(file:str):
  "demo csv reader"
  align(list(csv(file))[::30])

def eg__data(file:str):
  "demo data storage"
  d = Data(csv(file))
  align([mids(d)] + [d.cols.names] + d.rows[::30])

def eg__disty(file:str):
  "demo row distance to heaven"
  d = Data(csv(file))
  align([d.cols.names] + sorted(d.rows, key=lambda r: disty(d, r))[::30])

def eg__addsub(file:str):
  "demo incremental add then delete"
  d = Data(csv(file))
  rows=d.rows[:]
  for row in rows[::-1]:
     sub(d, row)
     if d.n == 50: one=mids(d)
  for row in rows:
     add(d, row)
     if d.n == 50: two=mids(d)
  assert all(abs(a-b)<0.00001 for a,b in zip(one,two))

def eg__bayes(file:str):
  "demo naive bayes likelihood"
  d = Data(csv(file))
  nall = len(d.rows)
  for r in d.rows[::30]:
    print(say(round(likes(d, r, nall, 1), 2)))

#---- main -----------------------------------------------------------
the = Thing(**{k: cast(v) for k, v in re.findall(r"(\S+)=(\S+)", __doc__)})
random.seed(the.seed)

def main(funs):
  args = sys.argv[1:]
  while args:
    if f := funs.get(f"eg_{args.pop(0)[1:].replace('-','_')}"):
      f(*[make(args.pop(0)) for make in f.__annotations__.values()])

if __name__ == "__main__": main(globals())

