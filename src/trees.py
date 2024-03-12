#!/usr/bin/env python3 -B
"""
Explore a `todo` set, within fewest queries to labels:

1. Label and move a few `initial` items to a `done`.
2. Sort the `done` into sqrt(n) `best` and `rest`.
3. Build a model that reports likelihood `b,r` of an item being in `best` or `rest`. 
4. Sort `todo` by `-b/r`. 
5. From that sorted `todo` space,   
   (a) delete the last `forget` percent (e.g. 20%);    
   (b) move  the first item into `done`.
6. Goto step 2.
"""
from __future__ import annotations 
from typing import Any,Iterable,Callable
import re,ast,sys,math,random
from collections import Counter
from fileinput import FileInput as file_or_stdin 

big = 1E32
tiny = 1/big

# some types. just written here for documentation purposes
class Row    : has:list[Any]
class Rows   : has:list[Row]
class Klasses: has:dict[str, Rows]

class OBJ:
  "Base class, defines simple initialization and pretty print."
  def __init__(i,**d)    : i.__dict__.update(d)
  def __repr__(i) -> str : return i.__class__.__name__+show(i.__dict__)

the = OBJ(k=1, m=2, bins=10, file="../data/auto93.csv")
#----------------------------------------------------------------------------------------
class BIN(OBJ):
  """Stores in `ys` the klass symbols see between `lo` and `hi`. 
  - `merge` combines two BINs, if they are too small or they have similar distributions;
  - `selects` returns true when a BIN matches a row.
  """
  def __init__(i, at:int, lo:float, hi:float=None, ys:Counter=None):  
    i.at,i.lo,i.hi,i.ys = at,lo,hi or lo,ys or Counter()  

  def add(i, x:float, y:Any):
    i.lo = min(x, i.lo)
    i.hi = max(x, i.hi)
    i.ys[y] += 1

  # combine bins
  def merge(i, j:BIN, minSize:float) -> BIN: # or None if nothing merged
    if i.at == j.at:
      k     = BIN(i.at, min(i.lo,j.lo), hi=max(i.hi,j.hi), ys=i.ys+j.ys)
      ei,ni = entropy(i.ys)
      ej,nj = entropy(j.ys)
      ek,nk = entropy(k.ys)
      if ni < minSize or nj < minSize: return k # merge bins that are too small
      if ek <= (ni*ei + nj*ej)/nk    : return k # merge bins if combo not as complex

  # find relevant rules
  def selectss(i, klasses: Klasses) -> Klasses:
    return {klass:[row for row in lst if i.selects(row)] for klass,lst in klasses.items()}
  
  def selects(i, row: Row) -> bool: 
    x = row[i.at]
    return  x=="?" or i.lo == x == i.hi and i.lo <= x < i.hi
#----------------------------------------------------------------------------------------
class COL(OBJ):
  """Abstract class above NUM and SYM.   
  - `bins()` reports how col values are spread over a list of BINs.
  """
  def __init__(i, at:int=0, txt:str=" "): i.n,i.at,i.txt = 0,at,txt

  # discretization
  def bins(i, klasses: Klasses) -> list[BIN]:
    out = {}
    def send2bin(x,y): 
      k = i.bin(x)
      if k not in out: out[k] = BIN(i.at,x)
      out[k].add(x,y)
    [send2bin(row[i.at],y) for y,lst in klasses.items() for row in lst if row[i.at]!="?"] 
    return i._bins(sorted(out.values(), key=lambda z:z.lo), 
                   minSize = (sum(len(lst) for lst in klasses.values())/the.bins))
#----------------------------------------------------------------------------------------
class SYM(COL):
  """Summarizes a stream of symbols.
  - the `div()`ersity of the summary is the `entropy`;
  - the `mid()`dle of the summary is the mode value;
  - `like()` returns the likelihood of a value belongs in this distribution;
  - `bin()` and `_bin()` are used for generating BINs (for SYMs there is not much to do with BINs) 
  """
  def __init__(i,**kw): super().__init__(**kw); i.has = {}
  def add(i, x:Any):
    if x != "?":
      i.n += 1
      i.has[x] = i.has.get(x,0) + 1
 
  # discretization
  def _bins(i,bins:list[BIN],**_) -> list[BIN] : return bins
  def bin(i,x:Any) -> Any       : return x

  # stats
  def div(i)  -> float : return entropy(i.has)
  def mid(i)  -> Any   : return max(i.has, key=i.has.get)
  
  # bayes
  def like(i, x:Any, m:int, prior:float) -> float : 
    return (i.has.get(x, 0) + m*prior) / (i.n + m)
#----------------------------------------------------------------------------------------
class NUM(COL):
  def __init__(i,**kw): 
    super().__init__(**kw)
    i.mu,i.m2,i.lo,i.hi = 0,0,big, -big
    i.heaven = 0 if i.txt[-1]=="-" else 1

  def add(i, x:Any):
    if x != "?":
      i.n += 1
      d = x - i.mu
      i.mu += d/i.n
      i.m2 += d * (x -  i.mu)
      i.lo  = min(x, i.lo)
      i.hi  = max(x, i.hi)

  # discretization 
  def bin(i, x:float) -> int: return min(the.bins - 1, int(the.bins * i.norm(x)))
  def _bins(i, bins: list[BIN], minSize=2) -> list[BIN]: 
    bins = merges(bins,merge=lambda x,y:x.merge(y,minSize))
    bins[0].lo  = -big
    bins[-1].hi =  big
    for j in range(1,len(bins)): bins[j].lo = bins[j-1].hi
    return bins
  
  # distance
  def d2h(i, x:float) -> float: return abs(i.norm(x) - i.heaven)
  def norm(i,x:float) -> float: return x=="?" and x or (x - i.lo) / (i.hi - i.lo + tiny)   

  # stats
  def div(i) -> float : return  0 if i.n < 2 else (i.m2 / (i.n - 1))**.5
  def mid(i) -> float : return i.mu
  
  # bayes
  def like(i, x:float, *_) -> float:
    v     = i.div()**2 + tiny
    nom   = math.e**(-1*(x - i.mu)**2/(2*v)) + tiny
    denom = (2*math.pi*v)**.5
    return min(1, nom/(denom + tiny))
#----------------------------------------------------------------------------------------
class COLS(OBJ):
  def __init__(i, names: list[str]):
    i.x,i.y,i.all,i.names,i.klass = [],[],[],names,None
    for at,txt in enumerate(names):
      a,z = txt[0], txt[-1]
      col = (NUM if a.isupper() else SYM)(at=at,txt=txt)
      i.all.append(col)
      if z != "X":
        (i.y if z in "!+-" else i.x).append(col)
        if z == "!": i.klass= col

  def add(i,row: Row) -> Row:
    [col.add(row[col.at]) for col in i.all if row[col.at] != "?"]
    return row
#----------------------------------------------------------------------------------------
class DATA(OBJ):
  def __init__(i,src=Iterable[Row],order=False,fun=None):
    i.rows, i.cols = [],None
    [i.add(lst,fun) for lst in src]
    if order: i.order()

  def add(i, row:Row, fun:Callable=None):
    if i.cols: 
      if fun: fun(i,row)
      i.rows += [i.cols.add(row)]
    else: 
      i.cols = COLS(row)

  # creation
  def clone(i,lst:Iterable[Row]=[],ordered=False) -> DATA:  
    return DATA([i.cols.names]+lst)
  def order(i) -> Rows:
    i.rows = sorted(i.rows, key=i.d2h, reverse=False)
    return i.rows
  
  # distance
  def d2h(i, row:Row) -> float:
    d = sum(col.d2h( row[col.at] )**2 for col in i.cols.y)
    return (d/len(i.cols.y))**.5

  # bayes
  def loglike(i, row:Row, nall:int, nh:int, m:int, k:int) -> float:
    prior = (len(i.rows) + k) / (nall + k*nh)
    likes = [c.like(row[c.at],m,prior) for c in i.cols.x if row[c.at] != "?"]
    return sum(math.log(x) for x in likes + [prior] if x>0)
#----------------------------------------------------------------------------------------
class NB(OBJ):
  def __init__(i): i.nall=0; i.datas:Klasses = {}

  def loglike(i, data:DATA, row:Row):
    return data.loglike(row, i.nall, len(i.datas), the.m, the.k)

  def run(i,data:DATA, row:Row):
    klass = row[data.cols.klass.at]
    i.nall += 1
    if klass not in i.datas: i.datas[klass] =  data.clone()
    i.datas[klass].add(row)
#----------------------------------------------------------------------------------------
def isa(x,y): return isinstance(x,y)

def score(d:dist, BEST:int, REST:int, goal="+", how=lambda B,R: B - R) -> float:
  b,r = 0,0
  for k,n in d.items():
    if k==goal: b += n
    else      : r += n
  b,r = b/(BEST+tiny), r/(REST+tiny)
  return how(b,r)

def prints(matrix: list[list],sep=' | '):
  s    = [[str(e) for e in row] for row in matrix]
  lens = [max(map(len, col)) for col in zip(*s)]
  fmt  = sep.join('{{:{}}}'.format(x) for x in lens)
  for row in [fmt.format(*row) for row in s]: print(row)
    
def entropy(d: dict) -> float:
  N = sum(n for n in d.values()if n>0)
  return -sum(n/N*math.log(n/N,2) for n in d.values() if n>0), N

def merges(b4: list[BIN], merge:Callable) -> list[BIN]:
  j, now, most, repeat  = 0, [], len(b4), False 
  while j <  most:
    a = b4[j] 
    if j <  most - 1: 
      if tmp := merge(a, b4[j+1]):  
        a, j, repeat = tmp, j+1, True  # skip merged item, search down rest of list
    now += [a]
    j += 1
  return merges(now, merge) if repeat else b4 

def coerce(s:str) -> Any:
  try: return ast.literal_eval(s) # <1>
  except Exception:  return s

def csv(file=None) -> Iterable[Row]:
  with file_or_stdin(file) as src:
    for line in src:
      line = re.sub(r'([\n\t\r"\’ ]|#.*)', '', line)
      if line: yield [coerce(s.strip()) for s in line.split(",")]

def show(x:Any, n=3) -> Any:
  if   isa(x,(int,float)) : x= x if int(x)==x else round(x,n)
  elif isa(x,(list,tuple)): x= [show(y,n) for y in x][:10]
  elif isa(x,dict): x= "{"+', '.join(f":{k} {show(v,n)}" for k,v in sorted(x.items()) if k[0]!="_")+"}"
  return x
#----------------------------------------------------------------------------------------
class MAIN:
  def opt(): print(the)

  def header():
    top=["Clndrs","Volume","HpX","Model","origin","Lbs-","Acc+","Mpg+"]
    d=DATA([top])
    [print(col) for col in d.cols.all]

  def data(): 
   d=DATA(csv(the.file))
   print(d.cols.x[1])

  def rows():
    d=DATA(csv(the.file))
    print(sorted(show(d.loglike(r,len(d.rows),1, the.m, the.k)) for r in d.rows)[::50])

  def bore():
    d=DATA(csv(the.file),order=True)
    prints([r for r in d.rows[::25]])

  def bore2():
    d    = DATA(csv(the.file),order=True)
    n    = int(len(d.rows)*.1)
    best = d.rows[:n]
    rest = random.sample(d.rows[n:],n*3)
    for col in d.cols.x: 
      print("")
      for bin in col.bins(dict(best=best,rest=rest)):
        print(show(score(bin.ys, n,n*3,goal="best")),bin,sep="\t")

if __name__=="__main__" and len(sys.argv) > 1: 
	getattr(MAIN, sys.argv[1], MAIN.opt)()
