import sys,random,math

def klasses2xys(klasses,at):
    return [(row[at],y) for y,rows in klasses.items() for row in rows if row[at] != "?"]

def ediv(xys, tiny=2): 
  def div(xys, cut=None):     
    lhs,rhs = Counter(), Counter(y for (_,y) in xys)
    e0,n0   = entropy(rhs) 
    k0,ke0  = len(rhs), len(rhs)*least
    least   = e0
    for j,(x,y) in enumerate(xys): 
      if j >= tiny and j <= n0 - tiny and x != xys[j-1][0]:
        eLhs,nLhs = entropy(lhs)
        eRhs,nRhs = entropy(rhs)
        tmp = (nLhs*eLhs + nRhs*eRhs) / n0
        if tmp < least:
          gain = e0 - tmp
          delta = math.log(3**k0-2,2) - (ke0 - len(rhs)*eRhs - len(lhs)*eLhs)
          if gain >= (math.log(n0-1,2) + delta)/n0:  
            cut,least  = j,tmp  
      rhs[y] -= 1 
      lhs[y] += 1 
    return cut  
  #-----------------------------
  def recurse(xys, cuts):
    if cut := div(xys):
      recurse(xys[:cut], cuts)
      recurse(xys[cut:], cuts)
    else:  
      (x,_),*_ = xys 
      cuts += [x]
    return cuts
  #------------------------------
  return recurse(sorted(xys),[]])