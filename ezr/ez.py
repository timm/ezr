#!/usr/bin/env python3 -B
"""
ez.py: lightweight incremental Bayes classifier with add/delete support
(c) 2026 Tim Menzies timm@ieee.org, MIT license

Options:
  -A Any=4           initial start
  -A Any=4           initial start
  -B Budget=50       training evaluation budget
  -b bins=7          discretize numerics into this many bins
  -C Check=5         testing evaluation budget
  -d decs=2          print floats to this many decimals
  -F Few=128         search space for new rows
  -k k=1             for low value frequencies in Bayes
  -K Keep=256        how many numbers to keep in Nums
  -l leaf=3          min rows per tree leaf
  -m m=2             for low class frequencies in Bayes
  -p p=2             Minkowski distance coefficient (2:Euclidean)
  -s seed=1          random number seed
  -N Norm=0          CNB weight normalization (0/1)
  -S Show=30         width of tree display 
  -y yes=20          positive samples for text mining
  -Y no=20           negative samples for text mining 
  -T Top=100         top TF-IDF features to keep
  -v valid=20        number of repeats for statistical testing"""
  -N Norm=0          CNB weight normalization (0/1)
  -S Show=30         width of tree display 
  -y yes=20          positive samples for text mining
  -Y no=20           negative samples for text mining 
  -T Top=100         top TF-IDF features to keep
  -v valid=20        number of repeats for statistical testing"""
import random, sys, re
from math import log, exp, sqrt, pi
from random import random as r, choice
from bisect import insort, bisect_left
from typing import Iterable
from types import SimpleNamespace as o
from pathlib import Path

BIG = 1E32
Qty = int | float
Val = Qty | bool | str
Row = list[Val]
Col = "Num | Sym"

#---- Syms --------------------------------------------------------
class Sym(dict):
  def add(i, v:Val) -> Val:
    if v != "?": i[v] = i.get(v,0) + 1
    return v

  def sub(i, v:Val) -> Val:
    if v != "?": i[v] = i.get(v,0) - 1
    return v

  def mid(i) -> Val: return max(i, key=i.get)
  def spread(i) -> float: 
    n = sum(i.values())
    return -sum(p*log(p,2) for k in i if (p:=i[k]/n)>0)
  def norm(i, v:Val) -> Val:   return v
  def distx(i, u:Val, v:Val) -> int: return int(u!=v)
  def pick(i, _:Val=None) -> Val:   return pick(i)
  def like(i, v:Val, prior:float=0) -> float:
    n = sum(i.values())
    return max(1/BIG, (i.get(v,0) + the.k*prior) / (n + the.k))

#---- NUms --------------------------------------------------------
class Num(list):
  __repr__ = lambda i: str([say(v) for v in i])

  def __init__(i, mx:int=None): 
    super().__init__(); i.mx=mx or the.Keep; i.seen=0

  def add(i, v:Val) -> Val:
    if v!="?": 
      i.seen += 1
      if len(i) < i.mx: insort(i, v)
      elif r() < i.mx/i.seen: i.pop(int(r()*len(i))); insort(i, v)
    return v

  def sub(i, v:Val) -> Val:
    if v!="?": 
      i.seen -= 1
      if (p:=bisect_left(i,v)) < len(i) and i[p]==v: i.pop(p)
    return v

  def mid(i) -> float: return i[len(i)//2] if i else 0

  def spread(i) -> float:
    if len(i) < 2: return 0
    n = max(1, len(i)//10)             
    a,b = min(9*n, len(i)-1), min(n, len(i)-1)
    return (i[a]-i[b])/2.56

  def norm(i, v:Val) -> Val:
    if v=="?" or len(i)<2: return v
    a,b = i[int(.05*len(i))], i[int(.95*len(i))]
    return 0 if a==b else max(0, min(1, (v-a)/(b-a)))

  def pick(i, v:Qty=None) -> Val:
    result = (i.mid() if v is None or v=="?" else v) + choice(i) - choice(i)
    lo, hi = i[0], i[-1]
    return lo + ((result - lo) % (hi - lo + 1E-32))

  def distx(i, u:Val, v:Val) -> float:
    if u==v=="?": return 1
    u,v = i.norm(u), i.norm(v)
    u = u if u!="?" else (0 if v>0.5 else 1)
    v = v if v!="?" else (0 if u>0.5 else 1)
    return abs(u-v)

  def like(i, v:Qty, prior:float=0) -> float:
    s = i.spread() + 1/BIG
    return (1/sqrt(2*pi*s*s)) * exp(-((v-i.mid())**2) / (2*s*s))

#---- cols -----------------------------------------------------
def col(s:str): return (Num if s[0].isupper() else Sym)()

class Cols:
  __repr__ = lambda i: str(i.names)
  def __init__(i, names:list[str]):
    i.names = names
    i.all = {at:col(s) for at,s in enumerate(names)}
    i.w = {at: s[-1]!="-" for at,s in enumerate(names) if s[-1] in "-+!"}
    i.x = {at:c for at,c in i.all.items() if at not in i.w and names[at][-1] != "X"}
    i.y = {at:i.all[at] for at in i.w}
    i.klass = next((at for at,s in enumerate(names) if s[-1]=="!"), None)

#---- cols -----------------------------------------------------
class Data:
  def __init__(i, items:Iterable[Row]):
    i.rows=[]; i._mid=None
    i.cols = Cols(next(items := iter(items)))
    [i.add(row) for row in items]

  def add(i, row:Row) -> Row:
    i._mid=None
    for at,c in i.cols.all.items(): c.add(row[at])
    i.rows.append(row)
    return row

  def sub(i, row:Row) -> Row:
    i._mid=None
    for at,c in i.cols.all.items(): c.sub(row[at])
    i.rows.remove(row)
    return row

  def mid(i) -> Row:
    i._mid = i._mid or [c.mid() for c in i.cols.all.values()]
    return i._mid

  def like(i, row:Row, n_all:int, n_h:int) -> float:
    prior = (len(i.rows)+the.m) / (n_all+the.m*n_h)
    ls = [c.like(v,prior) for at,c in i.cols.x.items() if (v:=row[at])!="?"]
    return log(prior) + sum(log(v) for v in ls if v>0)

  def distx(i, r1:Row, r2:Row) -> float:
    return minkowski(c.distx(r1[at],r2[at]) for at,c in i.cols.x.items())

  def disty(i, r:Row) -> float:
    return minkowski(c.norm(r[at]) - i.cols.w[at] for at,c in i.cols.y.items())

  def sorty(i) -> "Data":
    i.rows.sort(key=lambda row: i.disty(row)); return i

  def sortx(i, r:Row, rows:list[Row]) -> list[Row]:
    return sorted(rows, key=lambda r2: i.distx(r,r2))

  def nearest(i,  r:Row, rows:list[Row]) -> Row: return i.sortx(r,rows)[0]
  def furthest(i, r:Row, rows:list[Row]) -> Row: return i.sortx(r,rows)[-1]
 
  def pick(i, row=None, n=1) -> Row:
    if not row: return [c.pick() for c in i.cols.all.values()]
    s, k = row[:], n if n > 0 else len(i.cols.x)
    for at, c in random.sample(list(i.cols.x.items()), min(k, len(i.cols.x))):
      s[at] = c.pick(s[at])
    return s

#---- lib ------------------------------------------------------------
def say(x, w:int=None) -> str:
  if type(x)==float: x = int(x) if int(x)==x else f"{x:.{the.decs}f}"
  elif isinstance(x,dict): x= {k:say(x[k]) for k in x}
  return f"{x:>{w}}" if w else x

def says(lst:list, w:int=None): print(*[say(x,w) for x in lst])

def adds(items:Iterable, col=None) -> "Num|Sym|Data":
  col = col or Num()
  [col.add(v) for v in items]; return col

def minkowski(items:Iterable) -> float:
  n=d=0
  for x in items: n,d = n+1, d+x**the.p
  return 0 if n==0 else (d/n)**(1/the.p)

def pick(d:dict) -> Val:
  n = sum(d.values()) * r()
  for k,v in d.items():
    if (n:=n-v) <= 0: return k

def shuffle(lst:list) -> list: random.shuffle(lst); return lst

CASTS = [int, float, lambda s: {"true":1,"false":0}.get(s.lower(),s)]

def cast(s:str) -> Val:
  for f in CASTS:
    try: return f(s)
    except ValueError: ...

def nocomments(s): return s.partition("#")[0].split(",")

def csv(f, clean=nocomments):
def nocomments(s): return s.partition("#")[0].split(",")

def csv(f, clean=nocomments):
  with open(f, encoding="utf-8") as file:
    for s in file:
      r = clean(s)
      if any(x.strip() for x in r):
        yield [cast(x.strip()) for x in r]
      r = clean(s)
      if any(x.strip() for x in r):
        yield [cast(x.strip()) for x in r]

def align(m:list[list]):
  m  = [[str(say(x)) for x in row] for row in m]
  ws = [max(len(x) for x in column) for column in zip(*m)]
  for row in m: print(", ".join(f"{v:>{w}}" for v,w in zip(row,ws)))

def posint(s:str):
  assert (v:=int(s)) >= 0,f"{s} not a posint"
  return v

def filename(s:str):
  assert Path(s).is_file(), f"unknown file {s}"
  return s

#---- demos ----------------------------------------------------------
def eg_h():
  "show help"
  print(__doc__)
  for k,fun in globals().items():
    if k.startswith("eg__"):
      args = " ".join(fun.__annotations__)
      print(f"  --{(k[4:]+' '+args).strip():<16} {fun.__doc__ or ''}")

def eg_s(n:int): the.seed=n; random.seed(n)
def eg_d(n:int): the.decs=n
def eg_S(n:int): the.Show=n
def eg_B(n:int): the.Budget=n
def eg_C(n:int): the.Check=n
def eg_p(n:int): the.p=n

def eg__the(): "show config"; print(the.__dict__)

def eg__csv(file:filename): "demo csv reader"; align(list(csv(file))[::30])

def eg__data(file:filename):
  "demo data storage"
  d = Data(csv(file))
  align([d.mid()] + [d.cols.names] + d.rows[::30])

def eg__disty(file:filename):
  "demo row distance to heaven"
  d = Data(csv(file))
  print({d.cols.names[i]:d.cols.w[i] for i in d.cols.w})

  align([d.cols.names] + sorted(d.rows, key=lambda r: d.disty(r))[::30])

def eg__addsub(file:filename):
  "demo incremental add then delete"
  d = Data(csv(file)); 
  d1=Data([d.cols.names]+ d.rows[:the.Keep])
  rows=d1.rows[:]
  m1=d1.mid()
  for row in rows[::-1]:
    d1.sub(row)
    if len(d1.rows)==the.Keep //3    : aone=d1.mid()
    if len(d1.rows)==the.Keep //3 * 2: atwo=d1.mid()
  m2=d1.mid()
  for row in rows:
    d1.add(row)
    if len(d1.rows)==the.Keep//3     : bone=d1.mid()
    if len(d1.rows)==the.Keep//3 * 2 : btwo=d1.mid()
  print(aone,atwo,m1)
  print(bone,btwo,m2)
  assert all(a==b for a,b in zip(aone,bone))
  assert all(a==b for a,b in zip(atwo,btwo))

def eg__like(file:filename):
  "demo naive bayes likelihood"
  d = Data(csv(file)); 
  d.rows.sort(key=lambda r: d.like(r,len(d.rows),2))
  for row in d.rows[::30]:
     print(row, say(d.like(row,len(d.rows),2)))

#---- main -----------------------------------------------------------

the= o(**{k:cast(v) for k,v in re.findall(r"(\S+)=(\S+)", __doc__)})
random.seed(the.seed)

def main(funs:dict):
  args = sys.argv[1:]
  while args:
    if f := funs.get(f"eg_{args.pop(0)[1:].replace('-','_')}"):
      f(*[make(args.pop(0)) for make in f.__annotations__.values()])

if __name__ == "__main__": main(globals())

