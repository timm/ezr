#!/usr/bin/env python3 
# MARK: help
"""
ez.py: Active learning, find best/rest seen so far in a Bayes classifier   
(c) 2024 Tim Menzies <timm@ieee.org>, BSD-2 license   

OPTIONS:  
  -s --seed     random number seed    = 1234567891    
  -g --go       start up action       = help
  -f --file     data file             = ../data/auto93.csv    
    
  Discretize:
  -B --Bins     max number of bins    = 16

  Classify:     
  -k --k        low frequency kludge  = 1 
  -m --m        low frequency kludge  = 2   
    
  Optimize:    
  -n --budget0  init evals            = 4   
  -N --Budget   max evals             = 16 
  -b --best     ratio of top          = .5
  -T --Top      keep top todos        = .8 
  
  Explain: 
  -l --leaf     leaf size             = 2 """

from __future__ import annotations   # <1> ## types  
import sys
sys.dont_write_bytecode = True
from collections import Counter
import re,ast,copy,json,math,random
from typing import Any,Iterable,Callable
from fileinput import FileInput as file_or_stdin 

# ----------------------------------------------------------------------------------------
# MARK: inits

# Some globals
big = 1E32
tiny = 1/big

# Special type annotations
class Row    : has:list[Any]
class Rows   : has:list[Row]
class Classes: has:dict[str, Rows] # a dictionary, one key for each class 

# Simple base object: defines simple initialization and pretty print. 

class OBJ:
  def __init__(i,**d)    : i.__dict__.update(d)
  def __repr__(i) -> str : return i.__class__.__name__+show(i.__dict__)

def settings(s:str) -> dict:
  return {m[1] : coerce(m[2]) for m in re.finditer(r"--(\w+)[^=]*=\s*(\S+)", s)}

# ----------------------------------------------------------------------------------------
# ## Classes

# MARK: BIN
#  Stores in `ys` the klass symbols see between `lo` and `hi`.
#  
# [1] `merge()` combines two BINs, if they are too small or they have similar distributions.   
# [2] `selects()` returns true when a BIN matches a row.       
# [3] `BIN.score()` reports how often we see `goals` symbols more than  other symbols.    
#   
# To  build decision trees,  split Rows on the best scoring bin, then recurse on each half.

#ZZZ add in __repr__
class BIN(OBJ):
  id=0
  def __init__(i, at:int, txt:str, lo:float, hi:float=None, ys:Counter=None):  
    i.at,i.txt,i.lo,i.hi,i.ys = at,txt, lo,hi or lo,ys or Counter()  
    i.id = BIN.id = BIN.id + 1
  
  def add(i, x:float, y:Any):
    i.lo = min(x, i.lo)
    i.hi = max(x, i.hi)
    i.ys[y] += 1

  def __repr__(i):
    if i.lo == i.hi: return f"{i.txt}={i.hi}"
    if i.lo == -big: return f"{i.txt} < {i.hi}"
    if i.hi == big:  return f"{i.txt} >= {i.lo}"
    return f"{i.lo} <= {i.txt} < {i.hi}"
      
  def merge(i, j:BIN, small:float) -> BIN: # or None if nothing merged ------------[1]
    if i.at == j.at:
      k     = BIN(i.at, i.txt, min(i.lo,j.lo), hi=max(i.hi,j.hi), ys=i.ys+j.ys)
      ei,ni = entropy(i.ys)
      ej,nj = entropy(j.ys)
      ek,nk = entropy(k.ys)
      if ni <  small or nj < small : return k # merge if bins too small 
      if ek <= (ni*ei + nj*ej)/nk:  return k # merge if parts are more complex
     
  def selects(i, row: Row) -> bool:  #-----------------------------------------------[2]
    x = row[i.at]
    return  x=="?" or i.lo == x == i.hi or i.lo <= x < i.hi
   
  def selectsRejects(i, classes: Classes) -> tuple[Classes,Classes]:
    yes = {k:[] for k in classes}
    no  = {k:[] for k in classes}
    for k,rows in classes.items():
      [(yes if i.selects(row) else no)[k].append(row) for row in rows]  
    return yes,no 
  
# MARK:  COL
# is an abstract class above NUM and SYM.    
#     
#  - `bins()` reports how col values are spread over a list of BINs.

class COL(OBJ):
  def __init__(i, at:int=0, txt:str=" "): i.n,i.at,i.txt = 0,at,txt

  def bins(i, classes: Classes, small=None) -> list[BIN]:
    def send2bin(x,y): 
      k = i.bin(x)
      if k not in out: out[k] = BIN(i.at,i.txt,x)
      out[k].add(x,y)
    out = {}
    [send2bin(row[i.at],y) for y,lst in classes.items() for row in lst if row[i.at]!="?"] 
    return i.binsComplete(sorted(out.values(), key=lambda z:z.lo), 
                   small = small or (sum(len(lst) for lst in classes.values())/the.Bins))

# MARK: SYM 
# summarizes a stream of numbers.
# 
# - the `div()`ersity of a SYM summary is the `entropy`;
# - the `mid()`dle of a SYM summary is the mode value;
# - `like()` returns the likelihood of a value belongs in a SYM distribution;
# - `bin()` and `binsComplete()` are used for generating BINs (for SYMs there is not much to do with BINs) 

class SYM(COL):
  def __init__(i,**kw): super().__init__(**kw); i.has = {}
  def add(i, x:Any):
    if x != "?":
      i.n += 1
      i.has[x] = i.has.get(x,0) + 1
 
  def bin(i,x:Any) -> Any  : return x
  def binsComplete(i,bins:list[BIN],**_) -> list[BIN] : return bins

  def div(i)  -> float : return entropy(i.has)
  def mid(i)  -> Any   : return max(i.has, key=i.has.get)
  
  def like(i, x:Any, prior:float) -> float : 
    return (i.has.get(x, 0) + the.m*prior) / (i.n + the.m)

# MARK: NUM
# summarizes a stream of numbers.
#
# - the `div()`ersity of a NUM summary is the standard deviation;
# - the `mid()`dle of a NUM summary is the mean value;
# - `like()` returns the likelihood of a value belongs in a NUM distribution;
# - `bin(n)`  places `n` in  one equal width bin (spread from `lo` to `hi`)
#   `_bin(bins)` tries to merge numeric bins
# - `d2h(n)`  reports how far n` is from `heaven` (which is 0 when minimizing, 1 otherwise
# - `norm(n)` maps `n` into 0..1 (min..max)

class NUM(COL):
  def __init__(i,**kw): 
    super().__init__(**kw)
    i.mu,i.m2,i.lo,i.hi = 0,0,big, -big
    i.heaven = 0 if i.txt[-1]=="-" else 1

  def add(i, x:Any): #= sd
    if x != "?":
      i.n += 1
      d = x - i.mu
      i.mu += d/i.n
      i.m2 += d * (x -  i.mu)
      i.lo  = min(x, i.lo)
      i.hi  = max(x, i.hi) 

  def bin(i, x:float) -> int: 
    return min(the.Bins - 1, int(the.Bins * i.norm(x)))

  def binsComplete(i, bins: list[BIN], small=2) -> list[BIN]: 
    bins = merges(bins,merge=lambda x,y:x.merge(y,small))
    bins[0].lo  = -big
    bins[-1].hi =  big
    for j in range(1,len(bins)): bins[j].lo = bins[j-1].hi
    return bins
  
  def d2h(i, x:float) -> float: return abs(i.norm(x) - i.heaven)
  def norm(i,x:float) -> float: return x=="?" and x or (x - i.lo) / (i.hi - i.lo + tiny)   

  def div(i) -> float : return  0 if i.n < 2 else (i.m2 / (i.n - 1))**.5
  def mid(i) -> float : return i.mu
  
  def like(i, x:float, _) -> float:
    v     = i.div()**2 + tiny
    nom   = math.e**(-1*(x - i.mu)**2/(2*v)) + tiny
    denom = (2*math.pi*v)**.5
    return min(1, nom/(denom + tiny))

# MARK: COLS
# is a factory for building  and storing COLs from column names. All columns are in `all`. 
# References to the independent and dependent variables are in `x` and `y` (respectively).
# If there is a klass, that is  referenced in `klass`. And all the names are stored in `names`.

class COLS(OBJ): 
  def __init__(i, names: list[str]): 
    i.x, i.y, i.all, i.names, i.klass = [], [], [], names, None
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

# MARK: DATA
# stores `rows`, summarized into `cols`. Optionally, `rows` can be sorted by distance to
# heaven (`d2h()`).  A `clone()` is a new `DATA` of the same structure. Can compute
# `loglike()`lihood of  a `Row` belonging to this `DATA`.

class DATA(OBJ):
  def __init__(i, src=Iterable[Row], order=False, fun=None):
    i.rows, i.cols = [], None
    [i.add(lst,fun) for lst in src]
    if order: i.order()

  def add(i, row:Row, fun:Callable=None):
    if i.cols: 
      if fun: fun(i,row)
      i.rows += [i.cols.add(row)]
    else: 
      i.cols = COLS(row)

  def clone(i,lst:Iterable[Row]=[],order=False) -> DATA:  
    return DATA([i.cols.names]+lst,order=order)

  def stats(i, cols=None, what:str=None):
    return {col.txt:show(getattr(col,what or "mid")()) 
            for col in cols or i.cols.y}  
  
  def order(i) -> Rows:
    i.rows = sorted(i.rows, key=i.d2h, reverse=False)
    return i.rows
  
  def d2h(i, row:Row) -> float:
    d = sum(col.d2h( row[col.at] )**2 for col in i.cols.y)
    return (d/len(i.cols.y))**.5

  def loglike(i, row:Row, nall:int, nh:int) -> float:
    prior = (len(i.rows) + the.k) / (nall + the.k*nh)
    likes = [c.like(row[c.at],prior) for c in i.cols.x if row[c.at] != "?"]
    return sum(math.log(x) for x in likes + [prior] if x>0)

# MARK: smo 
def smo(data0:DATA, score=lambda B,R: B-R) -> Row:
  def like(row,data,nall): 
    return data.loglike(row,nall,2)
  def acquire(best, rest, rows):
    nall = len(best.rows) + len(rest.rows)
    rows.sort(key=lambda r: -score(like(r,best,nall),like(r,rest,nall)))
    chop = int(len(rows) * the.Top) 
    return rows[:chop]
  #-----------
  random.shuffle(data0.rows)
  done, todo = data0.rows[:the.budget0], data0.rows[the.budget0:]
  data1 = data0.clone(done, order=True) 
  for i in range(the.Budget):
    if len(todo) < 3: break
    n = int(len(done)**the.best + .5) 
    top,*todo = acquire(data0.clone(data1.rows[:n]),
                        data0.clone(data1.rows[n:]),
                        todo)
    done.append(top)
    data1 = data0.clone(done, order=True) 
  return data1.rows[0]

# MARK: CONTRAST
class CONTRAST(OBJ): 
  def show(i):
    for lvl,node in i.nodes():
      print("|.. " * lvl,   
            counts(node.yes) if node.isLeaf else node.bin )
  def nodes(i,lvl=0):
    yield lvl,i 
    if not i.isLeaf:
      for x in [i.yes,i.no]: 
        for lvl1,y in x.nodes(lvl+1): yield lvl1,y

class CONTRASTS(OBJ):
  def __init__(i, data:DATA, classes:Classes, 
               best:str="best", rest:str="rest", score=lambda B,R: B-R): 
    i.bins = [bin for col in data.cols.x for bin in col.bins(classes)]
    i.best, i.score, i.bests, i.rests =  best, score, len(classes[best]), len(classes[rest])
    print(counts(classes))
    i.root = i.grow(classes, 0 ,1E30)

  def grow(i, classes:Classes, lvl:int, above:int) -> OBJ:
    myBest = len(classes[i.best]) 
    if myBest <= the.leaf or myBest == above: 
      return CONTRAST(isLeaf=True, yes=classes, no={}, lvl=lvl)
    else:
      bin = max(i.bins, key = lambda bin: i.sorter(bin,classes)) 
      yes,no = bin.selectsRejects(classes)
      print(counts(yes), counts(no))
      return CONTRAST(isLeaf=False, lvl=lvl, bin=bin, 
                      yes = i.grow(yes, lvl+1, myBest), 
                      no  = i.grow(no,  lvl+1, myBest))

  def sorter(i, bin:BIN, classes:Classes) -> float:
    b,r = 0,0 # counts of best,rest
    for k,rows in classes.items():
      for row in rows: 
        if bin.selects(row): 
          if k==i.best: b += 1
          else        : r += 1
    return i.score( b/(i.bests+tiny), r/(i.rests+tiny) )

# MARK: NB 
# Visitor object carried along by a DATA. Internally maintains its own `DATA` for rows 
# from different class.

class NB(OBJ):
  def __init__(i): i.nall=0; i.datas:Classes = {}; i.acc=0

  def classify(i,data,row):
    return max(i.datas, 
               key=lambda k: i.datas[k].loglike(row, i.nall, len(i.datas)))

  def run(i, data:DATA, row:Row):
    want = row[data.cols.klass.at]
    i.nall += 1
    if i.nall>10:
      got  = i.classify(data,row)  
      i.acc += (want==got)
    if want not in i.datas: i.datas[want] =  data.clone()
    i.datas[want].add(row)
  
#----------------------------------------------------------------------------------------
# MARK: misc functions

def shuffle(lst): random.shuffle(lst); return lst
def counts(d):  return {k:len(v) for k,v in d.items()}
def first(lst): return lst[0]

# ### Data mining tricks 
def entropy(d: dict) -> float:
  N = sum(n for n in d.values()if n>0)
  return -sum(n/N*math.log(n/N,2) for n in d.values() if n>0), N

def merges(b4: list[BIN], merge:Callable) -> list[BIN]: 
  j, now  = 0, [] 
  while j <  len(b4):
    x = b4[j] 
    if j <  len(b4) - 1: 
      y = b4[j+1]
      if xy := merge(x, y):
        x = xy  
        j = j+1  # if i can merge, jump over the merged item
    now += [x]
    j += 1
  return b4 if len(now) == len(b4) else merges(now, merge) 

# ### Strings to things  
def coerce(s:str) -> Any:
  try: return ast.literal_eval(s) # <1>
  except Exception:  return s

def csv(file=None) -> Iterable[Row]:
  with file_or_stdin(file) as src:
    for line in src:
      line = re.sub(r'([\n\t\r"\’ ]|#.*)', '', line)
      if line: yield [coerce(s.strip()) for s in line.split(",")]

def cli(d:dict) -> None: 
  for k,v in d.items(): 
    v = str(v)
    for c,arg in enumerate(sys.argv):
      after = "" if c >= len(sys.argv) - 1 else sys.argv[c+1]
      if arg in ["-"+k[0], "--"+k]: 
        v = "false" if v=="true" else ("true" if v=="false" else after)
        d[k] = coerce(v)
  if d.get("help", False): sys.text( MAIN.help() )

# ### Printing  
def show(x:Any, n=3) -> Any:
  if   isinstance(x,(int,float)) : x= x if int(x)==x else round(x,n)
  elif isinstance(x,(list,tuple)): x= [show(y,n) for y in x][:10]
  elif isinstance(x,dict): 
        x= "{"+', '.join(f":{k} {show(v,n)}" for k,v in sorted(x.items()) if k[0]!="_")+"}"
  return x

def prints(matrix: list[list],sep=' | ') -> None:
  s    = [[str(e) for e in row] for row in matrix]
  lens = [max(map(len, col)) for col in zip(*s)]
  fmt  = sep.join('{{:>{}}}'.format(x) for x in lens)
  [print(fmt.format(*row)) for row in s] 

def asRed(pat,s)   : return re.sub(pat, r"\033[91m\1\033[00m",s)
def asYellow(pat,s): return re.sub(pat, r"\033[93m\1\033[00m",s)

#----------------------------------------------------------------------------------------
# MARK: main 
# `./trees.py _all` : run all functions , return to operating system the count of failures.   
# `MAIN._one()` : reset all options to defaults, then run one start-up action.

class MAIN:
  def main():
    global the
    if __name__=="__main__": cli(the.__dict__)
    MAIN.one(the.go)

  def one(s:str) -> any:
    global the
    cache = copy.deepcopy(the)
    random.seed(the.seed) 
    out = getattr(MAIN, s, lambda :print(f"E> '{s}' unknown."))() 
    the = cache
    return out

  def all() -> None: 
    sys.exit(sum(MAIN.one(s) == False for s in sorted(dir(MAIN)) 
                 if s[0] != "_" and s not in ["all", "one", "main"]))

  def help(): 
    print(asRed(r"(\n[\s]+-\S)", asYellow(r"( --[\S]+)", __doc__)))
  
  def opt(): print(the)

  def header():
    top=["Clndrs","Volume","HpX","Model","origin","Lbs-","Acc+","Mpg+"]
    [print(col) for col in COLS(top).all]

  def data(): 
   d=DATA(csv(the.file))
   print("mid", d.stats()) 
   print("div", d.stats(cols=d.cols.all,what="div")) 

  def rows():
    d1=DATA(csv(the.file))
    d2=d1.clone(d1.rows, order=True)
    for d in [d1,d2]:
       print(sorted(show(d.loglike(r,len(d.rows),1)) for r in d.rows)[::50])

  def nbayes():
    the.file="../data/soybean.csv"
    the.m,the.k = 1,0
    nb = NB()
    d=DATA(csv(the.file),order=False,
           fun=nb.run)
    print(show(nb.acc/len(d.rows)))

  def bore():
    d=DATA(csv(the.file),order=True); print("")
    prints([d.cols.names] + [r for r in d.rows[::50]])

  def bore2():
    d    = DATA(csv(the.file),order=True)
    n    = int(len(d.rows)**.5) 
    for col in d.cols.x:
      print("")
      for bin in col.bins(dict(best=d.rows[:n] ,rest=d.rows[-n:])):
        print(bin, sep="\t") 

  def contrasts():
    d    = DATA(csv(the.file),order=True)
    n    = int(len(d.rows)**.5)
    best = d.rows[:n] 
    rest = shuffle(d.rows[n:])[-n:]

    tree = CONTRASTS(d,dict(best=best,rest=rest)).root
    tree.show()
    #print(json.dumps(tree, indent=2))

  def guess(): 
    budget = 20 
    d = DATA(csv(the.file),order=True)
    asIs, toBe = NUM(), NUM()
    [asIs.add(d.d2h(row)) for row in d.rows]
    for _ in range(20):
      tmp = [random.choice(d.rows) for _   in range(budget)]
      toBe.add( d.d2h( sorted(tmp, key=lambda r: d.d2h(r))[0]))
    print(show(dict(budget= budget,
                    mu= dict( asIs=asIs.mid(), guess= toBe.mid()),
                    sd= dict(asIs=asIs.div(), guess= toBe.div())))) 
     
  def smo():
    d = DATA(csv(the.file))
    print(d.d2h( smo( d )))
  
  def smo20():
    import cProfile
    agains = 20 
    d = DATA(csv(the.file),order=True)
    asIs, toBe = NUM(), NUM()
    [asIs.add(d.d2h(row))    for row in d.rows]
    pr = cProfile.Profile()
    pr.enable()
    [toBe.add(d.d2h(smo(d))) for _   in range(agains)]
    pr.disable()
    pr.print_stats(sort='time') 
    print(show(dict(agains=agains,
                    mu= dict(asIs=asIs.mid(), toBe= toBe.mid()),
                    sd= dict(asIs=asIs.div(), toBe= toBe.div()))))
                                     
# --------------------------------------------
# MARK: Start-up
the = OBJ(**settings(__doc__))
if __name__=="__main__": MAIN.main() 
