import sys,random,math

def ediv(klasses, at, tiny=2): 
  def div(xys):     
    lhs,rhs = Counter(), Counter(y for (_,y) in xys)
    least,n  = entropy(rhs)
    e0,cut = least,None
    k0,ke0 = len(rhs), len(rhs)*least
    for j,(x,y) in enumerate(xys): 
      if lhs.total() > tiny and rhs.total() > tiny and x != xys[j-1][0]:
        eLhs,nLhs = entropy(lhs)
        eRhs,nRhs = entropy(rhs)
        tmp = (nLhs*eLhs + nRhs*eRhs) / n
        if tmp < least:
          gain = e0 - tmp
          delta = math.log(3**k0-2,2)-(ke0 - len(rhs)*eRhs - len(lhs)*eLhs)
          if gain >= (math.log(n-1,2) + delta)/n:  
            cut,least  = j,tmp  
      rhs[y] -= 1 
      lhs[y] += 1 
    return cut  
     
  #----------------------------------------------
  def recurse(xys, cuts):
    if cut := div(xys):
      recurse(xys[:cut], cuts)
      recurse(xys[cut:], cuts)
    else:   
      cuts += [xys[0][0]]
    return cuts
  #---| main |-----------------------------------
  xys = [(row[at],y) for y,rows in klasses.items() for row in rows if row[at] != "?"]
  return recurse(sorted(xys),div)