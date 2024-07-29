#!/usr/bin/env python3 -B
# <!-- vim: set ts=2 sw=2 sts=2 et: -->
# <img src="mqs.png" align=left width=200>
# &copy; 2024 Tim Menzies<br>BSD-2 license (share and enjoy)   
from __future__ import annotations
from typing import Any as any
from typing import Callable
from fileinput import FileInput as file_or_stdin
from dataclasses import dataclass, field, fields
import datetime
from typing import Any, List, Dict, Type
from math import log,cos,sqrt,pi
import re,sys,random,inspect
R  = random.random 

# ## Types
# Linus Torvalds:
# "I’m a huge proponent of designing your code around the data, rather than the other way around....
# Bad programmers worry about the code. Good programmers worry about data structures and their relationships."

# All programs have magic control options, which we keep the `the` variables.
@dataclass
class CONFIG:
  k:int  = 1
  label:int = 4
  Last :int = 30
  m :int = 2
  p :int = 2
  seed : int = 1234567891
  train:str = "../data/misc/auto93.csv"

the = CONFIG()

# Some misc types..
def LIST(): return field(default_factory=list)
def DICT(): return field(default_factory=dict)

number  = float  | int   #
atom    = number | bool | str # and sometimes "?"
row     = list[atom]
rows    = list[row]
classes = dict[str,rows] # `str` is the class name

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
  has  : Dict = DICT()
  mode : atom=None
  most : int=0 

# NUMs tracks  `lo,hi` seen so far, as well the `mu` (mean) and `sd` (standard deviation),
# using Welford's algorithm.
@dataclass
class NUM(COL):
  mu : number =  0
  m2 : number =  0
  sd : number =  0
  lo : number =  1E21
  hi : number = -1E32
  goal : number = 1

  # A minus sign at end of a NUM's name says "this is a column to minimize"
  # (all other goals are to be maximizes).
  def __post_init__(self:COLS) -> None:  
    if  self.txt and self.txt[-1] == "-": self.goal=0

# 
@dataclass
class COLS:
  names: List   # column names
  all  : List = LIST()  # all NUMS and SYMS
  x    : List = LIST()  # independent COLums
  y    : List = LIST()  # depedent COLumns

  # Collect  `all` the COLs as well as the dependent/indepedent `x`,`y` lists.
  def __post_init__(self:COLS) -> None:
    for at,txt in enumerate(self.names):
      a,z = txt[0],txt[-1]
      col = (NUM if a.isupper() else SYM)(at=at,txt=txt)
      self.all.append(col)
      if z != "X":
        (self.y if z in "+-" else self.x).append(col)
        if z=="-": col.goal = 0

@dataclass  
class DATA:
  cols : COLS = None         # summaries of rows
  rows : rows = LIST() # rows

  def clone(self:DATA, rows:rows=[]) -> DATA:
    return DATA().inc(self.cols.names).incs(rows)

# ## Decorators

# Define methods separately to class definition.
def of(doc):
  def doit(fun):
    fun.__doc__ = doc
    self = inspect.getfullargspec(fun).annotations['self']
    setattr(globals()[self], fun.__name__, fun)
  return doit

# ## misc methods

@of("Returns 0..1 for min..max.")
def norm(self:NUM, x) -> number:
  return x=="?" and x or (x - self.lo) / (self.hi - self.lo + 1E-32)

@of("Entropy = measure of disorder.")
def ent(self:SYM) -> number:
  return - sum(n/self.n * log(n/self.n,2) for n in self.has.values())

# ## Inc (incremental update)

@of("Update DATA with many values.")
def incs(self:DATA, src) -> DATA:
  [self.inc(row) for row in src]; return self

@of("Update COL with many values.")
def incs(self:COL,  src) -> COL:
  [self.inc(row) for row in src]; return self

@of("Cache one more row, summarizes in `cols`.")
def inc(self:DATA,row:row) -> DATA:
  if    self.cols: self.rows += [self.cols.inc(row)]
  else: self.cols = COLS(names=row) # for row q
  return self

@of("Update all the `x` and `y` cols. If needed, coerce strings to (e.g.) NUMs")
def inc(self:COLS, row:row) -> row:
  for cols in [self.x, self.y]:
    for col in cols:
        row[col.at] = col.inc(row[col.at])
  return row

@of("If `x` is known, update this COL.")
def inc(self:COL, x:any) -> any:
  if x != "?":
     self.n += 1
     x = self.inc1(x)
  return x

@of("Update symbol counts.")
def inc1(self:SYM, x:any) -> any:
  self.has[x] = self.has.get(x,0) + 1
  if self.has[x] > self.most: self.mode, self.most = x, self.has[x]
  return x

@of("Update `mu` and `sd` (and `lo` and `hi`). If `x` is a string, coerce to a number.")
def inc1(self:NUM, x:any) -> number:
  if isinstance(x,str): x = _coerce(x)
  self.lo  = min(x, self.lo)
  self.hi  = max(x, self.hi)
  d        = x - self.mu
  self.mu += d / self.n
  self.m2 += d * (x -  self.mu)
  self.sd  = 0 if self.n <2 else (self.m2/(self.n-1))**.5
  return x

def _coerce(x:str) -> number:
  try: return float(x)
  except ValueError: return int(x)

# ## Guessing values

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
      return self.mu + self.sd * x1 * sqrt((-2*log(w))/w)

@of("Guess a value like `self`, most unlike `other`.")
def exploit(self:COL, other:COL, n=20):
  n       = (self.n + other.n + 2*the.k)
  pr1,pr2 = (self.n + the.k) / n, (other.n + the.k) / n
  key     = lambda x: self.like(x,pr1) - other.like(x,pr2)
  return max([self.guess() for _ in range(n)], key=key)

@of("Guess value on the border between `self` and `other`.")
def explore(self:COL, other:COL, n=20):
  n       = (self.n + other.n + 2*the.k)
  pr1,pr2 = (self.n + the.k) / n, (other.n + the.k) / n
  key     = lambda x: abs(self.like(x,pr1) - other.like(x,pr2))
  return min([self.guess() for _ in range(n)], key=key)

@of("Guess a row like the other rows in DATA.")
def guess(self:DATA, fun:Callable=None) -> row:
  fun = fun or (lambda col: col.guess())
  out = ["?" for _ in self.cols.all]
  for col in self.cols.x: out[col.at] = fun(col)
  return out

@of("Guess a row more like `self` than `other`.")
def exploit(self:DATA, other:DATA):
  out=self.guess()
  for coli,colj in zip(iself.cols.x, other.cols.x): out[coli.at] = coli.exploit(colj)
  return out

@of("Guess a row in between the rows of `self` and `other`.")
def explore(self:DATA, other:DATA):
  out = self.guess()
  for coli,colj in zip(self.cols.x, other.cols.x): out[coli.at] = coli.explore(colj)
  return out

# ## Distance calculations

@of("Sort rows by their distance to heaven.")
def d2hs(self:DATA) -> DATA:
  self.rows = sorted(self.rows, key=lambda r: self.d2h(r))
  return self

@of("Distance of one row to the best `y` values.")
def d2h(self:DATA,row:row) -> number:
  d = sum(abs(c.goal - c.norm(row[c.at]))**2 for c in self.cols.y)
  return (d/len(self.cols.y)) ** (1/the.p)

@of("Euclidean distance between two rows.")
def dist(self:DATA, r1:row, r2:row) -> float:
  n = sum(c.dist(r1[c.at], r2[c.at])**the.p for c in self.cols.x)
  return (n / len(self.cols.x))**(1/the.p)

@of("Sort `rows` by their distance to `row1`'s x values.")
def neighbors(self:DATA, row1:row, rows:rows=None) -> rows:
  return sorted(rows or self.rows, key=lambda row2: self.dist(row1, row2))

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

# ## Bayes

@of("How much DATA likes a `row`.")
def like(self:DATA, r:row, nall:int, nh:int) -> float:
  prior = (len(self.rows) + the.k) / (nall + the.k*nh)
  likes = [c.like(r[c.at], prior) for c in self.cols.x if r[c.at] != "?"]
  return sum(log(x) for x in likes + [prior] if x>0)

@of("How much a SYM likes a value `x`.")
def like(self:SYM, x:any, prior:float) -> float:
  return (self.has.get(x,0) + the.m*prior) / (self.n + the.m)

@of("How much a NUM likes a value `x`.")
def like(self:NUM, x:number) -> float:
  v     = self.sd**2 + 1E-30
  nom   = math.exp(-1*(x - self.mu)**2/(2*v)) + 1E-30
  denom = (2*math.pi*v) **0.5
  return min(1, nom/(denom + 1E-30))

def smo(self:data, score=lambda B,R: B-R, ):
  "Sequential model optimization."
  def _ranked(rows):
   return self.clone(rows).d2hs().rows

  def _guess(todo:rows, done:rows) -> rows:
    cut  = int(.5 + len(done) ** the.N)
    best = self.clone(done[:cut])
    rest = self.clone(done[cut:])
    key  = lambda got : - self.dist(got, best.exploit(rest))
    random.shuffle(todo)
    return sorted(todo[:the.any], key=key) + todo[the.any:]

  def _smo1(todo:rows, done:rows) -> rows:
    for k in range(the.Last - the.label):
      if len(todo) < 3: break
      top,*todo = _guess(todo, done)
      done += [top]
      done = _ranked(done)
    return done

  random.shuffle(i.rows) # remove any  bias from older runs
  return _smo1(i.rows[the.label:], _ranked(data.rows[:the.label]))

# ## Utils

def csv(file) -> row:
  with file_or_stdin(None if file=="-" else file) as src:
    for line in src:
      line = re.sub(r'([\n\t\r ]|#.*)', '', line)
      if line: yield [s.strip() for s in line.split(",")]

# ## Examples

class egs: # sassdddsf
  def all():
   for s in dir(egs):
     if s[0] != "_" and s != "all":
        print(s)
        random.seed(the.seed)
        getattr(egs,s)()

  def nums():
    r  = 256
    n1 = NUM().incs([R()**2 for _ in range(r)])
    n2 = NUM().incs([n1.guess() for _ in range(r)])
    assert abs(n1.mu - n2.mu) < 0.05, "nums mu?"
    assert abs(n1.sd - n2.sd) < 0.05, "nums sd?"

  def syms():
    r  = 256
    n1 = SYM().incs("aaaabbc")
    n2 = SYM().incs(n1.guess() for _ in range(r))
    assert abs(n1.mode == n2.mode), "syms mu?"
    assert abs(n1.ent() -  n2.ent()) < 0.05, "syms ent?"

  def csv():
    d = DATA()
    n=0
    for row in csv(the.train): n += len(row)
    assert n== 3192,"csv?"

  def reads():
    d = DATA().incs(csv(the.train))
    assert d.cols.y[1].n==398,"reads?"

  def dists():
    d = DATA().incs(csv(the.train))
    random.shuffle(d.rows)
    lst = sorted( round(d.dist(d.rows[0], row),2) for row in d.rows[:100])
    for x in lst: assert 0 <= x <= 1, "dists1?" 
    assert .33 <= lst[len(lst)//2] <= .66, "dists2?"

  def d2h():
    d = DATA().incs(csv(the.train)).d2hs()
    lst = [row for i,row in enumerate(d.rows) if i % 30 ==0]
    assert d.d2h(d.rows[0]) < d.d2h(d.rows[-1]), "d2h?"

  def clone():
    d1 = DATA().incs(csv(the.train))
    d2 = d1.clone(d1.rows)
    for a,b in zip(d1.cols.y, d2.cols.y):
      for k,v1 in a.__dict__.items():
        assert v1 == b.__dict__[k],"clone?"

# ## Start-up

if __name__ == "__main__" and len(sys.argv)> 1:
  random.seed(the.seed)
  getattr(egs, sys.argv[1])()
