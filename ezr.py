#!/usr/bin/env python3 -B
# <!-- vim: set ts=2 sw=2 sts=2 et: -->
"""
    ezr.py : an experiment in easier explainable AI (less is more).    
    (C) 2024 Tim Menzies (timm@ieee.org) BSD-2 license.    
        
    OPTIONS:    
      -a --any     #todo's to explore             = 100    
      -d --decs    #decimals for showing floats   = 3    
      -e --enough  want cuts at least this good   = 0.1   
      -F --Far     how far to seek faraway        = 0.8    
      -h --help    show help                      = False
      -H --Half    #rows for searching for poles  = 128    
      -k --k       bayes low frequency hack #1    = 1    
      -l --label   initial number of labelings    = 4    
      -L --Last    max allow labelings            = 30    
      -m --m       bayes low frequency hack #2    = 2    
      -n --n       tinyN                          = 12    
      -N --N       smallN                         = 0.5    
      -p --p       distance function coefficient  = 2    
      -R --Run     start up action method         = help    
      -s --seed    random number seed             = 1234567891    
      -t --train   training data                  = ../data/misc/auto93.csv    
      -T --test    test data (defaults to train)  = None  
      -v --version show version                   = False   
      -x --xys     max #bins in discretization    = 10    
"""
# <h2>Note</h2><p align="left">See end-of-file for this file's  conventions / principles /practices.
# And FYI, our random number seed is an 
# [odious, apocalyptic, deficient, pernicious, polite, prime](https://numbersaplenty.com/1234567891) 
# number. </center>     

__author__  = "Tim Menzies"
__version__ = "0.1.0"

import re,ast,sys,math,random,copy,traceback
from fileinput import FileInput as file_or_stdin
from typing import Any as any
from typing import Callable as callable

#--------- --------- --------- --------- --------- --------- --------- --------- --------
# ## Types

class o:
  "`o` is a Class for quick inits of structs,  and for pretty prints."
  def __init__(i,**d): i.__dict__.update(d)
  def __repr__(i): return i.__class__.__name__+str(show(i.__dict__))

# Other types used in this system.
xy,cols,data,node,num,sym = o,o,o,o,o,o
col     = num    | sym
number  = float  | int
atom    = number | bool | str # and sometimes "?"
row     = list[atom]
rows    = list[row]
classes = dict[str,rows] # `str` is the class name

#--------- --------- --------- --------- --------- --------- --------- --------- --------
# ## Settings

def coerce(s:str) -> atom:
  "Coerces strings to atoms."
  try: return ast.literal_eval(s)
  except Exception:  return s

# Build the global settings variable by parsing the `__doc__` string.
the=o(**{m[1]:coerce(m[2]) for m in re.finditer(r"--(\w+)[^=]*=\s*(\S+)",__doc__)})

# All the settings in `the`  can be updated via command line.   
# If `the` has a key `xxx`, and if command line has `-x v`, then the["xxx"]=coerce(v)`.
# Boolean settings don't need an argument (we just flip the default).
def cli(d:dict):
  "For dictionary key `k`, if command line has `-k X`, then `d[k]=coerce(X)`."
  for k,v in d.items():
    v = str(v)
    for c,arg in enumerate(sys.argv):
      after = sys.argv[c+1] if c < len(sys.argv) - 1 else ""
      if arg in ["-"+k[0], "--"+k]:
        d[k] = coerce("False" if v=="True" else ("True" if v=="False" else after))

#--------- --------- --------- --------- --------- --------- --------- --------- --------
# ## Structs

# Anything named "_X" is a primitive constructor called by  another constructor "X".

def _DATA() -> data:
  "DATA stores `rows` (whose columns  are summarized in `cols`)."
  return o(this=DATA, rows=[], cols=None) # cols=None means 'have not read row1 yet'

def _COLS(names: list[str]) -> cols:
  "COLS are factories to make columns. Stores independent/dependent cols `x`/`y` and `all`."
  return o(this=COLS, x=[], y=[], all=[], klass=None, names=names)

def SYM(txt=" ",at=0) -> sym:
  "SYM columns incrementally summarizes a stream of symbols."
  return o(this=SYM, txt=txt, at=at, n=0, has={})

def NUM(txt=" ",at=0,has=None) -> num:
  "NUM cokumns incrementally summarizes a stream of numbers."
  return o(this=NUM, txt=txt, at=at, n=0, hi=-1E30, lo=1E30, 
           has=has, rank=0, # if has non-nil, used by the stats package
           mu=0, m2=0, maximize = txt[-1] != "-")

def XY(at,txt,lo,hi=None,ys=None) -> xy:
  "`ys` counts symbols seen in one column between `lo`.. `hi` of another column."
  return o(this=XY, n=0, at=at, txt=txt, lo=lo, hi=hi or lo, ys=ys or {})

def NODE(klasses: classes, left=None, right=None):
  "NODEs are parts of binary trees."
  return o(classes=klasses, left=left, right=right)

#--------- --------- --------- --------- --------- --------- --------- --------- --------
# ## CRUD (create, read, update, delete)
# We don't need to delete (thanks to garbage collection).  But we need create, update.
# And "read" is really "read in from some source" and "read out; i.e. query the structs.

# ### Create

def COLS(names: list[str]) -> cols:
  "Create columns (one for each string in `names`)."
  i = _COLS(names)
  i.all = [add2cols(i,n,s) for n,s in enumerate(names)]
  return i

# Rules for column names:    
# (1) Upper case names are NUM.      
# (2) `klass` names ends in '!'.       
# (3) A trailing 'X' denotes 'ignore'.      
# (4)  If not ignoring, then the column is either a dependent goals (held in `cols.y`) or 
#   a independent variable (held in `cols.x`  
# Using those rules,
def add2cols(i:cols, n:int, s:str) -> col:
  "create a NUM or SYM from `s`. Adds it to `x`, `y`, `all` (if appropriate)."
  new = (NUM if s[0].isupper() else SYM)(txt=s, at=n)
  if s[-1] == "!": i.klass = new
  if s[-1] != "X": (i.y if s[-1] in "!+-" else i.x).append(new)
  return new

def DATA(src=None, rank=False) -> data:
  "Adds rows from `src` to a DATA. Summarizes them in `cols`. Maybe sorts the rows."
  i = _DATA()
  [add2data(i,lst) for  lst in src or []]
  if rank: i.rows.sort(key = lambda r:d2h(i,r))
  return i

# ### Update

def adds(i:col, lst:list) -> col:
  "Update a NUM or SYM with many items."
  [add2col(i,x) for x in lst]
  return i

def add2data(i:data,row1:row) -> None:
  "Update contents of a DATA. Used by `DATA()`. First time through, `i.cols` is None."
  if    i.cols: i.rows.append([add2col(col,x) for col,x in zip(i.cols.all,row1)])
  else: i.cols= COLS(row1)

def add2col(i:col, x:any, n=1) -> any:
  "`n` times, update NUM or SYM with one item. Used by `add2data()`." 
  if x != "?":
    i.n += n
    if i.this is NUM: _add2num(i,x,n)
    else: i.has[x] = i.has.get(x,0) + n
  return x

def _add2num(i:num, x:any, n:int) -> None:
  "`n` times, update a NUM with one item. Used by `add2col()`."
  i.lo = min(x, i.lo)
  i.hi = max(x, i.hi)
  for _ in range(n):
    if i.has != None: i.has += [x]
    d     = x - i.mu
    i.mu += d / i.n
    i.m2 += d * (x -  i.mu)

def add2xy(i:xy, x: int | float , y:atom) -> None:
  "Update an XY with `x` and `y`."
  if x != "?":
    i.n    += 1
    i.lo    =  min(i.lo, x)
    i.hi    =  max(i.hi, x)
    i.ys[y] = i.ys.get(y,0) + 1

def mergable(xy1: xy, xy2: xy, small:int) -> xy | None:
  "Return the merge  if the whole is better than the parts. Used  by `merges()`."
  mabye = merge([xy1,xy2])
  e1  = ent(xy1.ys)
  e2  = ent(xy2.ys)
  e3  = ent(out.ys)
  if xy1.n < small or xy2.n < small or e3 <= (xy1.n*e1 + xy2.n*e2)/out.n: return maybe 

def merge(xys : list[xy]) -> xy:
  "Fuse together some  XYs into one XY. Called by `mergable`."
  out = XY(xys[0].at, xys[0].txt, xys[0].lo)
  for xy1 in xys:
    out.n += xy1.n
    out.lo = min(out.lo, xy1.lo)
    out.hi = max(out.hi, xy1.hi)
    for y,n in xy1.ys.items(): out.ys[y] = out.ys.get(y,0) + n
  return out

# ### Read (read in from another source)

# Read rows into a new DATA, guided by an old DATA.
def clone(i:data, inits=[], rank=False) -> data:
  "Copy a DATA (same column structure, with different rows). Optionally, sort it."
  return DATA([i.cols.names] + inits, rank=rank )

# Read rows  from disk.
def csv(file="-") -> row:
  "Iteratively  return `row` from a file, or standard input."
  with file_or_stdin(None if file=="-" else file) as src:
    for line in src:
      line = re.sub(r'([\n\t\r ]|#.*)', '', line)
      if line: yield [coerce(s.strip()) for s in line.split(",")]

# ### Read (read out: query the structs)

def mid(i:col) -> atom:
  "Middle of a column."
  return i.mu if i.this is NUM else max(i.has, key=i.has.get)

def div(i:col) -> float:
  "Diversity of a column."
  return  (0 if i.n <2 else (i.m2/(i.n-1))**.5) if i.this is NUM else ent(i.has)

def stats(i:data, fun=mid, what:cols=None) -> dict[str,atom]:
  "Stats of some columns (defaults to `fun=mid` of `data.cols.x`)."
  return {c.txt:fun(c) for c in what or i.cols.x}

def norm(i:num,x) -> float:
  "Normalize `x` to 0..1"
  return x if x=="?" else (x-i.lo)/(i.hi - i.lo - 1E-30)

def isLeaf(i:node):
  "True if a node has no leaves."
  return i.left==i.right==None

def selects(i:xy, r:row) -> bool:
  "Returns true if a row falls within the lo/hi range of an XY."
  x = r[i.at]
  return x=="?" or i.lo==x if i.lo==i.hi else i.lo <= x < i.hi

def wanted(i:want, d:dict) -> float :
  "How much does d selects for `i.best`? "
  b,r = 1E-30,1E-30 # avoid divide by zero errors
  for k,v in d.items():
    if k==i.best: b += v/i.BESTS
    else        : r += v/i.RESTS
  support     = b        # how often we see best
  probability = b/(b+r)  # probability of seeing best, relative to  all probabilities
  return support * probability

#--------- --------- --------- --------- --------- --------- --------- --------- --------
# ## Discretization
# Divide a range into many bins. Iteratively merge adjacent bins if
# they  are too underpopulated  or too uninformative (as measured by
# entropy). This approach was inspired by Kerber's
# [ChiMerge](https://sci2s.ugr.es/keel/pdf/algorithm/congreso/1992-Kerber-ChimErge-AAAI92.pdf)
# algorithm.

def discretize(i:col, klasses:classes, want: callable) -> list[xy] :
  "Find good ranges for the i-th column within `klasses`."
  bins = {}
  [_divideIntoBins(i, r[i.at], klass, bins) for klass,rows1 in klasses.items()
                                  for r in rows1 if r[i.at] != "?"]
  return _combine(col, sorted(bins.values(), key=lambda z:z.lo),
                       sum(len(rs) for rs in klasses.values()) / the.xys,
                       want)

def _divideIntoBins(i:col,x:atom, y:str, bins:dict) -> None:
  "Store `x,y` in the right part of `bins`. Used by `discretize()`."
  k = x if i.this is SYM else min(the.xys -1, int(the.xys * norm(i,x)))
  bins[k] = bins[k] if k in bins else XY(i.at,i.txt,x)
  add2xy(bins[k],x,y)

def _combine(i:col, xys: list[xy], small, want) -> list[xy] :
  if col.this is NUM:
    xys = _span(_merges(xys, lambda a,b: mergable(a,b,small))) 
    n   = the.wanted * sorted(wanted(want,xy1.ys) for xys1 in xys])[-1]
    xys = _merges(xys, lambda a,b: wanted(want, a.ys) < n wanted(want, b.ys) < n)
  return xys

def _merges(b4, fun):
  "Try merging adjacent items in `b4`. If successful, repeat. Used by `_combine()`."
  j, now  = 0, []
  while j <  len(b4):
    a = b4[j]
    if j <  len(b4) - 1:
      b = b4[j+1]
      if ab := fun(a,b):
        a = ab
        j = j+1  # if i can merge, jump over the merged item
    now += [a]
    j += 1
  return b4 if len(now) == len(b4) else _merges(now, fun)

def _span(xys : list[xy]) -> list[xy]:
  "Ensure there are no gaps in the `x` ranges of `xys`. Used by `discretize()`."
  for j in range(1,len(xys)):  xys[j].lo = xys[j-1].hi
  xys[0].lo  = -1E30
  xys[-1].hi =  1E30
  return xys

#--------- --------- --------- --------- --------- --------- --------- --------- --------
# ## Trees

def tree(i:data, klasses:classes, wanted:callable, stop:int=4) -> node:
  "Return a binary tree, each level splitting on the range  with most `score`."
  def _grow(klasses:classes, lvl:int=1, above:int=1E30) -> node:
    "Collect the stats needed for branching, then call `_branch()`."
    counts = {k:len(rows1) for k,rows1 in klasses.items()}
    total  = sum(n for n in counts.values())
    most   = max(counts, key=counts.get)
    return _branch(NODE(klasses), lvl, above, total, most)

  def _branch(here:node, lvl:int, above:int, total:int, most:int) -> node:
    "Divide the data on tbe best cut. Recurse."
    if total > 2*stop and total < above and most < total: #most==total means "purity" (all of one class)
      cut = max(cuts,  key=lambda cut0: _want(cut0, here.klasses))
      left,right = _split(cut, here.klasses)
      here.left  = _grow(left,  lvl+1, total)
      here.right = _grow(right, lvl+1, total)
    return here

  def _want(cut:xy, klasses:classes) -> float :
    "How much do we want each way that `cut` can split the `klasses`?"
    return want(wanted, {k:len(rows1) for k,rows1 in _split(cut,klasses)[0].items()})

  cuts = [cut for col1 in i.cols.x for cut in discretize(col1,klasses)]
  return _grow(klasses)

def _split(cut:xy, klasses:classes) -> tuple[classes,classes]:
  "Find the  classes that `are`, `arent` selected by `cut`."
  are  = {klass:[] for klass in klasses}
  arent = {klass:[] for klass in klasses}
  for klass,rows1 in klasses.items():
    [(are if i.selects(row1) else arent)[klass].append(row1) for row1 in rows1]
  return are,arent

#--------- --------- --------- --------- --------- --------- --------- --------- --------
# ## Distances

def d2h(i:data, r:row) -> float:
  "distance to `heaven` (which is the distance of the `y` vals to the best values)."
  n = sum(abs(norm(num,r[num.at]) - num.maximize)**the.p for num in i.cols.y)
  return (n / len(i.cols.y))**(1/the.p)

def dists(i:data, r1:row, r2:row) -> float:
  "Distances between two rows."
  n = sum(dist(c, r1[c.at], r2[c.at])**the.p for c in i.cols.x)
  return (n / len(i.cols.x))**(1/the.p)

def dist(i:col, x:any, y:any) -> float:
  "Distance between two values. Used by `dists()`."
  if  x==y=="?": return 1
  if i.this is SYM: return x != y
  x, y = norm(i,x), norm(i,y)
  x = x if x !="?" else (1 if y<0.5 else 0)
  y = y if y !="?" else (1 if x<0.5 else 0)
  return abs(x-y)

def neighbors(i:data, r1:row, region:rows=None) -> list[row]:
  "Sort the `region` (default=`i.rows`),ascending, by distance to `r1`."
  return sorted(region or i.rows, key=lambda r2: dists(i,r1,r2))

#--------- --------- --------- --------- --------- --------- --------- --------- --------
# ## Clustering

def branch(i:data, region:rows=None, stop=None, rest=None, evals=1, before=None):
  "Recursively bi-cluster `region`, reursing only down the best half."
  region = region or i.rows
  stop = stop or 2*len(region)**the.N
  rest = rest or []
  if len(region) > stop:
    lefts,rights,left  = half(i,region, True, before)
    return branch(i,lefts, stop, rest+rights, evals+1, left)
  else:
    return region,rest,evals

def half(i:data, region:rows, sortp=False, before=None) -> tuple[rows,rows,row]:
  "Split the `region` in half according to each row's distance to two distant points. Used by `branch()`."
  mid = int(len(region) // 2)
  left,right,C = _twoFaraway(i, region, sortp=sortp, before=before)
  project = lambda row1: (dists(i,row1,left)**2 + C**2 - dists(i,row1,right)**2)/(2*C)
  tmp = sorted(region, key=project)
  return tmp[:mid], tmp[mid:], left

def _twoFaraway(i:data, region:rows,before=None, sortp=False) -> tuple[row,row,float]:
  "Find two distant points within the `region`. Used by `half()`." 
  region = random.choices(region, k=min(the.Half, len(region)))
  x = before or _faraway(i, random.choice(region), region)
  y = _faraway(i, x, region)
  if sortp and d2h(i,y) < d2h(i,x): x,y = y,x
  return x, y,  dists(i,x,y)

def _faraway(i:data, r1:row, region:rows) -> row:
  "Find something far away from `r1` with the `region`. Used by `_twoFaraway()`."
  farEnough = int( len(region) * the.Far) # to avoid outliers, don't go 100% far away
  return neighbors(i,r1, region)[farEnough]

#--------- --------- --------- --------- --------- --------- --------- --------- --------
# ## Likelihoods

def loglikes(i:data, r:row|dict, nall:int, nh:int) -> float:
  "Likelihood of a `row` belonging to a DATA."
  prior = (len(i.rows) + the.k) / (nall + the.k*nh)
  likes = [like(c, r[c.at], prior) for c in i.cols.x if r[c.at] != "?"]
  return sum(math.log(x) for x in likes + [prior] if x>0)

def like(i:col, x:any, prior:float) -> float:
  "Likelihood of `x` belonging to a col. Used by `loglikes()`."  
  return _like4num(i,x) if i.this is NUM else (i.has.get(x,0) + the.m*prior) / (i.n+the.m)

def _like4num(i:num,x):
  "Likelihood of `x` belonging to a NUM. Used by `like()`."
  v     = div(i)**2 + 1E-30
  nom   = math.e**(-1*(x - mid(i))**2/(2*v)) + 1E-30
  denom = (2*math.pi*v) **0.5
  return min(1, nom/(denom + 1E-30))

#--------- --------- --------- --------- --------- --------- --------- --------- --------
# ## Optimization

def smo(i:data, score=lambda B,R: B-R):
  "Sequential model optimization."
  def _ranked(lst:rows) -> rows:
    "Sort `lst` by distance to heaven. Called by `_smo1()`."
    return sorted(lst, key = lambda r:d2h(i,r))

  def _guess(todo:rows, done:rows) -> rows:
    "Divide `done` into `best`,`rest`. Use those to guess the order of unlabelled rows. Called by `_smo1()`."
    cut  = int(.5 + len(done) ** the.N)
    best = clone(i, done[:cut])
    rest = clone(i, done[cut:])
    key  = lambda r: score(loglikes(best, r, len(done), 2),
                           loglikes(rest, r, len(done), 2))
    random.shuffle(todo) # optimization: only sort a random subset of todo 
    return sorted(todo[:the.any], key=key, reverse=True) + todo[the.any:]

  def _smo1(todo:rows, done:rows) -> rows:
    "Guess the `top`  unlabeled row, add that to `done`, resort `done`, and repeat"
    for _ in range(the.Last - the.label):
      if len(todo) < 3: break
      top,*todo = _guess(todo, done)
      done += [top]
      done = _ranked(done)
    return done

  random.shuffle(i.rows) # remove any  bias from older runs
  return _smo1(i.rows[the.label:], _ranked(i.rows[:the.label]))

#--------- --------- --------- --------- --------- --------- --------- --------- ---------
# ## Misc Functions:

def ent(d:dict) -> float:
  "Entropy of a distribution."
  N = sum(v for v in d.values())
  return -sum(v/N*math.log(v/N,2) for v in d.values())


def show(x:any) -> any:
  "Some pretty-print tricks."
  it = type(x)
  if it == o and x.this is XY: return showXY(x)
  if it == float: return round(x,the.decs)
  if it == list:  return [show(v) for v in x]
  if it == dict:  return "("+' '.join([f":{k} {show(v)}" for k,v in x.items()])+")"
  if it == o:     return show(x.__dict__)
  if it == str:   return '"'+str(x)+'"'
  if callable(x): return x.__name__
  return x

def showXY(i:xy):
  "Pretty prints for XYs. Used when (e.g.) printing  conditions in a tree."
  if i.lo == -1E30: return f"{i.txt} < {i.hi}"
  if i.hi ==  1E30: return f"{i.txt} >= {i.lo}"
  if i.lo == i.hi:  return f"{i.txt} == {i.lo}"
  return f"{i.lo} <= {i.txt} < {i.hi}"

def btw(*args, **kwargs):
  "Print to standard error, flush standard error, do not print newlines."
  print(*args, file=sys.stderr, end="", flush=True, **kwargs)

#--------- --------- --------- --------- --------- --------- --------- --------- ---------
# ## Main

def main() -> None: 
  "Update `the` from the command line; call the start-up command `the.Run`."
  cli(the.__dict__)
  if   the.help: eg.help()
  elif the.version: print("Ezr",__version__)
  else: run(the.Run)

def run(s:str) -> int:
  "Reset the seed. Run `eg.s()`, then restore old settings. Return '1' on failure. Called by `main()`."
  reset = {k:v for k,v in the.__dict__.items()}
  random.seed(the.seed)
  out = _run1(s)
  for k,v in reset.items(): the.__dict__[k]=v
  return out

def _run1(s:str) -> False:
  "Return either the result for running `eg.s()`, or `False` (if there was a crash). Called by `run()`."
  try:
    return getattr(eg, s)()
  except Exception:
    print(traceback.format_exc())
    return False

#--------- --------- --------- --------- --------- --------- --------- --------- ---------
# ## Start-up Actions
# `./ezr.py -R xx` with execute `eg.xx()` at start-up time.

class eg:
  "Store all the start up actions"
  def all():
    "Run all actions. Return to OS a count of failing actions (those returning `False`.."
    sys.exit(sum(run(s)==False for s in dir(eg) if s[0] !="_" and s !=  "all"))

  def help():
    "Print help."
    print(re.sub(r"\n    ","\n",__doc__))
    print("Start-up commands:")
    [print(f"  -R {k:15} {getattr(eg,k).__doc__}") for k in dir(eg) if k[0] !=  "_"]

  def the(): 
    "Show settings."
    print(the)

  def csv(): 
    "Print some of the csv rows."
    [print(x) for i,x in enumerate(csv(the.train)) if i%50==0]

  def cols():
    "Demo of column generation."
    [print(show(col)) for col in 
       COLS(["Clndrs","Volume","HpX","Model","origin","Lbs-","Acc+","Mpg+"]).all]

  def num():
    "Show mid and div from NUMbers."
    n= adds(NUM(),range(100))
    print(show(dict(div=div(n), mid=mid(n))))

  def sym():
    "Show mid and div from SYMbols."
    s= adds(SYM(),"aaaabbc")
    print(show(dict(div=div(s), mid=mid(s))))

  def klasses():
    "Show sorted rows from a DATA."
    data1= DATA(csv(the.train), rank=True)
    print(show(stats(data1, what=data1.cols.y)))
    print(data1.cols.names)
    for i,row in enumerate(data1.rows):
      if i % 40 == 0: print(i,"\t",row)

  def clone():
    "Check that clones have same structure as original."
    data1= DATA(csv(the.train), rank=True)
    print(show(stats(data1)))
    print(show(stats(clone(data1, data1.rows))))

  def loglike():
    "Show some bayes calcs."
    data1= DATA(csv(the.train))
    print(show(sorted(loglikes(data1,row,1000,2)
                      for i,row in enumerate(data1.rows) if i%10==0)))

  def dists():
    "Show some distance calcs."
    data1= DATA(csv(the.train))
    print(show(sorted(dists(data1, data1.rows[0], row)
                      for i,row in enumerate(data1.rows) if i%10==0)))
    for _ in range(5):
      print("")
      x,y,C = twoFaraway(data1,data1.rows)
      print(x,C);print(y)

  def branch():
    "Halve the data."
    data1 = DATA(csv(the.train))
    a,b,_ = half(data1,data1.rows)
    print(len(a), len(b))
    best,rest,n = branch(data1,stop=4)
    print(n,d2h(data1,best[0]))

  def smo():
    "Optimize something."
    d = DATA(csv(the.train))
    print(show(d.cols.all[1]))
    print(">",len(d.rows))
    best = smo(d)
    print(len(best),d2h(d, best[0]))

  def profileSmo():
    "Example of profiling."
    import cProfile
    import pstats
    cProfile.run('smo(DATA(csv(the.train)))','/tmp/out1')
    p = pstats.Stats('/tmp/out1')
    p.sort_stats('time').print_stats(20)

  def smo20():
    "Run smo 20 times."
    d   = DATA(src=csv(the.train))
    b4  = adds(NUM(), [d2h(d,row) for row in d.rows])
    now = adds(NUM(), [d2h(d, smo(d)[0]) for _ in range(20)])
    sep=",\t"
    print("mid",show(mid(b4)), show(mid(now)),show(b4.lo),sep=sep,end=sep)
    print("div",show(div(b4)), show(div(now)),sep=sep,end=sep)
    print(the.train)

  def discretize():
    "Find useful ranges."
    data1 = DATA(csv(the.train), rank=True)
    n = int(len(data1.rows)**.5)
    klasses = dict(best=data1.rows[:n], rest=(data1.rows[n:]))
    for xcol in data1.cols.x:
      print("")
      for xy1 in discretize(xcol, klasses):
        print(show(bore(xy1.ys,"best",n,4*n)),f"{show(xy1):20}",xy1.ys,sep="\t") 

#--------- --------- --------- --------- --------- --------- --------- --------- ---------
if __name__ == "__main__": main()

# ## Conventions in this code

# - **Doc, Config:** At top of file, add in all settings to the __doc__ string. 
#   Parse that string to create `the` global settings.
#   Also, every function gets a one line doc string. For documentation longer than one line,
#   add this outside the function.
# - **TDD:** Lots of little tests. At end of file, add in demos/tests as methods of the `eg` class 
#   Report a test failure by return `False`. Note that `eg.all()` will run all demos/tests
#   and return the number of failures to the operating system.
# - **Composition:** Allow for reading from standard input (so this code can be used in a pipe).
# - **Abstraction:** Make much use of error handling and iterators.
# - **Types:** Use type hints for function args and return types.
#   Don't use type names for variables or function names.  E.g. use `rows1` not `rows`. E.g. use `klasses` not `classes`; 
# - **OO? Hell no!:** Group together similar functionality for difference types (so don't use classes).
#   And to enable polymorphism, add a `this=CONSTRUCTOR` field to all objects.
# - **Functional programming? heck yeah! :** lots of comprehensions and lambda bodies.
# - **Information hiding:** Mark private functions with a leading  "_". 
#   (such functions  should not be called by outside users).
# - **Refactoring:**  Functions over 5 lines get a second look: can they be split in two?
#   Also, line length,  try not to blow 90 characters.
# - **Misc:**  Some functions "chain"; i.e. `f1()` calls `f2()` which calls `f3()`.
#   And the sub-functions are never called from anywhere else. For such chained
#   functions, add the comment (e.g.)  `Used by f1()`.
#   Also,  if a function is about some data type, use `i` (not `self` and not `this`)
#   for first function argument.
#   And do not use `i` otherwise (e.g. not as a loop counter).

