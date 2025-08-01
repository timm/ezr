#!/usr/bin/env python3 -B
from lib import *

#--------------------------------------------------------------------
def Sym(at=0, txt="") -> o: 
  "summarize symbols"
  return o(it=Sym, at=at,txt=txt,has={})

def Num(at=0, txt=" ") -> o: 
  "summarize numbers"
  return o(it=Num, at=at, txt=txt, lo=1e32, mu=0, m2=0, sd=0, n=0, 
           hi=-1e32, more = 0 if txt[-1] == "-" else 1)

def Data(src) -> o:
  "store rows, summarized in cols"
  src = iter(src)
  return adds(src, o(it=Data, n=0, rows=[], cols= Cols(next(src))))

def Cols(names: List[str]) -> o:
  "generate columns from column names"
  all, x, y, klass = [],[],[],None
  for c,s in enumerate(names):
    all += [(Num if s[0].isupper() else Sym)(c,s)]
    if s[-1] == "X": continue
    if s[-1] == "!": klass = all[-1]
    (y if s[-1] in "!-+" else x).append(all[-1])
  return o(it=Cols, names=names, all=all, x=x, y=y, klass=klass)

def clone(data:Data, rows=None) -> o:
  "copy data structure, maybe add in rows"
  return adds(rows or [], Data([data.cols.names]))

#--------------------------------------------------------------------
def adds(src, it=None) -> o:
  "add many things to it, return it"
  for x in src:
     it = it or (Num if isinstance(x,(int,float)) else Sym)()
     add(it, x)
  return it

def sub(x:o, v:Any, zap=False) -> Any: 
  "subtraction is just adding -1"
  return add(x,v,-1,zap)

def add(x: o, v:Any, inc=1, zap=False) -> Any:
  "incrementally update Syms,Nums or Datas"
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
    if inc > 0: x.rows += [v]
    elif zap: x.rows.remove(v) # slow for long rows
    [add(col, v[col.at],inc) for col in x.cols.all]
  return v

#--------------------------------------------------------------------
def norm(num:Num, v:float) -> float:  # 0..1
  "map 'v' to range 0..1"
  return  (v - num.lo) / (num.hi - num.lo + 1E-32)

def mids(data):
  "Return the central tendency for each column."
  return [mid(col) for col in data.cols.all]

def mid(col):
  "Return the central tendnacy for one column."
  return max(col.has, key=col.has.get) if col.it is Sym else col.mu

def divs(data):
  "Return the central tendency for each column."
  return [div(col) for col in data.cols.all]

def div(col):
  "Return the central tendnacy for one column."
  if col.it is Num: return col.sd
  vs = col.has.values()
  N  = sum(vs)
  return -sum(p*math.log(p,2) for n in vs if (p:=n/N) > 0)

#--------------------------------------------------------------------
def eg__sym(): 
  "Sym:  demo"
  print(x := adds("aaaabbc",Sym()).has["a"])
  assert x==4

def eg__num(): 
  "Num: check Num sample tacks gaussians"
  print(x := round(adds(random.gauss(10,2) for _ in range(1000)).mu,1))
  assert x == 10

def eg__data():
  "check we can read csv files from disk"
  print(x := round(sum(y.mu for y in Data(csv(the.file)).cols.y),2))
  assert x == 3009.84

#--------------------------------------------------------------------
def eg__all()  : mainAll(globals())
def eg__list() : mainList(globals())
def eg_h()     : print(helpstring)
if __name__ == "__main__": main(globals())
