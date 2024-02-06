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
     -E --Experiments number of Bootstraps       = 256
     -f --file        csv data file name         = '../data/auto93.csv'  
     -F --Far         far search outlier control = .95
     -h --help        print help                 = false
     -H --Half        #items for far search      = 256
     -k --k           rare class  kludge         = 1  
     -m --m           rare attribute  kludge     = 2  
     -M --Min         min size is N**Min         = .5
     -p --p           distance coefficient       = 2
     -s --seed        random number seed         = 31210   
     -t --todo        start up action            = 'help'   
     -T --Top         best section               = .5   
"""

from heapq import merge
import re,sys,math,random
from collections import Counter
from stats import sk
from etc import o,isa,struct 
import etc

the = etc.THE(__doc__)
tiny= sys.float_info.min 

#          _   _   |   _ 
#         (_  (_)  |  _>                       

def isGoal(s):   return s[-1] in "+-!"
def isHeaven(s): return 0 if s[-1] == "-" else 1
def isNum(s):    return s[0].isupper() 

class SYM(Counter):
  "Adds `add` to Counter"
  def add(self,x): self[x] += 1

  def entropy(self): 
    n = sum(self.values()) 
    return -sum(v/n*math.log(v/n,2) for _,v in self.items() if v>0)
  
class NUM(struct):
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
 
#         ._   _          _ 
#         |   (_)  \/\/  _> 

class DATA(struct):
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
    return [col.entropy() if isa(col,SYM) else col.sd for col in self.cols]
  
#                                  _     
#          _  |   _.   _   _  o  _|_     
#         (_  |  (_|  _>  _>  |   |   \/ 
#                                     /  

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
            
#          _   ._   _|_  o  ._ _   o  _    _   /| 
#         (_)  |_)   |_  |  | | |  |  /_  (/_   | 
#              |                                  

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
                                     
#          _  |        _  _|_   _   ._ 
#         (_  |  |_|  _>   |_  (/_  |  
                                      
  def dist(self,row1,row2):
    def sym(_,x,y): 
      return 1 if x=="?" and y=="?" else (0 if x==y else 1)     
    def num(col,x,y):
      if x=="?" and y=="?" : return 1 
      x, y = col.norm(x), col.norm(y) 
      if x=="?" : x= 1 if y<.5 else 0
      if y=="?" : y= 1 if x<.5 else 0 
      return abs(x-y)  
    #-----------------
    d, n, p = 0, 0, the.p
    for c,col in  enumerate(self.cols):
      if c not in self.ys:
        n   = n + 1
        inc = (sym if isa(col,SYM) else num)(col, row1[c],row2[c])
        d   = d + inc**p 
    return (d/n)**(1/p) 

  def near(self, row1, rows=None):
    return sorted(rows or self.rows, key=lambda row2: self.dist(row1,row2))

  def far(self, rows, sortp=False, before=None):
    n     = int(len(rows) * the.Far)
    left  = before or self.near(random.choice(rows),rows)[n]
    right = self.near(left,rows)[n]
    if sortp and self.d2h(right) < self.d2h(left): left,right = right,left
    return left, right 
    
  def half(self, rows, sortp=False, before=None):
    def dist(r1,r2): return self.dist(r1, r2)
    def proj(row)  : return (dist(row,left)**2 + C**2 - dist(row,right)**2)/(2*C)
    left,right = self.far(random.choices(rows, k=min(the.Half, len(rows))),
                          sortp=sortp, before=before)
    lefts,rights,C = [],[], dist(left,right)
    for n,row in enumerate(sorted(rows, key=proj)):  
      (lefts if n < len(rows)/2 else rights).append(row)
    return lefts, rights, left

#                                              _  
#          _   ._   _|_  o  ._ _   o  _    _    ) 
#         (_)  |_)   |_  |  | | |  |  /_  (/_  /_ 
#              |                                  

  def branch(self, rows, stop=None, rest=None, evals=1, before=None):
    stop = stop or 2*len(rows)**the.Min
    rest = rest or []
    if len(rows) > stop:
      lefts,rights,left  = self.half(rows, True, before)
      return self.branch(lefts, stop, rest+rights, evals+1, left)
    else:
      return rows,rest,evals

                                               
#          _|  o   _   _  ._   _   _|_  o  _    _  
#         (_|  |  _>  (_  |   (/_   |_  |  /_  (/_                                                

class RANGE(struct):
  def __init__(self,txt="",at=0,lo=None,hi=None,ys=None):
    self.txt=""
    self.lo = lo
    self.hi = hi or lo
    self.ys = ys  

  def add(self,x,y): 
    self.lo  = min(self.lo, x) 
    self.hi  = max(self.hi, x)
    self.ys.add(y)

  def merge(self,other,small):
    both = RANGE(txt=self.txt, at=self.at, lo=self.lo, hi=other.hi, ys=self.ys + other.ys)
    m,n = sum(self.ys.values()), sum(other.ys.values())
    if m < small: return both
    if n < small: return both
    if both.ys.entropy() <= (m*self.ys.entropy() + n*other.ys.entropy())/(m+n): return both

  def __repr__(self): 
    lo,hi,s = self.x.lo, self.x.hi,self.txt
    if lo == -sys.maxsize: return f"{s} <  {hi}" 
    if hi ==  sys.maxsize: return f"{s} >= {lo}" 
    if lo ==  hi         : return f"{s} == {lo}" 
    return f"{lo} <= {s} < {hi}" 

def discretize(c,col,rowss):
  def bin(col,x): 
    if isa(col,SYM): return x
    tmp = (col.hi - col.lo)/(the.bins - 1)
    return col.hi==col.lo and 0 or int(.5 + x/tmp) 
  #------------
  bins,n = {},0
  for y,rows in rowss.items(): 
    for row in rows:
      x = row[c]
      if x != "?": 
        n += 1
        b = bin(col,x)
        bins[b] = bins[b] if b in bins else RANGE(txt=col.txt, at=c,lo=x, hi=x, ys=SYM()) 
        bins[b].add(x, y) 
  bins = bins.values().sort(key=lambda bin:bin.lo)
  return bins if isa(col,SYM) else _merges(bins, n/the.bins)
  
def _merges(bins,small): 
  i, tmp, most =  0, [], len(bins)
  while i < most - 2:
    a = bins[i]
    if i < most - 1:
      b = bins[i+1]
      if ab := a.merge(b, small):
        a = ab
        i += 1
    tmp += [a]
    i += 1
  if len(tmp) < len(bins): return  _merges(tmp,small)
  else: 
    for i in range(1,len(bins)): bins[i].lo = bins[i-1].hi  
    bins[0].lo  = -sys.maxsize
    bins[-1].hi =  sys.maxsize
    return bins  
                                      
#          _       ._   |   _.  o  ._  
#         (/_  ><  |_)  |  (_|  |  | | 
#                  |                   

class RULE(struct):
  def __init__(self,ranges):
    self.parts, self.scored = {},0
    for range in ranges:
      self.parts[range.txt] = self.parts.get(range.txt,[])
      self.parts[range.txt] += [range]

  def _or(self,ranges,row):
    x =  row[ranges[1].at]
    if x== "?": return True
    for range in ranges:
      if self.lo==self.hi==x:    return True
      if self.lo <= x < self.hi: return True
    return False
  
  def _and(self,row):
    for ranges in self.parts.values():
      if  not self._or(ranges,row): return False
    return True
  
  def selects(self,rows):
    return [row for row in rows if self._and(row)]
  
  def selectss(rowss): 
    return [row for _,rows in rowss.items() for row in self.selects(rows)]
  
  def __repr__(self):
    all= sorted([[r.txt,r.lo,r.hi] for _,ranges in self.parts.items() for r in ranges])
    i=1
    while i < len(all) :
      a  = all[i] 
      if i < len(all)-2:
        b=aall[i+1]
        and a[0]==b[0] and a[2] == b[1]: 
        a[-1]=b[-1]
        all.pop(i+1)
      else:
        i += 1


  
