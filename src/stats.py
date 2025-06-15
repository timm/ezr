import random
from collections import namedtuple

Abcd = namedtuple('Abcd', 'a b c d pd pf prec acc')

def abcd(got, want, this=None):
  this = this or dict(yes=0, no=0, known={}, stats={})
  for x in [want, got]:
    if x not in this["known"]:
      this["known"][x] = 1
      this["stats"][x] = Abcd(this["yes"]+this["no"],0,0,0,0,0,0,0)
    else:
      this["known"][x] += 1
  this["yes" if got==want else "no"] += 1
  for x in this["known"]:
    a, b, c, d, *_ = this["stats"][x]
    if x == want: b, d = (b+1, d) if got != want else (b, d+1)
    else:         c, a = (c+1, a) if got == x    else (c, a+1)
    this["stats"][x] = Abcd(a, b, c, d, 0,0,0,0)
  return this

def abcdReport(self):
  eps, p = 1e-32, lambda n: int(round(100*n,0))
  for x, abcd in self["stats"].items():
    a, b, c, d, *_ = abcd
    pd   = d / (b + d + eps)
    pf   = c / (a + c + eps)
    prec = d / (c + d + eps)
    acc  = (a + d) / (a + b + c + d + eps)
    self["stats"][x] = Abcd(a,b,c,d,p(pd),p(pf),p(prec),p(acc))
  return self

def same(xs,ys,Num,cliff,n,conf):
  return cliffs(xs,ys,cliff) and bootstrap(xs,ys,Num,n,conf)

def cliffs(xs,ys, cliff):
  "Effect size. Tb1 of doi.org/10.3102/10769986025002101"
  n,lt,gt = 0,0,0
  for x in xs:
    for y in ys:
      n += 1
      if x > y: gt += 1
      if x < y: lt += 1 
  return abs(lt - gt)/n  < cliff # 0.197)  #med=.28, small=.11

# Non-parametric significance test from Chp20,doi.org/10.1201/9780429246593.
# Distributions are the same if, often, we `_see` differences just by chance.
# We center both samples around the combined mean to simulate
# what data might look like if vals1 and vals2 came from the same population.
def bootstrap(xs, ys, Num, bootstrap,conf):
  "Non-parametric significance test from Chp20,doi.org/10.1201/9780429246593."
  _see = lambda i,j: abs(i.mu - j.mu) / (
                     (i.sd**2/i.n + j.sd**2/j.n)**.5 +1E-32)
  x,y,z = Num(xs+ys), adds(xs), Num(ys)
  yhat  = [y1 - mid(y) + mid(x) for y1 in xs]
  zhat  = [z1 - mid(z) + mid(x) for z1 in ys] 
  n     = 0
  for _ in range(bootstrap):
    n += _see(Num(random.choices(yhat, k=len(yhat))), 
              Num(random.choices(zhat, k=len(zhat)))) > _see(y,z) 
  return n / bootstrap >= (1- conf)

def scottKnott(rxs, eps, reverse, Num,*opts):
  "Recurive bi-cluster of treatments. Stops when splits are the same."
  rxs = [(Num(a,txt=k, rank=0), len(a), sum(a), a) for k,a in rxs.items()]
  rxs.sort(key=lambda x: x[0].mu, reverse=reverse)
  _div(rxs, eps, 0, Num, *opts)
  return {num.txt:num for num,_,_,_ in rxs}

def _div(rxs, eps, rank, *opts):
  _flat = lambda rxs: [x for _,_,_,lst in rxs for x in lst]
  if len(rxs) > 1:
    if (cut := _cut(rxs,eps)):
      left, right = rxs[:cut], rxs[cut:]
      if not same(_flat(left), _flat(right), *opts): 
        rank = _div(left,  eps, rank, *opts) + 1
        return _div(right, eps, rank, *opts)
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
        if (tmp := (n1*abs(m1-m0) + n2*abs(m2-m0)) / (n1+n2)) >most:
          most, out = tmp, i
    n1, s1, n2, s2 = n1+n, s1+s, n2-n, s2-s
  return out 
