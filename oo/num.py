from lib import BIG
import obj

class Num(obj.ezr):
  "Summary of numeric columns."
  def __init__(i, inits=[], at=0, txt="", rank=0):
     i.n = i.mu = i.m2 = i.sd = 0    ## items seen  
     i.at   = at   ## column position
     i.txt  = txt  ## column name
     i.hi   = -BIG ## biggest seen
     i.lo   =  BIG ## smallest seen
     i.rank = rank ## used only by stats
     i.heaven = 0 if  txt.endswith("-") else 1 ## goal. 0,1=min,max
     i.adds(inits)

  def _add(i,n, inc, _):
    "Update"
    i.lo, i.hi = min(n,i.lo), max(n,i.hi)
    if inc < 0 and i.n < 2: 
      i.sd = i.m2 = i.mu = i.n = 0
    else:
      d       = n - i.mu
      i.mu += inc * (d / i.n)
      i.m2 += inc * (d * (n - i.mu))
      i.sd  = 0 if i.n <= 2 else (max(0,i.m2)/(i.n-1))**.5

  def mid(i) : 
    "Cental tendancy."
    return i.mu

  def spread(i) : 
    "Deviation from central tendancy."
    return i.sd

  def norm(i, v): 
    "Normalize 0..1 for min..max."
    return v if v=="?" else (v - i.lo) / (i.hi - i.lo + 1/BIG)
