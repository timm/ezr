from data import Num, Sym

def sub(i,v,purge=False): 
  "Subtraction is like addition, just with a negative increment."
  return add(i, v, inc= -1, purge=purge)

def add(i, v, inc=1, purge=False): # -> v
  "Add `v` to `i`. Skip unknowns ('?'), return v."
  if v != "?": 
    i.n += inc
    if   i.it is Num: _num(i,v,inc)
    elif i.it is Sym: _sym(i,v,inc)
    else: # i.it is Data
      if inc > 0: i._rows.append(v)
      elif purge: i._rows.remove(v) # only on explicit purge
      for col in i.cols.all: add(col, v[col.at], inc)
  return v

def _num(num,n,inc): 
  "To udpate Num, update mu,sd,m2,lo,hi."
  num.lo, num.hi = min(n,num.lo), max(n,num.hi)
  if inc < 0 and num.n < 2: 
    num.sd = num.m2 = num.mu = num.n = 0
  else:
    d       = n - num.mu
    num.mu += inc * (d / num.n)
    num.m2 += inc * (d * (n - num.mu))
    num.sd  = 0 if num.n <= 2 else (max(0,num.m2)/(num.n-1))**.5

def _sym(sym,s,inc): 
  "To update Syms, update symbol counts."
  sym.has[s] = inc + sym.has.get(s,0)
