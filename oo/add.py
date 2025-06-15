from lib import of
from Data import Data
from Num import Num
from Sym import Sym

def add(i, v, inc=1, purge=False): # -> v
  "For inc additions; add `v` to `i`. Skip unknowns. Return v."
  if v != "?": 
    i.n += inc
    i.add(v,inc,purge)
  return i

def sub(i,v,purge=False): 
  "Subtraction is just addition, with a negative increment."
  return add(i, v, inc= -1, purge=purge)

@of("Update rows and columns")
def add(i:Data,row,inc,purge):  
  if inc > 0: i._rows.append(row) 
  elif purge: i._rows.remove(row) # slow for large lists
  for col in i.cols.all: col.add(row[col.at], inc)

@of("update nu,sd,m2,lo,hi")
def add(i:Num,n,inc,_): 
  i.lo, i.hi = min(n,i.lo), max(n,i.hi)
  if inc < 0 and i.n < 2: 
    i.sd = i.m2 = i.mu = i.n = 0
  else:
    d       = n - i.mu
    i.mu += inc * (d / i.n)
    i.m2 += inc * (d * (n - i.mu))
    i.sd  = 0 if i.n <= 2 else (max(0,i.m2)/(i.n-1))**.5

@of("Update symbol counts")
def add(i:Sym,s,inc,_): 
  i.has[s] = inc + i.has.get(s,0)
