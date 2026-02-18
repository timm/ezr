#!/usr/bin/env python3 -B
"""
ez1.py: asdas
(c) 2026 Tim Menzies timm@ieee.org, MIT license

Options:
  -d decs=2          print floats to this many decimals
  -K Keep=256        keep this many nums per column
  -p p=2             Minkowski distance coeffecience (2:Euclidean)
  -s seed=1          random number seed """

from typing import Iterator,Iterable,Any
import random,sys,re
rand=random.random
choice=random.choice

class Box(dict):
  __getattr__,__setattr__ = dict.__getitem__,dict.__setitem__
  __repr__ = lambda self: str({k:say(self[k]) for k in self})

Qty  = int | float
Row  = list[Qty | str]
Rows = list[Row]
Data = Box

#--------------------------------------------------------------------
Num,Sym,isa = list,dict,isinstance

def Col(s:str) -> Num | Sym: 
  return (Num if s[0].isupper() else Sym)()

def mid(c:Col) -> Any:
  return c[len(c)//2] if isa(c,Num) else max(c, key=c.get)

def sd(n:Num) -> float: 
  i = len(n)//10; return (n[9*i] - n[i]) / 2.56

def ent(d:Sym) -> float: 
  n = sum(d.values())
  return -sum(p*log(p,2) for v in d.values() if (p:=v/n) > 0)

def norm(c:Col,v) -> float:
  if v=="?" or isa(c,Sym): return v
  lo, hi = c[0], c[-1]
  return (v - lo) / (hi - lo + 1E-32)

def keep(l:Num, v:Any, seen:int):
  if len(l) < the.Keep: l.append(v)
  elif rand() < the.Keep / seen: l[1+int(rand() * (the.Keep-2))] = v

#--------------------------------------------------------------------
def Data(items:Iterable) -> Data:
  d = Box(rows=[], cols=None, mids=None)
  for row in items: adds(d,row)
  return ok(d)

def adds(d:Data, row:Row):
  if not d.cols: # reading row0 with column names
    cols   = {i:Col(s) for i,s in enumerate(row)}
    x      = {i:c for i,c in cols.items() if row[i][-1] not in "-+!X"}
    y      = {i:c for i,c in cols.items() if row[i][-1]     in "-+!" }
    d.cols = Box(names=row, all=cols, x=x, y=y, 
                 w= {i:row[i][-1] != "-" for i in y})
  else: # reading remaining rows
    d.mid = None
    d.rows += [row]
    [add(c,row[i],len(d.rows)) for i, c in d.cols.all.items()]

def add(c:Col, v:Any, seen=0):
  if v=="?": return
  if isa(c,Sym): c[v] = 1 + c.get(v, 0)
  else: keep(c,v,seen)

def ok(d:Data) -> Data:
  if not d.mids:
    [c.sort() for c in d.cols.all.values() if isa(c,Num)]
    d.mids = [mid(c) for c in d.cols.all.values()]
  return d

#--------------------------------------------------------------------
def minkowski(items: Iterable) -> float:
  n,d = 0,0
  for item in items: 
    n, d = n+1, d+item ** the.p
  return (d / n) ** (1 / the.p)

def disty(d:Data, r:Row) -> float:
  return minkowski((norm(y,r[i]) - d.cols.w[i]) for i,y in ok(d).cols.y.items())

def distx(d:Data, r1:Row, r2:Row) -> float:
  return minkowski(aha(d,x,r1[i],r2[i]) for i,x in ok(d).cols.x.items())

def aha(d:Data, c:Col, u:Any, v:Any) -> float:
  if u==v=="?": return 1
  if isa(c,Sym): return u != v
  u,v = norm(c,u), norm(c,v)
  u = u if u != "?" else (0 if v>0.5 else 1)
  v = v if v != "?" else (0 if u>0.5 else 1)
  return abs(u - v)

def furthest(*args) -> Row: return order(*args)[-1]
def nearest(*args)  -> Row: return order(*args)[0]

def order(d:Data,r1:Row,rows:Rows) -> Rows: 
 return sorted(rows,key=lambda r2:distx(d,r1,r2))

def nearby(c:Col, v:Any) -> Any:
  if isa(c,Sym): return pick(c)
  lo,hi = c[0],c[-1]
  v = v if v != "?" else mid(c)
  return lo + (v + choice(c) - choice(c) - lo) % (hi-lo+1E-32)

def pick(d:Sym) -> Any:
  n = sum(d.values()) * rand()
  for k,v in d.items():
    if (n := n-v) <= 0: return k

def gauss(mu:float, s:float) -> float:
  return mu + 2 * s * (sum(rand() for _ in range(3)) - 1.5)

#--------------------------------------------------------------------
def shuffle(lst:list) -> list:
  random.shuffle(lst)
  return lst

def say(x:Any) -> Any:
  return x if not isa(x,float) else int(x) if int(x)==x else round(x,the.decs)

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
def eg_h(): 
  "show help"
  print(__doc__)
  for k, fun in globals().items():
    if k.startswith("eg__"): 
      args = " ".join([arg for arg in fun.__annotations__])#if arg != 'return'])
      cmd = f"{k[4:]} {args}".strip()
      print(f"  --{cmd:<16} {fun.__doc__ or ''}")

def eg_s(n:int): the.seed=n; random.seed(the.seed)
def eg_K(n:int): the.Keep=n
def eg_d(n:int): the.decs=n
def eg_p(n:int): the.p=n

def eg__the(): 
  "show config"
  print(the)

def eg__keep(): 
  "demo resovoir sampling"
  the.Keep,lst = 24,[]
  for i in range(10**3): keep(lst,i,i)
  print(sorted(lst))

def eg__csv(file:str):
  "demo csv reader"
  align(list(csv(file))[::30])

def eg__data(file:str):
  "demo data storage"
  d = Data(csv(file))
  align([ok(d).mids] + [d.cols.names] + d.rows[::30])

def eg__disty(file:str):
  "demo row sampling"
  d = Data(csv(file))
  align([d.cols.names] + sorted(d.rows,key=lambda r:disty(d,r))[::30])

#-----------------------------------------------------
the = Box(**{k: cast(v) for k, v in re.findall(r"(\S+)=(\S+)", __doc__)})
random.seed(the.seed)

def cli(funs):
  args = sys.argv[1:]
  while args:
    if f := funs.get(f"eg_{args.pop(0)[1:].replace('-','_')}"):
      f(*[make(args.pop(0)) for make in f.__annotations__.values()])

if __name__ == "__main__": cli(globals())
