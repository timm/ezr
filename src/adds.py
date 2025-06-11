# Add `v` to `i`. Skip unknowns ("?"), return v.
from data import Num, Sym

# Subtraction is like addition, just with a negative increment  
def sub(i,v,purge=False): 
  return add(i, v, inc= -1, purge=purge)

# Add `v` to `i`. Skip unknowns ("?"), return v.
def add(i,v, inc=1, purge=False): # -> v
  def _sym(sym,s): sym.has[s] = inc + sym.has.get(s,0)

  def _data(data,row): 
    if inc < 0:  
      if purge: data._rows.remove(v)  # Slow for very large lists
      [sub(c, row[c.at], inc) for c in data.cols.all]  
    else: 
      data._rows += [row] # update rows
      [add(c,row[c.at],inc) for c in data.cols.all] # update cols

  def _num(num,n): 
    num.lo = min(n, num.lo)
    num.hi = max(n, num.hi)
    if inc < 0 and num.n < 2: 
      num.sd = num.m2 = num.mu = num.n = 0
    else:
      d       = n - num.mu
      num.mu += inc * (d / num.n)
      num.m2 += inc * (d * (n - num.mu))
      num.sd  = 0 if num.n <=2 else (max(0,num.m2)/(num.n-1))**.5

  if v != "?": 
    i.n += inc
    (_num if i.it is Num else (_sym if i.it is Sym else _data))(i,v)
  return v
