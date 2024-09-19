#!/usr/bin/env python3 -B
# <!-- vim: set ts=2 sw=2 sts=2 et: -->
"""
## Ezr.py
&copy;  2024 Tim Menzies (timm@ieee.org). BSD-2 license

### USAGE:   

python3 ezr.py [OPTIONS]

This code explores multi-objective optimization; i.e. what
predicts for the better goal values? This code also explores
active learning; i.e. how to make predictions after looking at
the fewest number of goal values?

### OPTIONS:   

    -b --buffer int    chunk size, when streaming   = 100
    -B --branch bool   set branch method            = False  
    -d --divide int    half with mean or median     = 0
    -D --Dull   bool   if true, round to cohen's d  = False
    -L --Last   int    max number of labels         = 30  
    -c --cut    float  borderline best:rest         = 0.5  
    -C --Cohen  float  pragmatically small          = 0.35
    -e --eg     str    start up action              = mqs   
    -f --fars   int    number of times to look far  = 20   
    -h --help          show help                    = False  
    -i --iter   int    length of done minus label   = 0 
    -k --k      int    low frequency Bayes hack     = 1   
    -l --label  int    initial number of labels     = 4   
    -m --m      int    low frequency Bayes hack     = 2   
    -p --p      int    distance formula exponent    = 2   
    -s --seed   int    random number seed           = 1234567891   
    -S --Stop   int    min size of tree leaves      = 30   
    -t --train  str    training csv file. row1 has names = data/misc/auto93.csv

### Data File Format

Training data consists of csv files where "?" denotes missing values.
Row one  list the columns names, defining the roles of the columns:

- NUMeric column names start with an upper case letter.
- All other columns are SYMbolic.
- Names ending with "+" or "-" are goals to maximize/minimize
- Anything ending in "X" is a column we should ignore.

For example, here is data where the goals are `Lbs-,Acc+,Mpg+`
i.e. we want to minimize car weight and maximize acceleration
and maximize fuel consumption.

     Clndrs   Volume  HpX  Model  origin  Lbs-  Acc+  Mpg+
     -------  ------  ---  -----  ------  ----  ----  ----
      4       90      48   78     2       1985  21.4   40
      4       98      79   76     1       2255  17.7   30
      4       98      68   77     3       2045  18.6   30
      4       79      67   74     2       2000  16     30
      ...
      4      151      85   78     1       2855  17.6   20
      6      168      132  80     3       2910  11.4   30
      8      350      165  72     1       4274  12     10
      8      304      150  73     1       3672  11.5   10

Note that the top rows are
better than the bottom ones (lighter, faster cars that are
more economical).
"""
# todo: labelling via clustering.
# ## Setting-up
# ### Imports
from __future__ import annotations
from typing import Any as any
from typing import List, Dict, Type, Callable, Generator
from fileinput import FileInput as file_or_stdin
from dataclasses import dataclass, field, fields
import datetime
from math import exp,log,cos,sqrt,pi
import re,sys,ast,math,random,inspect
import traceback
from time import time
import stats
R = random.random
one = random.choice
#
# ###  Types and Classes
#
# Some misc types:
number  = float  | int   #
atom    = number | bool | str # and sometimes "?"
row     = list[atom]
rows    = list[row]
classes = dict[str,rows] # `str` is the class name

def LIST(): return field(default_factory=list)
def DICT(): return field(default_factory=dict)
#
# NUMs and SYMs are both COLumns. All COLumns count `n` (items seen),
# `at` (their column number) and `txt` (column name).
@dataclass
class COL:
  n   : int = 0
  at  : int = 0
  txt : str = ""

# SYMs tracks  symbol counts  and tracks the `mode` (the most common frequent symbol).
@dataclass
class SYM(COL):
  has  : dict = DICT()
  mode : atom=None
  most : int=0

  def clone(self:SYM): return SYM(at=self.at,txt=self.txt)
# NUMs tracks  `lo,hi` seen so far, as well the `mu` (mean) and `sd` (standard deviation),
# using Welford's algorithm.
@dataclass
class NUM(COL):
  mu : number =  0
  m2 : number =  0
  sd : number =  0
  lo : number =  1E32
  hi : number = -1E32
  goal : number = 1

  def clone(self:NUM): return NUM(at=self.at,txt=self.txt)

  # A minus sign at end of a NUM's name says "this is a column to minimize"
  # (all other goals are to be maximizes).
  def __post_init__(self:NUM) -> None:  
    if  self.txt and self.txt[-1] == "-": self.goal=0
#
# COLS are a factory that reads some `names` from the first
# row , the creates the appropriate columns.
@dataclass
class COLS:
  names: list[str]   # column names
  all  : list[COL] = LIST()  # all NUMS and SYMS
  x    : list[COL] = LIST()  # independent COLums
  y    : list[COL] = LIST()  # dependent COLumns
  klass: COL = None

  # Collect  `all` the COLs as well as the dependent/independent `x`,`y` lists.
  # Upper case names are NUMerics. Anything ending in `+` or `-` is a goal to
  # be maximized of minimized. Anything ending in `X` is ignored.
  def __post_init__(self:COLS) -> None:
    for at,txt in enumerate(self.names):
      a,z = txt[0],txt[-1]
      col = (NUM if a.isupper() else SYM)(at=at, txt=txt)
      self.all.append(col)
      if z != "X":
        (self.y if z in "!+-" else self.x).append(col)
        if z=="!": self.klass = col
        if z=="-": col.goal = 0
#
# DATAs store `rows`, which are summarized in `cols`.
@dataclass
class DATA:
  cols : COLS = None         # summaries of rows
  rows : rows = LIST() # rows

  # Another way to create a DATA is to copy the columns structure of
  # an existing DATA, then maybe load in some rows to that new DATA.
  def clone(self:DATA, rows:rows=[]) -> DATA:
    return DATA().add(self.cols.names).adds(rows)
#
# ### Decorators
# I like how JULIA and CLOS lets you define all your data types
# before anything else. Also, you can group together related methods
# from different classes. I think that really simplifies explaining the
# code. So this `of` decorator lets me
# define methods separately to class definition (and, btw,  it collects a
# documentation strings). 
def of(doc):
  def doit(fun):
    fun.__doc__ = doc
    self = inspect.getfullargspec(fun).annotations['self']
    setattr(globals()[self], fun.__name__, fun)
  return doit
#
# ## Methods
# ### Misc
#
@of("Return central tendency of a DATA.")
def mid(self:DATA) -> row: 
  return [col.mid() for col in self.cols.all]

@of("Return central tendency of NUMs.")
def mid(self:NUM) -> number: return self.mu

@of("Return central tendency of SYMs.")
def mid(self:SYM) -> number: return self.mode

@of("Return diversity of a NUM.")
def div(self:NUM) -> number: return self.sd

@of("Return diversity of a SYM.")
def div(self:SYM) -> number: return self.ent()

@of("Returns 0..1 for min..max.")
def norm(self:NUM, x) -> number:
  return x if x=="?" else  ((x - self.lo) / (self.hi - self.lo + 1E-32))

@of("Entropy = measure of disorder.")
def ent(self:SYM) -> number:
  return - sum(n/self.n * log(n/self.n,2) for n in self.has.values())

# ### Add 
@of("add COL with many values.")
def adds(self:COL,  src) -> COL:
  [self.add(row) for row in src]; return self

@of("add DATA with many values.")
def adds(self:DATA, src) -> DATA:
  [self.add(row) for row in src]; return self

@of("As a side-effect on adding one row (to `rows`), update the column summaries (in `cols`).")
def add(self:DATA,row:row) -> DATA:
  if    self.cols: self.rows += [self.cols.add(row)]
  else: self.cols = COLS(names=row) # for row q
  return self

@of("add all the `x` and `y` cols.")
def add(self:COLS, row:row) -> row:
  [col.add(row[col.at]) for cols in [self.x, self.y] for col in cols]
  return row

@of("If `x` is known, add this COL.")
def add(self:COL, x:any) -> any:
  if x != "?":
    self.n += 1
    self.add1(x)

@of("add symbol counts.")
def add1(self:SYM, x:any) -> any:
  self.has[x] = self.has.get(x,0) + 1
  if self.has[x] > self.most: self.mode, self.most = x, self.has[x]
  return x

@of("add `mu` and `sd` (and `lo` and `hi`). If `x` is a string, coerce to a number.")
def add1(self:NUM, x:any) -> number:
  self.lo  = min(x, self.lo)
  self.hi  = max(x, self.hi)
  d        = x - self.mu
  self.mu += d / self.n
  self.m2 += d * (x -  self.mu)
  self.sd  = 0 if self.n <2 else (self.m2/(self.n-1))**.5
#
# ### Guessing 
@of("Guess values at same frequency of `has`.")
def guess(self:SYM) -> any:
  r = R()
  for x,n in self.has.items():
    r -= n/self.n
    if r <= 0: return x
  return self.mode

@of("Guess values with some `mu` and `sd` (using Box-Muller).")
def guess(self:NUM) -> number:
  while True:
    x1 = 2.0 * R() - 1
    x2 = 2.0 * R() - 1
    w = x1*x1 + x2*x2
    if w < 1:
      tmp = self.mu + self.sd * x1 * sqrt((-2*log(w))/w)
      return max(self.lo, min(self.hi, tmp))

@of("Guess a row like the other rows in DATA.")
def guess(self:DATA, fun:Callable=None) -> row:
  fun = fun or (lambda col: col.guess())
  out = ["?" for _ in self.cols.all]
  for col in self.cols.x: out[col.at] = fun(col)
  return out

# @of("stochastic version of Guess. maybe too clever?")
# def exploit(self:COL, other:COL, n=20):
#   n       = (self.n + other.n + 2*the.k)
#   pr1,pr2 = (self.n + the.k) / n, (other.n + the.k) / n
#   key     = lambda x: 2*self.like(x,pr1) -  other.like(x,pr2)
#   def trio():
#     x=self.guess()
#     return key(x),self.at,x
#   return max([trio() for _ in range(n)], key=nth(0))
#
@of("Guess a value that is more like `self` than  `other`.")
def exploit(self:NUM, other:NUM):
  a = self.like(self.mid())
  b = other.like(self.mid())
  c = (self.n*a - other.n*b)/(self.n + other.n) 
  return c,self,self.mid()

@of("Guess a value that is more like `self` than  `other`.")
def exploit(self:SYM, other:SYM):
  priora = self.n/(self.n + other.n)
  priorb = other.n/(self.n + other.n)
  a = self.like(self.mid(),  priora)
  b = other.like(self.mid(), priorb)
  c = a - b 
  return c,self,self.mid(),

@of("Guess a row more like `self` than `other`.")
def exploit(self:DATA, other:DATA, top=1000,used=None):
  out = ["?" for _ in self.cols.all]
  for _,col,x in sorted([coli.exploit(colj) for coli,colj in zip(self.cols.x, other.cols.x)],
                       reverse=True,key=nth(0))[:top]:
     out[col.at] = x
     # if used non-nil, keep stats on what is used
     if used != None:
        used[col.at] = used.get(col.at,None) or col.clone()
        used[col.at].add(x)
  return out

@of("Guess a row in between the rows of `self` and `other`.")
def explore(self:DATA, other:DATA):
  out = self.guess()
  for coli,colj in zip(self.cols.x, other.cols.x): out[coli.at] = coli.explore(colj)
  return out

@of("Guess value on the border between `self` and `other`.")
def explore(self:COL, other:COL, n=20):
  n       = (self.n + other.n + 2*the.k)
  pr1,pr2 = (self.n + the.k) / n, (other.n + the.k) / n
  key     = lambda x: abs(self.like(x,pr1) - other.like(x,pr2))
  return min([self.guess() for _ in range(n)], key=key)
#
# ## Distance 
@of("Between two values (Aha's algorithm).")
def dist(self:COL, x:any, y:any) -> float:
  return 1 if x==y=="?" else self.dist1(x,y)

@of("Distance between two SYMs.")
def dist1(self:SYM, x:number, y:number) -> float: return x != y

@of("Distance between two NUMs.")
def dist1(self:NUM, x:number, y:number) -> float:
  x, y = self.norm(x), self.norm(y)
  x = x if x !="?" else (1 if y<0.5 else 0)
  y = y if y !="?" else (1 if x<0.5 else 0)
  return abs(x-y)

@of("Euclidean distance between two rows.")
def dist(self:DATA, r1:row, r2:row) -> float:
  n = sum(c.dist(r1[c.at], r2[c.at])**the.p for c in self.cols.x)
  return (n / len(self.cols.x))**(1/the.p)

@of("Sort rows randomly")
def shuffle(self:DATA) -> DATA:
  random.shuffle(self.rows)
  return self

@of("Sort rows by Chebyshev distance.")
def chebyshevs(self:DATA) -> DATA:
  self.rows = sorted(self.rows, key=lambda r: self.chebyshev(r))
  return self

@of("Compute Chebyshev distance of one row to the best `y` values.")
def chebyshev(self:DATA,row:row) -> number:
  return  max(abs(col.goal - col.norm(row[col.at])) for col in self.cols.y)

@of("Sort rows by the Euclidean distance of the goals to heaven.")
def d2hs(self:DATA) -> DATA:
  self.rows = sorted(self.rows, key=lambda r: self.d2h(r))
  return self

@of("Compute euclidean distance of one row to the best `y` values.")
def d2h(self:DATA,row:row) -> number:
  d = sum(abs(c.goal - c.norm(row[c.at]))**2 for c in self.cols.y)
  return (d/len(self.cols.y)) ** (1/the.p)
#
# ### Nearest Neighbor
@of("Sort `rows` by their distance to `row1`'s x values.")
def neighbors(self:DATA, row1:row, rows:rows=None) -> rows:
  return sorted(rows or self.rows, key=lambda row2: self.dist(row1, row2))

@of("Return predictions for `cols` (defaults to klass column).")
def predict(self:DATA, row1:row, rows:rows, cols=None, k=2):
  cols = cols or self.cols.y
  got = {col.at : [] for col in cols}
  for row2 in self.neighbors(row1, rows)[:k]:
    d =  1E-32 + self.dist(row1,row2)
    [got[col.at].append( (d, row2[col.at]) )  for col in cols]
  return {col.at : col.predict( got[col.at] ) for col in cols}
 
@of("Find weighted sum of numbers (weighted by distance).")
def predict(self:NUM, pairs:list[tuple[float,number]]) -> number:
  ws,tmp = 0,0
  for d,num in pairs:
    w    = 1/d**2
    ws  += w
    tmp += w*num
  return tmp/ws

@of("Sort symbols by votes (voting by distance).")
def predict(self:SYM, pairs:list[tuple[float,any]]) -> number:
  votes = {}
  for d,x in pairs:
    votes[x] = votes.get(x,0) + 1/d**2
  return max(votes, key=votes.get)
#
# ### Cluster
@dataclass
class CLUSTER:
  data   : DATA
  right  : row
  left   : row
  mid    : row
  cut    : number
  fun    : Callable
  lvl    : int = 0
  lefts  : CLUSTER = None
  rights : CLUSTER = None

  def __repr__(self:CLUSTER) -> str:
    return f"{'|.. ' * self.lvl}{len(self.data.rows)}"

  def leaf(self:CLUSTER, data:DATA, row:row) -> CLUSTER:
    d = data.dist(self.left,row)
    if self.lefts  and self.lefts.fun( d,self.lefts.cut):  return self.lefts.leaf(data,row)
    if self.rights and self.rights.fun(d,self.rights.cut): return self.rights.leaf(data,row)
    return self

  def nodes(self:CLUSTER):
    def leafp(x): return x.lefts==None or x.rights==None
    yield self, leafp(self)
    for node in [self.lefts,self.rights]:
      if node:
        for x,isLeaf in node.nodes(): yield x, isLeaf

@of("Return two distant rows, optionally sorted into best, then rest")
def twoFar(self:DATA, rows:rows, sortp=False, samples:int=None) -> tuple[row,row] :
  left, right =  max(((one(rows), one(rows)) for _ in range(samples or the.fars)),
                       key= lambda two: self.dist(*two))
  if sortp and self.chebyshev(right) < self.chebyshev(left): right,left = left,right
  return left, right

@of("Divide rows by distance to two faraway points")
def half(self:DATA, rows:rows, sortp=False) -> tuple[rows,rows,row,row,float]:
  if the.divide == 0:
    return self.half_mean(rows, True)
  if the.divide == 1:
    return self.half_median(rows, True)

@of("Divide rows by distance to two faraway points")
def half_mean(self:DATA, rows:rows, sortp=False) -> tuple[rows,rows,row,row,float]:
  left,right = self.twoFar(rows, sortp=sortp)
  C = self.dist(left,right)
  lefts,rights = [],[]
  project = lambda row: (self.dist(row,left)**2 + C**2 - self.dist(row,right)**2)/(2*C + 1E-30)
  for row in rows: 
    (lefts if project(row) <= C/2 else rights).append(row)
  return self.dist(left,lefts[-1]),lefts, rights, left, right

@of("Divide rows by distance to two faraway points")
def half_median(self:DATA, rows:rows, sortp=False) -> tuple[rows,rows,row,row,float]:
  mid = int(len(rows) // 2)
  left,right = self.twoFar(rows, sortp=sortp)
  C = self.dist(left,right)
  project = lambda row: (self.dist(row,left)**2 + C**2 - self.dist(row,right)**2)/(2*C + 1E-30)
  tmp = sorted(self.rows, key=project)
  return self.dist(left,tmp[mid]), tmp[:mid], tmp[mid:], left, right

@of("recursive divide rows using distance to two far points")
def cluster(self:DATA, rows:rows=None,  sortp=False, stop=None, cut=None, fun=None, lvl=0):
  stop = stop or the.Stop
  rows = rows or self.rows
  cut1, ls, rs, left, right = self.half(rows,sortp=sortp)
  it = CLUSTER(data=self.clone(rows), cut=cut, fun=fun, left=left, right=right, mid=rs[0], lvl=lvl)
  if len(ls)>stop and len(ls)<len(rows): it.lefts  = self.cluster(ls, sortp, stop, cut1, le, lvl+1)
  if len(rs)>stop and len(rs)<len(rows): it.rights = self.cluster(rs, sortp, stop, cut1, gt, lvl+1)
  return it

@of("Recursively bi-cluster `region`, recurse only down the best half.")
def branch(self:DATA, region:rows=None, stop=None, used=[], evals=1):
    region = region or self.rows
    if not stop: random.shuffle(region)
    stop = stop or the.Stop

    if len(region) > stop:
        distance, lefts, rights, left, right = self.half(region, True)
        if left not in used:
            used.append(left)
        if right not in used:
            used.append(right)

        return self.branch(lefts, stop, used, evals + 1)
    else:
        return [r for r in self.rows if r not in used], used

le = lambda x,y: x <= y
gt = lambda x,y: x >  y

@of("Diversity sampling (one per items).")
def diversity(self:DATA, rows:rows=None, stop=None):
  rows = rows or self.rows
  cluster = self.cluster(rows, stop=stop or math.floor(len(rows)**0.5))
  for node,leafp in cluster.nodes(): 
    if leafp:
        yield node.mid

#
# ## Bayes
# of("discretieze.")
# def bin(self:SYM,x): return x
#
# of("discretieze.")
# def bin(self:NUM,x): return math.floor( self.norm(x) * 20 )
#
# of("Return get bins.")
# def bins(self:COL, goal, klasses:classes):
#   tmp = {}
#   lst = sorted([(r[self.at], y) for y,rows in klasses.items() 
#                 for r in rows if r[self.t] != "?"], key=nth(0))
#   for x,y in lst:
#     b      = self.bin(x)
#     tmp[b] = tmp.get(b,None) or SYM(at=self.at)
#     tmp[b].add(y)
#   return self.bins1(tmp, goal,len(lst))
#
# def bins1(self:SYM, tmp, goal, n):
#   return max(tmp, key=lambda sym: sym.power(goal,n))
#
# def bins1(self.NUM, tmp,goal, n):
#
# klasses lst = [out[b] for b in  out.keys.sorted()]
#   for i,sym in enumerate(lst);
#     if i > 0              : sym.last = lst[i-1] 
#     if i < length(lst) -1 : sym.next = lst[i+1]
#   sorted(lst, key=lambda sym: sym.has.powerful
#   return most, out, len(lst)
#
# of("Return useful symbolic range.")
# def powerful(self:SYM, goal, klasses:classes):
#   most ,_, __ = self.bins(goal, klasses)
#   return most
#
# of("Return useful numeric range.")
# def powerful(self:NUM, goal, klasses:classes):
#   most, out, all = self.bins(goal, klasses)
#   return max(bins, max=lambda sym: sym.has.power(goal,all))
#
# of("Return useful ranges.")
# def power(self:SYM,goal,all):
#   b,r = 0,0
#   for k,n in self.has.items():
#     if k==goal: b += n/all
#     else      : r += n/all
#   return b*b/(b + r)
#
#
# def cdf(klasses:classes, x:Callable):
#    lo,hi = lst[0][0], lst[-1][0]
#    symp = not isinstance(lo,(inf,float)) 
#    for x,y  in lst
#      b =  x if symp else floor(((x-lo)/(hi-lo+1-32) *20))
#      bin[b] = bin.get(b,None) or  SYM(at=b)
#      bin[b].add(y)
#     if nump: return max(bin,key=
   


@of("How much DATA likes a `row`.")
def loglike(self:DATA, r:row, nall:int, nh:int) -> float:
  prior = (len(self.rows) + the.k) / (nall + the.k*nh)
  likes = [c.like(r[c.at], prior) for c in self.cols.x if r[c.at] != "?"]
  return sum(log(x) for x in likes + [prior] if x>0)

@of("How much a SYM likes a value `x`.")
def like(self:SYM, x:any, prior:float) -> float:
  return (self.has.get(x,0) + the.m*prior) / (self.n + the.m)

@of("How much a NUM likes a value `x`.")
def like(self:NUM, x:number, prior=None) -> float:
  v     = self.sd**2 + 1E-30
  nom   = exp(-1*(x - self.mu)**2/(2*v)) + 1E-30
  denom = (2*pi*v) **0.5
  return min(1, nom/(denom + 1E-30))
#
# ### Active Learning
@of("active learning")
def activeLearning(self:DATA, score=lambda B,R: B-R, generate=None, faster=True ):
  def ranked(rows): return self.clone(rows).chebyshevs().rows

  def todos(todo):
    if faster: # Apply our sorting heuristics to just a small buffer at start of "todo"
      # rotate back half of buffer to end of list, fill the gap with later items
       n = the.buffer//2
       return todo[:n] + todo[2*n: 3*n],  todo[3*n:] + todo[n:2*n]
    else: # Apply our sorting heuristics to all of todo.
      return todo,[]

  def guess(todo:rows, done:rows) -> rows:
    cut  = int(.5 + len(done) ** the.cut)
    best = self.clone(done[:cut])
    rest = self.clone(done[cut:])
    a,b  = todos(todo)
    the.iter = len(done) - the.label
    if generate:
      return self.neighbors(generate(best,rest), a) + b 
    else:
      key  = lambda r: score(best.loglike(r, len(done), 2), rest.loglike(r, len(done), 2))
      return  sorted(a, key=key, reverse=True) + b

  def loop(todo:rows, done:rows) -> rows:
    while len(todo) > 2 and len(done) < the.Last:
      top,*todo = guess(todo, done)
      done     += [top]
      done      = ranked(done)
    return done
  
  todo, done = self.rows[the.label:], ranked(self.rows[:the.label])

  if the.branch == True:
    todo, done = self.branch(used = [])
    #print(len(done))
    if the.Last==0: return done

  return loop(todo, done)
#
# ## Utils

# ### One-Liners

def cdf(x,mu,sd):
   def cdf1(z): return 1 - 0.5*2.718**(-0.717*z - 0.416*z*z)
   z = (x - mu) / sd
   return cdf1(z) if z >= 0 else 1 - cdf1(-z)

# non parametric mid and div
def medianSd(a: list[number]) -> tuple[number,number]:
  a = sorted(a)
  return a[int(0.5*len(a))], (a[int(0.9*len(a))] - a[int(0.1*len(a))])

# Return a function that returns the `n`-th idem.
def nth(n): return lambda a:a[n]

# Rounding off
def r2(x): return round(x,2)
def r3(x): return round(x,3)

# Pring to standard error
def dot(s="."): print(s, file=sys.stderr, flush=True, end="")

# Timing
def timing(fun) -> number:
  start = time()
  fun()
  return time() - start

# M-by-N cross val
def xval(lst:list, m:int=5, n:int=5, some:int=10**6) -> Generator[rows,rows]:
  for _ in range(m):
    random.shuffle(lst)
    for n1 in range (n):
      lo = len(lst)/n * n1
      hi = len(lst)/n * (n1+1)
      train, test = [],[]
      for i,x in enumerate(lst):
        (test if i >= lo and i < hi else train).append(x)
      train = random.choices(train, k=min(len(train),some))
      test = random.choices(test, k=min(len(test),some))
      yield train,test

# ### Strings to Things

def coerce(s:str) -> atom:
  "Coerces strings to atoms."
  try: return ast.literal_eval(s)
  except Exception:  return s

def csv(file) -> Generator[row]:
  infile = sys.stdin if file=="-" else open(file)
  with infile as src:
    for line in src:
      line = re.sub(r'([\n\t\r ]|#.*)', '', line)
      if line: yield [coerce(s.strip()) for s in line.split(",")]

# ### Settings and CLI
class SETTINGS:
  def __init__(self,s:str) -> None:
    "Make one slot for any line  `--slot ... = value`"
    self._help = s
    want = r"\n\s*-\w+\s*--(\w+).*=\s*(\S+)"
    for m in re.finditer(want,s): self.__dict__[m[1]] = coerce(m[2])
    self.sideEffects()

  def __repr__(self) -> str:
    "hide secret slots (those starting with '_'"
    return str({k:v for k,v in self.__dict__.items() if k[0] != "_"})

  def cli(self):
    "Update slots from command-line"
    d = self.__dict__
    for k,v in d.items():
      v = str(v)
      for c,arg in enumerate(sys.argv):
        after = sys.argv[c+1] if c < len(sys.argv) - 1 else ""
        if arg in ["-"+k[0], "--"+k]:
          d[k] = coerce("False" if v=="True" else ("True" if v=="False" else after))
    self.sideEffects()

  def sideEffects(self):
    "Run side-effects."
    d = self.__dict__
    random.seed(d.get("seed",1))
    if d.get("help",False):
      sys.exit(print(self._help))
#

# ## Tests
class egs: 
  def all():
   for s in dir(egs):
     if s[0] != "_" and s != "all":
        print("\n---------------------------",s,"-------------------------------")
        random.seed(the.seed)
        try:
            getattr(egs,s)()
        except Exception:
            print("FAIL!!!!!! ",s,Exception)

  def nums():
    r  = 256
    n1 = NUM().adds([R()**2 for _ in range(r)])
    n2 = NUM().adds([n1.guess() for _ in range(r)])
    assert abs(n1.mu - n2.mu) < 0.05, "nums mu?"
    assert abs(n1.sd - n2.sd) < 0.05, "nums sd?"

  def syms():
    r  = 256
    n1 = SYM().adds("aaaabbc")
    n2 = SYM().adds(n1.guess() for _ in range(r))
    assert abs(n1.mode == n2.mode), "syms mu?"
    assert abs(n1.ent() -  n2.ent()) < 0.05, "syms ent?"

  def csvs():
    d = DATA()
    n=0
    for row in csv(the.train): n += len(row)
    assert n== 3192,"csv?"

  def reads():
    d = DATA().adds(csv(the.train))
    assert d.cols.y[1].n==398,"reads?"

  def likings():
    d = DATA().adds(csv(the.train)).chebyshevs()
    random.shuffle(d.rows)
    lst = sorted( round(d.loglike(row,2000,2),2) for row in d.rows[:100])
    print(lst)

  def order():
    for i, row in enumerate( DATA().adds(csv(the.train)).chebyshevs().rows ):
      if i % 30 ==0 :print(f"{row}")

  def chebys():
    d = DATA().adds(csv(the.train))
    random.shuffle(d.rows)
    lst = d.chebyshevs().rows
    mid = len(lst)//2
    good,bad = lst[:mid], lst[mid:]
    dgood,dbad = d.clone(good), d.clone(bad)
    lgood,lbad = dgood.loglike(bad[-1], len(lst),2), dbad.loglike(bad[-1], len(lst),2)
    assert lgood < lbad, "chebyshev?"

  def guesses():
    d = DATA().adds(csv(the.train))
    random.shuffle(d.rows)
    lst = d.chebyshevs().rows
    mid = len(lst)//2
    good,bad = lst[:mid], lst[mid:]
    dgood,dbad = d.clone(good), d.clone(bad)
    print(good[0])
    print(bad[-1])
    print("exploit",dgood.exploit(dbad,top=2))
    print("exploit",dbad.exploit(dgood,top=2))

  def clones():
    d1 = DATA().adds(csv(the.train))
    d2 = d1.clone(d1.rows)
    for a,b in zip(d1.cols.y, d2.cols.y):
      for k,v1 in a.__dict__.items():
        assert v1 == b.__dict__[k],"clone?"

  def heavens():
    d = DATA().adds(csv(the.train)).d2hs()
    lst = [row for i,row in enumerate(d.rows) if i % 30 ==0]
    assert d.d2h(d.rows[0]) < d.d2h(d.rows[-1]), "d2h?"

  def distances():
    d = DATA().adds(csv(the.train))
    random.shuffle(d.rows)
    lst = sorted( round(d.dist(d.rows[0], row),2) for row in d.rows[:100])
    for x in lst: assert 0 <= x <= 1, "dists1?" 
    assert .33 <= lst[len(lst)//2] <= .66, "dists2?"

  def twoFar():
    d = DATA().adds(csv(the.train))
    for _ in range(100):
      a,b = d.twoFar(d.rows, sortp=True)
      assert d.chebyshev(a) <=  d.chebyshev(b), "twoFar?"
    for _ in range(100):
       cut,ls,rs,l,r = d.half(d.rows)
       print(len(ls),len(rs))

  def clusters():
    d = DATA().adds(csv(the.train))
    cluster = d.cluster(d.rows,sortp=True)
    for node,leafp in cluster.nodes(): 
      print(r2(d.chebyshev(node.left)) if node.left else "", node,sep="\t")

  def diversities(d=None):
    d = d or  DATA().adds(csv(the.train))
    #leafs = random.choices(leafs, k=min(50, len(leafs)))
    print(d.chebyshev(d.clone([row for row in d.diversity(stop=10)]).chebyshevs().rows[0]))
    #print(len([d.clone([row for row in d.diversity(stop=stop)]).chebyshevs().rows[0] for _ in range(20)]))

  def clusters1():
    d = DATA().adds(csv(the.train))
    mid = d.mid()
    mids  = stats.SOME(txt="mid")
    somes  = [mids]
    for k in [1,2,3,5]:
      ks   = stats.SOME(txt=f"k{k}")
      somes += [ks]
      for train,test in xval(d.rows): # 5 -by 5 cross-val
        d1 = d.clone(train)
        for want in test:
          for col in d1.cols.y:
            mids.add((mid[col.at] - want[col.at])/col.div())
          rows = d1.neighbors(want, train)[:k]
          got  = d.predict(want, rows, k=k) 
          for at,got1 in got.items():
            sd = d.cols.all[at].div()
            ks.add(  (want[at] - got1   )/sd)
    stats.report(somes)

  def clusters2():
    d = DATA().adds(csv(the.train))
    somes  = []
    mid1s  = stats.SOME(txt="mid-leaf")
    #mid0s  = stats.SOME(txt="mid-all")
    somes += [mid1s]
    for k in [1,2,3,4,5]:
      ks   = stats.SOME(txt=f"k{k}")
      somes += [ks]
      for train,test in xval(d.rows):
        all = d.clone(train)
        cluster = d.cluster(train)
        d1 = d.clone(train)
        mid0  = d1.mid()
        for want in test:
          #for col in d1.cols.y: mid0s.add((mid0[col.at] - want[col.at])/col.div())
          leaf = cluster.leaf(d, want)
          rows = leaf.data.rows
          got  = d.predict(want, rows, k=k) 
          mid1  = leaf.data.mid()
          for at,got1 in got.items():
            sd = d.cols.all[at].div()
            mid1s.add((want[at] - mid1[at])/sd)
            ks.add(  (want[at] - got1   )/sd)
    stats.report(somes)

  def clusters12():
    d = DATA().adds(csv(the.train))
    for k in [1,2,4]:
      for stop in [12,24,48]:
        for some in [10000000000]:
          for train,test in xval(d.rows,m=5,n=5,some=some):
            all = d.clone(train)
            cluster = d.cluster(train,stop=stop)
            for want in test:
              leaf = cluster.leaf(d, want)
              mid  = leaf.data.mid()
              rows = leaf.data.rows
              got  = d.predict(want, rows, k=k) 
              for at,got1 in got.items():
                sd = d.cols.all[at].div()
                print(k,some,stop,(want[at] - mid[at])/sd, (want[at] - got1)/sd,sep=",")

  def predicts(file=None):
    d = DATA().adds(csv(file or the.train)).shuffle()
    tests, train = d.rows[:10], d.rows[10:]
    for test in tests:
      for at, got in d.predict(test, train,  cols=d.cols.y, k=5).items():
        want = test[at]
        print(at, r3(abs(got - want)/d.cols.all[at].div()))

  def _MQS():
    for i,arg in enumerate(sys.argv):
      if arg[-4:] == ".csv":
        the.train=arg
        random.seed(the.seed)
        try:
            egs._mqs()
        except Exception:
            traceback.print_stack()

  def _mqs():
    print(the.train,  flush=True, file=sys.stderr)
    print("\n"+the.train)
    repeats  = 20
    d        = DATA().adds(csv(the.train))
    b4       = sorted([d.chebyshev(row) for row in d.rows])
    asIs,div = medianSd(b4)
    dull = div*the.Cohen
    rnd      = lambda z: ((int(z/dull) * dull) if the.Dull else z)
    least    = sorted([rnd(x) for x in b4])[0]

    print(f"asIs\t: {asIs:.3f}")
    print(f"div\t: {div:.3f}")
    print(f"dull\t: {dull:.3f}")
    print(f"least\t: {least:.3f}")
    print(f"rows\t: {len(d.rows)}")
    print(f"xcols\t: {len(d.cols.x)}")
    print(f"ycols\t: {len(d.cols.y)}\n")

    somes = [stats.SOME(b4,f"asIs,{len(d.rows)}")]

    for n in [15,20,25,30,50,100]:
      the.Last = n
      rand     = []
      for _ in range(repeats):
         some  = d.shuffle().rows[:n]
         d1    = d.clone().adds(some).chebyshevs()
         rand += [rnd(d.chebyshev(d1.rows[0]))]

      start = time()
      pool = [rnd(d.chebyshev(d.shuffle().activeLearning()[0]))
              for _ in range(repeats)]
      print(f"pool.{n}: {(time() - start) /repeats:.2f} secs")

      generate1 =lambda best,rest: best.exploit(rest,1000)
      start = time()
      mqs1000 = [rnd(d.chebyshev(d.shuffle().activeLearning(generate=generate1)[0]))
                 for _ in range(repeats)]
      print(f"mqs1K.{n}: {(time() - start)/repeats:.2f} secs")

      used={}
      generate2 =lambda best,rest: best.exploit(rest,top=4,used=used)
      start = time()
      mqs4 = []
      for _ in range(20):
          tmp = d.shuffle().activeLearning(generate=generate2)
          mqs4 += [rnd(d.chebyshev(tmp[0]))]
      for col in sorted(used.values(), key=lambda col: -col.n):
         print(f"\tfeature,{col.n},\t{col.mid()},\t{col.div():.3f},\t{col.txt}")

      print(f"mqs4.{n}: {(time() - start)/repeats:.2f} secs")

      somes +=   [stats.SOME(rand,    f"random,{n}"),
                  stats.SOME(pool,    f"pool,{n}"),
                  stats.SOME(mqs4,    f"mqs4,{n}"),
                  stats.SOME(mqs1000, f"mqs1000,{n}")]

    stats.report(somes, 0.01)

  def policies():
    def normalized_exp(k, n, shift):
        exp_values = [math.exp(0.25 * j) for j in range(n)]
        min_exp, max_exp = min(exp_values), max(exp_values)
        return (math.exp(0.25 * k) - min_exp) / (max_exp - min_exp) + shift
    
    def exploit(B, R):
        return B
    
    def explore(B, R):
        return (B + R) / (abs(B - R) + 10**-30)
    
    scoring_policies = [('exploit', lambda B, R,: exploit(B, R)),
                        ('explore', lambda B, R: explore(B, R)),
                        ('b2', lambda B, R: (B**2) / (R + 10**-30)),
                        ('Random', lambda B, R: random.random()),
                        ('SimAnneal', lambda B, R: ((exp(B) + 1) ** normalized_exp(the.iter, the.Last, 1) + (exp(R) + 1)) / (abs(exp(B) - exp(R)) + 10**-30)),
                        ('ExpProgressive', lambda B, R: normalized_exp(the.iter, the.Last, 0) * exploit(B,R) + (1 - normalized_exp(the.iter, the.Last, 0)) * explore(B,R))]
    
    print(the.train,  flush=True, file=sys.stderr)
    print("\n"+the.train)
    repeats  = 20
    d        = DATA().adds(csv(the.train))
    b4       = [d.chebyshev(row) for row in d.rows]
    asIs,div = medianSd(b4)
    rnd      = lambda z: z 

    print(f"asIs\t: {asIs:.3f}")
    print(f"div\t: {div:.3f}")
    print(f"rows\t: {len(d.rows)}")
    print(f"xcols\t: {len(d.cols.x)}")
    print(f"ycols\t: {len(d.cols.y)}\n")

    somes = [stats.SOME(b4,f"asIs,{len(d.rows)}")]

    for what,how in scoring_policies:
      for the.Last in [20, 30, 40]:
        start = time()
        result = [rnd(d.chebyshev(d.shuffle().activeLearning(score=how)[0]))
                for _ in range(repeats)]
        print(f"{what}.{the.Last}: {(time() - start) /repeats:.2f} secs")
        somes +=   [stats.SOME(result,    f"{what} ,{the.Last}")]

    stats.report(somes, 0.01)

  def eg():
    def normalized_exp(k, n, shift):
        exp_values = [math.exp(0.25 * j) for j in range(n)]
        min_exp, max_exp = min(exp_values), max(exp_values)
        return (math.exp(0.25 * k) - min_exp) / (max_exp - min_exp) + shift
    
    def exploit(B, R):
        return B
    
    def explore(B, R):
        return (B + R) / (abs(B - R) + 10**-30)
    
    scoring_policies = [('exploit', lambda B, R,: exploit(B, R)),
                        ('explore', lambda B, R: explore(B, R)),
                        ('expoit2', lambda B, R: (B**2) / (R + 10**-30)),
                        ('Random', lambda B, R: random.random()),
                        ('ExpProgressive', lambda B, R: normalized_exp(the.iter, the.Last, 0) * exploit(B,R) + (1 - normalized_exp(the.iter, the.Last, 0)) * explore(B,R))]
    
    print(the.train,  flush=True, file=sys.stderr)
    print("\n"+the.train)
    repeats  = 20
    d        = DATA().adds(csv(the.train))
    b4       = [d.chebyshev(row) for row in d.rows]
    asIs,div = medianSd(b4)
    rnd      = lambda z: z 

    print(f"asIs\t: {asIs:.3f}")
    print(f"div\t: {div:.3f}")
    print(f"rows\t: {len(d.rows)}")
    print(f"xcols\t: {len(d.cols.x)}")
    print(f"ycols\t: {len(d.cols.y)}\n")

    somes = [stats.SOME(b4,f"asIs,{len(d.rows)}")]

    for what,how in scoring_policies:
      for the.Last in [20, 30, 40]:
        start = time()
        result = [rnd(d.chebyshev(d.shuffle().activeLearning(score=how)[0]))
                for _ in range(repeats)]
        print(f"{what}.{the.Last}: {(time() - start) /repeats:.2f} secs")
        somes +=   [stats.SOME(result,    f"{what} ,{the.Last}")]

    stats.report(somes, 0.01)

  def branch():
    scoring_policies = [('exploit', lambda B, R,: B - R),
                        ('explore', lambda B, R :  (exp(B) + exp(R))/ (1E-30 + abs(exp(B) - exp(R))))]
    
    print(the.train,  flush=True, file=sys.stderr)
    print("\n"+the.train)
    repeats  = 20
    d        = DATA().adds(csv(the.train))
    b4       = [d.chebyshev(row) for row in d.rows]
    asIs,div = medianSd(b4)
    rnd      = lambda z: z 

    print(f"asIs\t: {asIs:.3f}")
    print(f"div\t: {div:.3f}")
    print(f"rows\t: {len(d.rows)}")
    print(f"xcols\t: {len(d.cols.x)}")
    print(f"ycols\t: {len(d.cols.y)}\n")

    somes = [stats.SOME(b4,f"asIs,{len(d.rows)}")]

    for what,how in scoring_policies:
      for the.Last in [0,20, 30, 40]:
        for the.branch in [False, True]:
          start = time()
          result = [] 
          runs = 0
          for _ in range(repeats):
             tmp=d.shuffle().activeLearning(score=how)
             runs += len(tmp)
             result += [rnd(d.chebyshev(tmp[0]))]

          pre=f"{what}/b={the.branch}" if the.Last >0 else "rrp"
          tag = f"{pre},{int(runs/repeats)}"
          print(tag, f": {(time() - start) /repeats:.2f} secs")
          somes +=   [stats.SOME(result,    tag)]

    stats.report(somes, 0.01)

  def mean_vs_median():
    scoring_policies = [('exploit', lambda B, R,: B),
                        ('Random', lambda B, R: random.random())]
    
    print(the.train,  flush=True, file=sys.stderr)
    print("\n"+the.train)
    repeats  = 20
    d        = DATA().adds(csv(the.train))
    b4       = [d.chebyshev(row) for row in d.rows]
    asIs,div = medianSd(b4)
    rnd      = lambda z: z 

    print(f"asIs\t: {asIs:.3f}")
    print(f"div\t: {div:.3f}")
    print(f"rows\t: {len(d.rows)}")
    print(f"xcols\t: {len(d.cols.x)}")
    print(f"ycols\t: {len(d.cols.y)}\n")

    somes = [stats.SOME(b4,f"asIs,{len(d.rows)}")]

    the.branch == True

    for what,how in scoring_policies:
      for the.divide in [0, 1]:
        divide = 'mean' if the.divide == 0 else 'median'
        for the.Last in [20, 30, 40]:
          start = time()
          result = [rnd(d.chebyshev(d.shuffle().activeLearning(score=how)[0]))
                  for _ in range(repeats)]
          print(f"{what}/branch={divide}.{the.Last}: {(time() - start) /repeats:.2f} secs")
          somes +=   [stats.SOME(result,    f"{what}/branch={divide} ,{the.Last}")]

    stats.report(somes, 0.01)

# #--------- --------- --------- --------- --------- --------- --------- --------- --------
# # ## Gaussian Process UCB (Sklearn)
#
# import numpy as np
# from sklearn.preprocessing import StandardScaler, OneHotEncoder
# from sklearn.compose import ColumnTransformer
# from sklearn.pipeline import Pipeline
# from sklearn.gaussian_process import GaussianProcessRegressor
# from sklearn.gaussian_process.kernels import RBF, ConstantKernel as C
#
# import warnings
# from sklearn.exceptions import ConvergenceWarning
# warnings.filterwarnings("ignore", category=ConvergenceWarning)
# warnings.filterwarnings("ignore", message="Predicted variances smaller than 0. Setting those variances to 0.")
#
# def UCB_GPM(d, todo, done):
#     kernel = C(1.0, (1e-8, 1e8)) * RBF(1.0, (1e-8, 1e8))
#     gp = GaussianProcessRegressor(kernel=kernel, n_restarts_optimizer=10)
#
#     num_indexes = [col.at for col in d.cols.x if type(col) == NUM]
#     sym_indexes = [col.at for col in d.cols.x if type(col) == SYM]
#
#     num_transformer = StandardScaler()
#     cat_transformer = OneHotEncoder(handle_unknown='ignore', sparse_output=False)
#
#     preprocessor = ColumnTransformer(
#         transformers=[
#             ('num', num_transformer, num_indexes),
#             ('cat', cat_transformer, sym_indexes)])
#
#     pipeline = Pipeline(steps=[('preprocessor', preprocessor)])
#
#     if sym_indexes:
#         cat_data = np.array([[str(row[idx]) for idx in sym_indexes] for row in done], dtype=object)
#         cat_transformer.fit(cat_data)
#     
#     def grid_search_optimizer(obj_func, initial_theta, bounds):
#         best_theta = np.copy(initial_theta).flatten()
#         best_value, _ = obj_func(best_theta)
#         
#         for i in range(10):
#             candidate_theta = initial_theta + np.random.uniform(-0.1, 0.1, size=initial_theta.shape)
#             candidate_theta = np.clip(candidate_theta, bounds[:, 0], bounds[:, 1])
#             candidate_theta = candidate_theta.flatten()
#             
#             candidate_value, _ = obj_func(candidate_theta)
#             
#             if candidate_value < best_value:
#                 best_theta = np.copy(candidate_theta)
#                 best_value = candidate_value
#         
#         return best_theta, best_value
#     
#     gp.optimizer = grid_search_optimizer
#
#     def update_gp_model(done_set):
#         X_done = np.array([x for x in done_set], dtype=object)
#         y_done = np.array([-d.chebyshev(x) for x in done_set])
#         X_done_transformed = pipeline.fit_transform(X_done)
#         gp.fit(X_done_transformed, y_done)
#     
#     def ucb(x, kappa=2.576):
#         x = np.array(x).reshape(1, -1).astype(object)
#         x_transformed = pipeline.transform(x)
#         mean, std = gp.predict(x_transformed, return_std=True)
#         return mean + kappa * std
#     
#     while todo and len(done) < the.Last:
#         update_gp_model(done)
#         random.shuffle(todo)
#         todo_subset = todo[:the.buffer]
#
#         ucb_values = [ucb(row) for row in todo_subset]
#         best_idx = np.argmax(ucb_values)
#         best_candidate = todo.pop(best_idx)
#          
#         done.append(best_candidate)
#     
#     return done
#
#
# ## Main
the = SETTINGS(__doc__)
if __name__ == "__main__" and len(sys.argv)> 1:
  the.cli()
  random.seed(the.seed)
  getattr(egs, the.eg, lambda : print(f"ezr: [{the.eg}] unknown."))()
