# vim : set et ts=2 sw=2 :
"""
ez: ai can be easy, let me show you how   
(c) 2023, Tim Menzies, <timm@ieee.org>, BSD-2  
  
USAGE:    
1. download ez.py, etc.py, eg.py    
2. python3 eg.py [OPTIONS]   
  
OPTIONS:  

     -b --budget0     initial evals              = 4  
     -B --Budget      subsequent evals           = 6   
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

import re,math,random
from collections import Counter
from stats import sk
from etc import o
import etc

the = etc.THE(__doc__)

#----------------------------------------------------------------------------------------
def strOfGoal(s):   return s[-1] in "+-!"
def strOfHeaven(s): return 0 if s[-1] == "-" else 1
def strOfNum(s):    return s[0].isupper()
def colOfSym(x):    return isinstance(x,Counter)

#----------------------------------------------------------------------------------------
class NUM(etc.struct):
  def __init__(self,lst,txt=" ",rank=0):
   self.n, self.mu, self.m2, self.sd = 0,0,0,0
   self.txt, self.rank, self._has    = txt,rank,sorted(lst)
   for x in lst:
     self.n += 1
     delta = x - self.mu
     self.mu += delta / self.n
     self.m2 += delta * (x -  self.mu)
   self.heaven = 0 if txt[-1] == "-" else 1
   if len(lst) > 1: self.sd = (self.m2 / (self.n - 1))**.5

  def d(self,x):
    if x=="?": return x
    tmp = (self.heaven==0 and (self.mu-x) or (x-self.mu))/(self.sd*the.cohen)
    return 0 if -1 <= tmp and tmp <= 1 else tmp

  def d2h(self,x):
    return abs(self.heaven - self.norm(x))

  def norm(self,x):
    return x=="?" and x or (x - self._has[0]) / (self._has[-1] - self._has[0] + 1E-30)

#----------------------------------------------------------------------------------------
class DATA(etc.struct):
  def __init__(self, lsts, order=False):
    self.names,*rows = list(lsts)
    rotated   = [[y for y in x if y !="?"] for x in zip(*rows)]
    self.cols = [NUM(lst,s) if strOfNum(s) else Counter(lst)
                 for s,lst in zip(self.names,rotated)]
    self.ys   = {n:c for n,(s,c) in enumerate(zip(self.names,self.cols)) if strOfGoal(s)}
    self.rows = sorted(rows, key=lambda row:self.d2h(row)) if order else rows

  def clone(self, rows=[], order=False):
    return DATA([self.names] + rows, order=order)

  def d2h(self,lst):
    x =  sum((col.d2h(lst[n])**2 for n,col in self.ys.items()))
    return (sum(col.d2h(lst[n])**2 for n,col in self.ys.items()) / len(self.ys))**.5

  def like(self,row,nall,nh,m=1,k=2):
    def num(col,x):
      v = col.sd**2 + 10**-64
      nom = math.e**(-1*(x - col.mu)**2/(2*v)) + 10**-64
      denom = (2*math.pi*v)**.5
      return min(1, nom/(denom + 10**-64))
    def sym(col,x):
      return (col.get(x, 0) + m*prior) / (len(self.rows) + m)
    #------------------------------------------
    prior = (len(self.rows) + k) / (nall + k*nh)
    out   = math.log(prior)
    for c,x in etc.slots(row):
      if x != "?" and c not in self.ys:
        col  = self.cols[c]
        inc  = (sym if colOfSym(col) else num)(col, x)
        out += math.log(inc)
    return out

  def mid(self):
    return [max(col,key=col.get) if colOfSym(col) else col.mu for col in self.cols]

  def div(self):
    return [etc.entropy(col) if colOfSym(col) else col.sd for col in self.cols]

  def smo(self, fun=None):
    def smo1(i, best, rest, rows):
      out,most = 0,-1E300
      for k,row in enumerate(rows):
        b = best.like(row, len(self.rows), 2, the.m, the.k)
        r = rest.like(row, len(self.rows), 2, the.m, the.k)
        tmp = b - r
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
          smo1( i + 1 + the.budget0,
                self.clone(data1.rows[:n],order=True),
                self.clone(data1.rows[n:]),
                todo)))
      data1 = self.clone(done, order=True)
    return data1.rows[0]
