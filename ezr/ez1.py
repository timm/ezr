#!/usr/bin/env python3 -B
"""
  -s seed=1
"""
import random,sys,re

NUM,SYM,isa = list,dict,isinstance

def what(s): return (NUM if s[0].isupper() else SYM)()

def COLS(names):
  cols = {n:what(s) for n,s in enumerate(names)}
  x    = {n:c for n,c in cols.items() if names[n][-1] not in "-+!X"}
  y    = {n:c for n,c in cols.items() if names[n][-1]     in "-+!" }
  w    = {n:names[n][-1] != "!" for n in y}
  return OBJ(names=names, all=cols, x=x, y=y, w=w)

def DATA(items=None):
  return adds(items, OBJ(rows=[], cols=None, mids=None))

#--------------------------------------------------------------------
def adds(items, it=None):
  it = it or NUM()
  for item in items or []: add(it,item)
  return it

def add(i, v):
  if v != "?":
    if isa(i,OBJ):
      if not i.cols: i.cols = COLS(v)
      else: 
        i.mid = None
        i.rows.append(v)
        for n, col in i.cols.all.items(): add(col,v[n])
    elif isa(i,NUM): i += [v]
    elif isa(i,SYM): i[v] = 1 + i.get(v, 0)
  return v

#--------------------------------------------------------------------
def ok(data):
  if not data.mids:
    [col.sort() for col in data.cols.all.values() if isa(col,NUM)]
    data.mids = [mid(col) for col in data.cols.all.values()]
  return data

def mid(col):
  return col[len(col)//2] if isa(col,NUM) else max(col, key=col.get)

def sd(lst): 
  n = len(lst)//10; return (lst[9*n] - lst[n]) / 2.56

def ent(d): 
  N = sum(d.values())
  return -sum(p*log(p,2) for n in d.values() if (p:=n/N)>0)

def norm(col,v):
  if v=="?" or isa(col,SYM): return v
  lo,hi = col[0],col[-1]
  return (v - lo) / (hi - lo + 1E-32)

#--------------------------------------------------------------------
def minkowski(items):
  n,d = 0,0
  for item in items: n, d = n+1, d+item ** the.p
  return 0 if n==0 else (d / n) ** (1 / the.p)

def disty(data, row):
  return minkowski((norm(y, row[n]) - data.cols.w[n]) 
                   for n,y in data.cols.y.items())

def o(t):
  match t:
    case dict(): return "{" + " ".join(f":{k} {o(t[k])}" for k in t) + "}"
    case float(): return f"{int(t)}" if int(t) == t else f"{t:.{the.decs}f}"
    case _: return str(t)

class OBJ(dict):
  __getattr__,__setattr__,__repr__ = dict.__getitem__,dict.__setitem__,o

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

def eg__the(): print(the)

def eg__csv(f:str):
  for row in csv(f): print(row)

def eg__data(f:str):
  data = ok(DATA(csv(f)))
  for row in data.rows: print(row)
  for n,c in data.cols.all.items(): print(n,mid(c))

#-----------------------------------------------------
the= OBJ(**{k: cast(v) for k, v in re.findall(r"(\S+)=(\S+)", __doc__)})
random.seed(the.seed)

def main(settings,funs):
  args = iter(sys.argv[1:])
  for s in args:
    if f := funs.get(f"eg_{s[1:].replace('-','_')}"):
      f(*[cast(next(args)) for t in f.__annotations__.values()])

if __name__ == "__main__": main(the,globals())
