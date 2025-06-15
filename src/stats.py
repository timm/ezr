import random

class Abcd:
  def __init__(i, a): 
    i.a = a; i.b = i.c = i.d = i.pd = i.pf = i.prec = i.acc = 0
  def add(i, want, got, x):
    if x==want: i.d += got==want; i.b += got!=want
    else:       i.c += got==x;    i.a += got!=x
    a,b,c,d = i.a,i.b,i.c,i.d
    p       = lambda z: int(100*z)
    i.pd    = p(d / (b + d + 1e-32))
    i.pf    = p(c / (a + c + 1e-32))
    i.prec  = p(d / (c + d + 1e-32))
    i.acc   = p((a + d) / (a + b + c + d + 1e-32))

def abcds(got, want, this=None):
  this = this or dict(n=0,stats={})
  for x in [want, got]:
    this["stats"][x] = this["stats"].get(x) or Abcd(this["n"])
  this["n"] += 1
  for x,s in this["stats"].items():
    s.add(want,got,x)
  return this

class Stats:
  def __init__(i, inits=[],txt="",rank=0): 
    i.n.i.mu,i.m2,i.sd = 0,0,0,0
    i.txt, i.rank = txt,rank
    [i.add(x) for x in inits]
  def add(i, x):
    i.n += 1
    d = x - i.mu
    i.mu += d / i.n
    i.m2 += d * (x - i.mu)
    i.sd = (i.m2 / (i.n - 1))**0.5 if i.n > 1 else 0

def same(xs,ys,cliff,n,conf):
  return cliffs(xs,ys,cliff) and bootstrap(xs,ys,n,conf)

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
def bootstrap(xs, ys, bootstrap,conf):
  "Non-parametric significance test from Chp20,doi.org/10.1201/9780429246593."
  _see = lambda i,j: abs(i.mu - j.mu) / (
                     (i.sd**2/i.n + j.sd**2/j.n)**.5 +1E-32)
  x,y,z = Stats(xs+ys), Stats(xs), Stats(ys)
  yhat  = [y1 - mid(y) + mid(x) for y1 in xs]
  zhat  = [z1 - mid(z) + mid(x) for z1 in ys] 
  n     = 0
  for _ in range(bootstrap):
    n += _see(Stats(random.choices(yhat, k=len(yhat))), 
              Stats(random.choices(zhat, k=len(zhat)))) > _see(y,z) 
  return n / bootstrap >= (1- conf)

def scottKnott(rxs, eps, reverse, *opts):
  "Recurive bi-cluster of treatments. Stops when splits are the same."
  rxs = [(Stats(a,txt=k, rank=0), len(a), sum(a), a) for k,a in rxs.items()]
  rxs.sort(key=lambda x: x[0].mu, reverse=reverse)
  _div(rxs, eps, 0, *opts)
  return {num.txt:num for num,_,_,_ in rxs}

def _div(rxs, eps, rank, *opts):
  "If can cut in two, recuse each side. Else, all have same `rank`."
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
  "Find cut that is maximally different to original."
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
