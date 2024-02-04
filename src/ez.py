# vim : set et ts=2 sw=2 :
"""
ez: ai can be easy, let me show you how   
(c) 2023, Tim Menzies, <timm@ieee.org>, BSD-2  
  
USAGE:    
1. download ez.py, etc.py, eg.py    
2. python3 eg.py [OPTIONS]   
  
OPTIONS:  

     -b --budget0     initial evals              = 4  
     -B --Budget      subsequent evals           = 5   
     -c --cohen       small effect size          = .35  
     -c --confidence  statistical confidence     = .05
     -e --effectSize  non-parametric small delta = 0.2385
     -E --Experiments number of Bootstraps       = 512
     -f --file        csv data file name         = '../data/auto93.csv'  
     -h --help        print help                 = false
     -k --k           rare class  kludge         = 1  
     -m --m           rare attribute  kludge     = 2  
     -s --seed        random number seed         = 31210   
     -t --todo        start up action            = 'help'   
     -T --Top         best section               = .5   
"""

import re,sys,math,random
from collections import Counter
from stats import sk
from etc import o,isa
import etc

the = etc.THE(__doc__)
tiny= sys.float_info.min 

#----------------------------------------------------------------------------------------
def isGoal(s):   return s[-1] in "+-!"
def isHeaven(s): return 0 if s[-1] == "-" else 1
def isNum(s):    return s[0].isupper() 

#----------------------------------------------------------------------------------------
class SYM(Counter):
  def add(self,x): self[x] += 1
  
class NUM(etc.struct):
  def __init__(self,lst=[],txt=" "):
   self.n, self.mu, self.m2, self.sd, self.txt = 0,0,0,0,txt 
   self.lo, self.hi = sys.maxsize, -sys.maxsize
   self.heaven = isHeaven(txt)
   [self.add(x) for x in lst]

  def add(self,x):
    self.lo = min(x,self.lo)
    self.hi = max(x,self.hi)
    self.n += 1
    delta = x - self.mu
    self.mu += delta / self.n
    self.m2 += delta * (x -  self.mu)
    self.sd = 0 if self.n < 2 else (self.m2 / (self.n - 1))**.5

  def norm(self,x):
    return x=="?" and x or (x - self.lo) / (self.hi - self.lo + tiny)

#----------------------------------------------------------------------------------------
class DATA(etc.struct):
  def __init__(self, lsts=[], order=False):
    self.names,*rows = list(lsts) 
    self.rows = []
    self.cols = [(NUM(txt=s) if isNum(s) else SYM()) for s in self.names] 
    self.ys   = {n:c for n,(s,c) in enumerate(zip(self.names,self.cols)) if isGoal(s)}
    [self.add(row) for row in rows] 
    if order: self.ordered()

  def ordered(self):
    self.rows = sorted(self.rows, key = self.d2h)

  def add(self,row): 
    self.rows += [row] 
    [col.add(x) for x,col in zip(row,self.cols) if x != "?"]

  def clone(self, rows=[], order=False):
    return DATA([self.names] + rows, order=order)

  def d2h(self,lst):
    nom = sum(abs(col.heaven - col.norm(lst[n]))**2 for n,col in self.ys.items())
    return (nom / len(self.ys))**.5

  def mid(self): 
    return [max(col,key=col.get) if isa(col,SYM) else col.mu for col in self.cols]

  def div(self):
    return [etc.entropy(col) if isa(col,SYM) else col.sd for col in self.cols]
  
  def loglike(self,row,nall,nh,m=1,k=2):
    def num(col,x):
      v     = col.sd**2 + tiny
      nom   = math.e**(-1*(x - col.mu)**2/(2*v)) + tiny
      denom = (2*math.pi*v)**.5
      return min(1, nom/(denom + tiny))
    def sym(col,x):
      return (col.get(x, 0) + m*prior) / (len(self.rows) + m)
    #------------------------------------------
    prior = (len(self.rows) + k) / (nall + k*nh)
    out   = math.log(prior)
    for c,x in etc.slots(row):
      if x != "?" and c not in self.ys:
        col  = self.cols[c]
        out += math.log((sym if isa(col,SYM) else num)(col, x))
    return out

  def smo(self, score=lambda B,R: 2*B-R, fun=None):
    def acquire(i, best, rest, rows):
      out,most = 0,-sys.maxsize
      for k,row in enumerate(rows):
        b = best.loglike(row, len(self.rows), 2, the.m, the.k)
        r = rest.loglike(row, len(self.rows), 2, the.m, the.k)
        tmp = score(b,r)
        if tmp > most: out,most = k,tmp
      if fun: fun(i, best.rows[0])
      return out
    #-----------
    random.shuffle(self.rows)
    done, todo = self.rows[:the.budget0], self.rows[the.budget0:]
    data1 = self.clone(done, order=True)
    for i in range(the.Budget):
      n = int(len(done)**the.Top + .5)
      done.append(
        todo.pop(
          acquire( i + 1 + the.budget0,
                   self.clone(data1.rows[:n]),
                   self.clone(data1.rows[n:]),
                   todo)))
      data1 = self.clone(done, order=True)
    return data1.rows[0]
