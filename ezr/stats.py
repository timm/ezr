import random, math
from types import SimpleNamespace as o
Qty  = int|float
Atom = Qty|str|bool
Row  = list[Atom]

def Confuse(): return o(klasses={}, total=0)

def confuse(cf:Confuse, want:str, got:str) -> str:
  for x in (want, got):
    if x not in cf.klasses:
      cf.klasses[x] = o(label=x, tn=cf.total, fn=0, fp=0, tp=0)
  for c in cf.klasses.values():
    if c.label == want: c.tp += got == want;    c.fn += got != want
    else:               c.fp += got == c.label; c.tn += got != c.label
  cf.total += 1
  return got

def confused(cf:Confuse, summary=False):
  p = lambda y,z: int(100*y/(z or 1e-32))
  def finalize(c):
    c.pd, c.prec, c.pf, c.acc = (
      p(c.tp, c.tp+c.fn), p(c.tp, c.fp+c.tp),
      p(c.fp, c.fp+c.tn), p(c.tp+c.tn, c.tp+c.fp+c.fn+c.tn))
    return c
  if summary:
    out = o(label="_OVERALL", tn=0, fn=0, fp=0, tp=0)
    for c in cf.klasses.values():
      for k in "tn fn fp tp".split():
        out.__dict__[k] += finalize(c).__dict__[k]
    return finalize(out)
  return sorted([finalize(v) for v in cf.klasses.values()] + 
                [confused(cf,True)],
                key=lambda c: c.fn + c.tp)

# ------------------------------------------------------------------------------
def same(x:list[Qty], y:list[Qty],Ks=0.95,Delta="smed") -> bool: 
  def _cliffs():
    gt = sum(a > b for a in x for b in y)
    lt = sum(a < b for a in x for b in y)
    return abs(gt - lt) / (n * m)
  
  def _ks():
    xs = sorted(x + y)
    fx = [sum(a <= v for a in x)/n for v in xs]
    fy = [sum(a <= v for a in y)/m for v in xs]
    return max(abs(v1 - v2) for v1, v2 in zip(fx, fy))

  x,y,n,m = sorted(x), sorted(y), len(x), len(y)
  ks      = {0.1:1.22, 0.05:1.36, 0.01:1.63}[round(1 - Ks,2)]
  cliffs  = {'small':0.11,'smed':0.195,'medium':0.28,'large':0.43}[Delta]
  return _cliffs() <= cliffs and _ks() <= ks * ((n + m)/(n * m))**0.5

#------------------------------------------------------------------------------
def top(rxs:dict[str,list[Qty]], 
        reverse=False, same=same, 
        eps=0.01, Ks=.95, Delta="smed") -> set:
  its = sorted([(sum(v)/len(v), len(v),k,v) for k,v in rxs.items() if v], 
               reverse=reverse)
  while len(its) > 1:
    vals = [v for _, _, _, v in its]
    mu = sum(l12 := sum(vals, [])) / len(l12)
    cut, sc, left, right = 0, 0, [], []
    for i in range(1, len(its)):
      l1, l2 = sum(vals[:i], []), sum(vals[i:], [])
      m1, m2 = sum(l1)/len(l1), sum(l2)/len(l2)
      s = (len(l1)*(m1-mu)**2 + len(l2)*(m2-mu)**2) / len(l12)
      if sc < s and abs(m1 - m2) > eps:
        sc, cut, left, right = s, i, l1, l2
    if not (cut > 0 and not same(left,right,Ks=Ks,Delta=Delta)): break
    its = its[:cut]
  return {k for _, _, k, _ in its}

#------------------------------------------------------------------------------
def weibulls(m=20,n=20):
  def weibull(n=100):
    shape, scale = random.uniform(0.5, 3), random.uniform(1, 4)
    return [min(10, scale * (-math.log(random.random())) ** (1/shape) * 2.5) 
            for _ in range(n)]
  return top({x:weibull(n) for x in range(m)})

