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
#----------------------------------------------------------------------------------------
# # System Inits
options = dict(k=1, m=2, bins=10, file="../data/auto93.csv", seed=1234567891) 

big = 1E32
tiny = 1/big

# ## Special type annotations
class Row    : has:list[Any]
class Rows   : has:list[Row]
class Klasses: has:dict[str, Rows]

class OBJ:
  """## Obj
  Base class, defines simple initialization and pretty print.  
  """ 
  def __init__(i,**d)    : i.__dict__.update(d)
  def __repr__(i) -> str : return i.__class__.__name__+show(i.__dict__)
#----------------------------------------------------------------------------------------
# # Classes 
class BIN(OBJ):
  """## BIN   
  Stores in `ys` the klass symbols see between `lo` and `hi`.
  
  - `BIN.score()` reports how often we see `goals` symbols more than  other symbols.
  - `merge()` combines two BINs, if they are too small or they have similar distributions;
  - `selects()` returns true when a BIN matches a row.   
  To  build decision trees,  split Rows on the best scoring bin, then recurse on each half.
  """
  id=0
  @staticmethod
  def score(d:dict, BEST:int, REST:int, goal="+", how=lambda B,R: B - R) -> float:
    b,r = 0,0
    for k,n in d.items():
      if k==goal: b += n
      else      : r += n
    b,r = b/(BEST+tiny), r/(REST+tiny)
    return how(b,r) 
  
  def __init__(i, at:int, txt:str, lo:float, hi:float=None, ys:Counter=None):  
    i.at,i.txt,i.lo,i.hi,i.ys = at,txt, lo,hi or lo,ys or Counter()  
    i.id = BIN.id = BIN.id + 1

  def add(i, x:float, y:Any):
    i.lo = min(x, i.lo)
    i.hi = max(x, i.hi)
    i.ys[y] += 1

  # ### Combine bins  
  def merge(i, j:BIN, minSize:float) -> BIN: # or None if nothing merged
    if i.at == j.at:
      k     = BIN(i.at, i.txt, min(i.lo,j.lo), hi=max(i.hi,j.hi), ys=i.ys+j.ys)
      ei,ni = entropy(i.ys)
      ej,nj = entropy(j.ys)
      ek,nk = entropy(k.ys)
      if ni < minSize or nj < minSize: return k # merge bins that are too small
      if ek <= (ni*ei + nj*ej)/nk    : return k # merge bins if combo not as complex

  # ### Find relevant rules 
  def selectss(i, klasses: Klasses) -> Klasses:
    yes,no = {},{}
    for klass,_ in klasses.items(): yes[klass],no[klass] = [],[]
    for klass,_ in klasses.items():
      for row in list:
        (yes[klass] if i.selects(row) else no[klass]).append(row) 
    return yes,no
  
  def selects(i, row: Row) -> bool: 
    x = row[i.at]
    return  x=="?" or i.lo == x == i.hi and i.lo <= x < i.hi
#----------------------------------------------------------------------------------------
class COL(OBJ):
  """## COL  
  Abstract class above NUM and SYM.  
  
  - `bins()` reports how col values are spread over a list of BINs.
  """
  def __init__(i, at:int=0, txt:str=" "): i.n,i.at,i.txt = 0,at,txt

  def bins(i, klasses: Klasses, minSize=None) -> list[BIN]:
    def send2bin(x,y): 
      k = i.bin(x)
      if k not in out: out[k] = BIN(i.at,i.txt,x)
      out[k].add(x,y)
    out = {}
    [send2bin(row[i.at],y) for y,lst in klasses.items() for row in lst if row[i.at]!="?"] 
    return i._bins(sorted(out.values(), key=lambda z:z.lo), 
                   minSize = minSize or (sum(len(lst) for lst in klasses.values())/the.bins))
#----------------------------------------------------------------------------------------
class SYM(COL):
  """## SYM 
  Summarizes a stream of numbers.
  
  - the `div()`ersity of a SYM summary is the `entropy`;
  - the `mid()`dle of a SYM summary is the mode value;
  - `like()` returns the likelihood of a value belongs in a SYM distribution;
  - `bin()` and `_bin()` are used for generating BINs (for SYMs there is not much to do with BINs) 
  """
  def __init__(i,**kw): super().__init__(**kw); i.has = {}
  def add(i, x:Any):
    if x != "?":
      i.n += 1
      i.has[x] = i.has.get(x,0) + 1
 
  # ### Discretization  
  def _bins(i,bins:list[BIN],**_) -> list[BIN] : return bins
  def bin(i,x:Any) -> Any  : return x

  # ### Stats  
  def div(i)  -> float : return entropy(i.has)
  def mid(i)  -> Any   : return max(i.has, key=i.has.get)
  
  # ### Bayes  
  def like(i, x:Any, m:int, prior:float) -> float : 
    return (i.has.get(x, 0) + m*prior) / (i.n + m)
#----------------------------------------------------------------------------------------
class NUM(COL):
  """## NUM
  Summarizes a stream of numbers.
  
  - the `div()`ersity of a NUM summary is the standard deviation;
  - the `mid()`dle of a NUM summary is the mean value;
  - `like()` returns the likelihood of a value belongs in a NUM distribution;
  - `bin(n)`  places `n` in  one equal width bin (spread from `lo` to `hi`)
    `_bin(bins)` tries to merge numeric bins
  - `d2h(n)`  reports how far n` is from `heaven` (which is 0 when minimizing, 1 otherwise
  - `norm(n)` maps `n` into 0..1 (min..max)
  """
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

  # ### Discretization 
  def bin(i, x:float) -> int: return min(the.bins - 1, int(the.bins * i.norm(x)))

  def _bins(i, bins: list[BIN], minSize=2) -> list[BIN]: 
    bins = merges(bins,merge=lambda x,y:x.merge(y,minSize))
    bins[0].lo  = -big
    bins[-1].hi =  big
    for j in range(1,len(bins)): bins[j].lo = bins[j-1].hi
    return bins
  
  # ### Distance  
  def d2h(i, x:float) -> float: return abs(i.norm(x) - i.heaven)
  def norm(i,x:float) -> float: return x=="?" and x or (x - i.lo) / (i.hi - i.lo + tiny)   

  # ### Stats  
  def div(i) -> float : return  0 if i.n < 2 else (i.m2 / (i.n - 1))**.5
  def mid(i) -> float : return i.mu
  
  # ### Bayes 
  def like(i, x:float, *_) -> float:
    v     = i.div()**2 + tiny
    nom   = math.e**(-1*(x - i.mu)**2/(2*v)) + tiny
    denom = (2*math.pi*v)**.5
    return min(1, nom/(denom + tiny))
#----------------------------------------------------------------------------------------
class COLS(OBJ): 
  """## COLS
  Factory for building  and storing COLs from column names. All columns are in `all`. 
  References to the independent and dependent variables are in `x` and `y` (respectively).
  If there is a klass, that is  referenced in `klass`. And all the names are stored in `names`.
  """
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
  """## DATA
  Stores `rows`, summarized into `cols`. Optionally, `rows` can be sorted by distance to
  heaven (`d2h()`).  A `clone()` is a new `DATA` of the same structure. Can compute
  `loglike()`lihood of  a `Row` belonging to this `DATA`.
  """
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

  # ### Creation  
  def clone(i,lst:Iterable[Row]=[],ordered=False) -> DATA:  
    return DATA([i.cols.names]+lst)
  def order(i) -> Rows:
    i.rows = sorted(i.rows, key=i.d2h, reverse=False)
    return i.rows
  
  # ### Distance  
  def d2h(i, row:Row) -> float:
    d = sum(col.d2h( row[col.at] )**2 for col in i.cols.y)
    return (d/len(i.cols.y))**.5

  # ### Bayes  
  def loglike(i, row:Row, nall:int, nh:int, m:int, k:int) -> float:
    prior = (len(i.rows) + k) / (nall + k*nh)
    likes = [c.like(row[c.at],m,prior) for c in i.cols.x if row[c.at] != "?"]
    return sum(math.log(x) for x in likes + [prior] if x>0)
#----------------------------------------------------------------------------------------
class NB(OBJ):
  """## NB 
  Visitor object carried along by a DATA. Internally maintains its own `DATA` for rows 
  from different class.
  """
  def __init__(i): i.nall=0; i.datas:Klasses = {}

  def loglike(i, data:DATA, row:Row):
    return data.loglike(row, i.nall, len(i.datas), the.m, the.k)

  def run(i,data:DATA, row:Row):
    klass = row[data.cols.klass.at]
    i.nall += 1
    if klass not in i.datas: i.datas[klass] =  data.clone()
    i.datas[klass].add(row)
#----------------------------------------------------------------------------------------
class TREE(obj):
  def __init__(i,data:DATA, klasses:Klasses, best:str="BEST", rest:str="REST"):
    i.BEST = len(klasses[best]) 
    i.REST = len(klasses[rest]) 
    rows = data.order()
    klasses = dict(best=best,rest=rest)
    bins = [BIN.score(bin.ys, n,n, goal="best") for c in data.cols.x for bin in c.bins(klasses)]

  def tree(i,klasses,bins,BEST,REST):
    for bin in bins:
      yes,no = bin.selects(klasses)
      yes1 = {k:len(rows) for k,rows in yes.items()}
      no1  = {k:len(rows) for k,rows in no.items()}
      s1   = BIN.score(yes1,BEST,REST,goal="best")
      s2  = BIN.score(no1,BEST,REST,goal="best")
#----------------------------------------------------------------------------------------
# ## Misc functions
# ### Data mining tricks 
def entropy(d: dict) -> float:
  N = sum(n for n in d.values()if n>0)
  return -sum(n/N*math.log(n/N,2) for n in d.values() if n>0), N

def merges(b4: list[BIN], merge:Callable) -> list[BIN]: 
  j, now, repeat  = 0, [], False 
  while j <  len(b4):
    a = b4[j] 
    if j <  len(b4) - 1: 
      if tmp := merge(a, b4[j+1]):  
        a, j, repeat = tmp, j+1, True  # skip merged item, search down rest of list
    now += [a]
    j += 1
  return merges(now, merge) if repeat else b4 

# ### Strings to things  
def coerce(s:str) -> Any:
  try: return ast.literal_eval(s) # <1>
  except Exception:  return s

def csv(file=None) -> Iterable[Row]:
  with file_or_stdin(file) as src:
    for line in src:
      line = re.sub(r'([\n\t\r"\’ ]|#.*)', '', line)
      if line: yield [coerce(s.strip()) for s in line.split(",")]

# ### Printing  
def show(x:Any, n=3) -> Any:
  if   isinstance(x,(int,float)) : x= x if int(x)==x else round(x,n)
  elif isinstance(x,(list,tuple)): x= [show(y,n) for y in x][:10]
  elif isinstance(x,dict): 
        x= "{"+', '.join(f":{k} {show(v,n)}" for k,v in sorted(x.items()) if k[0]!="_")+"}"
  return x

def prints(matrix: list[list],sep=' | '):
  s    = [[str(e) for e in row] for row in matrix]
  lens = [max(map(len, col)) for col in zip(*s)]
  fmt  = sep.join('{{:>{}}}'.format(x) for x in lens)
  [print(fmt.format(*row)) for row in s] 
#----------------------------------------------------------------------------------------
class MAIN:
  """`./trees.py _all` : run all functions , return to operating system the count of failures.   
  `MAIN._one()` : reset all options to defaults, then run one start-up action.
  """
  def _all(): 
    sys.exit(sum(MAIN._one(s) == False for s in sorted(dir(MAIN)) if s[0] != "_"))

  def _one(s):
    global the; the = OBJ( **options )
    random.seed(the.seed) 
    return getattr(MAIN, s, lambda :print(f"E> '{s}' unknown."))() 

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
    d=DATA(csv(the.file),order=True); print("")
    prints([d.cols.names] + [r for r in d.rows[::50]])

  def bore2():
    d    = DATA(csv(the.file),order=True)
    n    = int(len(d.rows)**.5)
    best = d.rows[:n] 
    rest = d.rows[-n:] 
    bins = [(BIN.score(bin.ys, n,n, goal="best"),bin)
            for col in d.cols.x for bin in col.bins(dict(best=best,rest=rest))]
    now=None
    for n, bin in bins:
      if now != bin.at: print("")
      now = bin.at
      print(show(n), bin, sep="\t")
    print("")
    [print(show(n), bin, sep="\t") for n, bin in sorted(bins, key=lambda z:z[0])]

# -----------------------
if __name__=="__main__" and len(sys.argv) > 1: 
    MAIN._one(sys.argv[1]) 