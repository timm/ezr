import sys,random,math

def ediv(lst, tiny=2): 
  def div(xys):   
    def n(z): return sum(n for n in z.values())
    lhs,rhs = Counter(), Counter(y for (_,y) in xys)
    e0,n0   = entropy(rhs)
    at,cut  = None, None
    a       = xys[0][0]
    z       = xys[-1][0]
    for j,(x,y) in enumerate(xys): 
      if n(lhs) > tiny and n(rhs) > tiny: 
        e1,n1 = entropy(lhs)
        e2,n2 = entropy(rhs)
        maybe = (n1*e1 + n2*e2)/n0
        if maybe < least: 
          cut,at,least,span = j,x,maybe,(a,x,z)
      rhs[y] -= 1
      lhs[y] += 1 
    return cut,at,span
    
  # gain  = e0 - maybe
  #         delta = log2(3**k0-2)-(ke0- ke(rhs)-ke(lhs))
          # if gain >= (log2(n0-1) + delta)/n0: 
  #----------------------------------------------
  def recurse(this, cuts):
    cut,at = div(this)
    if cut: 
      recurse(this[:cut], cuts)
      recurse(this[cut:], cuts)
    else:   
      cuts += [at]
    return cuts
  #---| main |-----------------------------------
  return recurse(sorted(lst,key=lambda z:z[0]),[])