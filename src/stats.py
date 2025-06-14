from about import the
from lib import picks,big
from data import Num
from query import mid

# Non-parametric significance test from Chp20,doi.org/10.1201/9780429246593.
# Distributions are the same if, often, we `_see` differences just by chance.
# We center both samples around the combined mean to simulate
# what data might look like if vals1 and vals2 came from the same population.
def bootstrap(vals1, vals2):
  "Non-parametric significance test from Chp20,doi.org/10.1201/9780429246593."
  _see = lambda i,j: abs(i.mu - j.mu) / ((i.sd**2/i.n + j.sd**2/j.n)**.5 +1/big)
  x,y,z= Num(vals1+vals2), Num(vals1), Num(vals2)
  yhat = [y1 - mid(y) + mid(x) for y1 in vals1]
  zhat = [z1 - mid(z) + mid(x) for z1 in vals2] 
  n    = 0
  for _ in range(the.bootstrap):
    n += _see(Num(picks(yhat, k=len(yhat))), 
              Num(picks(zhat, k=len(zhat)))) > _see(y,z) 
  return n / the.bootstrap >= (1- the.samples)

def cliffs(vals1,vals2):
  "Non-parametric effect size from Tb1 of  doi.org/10.3102/10769986025002101"
  n,lt,gt = 0,0,0
  for x in vals1:
    for y in vals2:
      n += 1
      if x > y: gt += 1
      if x < y: lt += 1 
  return abs(lt - gt)/n  < the.Cliffs # 0.197)  #med=.28, small=.11

def scottKnott(rxs, eps=0, reverse=False):
  "Recurive bi-cluster of treatments. Stops when splits are the same."
  rxs = [(Num(a,txt=k, rank=0), len(a), sum(a), a) for k,a in rxs.items()]
  rxs.sort(key=lambda x: x[0].mu, reverse=reverse)
  _div(rxs,eps)
  return {num.txt:num for num,_,_,_ in rxs}

def _div(rxs, eps, rank=0):
  _same = lambda a,b: cliffs(a,b) and bootstrap(a,b)
  _flat = lambda rxs: [x for _,_,_,lst in rxs for x in lst]
  if len(rxs) > 1:
    if (cut := _cut(rxs,eps)):
      left, right = rxs[:cut], rxs[cut:]
      if not _same(_flat(left), _flat(right)): 
        return _div(right,eps,  _div(left,eps,rank)+1)
  for row,_,_,_ in rxs: row.rank = rank
  return rank

def _cut(rxs,eps):
  out, most = None,0
  n1 = s1 = 0
  s0 = s2 = sum(s for _,_,s,_ in rxs)
  n0 = n2 = sum(n for _,n,_,_ in rxs)
  for i, (_,n,s,_) in enumerate(rxs):
    if i > 0:
      m0, m1, m2 = s0/n0, s1/n1, s2/n2
      if abs(m1 - m2) > eps:
        if (tmp := (n1*abs(m1 - m0) + n2*abs(m2 - m0)) / (n1 + n2)) > most:
          most, out = tmp, i
    n1, s1, n2, s2 = n1+n, s1+s, n2-n, s2-s
  return out 
