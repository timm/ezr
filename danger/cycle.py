#!/usr/bin/env python3 -B
import traceback, random, math, sys, re
from typing import Any, Callable, Iterator, List
from types import SimpleNamespace as o

the = o(p     = 2, 
        seed  = 1234567891,
        Any   = 4,
        Budget= 24,
        Check = 5,
        k     = 1,
        m     = 2,
        file  = "../../moot/optimize/misc/auto93.csv")

Atom = int|float|str|bool
Row  = List[Atom]

#--------------------------------------------------------------------
def Sym(at=0, txt="") -> o: 
  return o(it=Sym, at=at,txt=txt,has={})

def Num(at=0, txt=" ") -> o: 
  return o(it=Num, at=at, txt=txt, lo=1e32, mu=0, m2=0, sd=0, n=0, 
           hi=-1e32, more = 0 if txt[-1] == "-" else 1)

def Data(src) -> o:
  src = iter(src)
  return adds(src, o(it=Data, n=0, mids=None, rows=[], cols= Cols(next(src))))

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
      x.sd = x.m2 = x.mu = x.n = 0
    else:
      d     = v - x.mu
      x.mu += inc * (d / x.n)
      x.m2 += inc * (d * (v - x.mu))
      x.sd  = 0 if x.n < 2 else (max(0,x.m2)/(x.n-1))**.5
  elif x.it is Data:
    x.mids = None
    x.n += inc
    if inc > 0: x.rows += [v]
    elif zap: x.rows.remove(v) # slow for long rows
    [add(col, v[col.at],inc) for col in x.cols.all]
  return v

#--------------------------------------------------------------------
def norm(col, v:float) -> float:  # 0..1
  return  v if v =="?" or col.it is Sym else (
          (v - col.lo) / (col.hi - col.lo + 1E-32))

def mids(data):
  data.mids = data.mids or [mid(col) for col in data.cols.all]
  return data.mids 

def mid(col):
  return max(col.has, key=col.has.get) if col.it is Sym else col.mu

def divs(data):
  return [div(col) for col in data.cols.all]

def div(col):
  if col.it is Num: return col.sd
  vs = col.has.values()
  N  = sum(vs)
  return -sum(p*math.log(p,2) for n in vs if (p:=n/N) > 0)

#--------------------------------------------------------------------
def dist(src) -> float:
  d,n = 0,0
  for v in src: n,d = n+1, d + v**the.p;
  return (d/n) ** (1/the.p)

def disty(data:Data, row:Row) -> float:
  return dist(abs(norm(c, row[c.at]) - c.more) for c in data.cols.y)

def distysort(data:Data,rows=None) -> List[Row]:
  return sorted(rows or data.rows, key=lambda r: disty(data,r))

def distx(data, row1, row2):
  def _aha(col, a,b):
    if a==b=="?": return 1
    if col.it is Sym: return a != b
    a,b = norm(col,a), norm(col,b)
    a = a if a != "?" else (0 if b>0.5 else 1)
    b = b if b != "?" else (0 if a>0.5 else 1)
    return abs(a-b)
  return dist(_aha(col, row1[col.at], row2[col.at])  
              for col in data.cols.x)

#--------------------------------------------------------------------
def like(i:o, v:Any, prior=0) -> float :
  if i.it is Sym:
    tmp = ((i.has.get(v,0) + the.m*prior) 
           /(sum(i.has.values())+the.m+1e-32))
  else:
    var = 2 * i.sd * i.sd + 1E-32
    z  = (v - i.mu) ** 2 / var
    tmp =  math.exp(-z) / (2 * math.pi * var) ** 0.5
  return min(1, max(0, tmp))

def likes(data:Data, row:Row, nall=100, nh=2) -> float:
  prior= (data.n + the.k) / (nall + the.k*nh)
  tmp= [like(c,v,prior) for c in data.cols.x if (v:=row[c.at]) != "?"]
  return sum(math.log(n) for n in tmp + [prior] if n>0)    

#--------------------------------------------------------------------
def atom(s:str) -> Atom:
  for fn in [int,float]:
    try: return fn(s)
    except Exception as _: pass
  s = s.strip()
  return {'True':True,'False':False}.get(s,s)

def csv(file:str) -> List[Row]:
  with open(file,encoding="utf-8") as f:
    for line in f:
      if (line := line.split("%")[0]):
        yield [atom(s.strip()) for s in line.split(",")]

def shuffle(lst: List) -> List:
  random.shuffle(lst); return lst

def bin(col,x):
  return x if v =="?" or col.it is Sym else (
         min(the.Bins - 1, int(cdf(col,x) * the.Bins)))

def cdf(num,x):
  fn = lambda z: 1 − 0.5 * math.exp(−0.717 * z − 0.416 * z * z)
  z = (x − num.mu) / num.sd
  return fn(z) if z>=0 else 1 − fn(−z)

#--------------------------------------------------------------------
def eg__cycle():
  data = Data(csv(the.file))
  Y    = lambda r: disty(data,r)
  b4   = adds(Y(r) for r in data.rows)
  Win  = lambda r: int(100*(1 - (Y(r) - b4.lo) / (b4.mu - b4.lo)))
  print(Win(cycle(data)[0]))

def main(funs: dict[str,callable]) -> None:
  for n,arg in enumerate(sys.argv):
    if (fn := funs.get(f"eg{arg.replace('-', '_')}")):
      random.seed(the.seed); fn()
    else:
      for key in vars(the):
        if arg=="-"+key[0]: the.__dict__[key] = atom(sys.argv[n+1])

main(globals())
