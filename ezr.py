#!/usr/bin/env python3 -B
# <!-- vim: set ts=2 sw=2 sts=2 et: -->
"""
    ezr.py : an experiment in easier explainable AI (less is more).    
    (C) 2024 Tim Menzies (timm@ieee.org) BSD-2 license.    
        
    OPTIONS:    
      -a --any     #todo's to explore             = 100   
      -b  --beam    print factor for examples     =  1
      -c --cohen   size of the Cohen d            = 0.35
      -d --decs    #decimals for showing floats   = 3    
      -e --enough  want cuts at least this good   = 0.1   
      -F --Far     how far to seek faraway        = 0.8    
      -g --GuessFaster use fast guessing tricks   = True
      -h --help    show help                      = False
      -H --Half    #rows for searching for poles  = 128    
      -k --k       bayes low frequency hack #1    = 1    
      -l --label   initial number for labelling    = 4    
      -L --Last    max allow #labelling            = 30    
      -m --m       bayes low frequency hack #2    = 2    
      -n --n       tinyN                          = 12    
      -N --N       smallN                         = 0.5    
      -p --p       distance function coefficient  = 2    
      -R --Run     start up action method         = help    
      -s --seed    random number seed             = 1234567891    
      -t --train   training data                  = data/misc/auto93.csv    
      -T --test    test data (defaults to train)  = None  
      -v --version show version                   = False   
      -x --xys     max #bins in discretization    = 16    
"""
# <h2>Note</h2><p align="left">See end-of-file for this file's  conventions / principles /practices.
# And FYI, our random number seed is an 
# odious, apocalyptic, deficient, pernicious, polite, prime number
# (see https://numbersaplenty.com/1234567891).

from __future__ import annotations 

__author__  = "Tim Menzies"
__version__ = "0.1.0"

import re,ast,sys,math,random,traceback
from fileinput import FileInput as file_or_stdin
from typing import Any as any
from typing import Callable 

R= random.random
#--------- --------- --------- --------- --------- --------- --------- --------- --------
# ## Types

class o:
  "`o` is a Class for quick inits of structs,  and for pretty prints."
  def __init__(i,**d): i.__dict__.update(d)
  def __repr__(i): return i.__class__.__name__+str(show(i.__dict__))

# Other types used in this system.
xy,cols,data,node,num,sym,node,want = o,o,o,o,o,o,o,o
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
  "NUM columns incrementally summarizes a stream of numbers."
  return o(this=NUM, txt=txt, at=at, n=0, hi=-1E30, lo=1E30, 
           mu=0, m2=0, sd=0, maximize = txt[-1] != "-")

def XY(at,txt,lo,hi=None,ys=None) -> xy:
  "`ys` counts symbols seen in one column between `lo`.. `hi` of another column."
  return o(this=XY, n=0, at=at, txt=txt, lo=lo, hi=hi or lo, ys=ys or {})

def NODE(klasses: classes, parent: node, left=None, right=None) -> node:
  "NODEs are parts of binary trees."
  return o(this=NODE, klasses=klasses, parent=parent, left=left, right=right, cut=None)

def WANT(best="best", bests=1, rests=1) -> want:
  "Used to score how well a distribution selects for  `best'."
  return o(this=WANT, best=best, bests=bests, rests=rests)
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

def add2cols(i:cols, n:int, s:str) -> col:
  "Create a NUM or SYM from `s` using the above rules. Adds it to `x`, `y`, `all` (if appropriate)."
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
    d     = x - i.mu
    i.mu += d / i.n
    i.m2 += d * (x -  i.mu)
    i.sd  = 0 if i.n <2 else (i.m2/(i.n-1))**.5

def add2xy(i:xy, x: int | float , y:atom) -> None:
  "Update an XY with `x` and `y`."
  if x != "?":
    i.n    += 1
    i.lo    =  min(i.lo, x)
    i.hi    =  max(i.hi, x)
    i.ys[y] = i.ys.get(y,0) + 1

def mergable(xy1: xy, xy2: xy, small:int) -> xy | None:
  "Return the merge  if the whole is better than the parts. Used  by `merges()`."
  maybe = merge([xy1,xy2])
  e1  = entropy(xy1.ys)
  e2  = entropy(xy2.ys)
  if xy1.n < small or xy2.n < small: return maybe
  if entropy(maybe.ys) <= (xy1.n*e1 + xy2.n*e2)/maybe.n: return maybe

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
  return i.sd if i.this is NUM else entropy(i._has)

def mids(i:data,what:cols=None):
  return [show(mid(c)) for c in what or i.cols.all]

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
    if k==i.best: b += v/i.bests
    else        : r += v/i.rests
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

def discretize(i:col, klasses:classes) -> list[xy] :
  "Find good ranges for the i-th column within `klasses`."
  d,n  = {},0
  for klass,rows1 in klasses.items():
    for r in rows1:
      n += 1
      x = r[i.at]
      if x !="?": add2xy(_where(d,x,i), x, klass)
  xys = sorted(d.values(), key=lambda z:z.lo)
  xys = xys if i.this is SYM else _merges(xys, n/the.xys)
  return [] if len(xys) < 2 else xys

def _where(xys:dict[atom,xy], x:atom, i:col) -> xy:
  "Find and return the `k`-th bin within `xys` that should hold `x`."
  k = x if i.this is SYM else min(the.xys - 1, int(the.xys * norm(i,x)))
  xys[k] = xys[k] if k in xys else XY(i.at,i.txt,x)
  return xys[k]

def _merges(b4:list[xy], enough):
  "Try merging adjacent items in `b4`. If successful, repeat. Used by `_combine()`."
  j, now  = 0, []
  while j <  len(b4):
    a = b4[j]
    if j <  len(b4) - 1:
      b = b4[j+1]
      if ab := mergable(a,b,enough):
        a = ab
        j = j+1  # if i can merge, jump over the merged item
    now += [a]
    j += 1
  return _span(b4) if len(now) == len(b4) else _merges(now, enough)

def _span(xys : list[xy]) -> list[xy]:
  "Ensure there are no gaps in the `x` ranges of `xys`. Used by `_merges()`."
  for j in range(1,len(xys)):  xys[j].lo = xys[j-1].hi
  xys[0].lo  = -1E30
  xys[-1].hi =  1E30
  return xys

#--------- --------- --------- --------- --------- --------- --------- --------- --------
# ## Trees

def tree(i:data, klasses:classes, want1:Callable, stop:int=4) -> node:
  "Return a binary tree, each level splitting on the range  with most `score`."
  def _grow(klasses:classes, lvl:int=1, parent=None) -> node:
    "Collect the stats needed for branching, then call `_branch()`."
    counts = {k:len(rows1) for k,rows1 in klasses.items()}
    total  = sum(counts.values())
    most   = counts[max(counts, key=counts.get)]
    return _branch(NODE(klasses,parent), lvl, total, most)

  def _branch(here:node, lvl:int,  total:int, most:int) -> node:
    "Divide the data on tbe best cut. Recurse."
    if total > 2*stop and  most < total: #most==total means "purity" (all of one: class)
      here.cut = max(cuts,  key=lambda cut0: _want(cut0, here.klasses))
      left,right = _cut(here.cut, here.klasses)
      lefts = sum(len(rows1) for rows1 in left.values())
      rights = sum(len(rows1) for rows1 in right.values())
      if lefts < total and rights < total:
         here.left  = _grow(left,  lvl+1, here)
         here.right = _grow(right, lvl+1, here)
    return here

  def _want(cut:xy, klasses:classes) -> float :
    "How much do we want each way that `cut` can split the `klasses`?"
    return wanted(want1, {k:len(rows1) for k,rows1 in _cut(cut,klasses)[0].items()})

  cuts = [cut for col1 in i.cols.x for cut in discretize(col1,klasses)]
  return _grow(klasses)

def _cut(cut:xy, klasses:classes) -> tuple[classes,classes]:
  "Find the  classes that `are`, `arenot` selected by `cut`."
  are  = {klass:[] for klass in klasses}
  arenot = {klass:[] for klass in klasses}
  for klass,rows1 in klasses.items():
    [(are if selects(cut,row1) else arenot)[klass].append(row1) for row1 in rows1]
  return are,arenot

def nodes(i:node, lvl=0, left=True) -> node:
  "Iterator to return nodes."
  if i:
    yield i,lvl,left
    for j,lvl1,left1  in nodes(i.left,  lvl+1, left=True) : yield j,lvl1,left1
    for j,lvl1,right1 in nodes(i.right, lvl+1, left=False): yield j,lvl1,right1

def showTree(i:node):
  "Pretty print a tree."
  print("")
  for j,lvl,isLeft in nodes(i):
    pre=""
    if lvl>0:
      pre = f"if {showXY(j.parent.cut)}" if isLeft else "else "
    print(f"{'|.. '*(lvl-1) +  pre:35}",
          show({k:len(rows) for k,rows in j.klasses.items()}))
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

def where(i:data, dendo, row):
  if dendo.reference:
    if dists(i,row,dendo.reference) < dendo.enough:
       return where(i, dendo.right, row)
    return where(i, dendo.left,row)
  else:
    return dendo.here

def dendogram(i:data, region:rows=None, stop=None, before=None):
  region = region or i.rows
  stop = stop or 2*len(region)**the.N
  node = o(this="dendogram",here=clone(i,region),
           reference=None, enough=0,
           left=None,right=None)
  if len(region) > stop:
    lefts,rights,left,right  = half(i,region, False, before)
    node.enough = dists(i,right,rights[0])
    node.reference=right
    node.left=dendogram(i,lefts, stop, left)
    node.right=dendogram(i,rights,stop, right) 
  return node 

def showDendo(node,lvl=0):
    print(("|.. "*lvl) + str( len(node.here.rows)),end="")
    if node.left or node.right: print("")
    else: print("\t",show(mids(node.here,node.here.cols.y)))
    if node.left: showDendo(node.left,lvl+1)
    if node.right: showDendo(node.right,lvl+1)


def branch(i:data, region:rows=None, stop=None, rest=None, evals=1, before=None):
  "Recursively bi-cluster `region`, recurse only down the best half."
  region = region or i.rows
  if not stop: random.shuffle(region)
  stop = stop or 2*len(region)**the.N
  rest = rest or []
  if len(region) > stop:
    lefts,rights,left,_  = half(i,region, True, before)
    return branch(i,lefts, stop, rest+rights, evals+1, left)
  else:
    return region,rest,evals

def half(i:data, region:rows, sortp=False, before=None) -> tuple[rows,rows,row]:
  "Split the `region` in half according to each row's distance to two distant points. Used by `branch()`."
  mid = int(len(region) // 2)
  left,right,C = _twoFaraway(i, region, sortp=sortp, before=before)
  project = lambda row1: (dists(i,row1,left)**2 + C**2 - dists(i,row1,right)**2)/(2*C)
  tmp = sorted(region, key=project)
  return tmp[:mid], tmp[mid:], left, right

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
def _tile(lst):
   num = adds(NUM(),lst)
   n=100
   print(f"{len(lst):5} : {num.mu:5.3} ({num.sd:5.3})",end="")
   sd=int(num.sd*n/2)
   mu=int(num.mu*n)
   print(" "*(mu-sd), "-"*sd,"+"*sd,sep="")

def smo(i:data, score=lambda B,R: B-R, callBack=lambda x:x ):
  "Sequential model optimization."
  def _ranked(lst:rows) -> rows:
    "Sort `lst` by distance to heaven. Called by `_smo1()`."
    lst = sorted(lst, key = lambda r:d2h(i,r))
    callBack([d2h(i,r) for r in lst])
    return lst

  def _guess(todo:rows, done:rows) -> rows:
    "Divide `done` into `best`,`rest`. Use those to guess the order of unlabelled rows. Called by `_smo1()`."
    cut  = int(.5 + len(done) ** the.N)
    best = clone(i, done[:cut])
    rest = clone(i, done[cut:])
    key  = lambda r: score(loglikes(best, r, len(done), 2),
                           loglikes(rest, r, len(done), 2))
    if the.GuessFaster:
      random.shuffle(todo) # optimization: only sort a random subset of todo 
      todo= sorted(todo[:the.any], key=key, reverse=True) + todo[the.any:]
      return  todo[:int(len(todo) *the.beam)]
    else:
      return sorted(todo,key=key,reverse=True)
      
    #return sorted(todo,key=key,reverse=True)

  def _smo1(todo:rows, done:rows) -> rows:
    "Guess the `top`  unlabeled row, add that to `done`, resort `done`, and repeat"
    for k in range(the.Last - the.label):
      if len(todo) < 3: break
      top,*todo = _guess(todo, done)
      done += [top]
      done = _ranked(done)
    return done

  random.shuffle(i.rows) # remove any  bias from older runs
  return _smo1(i.rows[the.label:], _ranked(i.rows[:the.label]))

#--------- --------- --------- --------- --------- --------- --------- --------- ---------
# ## Stats

class SOME:
    "Non-parametric statistics using reservoir sampling."
    def __init__(i, inits=[], txt="", max=512): 
      "Start stats. Maybe initialized with `inits`. Keep no more than `max` numbers."
      i.txt,i.max=txt,max
      i.lo, i.hi = 1E30, -1E30
      i.rank,i.n,i._has,i.ok = 0,0,[],True
      i.adds(inits)  

    def __repr__(i) -> str: 
      "Print the reservoir sampling."
      return  'SOME(' + str(dict(
                txt=i.txt,rank="i.rank",n=i.n, all=len(i._has), ok=i.ok)) + ")"

    def adds(i,a:any) -> None:  #comments
      "Handle multiple nests samples."
      for b in a:
        if   isinstance(b,(list,tuple)): [i.adds(c) for c in b]  
        elif isinstance(b,SOME):         [i.add(c) for c in b._has]
        else: i.add(b) 

    def add(i,x:number) -> None:  
      i.n += 1
      i.lo = min(x,i.lo)
      i.hi = max(x,i.hi)
      now  = len(i._has)
      if   now < i.max   : i.ok=False; i._has += [x]
      elif R() <= now/i.n: i.ok=False; i._has[ int(R() * now) ]

    def __eq__(i,j:SOME) -> bool:
      "True if all of cohen/cliffs/bootstrap say you are the same."
      return i.cliffs(j) and i.bootstrap(j) ## ordered slowest to fastest

    def has(i) -> list[number]:
      "Return the numbers, sorted."
      if not i.ok: i._has.sort()
      i.ok=True
      return i._has

    def mid(i) -> number:
      "Return the middle of the distribution."
      l = i.has()
      return l[len(l)//2]

    def div(i) -> number:
       "Return the deviance from the middle." 
       l = i.has()
       n = len(l)//10
       return (l[9*n] - l[n])/2.56

    def pooledSd(i,j:SOME) -> number:
      "Return a measure of the combined standard deviation."
      sd1, sd2 = i.div(), j.div()
      return (((i.n - 1)*sd1 * sd1 + (j.n-1)*sd2 * sd2) / (i.n + j.n-2))**.5

    def norm(i, n:number) -> float:
      "Noramlize `n` to the range 0..1 for min..max"
      return (n-i.lo)/(i.hi - i.lo + 1E-30)

    def bar(i, some:SOME, fmt="%8.3f", word="%10s", width=50) -> str:
      "Pretty print `some.has`."
      has = some.has() 
      out = [' '] * width
      cap = lambda x: 1 if x > 1 else (0 if x<0 else x)
      pos = lambda x: int(width * cap(i.norm(x)))
      [a, b, c, d, e]  = [has[int(len(has)*x)] for x in [0.1,0.3,0.5,0.7,0.9]]
      [na,nb,nc,nd,ne] = [pos(x) for x in [a,b,c,d,e]] 
      for j in range(na,nb): out[j] = "-"
      for j in range(nd,ne): out[j] = "-"
      out[width//2] = "|"
      out[nc] = "*" 
      return ', '.join(["%2d" % some.rank, word % some.txt, fmt%c, fmt%(d-b),
                        ''.join(out),fmt%has[0],fmt%has[-1]])

    def delta(i,j:SOME) -> float:
      "Report distance between two SOMEs, modulated in terms of the standard deviation."
      return abs(i.mid() - j.mid()) / ((i.div()**2/i.n + j.div()**2/j.n)**.5 + 1E-30)

    def cohen(i,j:SOME):
      return abs( i.mid() - j.mid() ) < the.cohen * i.pooledSd(j)

    def cliffs(i,j:SOME, dull=0.147) -> bool:
      """non-parametric effect size. threshold is border between small=.11 and medium=.28 
      from Table1 of  https://doi.org/10.3102/10769986025002101
      """
      n,lt,gt = 0,0,0
      for x1 in i.has():
        for y1 in j.has():
          n += 1
          if x1 > y1: gt += 1
          if x1 < y1: lt += 1
      return abs(lt - gt)/n  < dull # true if same

    def  bootstrap(i,j:SOME,confidence=.05,samples=512) -> bool:
      """non-parametric significance test From Introduction to Bootstrap, 
        Efron and Tibshirani, 1993, chapter 20. https://doi.org/10.1201/9780429246593"""
      y0,z0  = i.has(), j.has()
      x,y,z  = SOME(inits=y0+z0), SOME(inits=y0), SOME(inits=z0)
      delta0 = y.delta(z)
      yhat   = [y1 - y.mid() + x.mid() for y1 in y0]
      zhat   = [z1 - z.mid() + x.mid() for z1 in z0] 
      pull   = lambda l:SOME(random.choices(l, k=len(l))) 
      n      = sum(pull(yhat).delta(pull(zhat)) > delta0 for _ in range(samples)) 
      return n / samples >= confidence # true if different

#--------- --------- --------- --------- --------- --------- --------- --------- ---------
# ## Misc Functions:

# SOME general Python tricks

def entropy(d:dict) -> float:
  "Entropy of a distribution."
  N = sum(v for v in d.values())
  return -sum(v/N*math.log(v/N,2) for v in d.values())

def normal(mu:number,sd:number) -> float:
  "Generate a number from `N(mu,sd)`."
  return mu+sd*math.sqrt(-2*math.log(R())) * math.cos(2*math.pi*R())

def show(x:any) -> any:
  "SOME pretty-print tricks."
  it = type(x)
  if it == float: return round(x,the.decs)
  if it == list:  return [show(v) for v in x]
  if it == dict:  return "("+' '.join([f":{k} {show(v)}" for k,v in x.items()])+")"
  if it == o:     return show(x.__dict__)
  if it == str:   return '"'+str(x)+'"'
  if callable(x): return x.__name__
  if it == o and x.this is XY: return showXY(x)
  return x

def showXY(i:xy) -> str:
  "Pretty prints for XYs. Used when (e.g.) printing  conditions in a tree."
  if i.lo == -1E30: return f"{i.txt} < {i.hi}"
  if i.hi ==  1E30: return f"{i.txt} >= {i.lo}"
  if i.lo == i.hi:  return f"{i.txt} == {i.lo}"
  return f"{i.lo} <= {i.txt} < {i.hi}"

def btw(*args, **kwargs) -> None:
  "Print to standard error, flush standard error, do not print newlines."
  print(*args, file=sys.stderr, end="", flush=True, **kwargs)

def sk(somes:list[SOME]) -> list[SOME]:
  "Sort nums on mid. give adjacent nums the same rank if they are statistically the same"
  def sk1(somes: list[SOME], rank:integer, cut:integer=None) -> interger:
    most, b4 = -1, SOME(somes)
    for j in range(1,len(somes)):
      lhs = SOME(somes[:j])
      rhs = SOME(somes[j:])
      tmp = (lhs.n*abs(lhs.mid() - b4.mid()) + rhs.n*abs(rhs.mid() - b4.mid())) / b4.n
      if tmp > most:
         most,cut = tmp,j
    if cut:
      some1,some2 = SOME(somes[:cut]), SOME(somes[cut:])
      if not some1.cohen(some2):
        if some1 != some2:
          rank = sk1(somes[:cut], rank) + 1
          rank = sk1(somes[cut:], rank)
          return rank
    for some in somes: some.rank = rank
    return rank
 
  somes = sorted(somes, key=lambda some: some.mid()) #lambda some : some.mid())
  sk1(somes,0)
  return somes

def file2somes(file:str) -> list[SOME]:
  "Reads text file into a list of `SOMEs`."
  def asNum(s):
    try: return float(s)
    except Exception: return s
   
  somes=[]
  with open(file) as fp: 
    for word in [asNum(x) for s in fp.readlines() for x in s.split()]:
      if isinstance(word,str): some = SOME(txt=word); somes.append(some)
      else                   : some.add(word)    
  return somes

def bars(somes: list[SOME], width:integer=40) ->  None:
  "Prints multiple `somes` on the same scale."
  all = SOME(somes)
  last = None
  for some in sk(some):
    if some.rank != last: print("#")
    last=some.rank
    print(all.bar(some.has(), width=width, word="%20s", fmt="%5.2f"))

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
    print(', '.join(["N"]+ data1.cols.names))
    for i,row in enumerate(data1.rows):
      if i % 20 == 0: print(i,"\t",row)

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
      x,y,C = _twoFaraway(data1,data1.rows)
      print(x,C);print(y)

  def branch():
    "Halve the data."
    data1 = DATA(csv(the.train))
    print(*data1.cols.names,"evals","d2h", "rx",sep=",")
    print(mids(data1),len(data1.rows),show(d2h(data1,mids(data1))), "base",sep=",")
    #a,b,_,__ = half(data1,data1.rows)
    best,rest,n = branch(data1,stop=4)
    middle=mids(clone(data1,best))
    top=best[0]
    print(middle,n+len(best)-1,show(d2h(data1,middle)),"mid of final leaf",sep=",")
    print(top,n+len(best)-1,show(d2h(data1,top)),"best item in final leaf",sep=",")
    return best,rest,data1


  def branchTree():
    best,rest,data1 = eg.branch()

    bests   = len(best)
    rests   = len(rest)
    klasses = dict(best=best,rest=rest)
    want1   = WANT(best="best", bests=bests, rests=rests)
    showTree(tree(data1,klasses,want1))


  def dendogram():
    "Genrate a tree"
    data1 = DATA(csv(the.train))
    row =data1.rows[0]
    print(row)
    d = dendogram(data1)
    showDendo(d)
    print(mids(where(data1,d,row)))

  def smo():
    "Optimize something."
    d = DATA(csv(the.train))
    print(">",len(d.rows))
    done = smo(d,lambda B,R: B-R, _tile)
    bests   = int(len(done)**.5)
    rests   = len(done) - bests
    klasses = dict(best=done[:bests], rest=(done[bests:]))
    want1   = WANT(best="best", bests=bests, rests=rests)
    showTree(tree(d,klasses,want1))

  def alls():
    "try different sample sizes"
    policies = dict(exploit = lambda B,R: B-R)
    repeats=20
    d = DATA(csv(the.train))
    e = math.exp(1)
    rxs={}
    rxs["baseline"] = SOME(txt=f"baseline,{len(d.rows)}",inits=[d2h(d,row) for row in d.rows])
    for last in [15,20,25,30,35,40]:
      the.Last= last
      guess = lambda : clone(d,random.choices(d.rows, k=last+the.label),rank=True).rows[0]
      rx=f"random,{last}"
      rxs[rx] = SOME(txt=rx, inits=[d2h(d,guess()) for _ in range(repeats)])
      for beam in [1,0.9,0.8,0.7,0.6]:
        the.beam = beam
        for  guessFaster in [True]:
          for what,how in  policies.items():
            the.GuessFaster = guessFaster
            rx=f"{what}/{the.GuessFaster}/{beam},{the.Last}"
            rxs[rx] = SOME(txt=rx)
            for _ in range(repeats):
               btw(".")
               rxs[rx].add(d2h(d,smo(d,how)[0]))
            btw("\n")
    report(rxs.values())

  def smos():
    "try different sample sizes"
    policies = dict(exploit = lambda B,R: B-R,
                    EXPLORE = lambda B,R: (e**B + e**R)/abs(e**B - e**R + 1E-30))
    repeats=20
    d = DATA(csv(the.train))
    e = math.exp(1)
    rxs={}
    rxs["baseline"] = SOME(txt=f"baseline,{len(d.rows)}",inits=[d2h(d,row) for row in d.rows])
    for last in [10,20,30,40]:
      the.Last= last
      guess = lambda : clone(d,random.choices(d.rows, k=last+the.label),rank=True).rows[0]
      rx=f"random,{last}"
      rxs[rx] = SOME(txt=rx, inits=[d2h(d,guess()) for _ in range(repeats)])
      for  guessFaster in [False,True]:
        for what,how in  policies.items():
          the.GuessFaster = guessFaster
          rx=f"{what}/{the.GuessFaster},{the.Last}"
          rxs[rx] = SOME(txt=rx)
          for _ in range(repeats):
             btw(".")
             rxs[rx].add(d2h(d,smo(d,how)[0]))
          btw("\n")
    report(rxs.values())

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
    b4  = [d2h(d,row) for row in d.rows]
    _tile(b4)
    for n in [10,20,40,80,160,320]:
      print("\n RX, samples,   b4,      now,   lowest")
      the.Label=n
      d   = DATA(src=csv(the.train))
      b4  = [d2h(d,row) for row in d.rows] 
      b4  = adds(NUM(), b4)
      now = adds(NUM(), [d2h(d, smo(d)[0]) for _ in range(20)])
      sep=",\t"
      print("mid",n,show(mid(b4)), show(mid(now)), "lo:", show(b4.lo),sep=sep)
      print("div",n,show(div(b4)), show(div(now)), sep=sep)

  def divide():
    data1   = DATA(csv(the.train), rank=True)
    bests   = int(len(data1.rows)**.5)
    rests   = len(data1.rows) - bests
    klasses = dict(best=data1.rows[:bests], rest=(data1.rows[bests:]))
    want1   = WANT(best="best", bests=bests, rests=rests)
    for col1 in data1.cols.x :
      print("")
      bins = {}
      [_divideIntoBins(col1, r[col1.at], klass, bins) for klass,rows1 in klasses.items()
                                  for r in rows1 if r[col1.at] != "?"]
      for bin in sorted(bins.values(), key=lambda b:b.lo):
         print(show(wanted(want1,bin.ys)), show(bin), bin.ys, show(entropy(bin.ys)),sep="\t") 

  def discretize():
    "Find useful ranges."
    data1   = DATA(csv(the.train), rank=True)
    bests   = int(len(data1.rows)**.5)
    rests   = len(data1.rows) - bests
    klasses = dict(best=data1.rows[:bests], rest=(data1.rows[bests:]))
    want1   = WANT(best="best", bests=bests, rests=rests)
    print("\nbaseline", " "*22, dict(best=bests,rest=rests))
    for x in data1.cols.x:
      print("")
      for xy1 in discretize(x, klasses):
        print(show(wanted(want1,xy1.ys)),f"{show(xy1):20}",xy1.ys,sep="\t") 

  def tree():
    "Test the generation of binary decision tree."
    data1   = DATA(csv(the.train), rank=True)
    bests   = int(len(data1.rows)**.5)
    rests   = len(data1.rows) - bests
    klasses = dict(best=data1.rows[:bests], rest=(data1.rows[bests:]))
    want1   = WANT(best="best", bests=bests, rests=rests)
    showTree(tree(data1,klasses,want1))

  def _bad():
    "To test if `ezr.py -R all`  can handle failing tests,  remove underscore in this function's name."

  def some(): 
    "basic test of reservoir sampling"
    s=SOME([x for x in range(100)])
    print(s.mid(), s.div(), s)

  def someErrors():
    "how does reservoir size effect accuracy?"
    for k in [32,64,128,256,512,1024, 2048]:
      print("")
      for n in [10,100,1_000,10_000,100_000]:
        s=SOME([normal(10,2) for x in range(n)],max=k)
        print([round(x,3) for x in [100*(s.mid()-10)/10, 100*(s.div()-2)/2]],k,n)

  def file2somes():
    "Read somes from file."
    [print(x) for x in file2somes("data/stats.txt")]

  def someSame():
    def it(x): return "T" if x else "."
    print("inc","\tcd","\tboot","\tcohen","==")
    x=1
    while x<1.75:
      a1 = [random.gauss(10,3) for x in range(20)]
      a2 = [y*x for y in a1]
      s1 = SOME(a1)
      s2 = SOME(a2)   
      t1 = s1.cliffs(s2) 
      t2 = s1.bootstrap(s2) 
      t3 = s1.cohen(s2) 
      print(round(x,3),it(t1), it(t2),  it(t3), it(s1==s2), sep="\t")
      x *= 1.02

  def some2(n=5):
    report([ SOME([0.34, 0.49 ,0.51, 0.6]*n,   txt="x1"),
          SOME([0.6  ,0.7 , 0.8 , 0.89]*n,  txt="x2"),
          SOME([0.09 ,0.22, 0.28 , 0.5]*n, txt="x3"),
          SOME([0.6  ,0.7,  0.8 , 0.9]*n,   txt="x4"),
          SOME([0.1  ,0.2,  0.3 , 0.4]*n,   txt="x5")])
    
  def some3():
    report([ SOME([0.32,  0.45,  0.50,  0.5,  0.55],    "one"),
          SOME([ 0.76,  0.90,  0.95,  0.99,  0.995], "two")])

  def some4(n=20):
    report([ SOME([0.24, 0.25 ,0.26, 0.29]*n,   "x1"),
          SOME([0.35, 0.52 ,0.63, 0.8]*n,   "x2"),
          SOME([0.13 ,0.23, 0.38 , 0.48]*n, "x3"),
          ])
    
def report(somes):
  all = SOME(somes)
  last = None
  for some in sk(somes):
    if some.rank != last: print("#")
    last=some.rank
    print(all.bar(some,width=40,word="%20s", fmt="%5.2f"))
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
# - **Misc:**  SOME functions "chain"; i.e. `f1()` calls `f2()` which calls `f3()`.
#   And the sub-functions are never called from anywhere else. For such chained
#   functions, add the comment (e.g.)  `Used by f1()`.
#   Also,  if a function is about some data type, use `i` (not `self` and not `this`)
#   for first function argument.
#   And do not use `i` otherwise (e.g. not as a loop counter).

