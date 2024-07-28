#!/usr/bin/env python3 -B
# <!-- vim: set ts=2 sw=2 sts=2 et: -->
from __future__ import annotations 
from typing import Any as any
from typing import Callable 
from fileinput import FileInput as file_or_stdin
from dataclasses import dataclass, field, fields
from typing import Any, List, Dict, Type
from math import log,cos,sqrt,pi
import re,sys,random

R  = random.random ##

# Types
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

def LIST(): return field(default_factory=list)
def DICT(): return field(default_factory=dict)

number  = float  | int   # 
atom    = number | bool | str # and sometimes "?"
row     = list[atom]
rows    = list[row]
classes = dict[str,rows] # `str` is the class name

@dataclass
class COL:
  n   : int = 0
  at  : int = 0
  txt : str = ""

@dataclass
class SYM(COL):
  has  : Dict = DICT()
  mode : atom=None
  most : int=0

@dataclass     
class NUM(COL):
  mu : number =  0
  m2 : number =  0
  sd : number =  0
  lo : number =  1E21
  hi : number = -1E32
  goal : number = 1

  def norm(self, x): return x=="?" and x or (x - self.lo) / (self.hi - self.lo + 1E-32)


@dataclass
class COLS:
  names: List = LIST()  # column names
  all  : List = LIST()  # all NUMS and SYMS
  x    : List = LIST()  # independent COLums
  y    : List = LIST()  # depedent COLumns

  def init(self : COLS, row:row) -> COLS:
    self.names = row
    for at,txt in enumerate(row): self.init1(at,txt, txt[0],txt[-1])
    return self
   
  def init1(self:COLS, at,txt, a,z):
    col = (NUM if a.isupper() else SYM)(at=at,txt=txt)
    self.all += [col]
    if z != "X":
      (self.y if z in "+-" else self.x).append(col)
      if z=="-": col.goal = 0

  def add(self : COLS, row):
    for cols in [self.x, self.y]:
      for col in cols: 
        row[col.at] = col.add(row[col.at])
    return row

@dataclass
class DATA:
  cols   : COLS = None         # summaries of rows
  rows   : rows = LIST() # rows

  def clone(self : DATA, rows:rows==[]) -> DATA:
    return DATA().add(self.cols.names).adds(rows)

  def sorted(self:DATA):
    self.rows = sorted(self.rows, key=lambda r: self.d2h(r))
    return self

  def adds(self:DATA, src): 
    [self.add(row) for row in src]; return self

  def add(self,row):
    if    self.cols: self.rows += [self.cols.add(row)]
    else: self.cols = COLS().init(row)
    return self

#---------------------------
import inspect
def inn(fun): print(1)
def of(fun):
    spec = inspect.getfullargspec(fun).annotations
    cls  = globals()[spec['self']]
    setattr(cls, fun.__name__, fun)
    return fun
#---------------------------
@of
def add(self:COL, x:any) -> any:
  if x != "?":
     self.n += 1
     x = self.add1(x)
  return x

@of
def add1(self:SYM, x:any) -> any: 
  self.has[x] = self.has.get(x,0) + 1
  if self.has[x] > self.most: self.mode, self.most = x, self.has[x]
  return x

@of
def add1(self:NUM, x:any) -> number: 
  if isinstance(x,str): x = _coerce(x)
  # -- lo,hi
  self.lo = min(x, self.lo)
  self.hi = max(x, self.hi)
  # -- update sd
  d        = x - self.mu
  self.mu += d / self.n
  self.m2 += d * (x -  self.mu)
  self.sd  = 0 if self.n <2 else (self.m2/(self.n-1))**.5
  return x

def _coerce(x:str) -> number:
  try: return float(x)
  except ValueError: return int(x)

# ------------------
# guess
@of
def any(self:DATA, fun:Callable=None) -> row:
  fun = fun or (lambda col: col.any())
  out = ["?" for _ in self.cols.all]
  for col in self.cols.x: out[col.at] = fun(col)
  return out

@of
def any(self:SYM) -> any: 
  r = R()
  for x,n in self.has.items():
    r -= n/self.n
    if r <= 0: return x
  return self.mode

@of
def any(self:NUM) -> number:
  while True:
    x1 = 2.0 * R() - 1
    x2 = 2.0 * R() - 1
    w = x1*x1 + x2*x2
    if w < 1: break
  x=x1   
  w=sqrt((-2*log(w))/w)
  y1 = x*w
  return m + y1*s

@of
def explore(self:DATA, other:DATA):
  out=self.any()
  for coli,colj in zip(self.cols.x, other.cols.x): out[coli.at] = coli.explore(colj)
  return out

@of
def exploit(self:DATA, other:DATA):
  out=self.any()
  for coli,colj in zip(iself.cols.x, other.cols.x): out[coli.at] = coli.exploit(colj)
  return out

@of
def explot(self:COL, other:COL, n=20):
  key     = lambda x: self.like(x,pr1) - other.like(x,pr2)
  nij     = (self.n + other.n + 2*the.k)
  pr1,pr2 = (self.n + the.k) / nij, (other.n + the.k) / nij
  return max([self.any() for _ in range(n)], key=key)

@of
def explore(self:COL, other:COL, n=20):
  key     = lambda x: abs(self.like(x,pr1) - other.like(x,pr2))
  nij     = (self.n + other.n + 2*the.k)
  pr1,pr2 = (self.n + the.k) / nij, (other.n + the.k) / nij
  return min([self.any() for _ in range(n)], key=key)

#--------------
# Dist
@of
def d2h(self:DATA,row:row) -> number:
  d = sum(abs(c.goal - c.norm(row[c.at]))**2 for c in self.cols.y)
  return (d/len(self.cols.y)) ** (1/the.p)

@of
def dist(self:DATA, r1:row, r2:row) -> float:
  n = sum(c.dist(r1[c.at], r2[c.at])**the.p for c in self.cols.x)
  return (n / len(self.cols.x))**(1/the.p)

@of
def neighbors(self:DATA, r1:row, rows:rows=None) -> rows:
  return sorted(rows or self.rows, key=lambda r2: self.dist(r1,r2))

@of
def dist(self:COL, x:any, y:any) -> float:
  return 1 if x==y=="?" else self.dist1(x,y)

@of
def dist1(self:SYM, x:number, y:number) -> float: return x != y

@of
def dist1(self:NUM, x:number, y:number) -> float:
  x, y = self.norm(x), self.norm(y)
  x = x if x !="?" else (1 if y<0.5 else 0)
  y = y if y !="?" else (1 if x<0.5 else 0)
  return abs(x-y)

#--------------
# Bayes
@of
def like(self:DATA, r:row, nall:int, nh:int) -> float:
  prior = (len(self.rows) + the.k) / (nall + the.k*nh)
  likes = [c.like(r[c.at], prior) for c in the.cols.x if r[c.at] != "?"]
  return sum(log(x) for x in likes + [prior] if x>0)

@of
def like(self:SYM, x:any, prior:float) -> float:
  return (self.has.get(x,0) + the.m*prior) / (self.n + the.m)

@of
def like(self:NUM, x:number) -> float:
  v     = self.sd**2 + 1E-30
  nom   = math.exp(-1*(x - self.mu)**2/(2*v)) + 1E-30
  denom = (2*math.pi*v) **0.5
  return min(1, nom/(denom + 1E-30))

def smo(self:data, score=lambda B,R: B-R, ):
  "Sequential model optimization."
  def _ranked(rows):
   return self.clone(rows).sorted().rows

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

#---------------------------
def csv(file) -> row:
  with file_or_stdin(None if file=="-" else file) as src:
    for line in src:
      line = re.sub(r'([\n\t\r ]|#.*)', '', line)
      if line: yield [s.strip() for s in line.split(",")]

class eg:
  def all(): 
   for s in dir(eg):
     if s[0] != "_" and s != "all": getattr(eg,s)()

  def csv(): 
    d = DATA()
    [print(row) for row in csv(the.train)]

  def reads():
    d = DATA().adds(csv(the.train))
    print(d.cols.y[1])

  def dists():
    d = DATA().adds(csv(the.train))
    random.shuffle(d.rows)
    print(
      sorted(
        round(d.dist(d.rows[0], row),2) 
          for row in d.rows[:100]))

  def d2h():
    d = DATA().adds(csv(the.train)).sorted()
    for i,row in enumerate(d.rows):
      if i % 30 == 0: print(i,row,sep="\t")

  def clone():
    d1 = DATA().adds(csv(the.train))
    d2 = d1.clone(d1.rows)
    for a,b in zip(d1.cols.y, d2.cols.y):
      print("")
      print(a)
      print(b)

if __name__ == "__main__" and len(sys.argv)> 1: 
  random.seed(the.seed)
  getattr(eg, sys.argv[1])()
