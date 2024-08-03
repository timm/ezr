#!/usr/bin/env python3 -B
# <!-- vim: set ts=2 sw=2 sts=2 et: -->
# % ezr.py:<br>multi-objective active learning
# % by timm, <timm@ieee.org>
# % &copy; 2024, BSD-2 license {[se/tut/license](se/tut/license.md)}
# --------
from __future__ import annotations
from typing import Any as any
from typing import List, Dict, Type, Callable, Generator
from fileinput import FileInput as file_or_stdin
from dataclasses import dataclass, field, fields
import datetime
from math import exp,log,cos,sqrt,pi
import re,sys,ast,random,inspect
from time import time
import stats
R = random.random
one = random.choice
#
# ##  Types
# All programs have magic control options, which we keep the `the` variables.
@dataclass
class CONFIG:
  buffer: int = 100 # chunk size, when streaming
  Last  : int = 30  # max number of labels
  cut   : float = 0.5 # borderline best:rest
  eg    : str = "mqs"  #start up action
  fars  : int = 20  # number of times to look for far pairs
  k     : int = 1   # low frequency Bayes hack
  label : int = 4   # initial number of labels
  m     : int = 2   # low frequency Bayes hack
  p     : int = 2   # distance formula exponent
  seed  : int = 1234567891 # random number seed
  Stop  : int = 30   # min size of tree leaves
  train : str = "data/misc/auto93.csv" # csv file. row1 has column names

the = CONFIG()
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
#
# SYMs tracks  symbol counts  and tracks the `mode` (the most common frequent symbol).
@dataclass
class SYM(COL):
  has  : dict = DICT()
  mode : atom=None
  most : int=0
#
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

  # A minus sign at end of a NUM's name says "this is a column to minimize"
  # (all other goals are to be maximizes).
  def __post_init__(self:COLS) -> None:  
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
# ## Decorators
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
# ## MiscMethods
#
@of("Returns 0..1 for min..max.")
def norm(self:NUM, x) -> number:
  return x if x=="?" else  ((x - self.lo) / (self.hi - self.lo + 1E-32))

@of("Entropy = measure of disorder.")
def ent(self:SYM) -> number:
  return - sum(n/self.n * log(n/self.n,2) for n in self.has.values())

# ## add 
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
  if isinstance(x,str): x = coerce(x)
  self.lo  = min(x, self.lo)
  self.hi  = max(x, self.hi)
  d        = x - self.mu
  self.mu += d / self.n
  self.m2 += d * (x -  self.mu)
  self.sd  = 0 if self.n <2 else (self.m2/(self.n-1))**.5
#
# ## Guessing 
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

@of("Guess a value that is more like `self` than  `other`.")
def exploit(self:COL, other:COL, n=20):
  n       = (self.n + other.n + 2*the.k)
  pr1,pr2 = (self.n + the.k) / n, (other.n + the.k) / n
  key     = lambda x: 2*self.like(x,pr1) -  other.like(x,pr2)
  def trio():
    x=self.guess()
    return key(x),self.at,x
  return max([trio() for _ in range(n)], key=nth(0))

@of("Guess a row more like `self` than `other`.")
def exploit(self:DATA, other:DATA, top=1000,used=None):
  out = ["?" for _ in self.cols.all]
  for _,at,x in sorted([coli.exploit(colj) for coli,colj in zip(self.cols.x, other.cols.x)],
                       reverse=True,key=nth(0))[:top]:
     out[at] = x
     if used != None:
        used[at] = used.get(at,None) or NUM(at=at)
        used[at].add(x)
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

@of("Sort rows by the Euclidean distance of the goals to heaven.")
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
# ## Nearest Neighbor
@of("Sort `rows` by their distance to `row1`'s x values.")
def neighbors(self:DATA, row1:row, rows:rows=None) -> rows:
  return sorted(rows or self.rows, key=lambda row2: self.dist(row1, row2))

@of("Return predictions for `cols` (defaults to klass column).")
def predict(self:DATA, row1:row, rows:rows, cols=None, k=2):
  cols = cols or [self.cols.klass]
  got = {col : [] for col in cols}
  for row2 in self.neighbors(row1, rows)[:k]:
    d = 1E-32 + self.dist(row1,row2)
    [lst.append((d, row2[col.at])) for col,lst in got.items()]
  return {col.at : col.predict(lst) for col,lst in got.items()}
 
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
# ## Cluster
@dataclass
class CLUSTER:
  data :DATA
  right : row
  left  : row
  cut  : number
  fun  : Callable
  lvl : int = 0
  lefts : CLUSTER = None
  rights : CLUSTER = None

  def __repr__(self:CLUSTER) -> str:
    return f"{'|.. ' * self.lvl}{len(self.data.rows)}"

  def leaf(self:CLUSTER, data:DATA, row:row) -> CLUSTER:
    d = data.dist(self.left,row)
    if self.lefts  and self.lefts.fun( d,self.lefts.cut):  return self.lefts.leaf(data,row)
    if self.rights and self.rights.fun(d,self.rights.cut): return self.rights.leaf(data,row)
    return self

  def nodes(self:CLUSTER):
    def leafp(x): return x.lefts==None and x.rights==None
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
  left,right = self.twoFar(rows, sortp=sortp)
  cut = self.dist(left,right)/2
  lefts,rights = [],[]
  for row in rows: 
    (lefts if self.dist(row,left) <= cut else rights).append(row)
  return self.dist(left,lefts[-1]),lefts, rights, left, right

@of("recursive divide rows using distance to two far points")
def cluster(self:DATA, rows:rows=None,  sortp=False, stop=None, cut=None, fun=None,lvl=0):
  stop = stop or the.Stop
  rows = rows or self.rows
  cut1, ls, rs, left, right = self.half(rows,sortp=sortp)
  it = CLUSTER(data=self.clone(rows), cut=cut, fun=fun, left=left, right=right, lvl=lvl)
  if len(ls)>stop and len(ls)<len(rows): it.lefts  = self.cluster(ls, sortp, stop, cut1, le,lvl+1)
  if len(rs)>stop and len(rs)<len(rows): it.rights = self.cluster(rs, sortp, stop, cut1, gt,lvl+1)
  return it

le = lambda x,y: x <= y
gt = lambda x,y: x >  y

#
# ## Bayes
@of("How much DATA likes a `row`.")
def loglike(self:DATA, r:row, nall:int, nh:int) -> float:
  prior = (len(self.rows) + the.k) / (nall + the.k*nh)
  likes = [c.like(r[c.at], prior) for c in self.cols.x if r[c.at] != "?"]
  return sum(log(x) for x in likes + [prior] if x>0)

@of("How much a SYM likes a value `x`.")
def like(self:SYM, x:any, prior:float) -> float:
  return (self.has.get(x,0) + the.m*prior) / (self.n + the.m)

@of("How much a NUM likes a value `x`.")
def like(self:NUM, x:number, _) -> float:
  v     = self.sd**2 + 1E-30
  nom   = exp(-1*(x - self.mu)**2/(2*v)) + 1E-30
  denom = (2*pi*v) **0.5
  return min(1, nom/(denom + 1E-30))

@of("active learning")
def activeLearning(self:DATA, score=lambda B,R: B-R, generate=None, faster=True ):
  def ranked(rows): return self.clone(rows).chebyshevs().rows

  def todos(todo):
    if faster: # replace back half of `a` with items from `b`
       a,b = todo[:the.buffer//2], todo[the.buffer:]
       return a + b[:len(a)], b[len(a):]
    else:
      return todo,[]

  def guess(todo:rows, done:rows) -> rows:
    cut  = int(.5 + len(done) ** the.cut)
    best = self.clone(done[:cut])
    rest = self.clone(done[cut:])
    a,b  = todos(todo)
    if generate:
      return self.neighbors(generate(best,rest), a) + b # todo[:some]) + todo[some:] 
    else:
      key  = lambda r: score(best.loglike(r, len(done), 2), rest.loglike(r, len(done), 2))
      return  sorted(a, key=key, reverse=True) + b

  def loop(todo:rows, done:rows) -> rows:
    for k in range(the.Last - the.label):
      if len(todo) < 3 : break
      top,*todo = guess(todo, done)
      done     += [top]
      done      = ranked(done)
    return done

  return loop(self.rows[the.label:], ranked(self.rows[:the.label]))
#
# ## Utils
def dot(s="."): print(s, file=sys.stderr, flush=True, end="")

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
      yield train,test

def timing(fun) -> number:
  start = time()
  fun()
  return time() - start

def nth(n): return lambda a:a[n]

def coerce(s:str) -> atom:
  "Coerces strings to atoms."
  try: return ast.literal_eval(s)
  except Exception:  return s

def r2(x): return round(x,2)
def r3(x): return round(x,3)

def csv(file) -> Generator[row]:
  with file_or_stdin(None if file=="-" else file) as src:
    for line in src:
      line = re.sub(r'([\n\t\r ]|#.*)', '', line)
      if line: yield [coerce(s.strip()) for s in line.split(",")]

def cli(d:dict):
  "For dictionary key `k`, if command line has `-k X`, then `d[k]=coerce(X)`."
  for k,v in d.items():
    v = str(v)
    for c,arg in enumerate(sys.argv):
      after = sys.argv[c+1] if c < len(sys.argv) - 1 else ""
      if arg in ["-"+k[0], "--"+k]:
        d[k] = coerce("False" if v=="True" else ("True" if v=="False" else after))
#
# ## Examples
class egs: 
  def all():
   for s in dir(egs):
     if s[0] != "_" and s != "all":
        print(s)
        random.seed(the.seed)
        getattr(egs,s)()

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

  def predict(file=None):
    d = DATA().adds(csv(file or the.train))
    for train,test in xval(d.rows):
      trained = d.clone(train)
      cluster = trained.cluster()
      for row in test:
        trained.predict(row, cluster.leaf(row,d).data.rows)

  def mqs():
    print("\n"+the.train)
    repeats=20
    d = DATA().adds(csv(the.train))
    b4 = [d.chebyshev(row) for row in d.rows]
    print(f"rows\t: {len(d.rows)}")
    print(f"xcols\t: {len(d.cols.x)}")
    print(f"ycols\t: {len(d.cols.y)}")

    start = time()
    pool = [d.chebyshev(d.shuffle().activeLearning()[0]) for _ in range(repeats)]
    print(f"pool\t: {(time() - start) /repeats:.2f} secs")

    generate1 =lambda best,rest: best.exploit(rest,1000)
    start = time()
    mqs1000 = [d.chebyshev(d.shuffle().activeLearning(generate=generate1)[0]) for _ in range(repeats)]
    print(f"mqs1K\t: {(time() - start)/repeats:.2f} secs")

    used={}
    generate2 =lambda best,rest: best.exploit(rest,top=4,used=used)
    start = time()
    mqs4 = [d.chebyshev(d.shuffle().activeLearning(generate=generate2)[0]) for _ in range(20)]
    print(f"mqs4\t: {(time() - start)/repeats:.2f} secs")

    stats.report([ stats.SOME(b4,"baseline"),
                  stats.SOME(pool,"pool"),
                  stats.SOME(mqs4,"mqs4"),
                  stats.SOME(mqs1000,"mqs1000")])
#
# ## Start
if __name__ == "__main__" and len(sys.argv)> 1:
  cli(the.__dict__)
  random.seed(the.seed)
  getattr(egs, the.eg, lambda : print(f"ezr: [{the.eg}] unknown."))()
