#!/usr/bin/env python3 -B
from ezr.lib import *

#--------------------------------------------------------------------
def Sym(at=0, txt="") -> o: 
  "summarize symbols"
  return o(it=Sym, 
           n=0,             ## number of items
           at=at, txt=txt,  ## position and name of column
           has={})          ## symbol counter

def Num(at=0, txt=" ") -> o: 
  "summarize numbers"
  return o(it=Num, 
           n=0,                ## number of items
           at=at, txt=txt,     ## position and name of column
           mu=0, m2=0, sd=0,   ## to track mean and stdev
           lo=1e32, hi=-1e32,  ## low and high range
           more = 0 if txt[-1] == "-" else 1) ## heaven

def Data(src: Iterator[Row]) -> o:
  "store rows, summarized in cols"
  src = iter(src)
  return adds(src, o(it=Data, 
                     n=0,       ## number of items
                     mid=None,  ## place to cache centroid
                     rows=[],   ## row storage
                     cols= Cols(next(src)))) # column summaries

def Cols(names: List[str]) -> o:
  "generate columns from column names"
  all, x, y, klass = [],[],[],None
  for c,s in enumerate(names):
    all += [(Num if s[0].isupper() else Sym)(c,s)]
    if s[-1] == "X": continue
    if s[-1] == "!": klass = all[-1]
    (y if s[-1] in "!-+" else x).append(all[-1])
  return o(it=Cols, 
           names=names,    ## column names
           all=all,        ## all the columns
           x=x,            ## all the x columns
           y=y,            ## all the y columns
           klass=klass)    ## pointer to the klass column

def clone(data:Data, rows=None) -> o:
  "copy data structure, maybe add in rows"
  return adds(rows or [], Data([data.cols.names]))

def adds(src:Iterator, it=None) -> o:
  "add many things to it, return it"
  it = it or Num(); [add(it,x) for x in src]; return it

#--------------------------------------------------------------------
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
    x.mid=None
    x.n += inc
    if inc > 0: x.rows += [v]
    elif zap: x.rows.remove(v) # slow for long rows
    [add(col, v[col.at],inc) for col in x.cols.all]
  return v

#--------------------------------------------------------------------
def norm(col, v:float) -> float:  # 0..1
  "map 'v' to range 0..1"
  return  v if v =="?" or col.it is Sym else (
          (v - col.lo) / (col.hi - col.lo + 1E-32))

def mids(data: Data) -> Row:
  "Return the central tendency for each column."
  data.mid = data.mid or  [mid(col) for col in data.cols.all]
  return data.mid

def mid(col:o) -> Atom: 
  "Return the central tendnacy for one column."
  return max(col.has, key=col.has.get) if col.it is Sym else col.mu

def divs(data:Data) -> float:
  "Return the central tendency for each column."
  return [div(col) for col in data.cols.all]

def div(col:o) -> float:
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
  print(mu := round(adds(random.gauss(10,2) for _ in range(1000)).mu,1))
  print(sd := round(adds(random.gauss(10,2) for _ in range(1000)).sd,2))
  assert sd == 1.99
  assert mu == 10

def eg__checkData():
  "check we can read csv files from disk"
  try: Data(csv(the.file))
  except Exception as _ : print(the.file)

def eg__data():
  "check we can read csv files from disk"
  print(x := round(sum(y.mu for y in Data(csv(the.file)).cols.y),2))
  #assert x == 3009.84


