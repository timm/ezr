#!/usr/bin/env python3 -B 
from types import SimpleNamespace as o
from typing import Any,List,Iterator
import random, math, sys, re

the=o(Any   = 4, 
      Build = 24, 
      Few   = int(math.log(1-.95) / math.log(1-.2/6)),
      p     = 2,
      seed  = 1234567891,
      file  = "../../moot/optimize/misc/auto93.csv")

Atom = int|float|str|bool
Row  = List[Atom]
big  = 1e32

#--------------------------------------------------------------------
def Num(i=0,s=" "): 
  return o(it=Num, i=i, txt=s, n=0, mu=0, m2=0, sd=0, hi=-big, lo=big,
           more = 0 if s[-1] == "-" else 1)

def Sym(i=0,s=" "): 
  return o(it=Sym, i=i, txt=s, n=0, has={})

def Cols(names : List[str]) -> o:
  all=[(Num if s[0].isupper() else Sym)(c,s) for c,s in enumerate(names)]
  return o(it=Cols, names = names, all = all,
           x   = [col for col in all if col.txt[-1] not in "X-+"],
           y   = [col for col in all if col.txt[-1] in "-+"])

def Data(src) -> o:
  src = iter(src)
  return adds(src, o(it=Data, n=0, mids=None, rows=[], cols=Cols(next(src))))

def clone(data:Data, rows=None) -> o:
  return adds(rows or [], Data([data.cols.names]))

#--------------------------------------------------------------------
def adds(src, it=None) -> o:
  it = it or Num()
  [add(it,x) for x in src]
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
      x.sd = x.m2 = x.mu = x.n = 0
    else: 
      d     = v - x.mu
      x.mu += inc * (d / x.n)
      x.m2 += inc * (d * (v - x.mu))
      x.sd  = 0 if x.n < 2 else (max(0,x.m2)/(x.n-1))**.5
  elif x.it is Data:
    x.n += inc
    x.mid = None
    if inc > 0: x.rows += [v]
    elif zap: x.rows.remove(v) # slow for long rows
    [add(col, v[col.i],inc) for col in x.cols.all]
  return v

#--------------------------------------------------------------------
def norm(num:Num, v:float) -> float:  
  return  v if v=="?" else (v - num.lo) / (num.hi - num.lo + 1E-32)

def mids(data: Data) -> Row:
  data.mids = data.mids or [mid(col) for col in data.cols.all]
  return data.mids

def mid(col: o) -> Atom:
  return max(col.has, key=col.has.get) if col.it is Sym else col.mu

#--------------------------------------------------------------------
def dist(src) -> float:
  d,n = 0,0
  for v in src: n,d = n+1, d + v**the.p;
  return (d/n) ** (1/the.p)

def disty(data:Data, row:Row) -> float:
  return dist(abs(norm(c, row[c.i]) - c.more) for c in data.cols.y)

def distysort(data:Data,rows=None) -> List[Row]:
  return sorted(rows or data.rows, key=lambda r: disty(data,r))

def distx(data:Data, row1:Row, row2:Row) -> float:
  def _aha(col, a,b):
    if a==b=="?": return 1
    if col.it is Sym: return a != b
    a,b = norm(col,a), norm(col,b)
    a = a if a != "?" else (0 if b>0.5 else 1)
    b = b if b != "?" else (0 if a>0.5 else 1)
    return abs(a - b)
  return dist(_aha(col, row1[col.i], row2[col.i])  
              for col in data.cols.x)

#--------------------------------------------------------------------
def cycle(names,rows):
  xy,best,rest = Data([names]), Data([names]), Data([names])
  for n,row in enumerate(rows):
    if n <=  3: add(xy, row)
    if n == 3: 
      distysort(xy)
      adds(xy.rows[:2], best)
      adds(xy.rows[2:], rest)
    if n > 3 :
      if distx(xy, mids(best), row) < distx(xy, mids(rest), row):
        add(xy, add(best, row)) 
        if best.n > (best.n + rest.n)**0.5:
          distysort(best)
          add(rest, sub(best, best.rows.pop(-1)))
    if xy.n > the.Build: break
  return distysort(xy)

#--------------------------------------------------------------------
def atom(s:str) -> o:
  for fn in [int,float]:
    try: return fn(s)
    except Exception as _: pass
  s = s.strip()
  return {'True':True,'False':False}.get(s,s)

def csv(file: str ) -> Iterator[Row]:
  with open(file,encoding="utf-8") as f:
    for line in f:
      if (line := line.split("%")[0]):
        yield [atom(s.strip()) for s in line.split(",")]

def shuffle(lst:List):
  random.shuffle(lst)
  return lst

def main(funs: dict[str,callable]) -> None:
  "from command line, update config find functions to call"
  for n,arg in enumerate(sys.argv):
    if (fn := funs.get(f"eg{arg.replace('-', '_')}")):
      random.seed(the.seed); fn()
    else:
      for key in vars(the):
        if arg=="-"+key[0]: the.__dict__[key] = atom(sys.argv[n+1])

#--------------------------------------------------------------------
def eg__cycle():
  data  = Data(csv(the.file))
  b4    = adds(disty(data,r) for r in data.rows)
  win   = lambda n: int(100*(1 - (n - b4.lo) / (b4.mu - b4.lo)))
  nears = adds([ disty(data, cycle(data.cols.names, shuffle(data.rows))[0]) 
                 for _ in range(20)])
  print("cycle",win(nears.mu),
        len(data.rows),
        len(data.cols.x),
        len(data.cols.y),
        re.sub(".*/","",the.file))

def eg__near():
  data = Data(csv(the.file))
  b4   = adds(disty(data,r) for r in data.rows)
  win  = lambda n: int(100*(1 - (n - b4.lo) / (b4.mu - b4.lo)))
  nears  = adds([ disty(data, likely(data)[0]) for _ in range(20)])
  rands  = adds([ disty(data, 
                        distysort(data, shuffle(data.rows)[:the.Build])[0])
                        for _ in range(20)])
  print("nears",win(nears.mu),"delta",win(nears.mu) - win(rands.mu), "|",
        len(data.rows),
        len(data.cols.x),
        len(data.cols.y),
        re.sub(".*/","",the.file))

if __name__ == "__main__": main(globals())
