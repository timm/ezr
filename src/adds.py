from data import Num, Sym

def sub(i,v,purge=False): 
  "Subtraction is like addition, just with a negative increment."
  return add(i, v, inc= -1, purge=purge)

def add(i,v, inc=1, purge=False): # -> v
  "Add `v` to `i`. Skip unknowns ("?"), return v."
  def _sym(sym,s): 
    "Updating Syms means just updating symbol counts."
    sym.has[s] = inc + sym.has.get(s,0)

  def _data(data,row): 
    "To udpate Data, change the rows and update the columns."
    if inc < 0:  
      if purge: data._rows.remove(v)  # Slow for very large lists
      [sub(c, row[c.at], inc) for c in data.cols.all]  
    else: 
      data._rows += [row] # update rows
      [add(c,row[c.at],inc) for c in data.cols.all] # update cols

  def _num(num,n): 
    "To udpate Num, change mu,sd,m2,lo,hi."
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
