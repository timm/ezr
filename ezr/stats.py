#!/usr/bin/env python3 -B
from ezr.lib import *

#--------------------------------------------------------------------
def Confuse(): 
  "Create a confusion stats for classification matrix."
  return o(klasses={}, total=0)

def confuse(cf:Confuse, want:str, got:str) -> str:
  "Update the confusion matrix."
  for x in (want, got):
    if x not in cf.klasses: 
      cf.klasses[x] = o(label=x,tn=cf.total,fn=0,fp=0,tp=0)
  for c in cf.klasses.values():
    if c.label==want: c.tp += (got==want);    c.fn += (got != want)
    else            : c.fp += (got==c.label); c.tn += (got != c.label)
  cf.total += 1
  return got

def confused(cf:Confuse, summary=False) -> List[Confuse]:
  "Report confusion metric statistics."
  p = lambda y, z: round(100 * y / (z or 1e-32), 0)  # one decimal
  def finalize(c):
    c.pd   = p(c.tp, c.tp + c.fn)
    c.prec = p(c.tp, c.fp + c.tp)
    c.pf   = p(c.fp, c.fp + c.tn)
    c.acc  = p(c.tp + c.tn, c.tp + c.fp + c.fn + c.tn)
    return c

  if summary:
    out = o(label="_OVERALL", tn=0, fn=0, fp=0, tp=0)
    for c in cf.klasses.values():
      c = finalize(c)
      for k in ["tn", "fn", "fp", "tp"]:
        setattr(out, k, getattr(out, k) + getattr(c, k))
    return finalize(out)
  [finalize(v) for v in cf.klasses.values()]
  return sorted(list(cf.klasses.values()) + 
                [confused(cf, summary=True)],
                key=lambda cf: cf.fn + cf.tp)

#--------------------------------------------------------------------
# While ks_code is elegant (IMHO), its slow for large samples. That
# said, it is nearly instantaneous  for the typical 20*20 cases.

def statsSame(x:list[Number], y:list[Number], 
              ks=the.Ks, cliffs=the.Delta) -> bool:
  "True if x,y indistinguishable and differ by just a small effect."
  x, y = sorted(x), sorted(y)
  n, m = len(x), len(y)

  def _cliffs():
    "How frequently are x items are gt,lt than y items?"
    gt = sum(a > b for a in x for b in y)
    lt = sum(a < b for a in x for b in y)
    return abs(gt - lt) / (n * m)

  def _ks():
    "Return max distance between cdf."
    xs = sorted(x + y)
    fx = [sum(a <= v for a in x)/n for v in xs]
    fy = [sum(a <= v for a in y)/m for v in xs]
    return max(abs(v1 - v2) for v1, v2 in zip(fx, fy))

  ks    = {0.1:1.22, 0.05:1.36, 0.01:1.63}[round(1 - ks,2)]
  cliffs= {'small':0.11,'smed':0.195,'medium':0.28,'large':0.43}[cliffs]
  return _cliffs() <= cliffs and _ks() <= ks * ((n + m)/(n * m))**0.5

def statsTop(rxs:dict[str,list[Number]], 
                       reverse=False, same=statsSame, eps=0.01) -> set:
  "return the keys of the top-ranked treatments"
  items = sorted(((sum(v)/len(v), k, v) for k,v in rxs.items() if v), 
                 reverse=reverse)
  m, k, vs = items[0]
  out = {k}
  for m1, k1, vs1 in items[1:]:
    if not same(vs, vs1) or abs(m1 - m) > eps: break
    n, n1 = len(vs), len(vs1)
    m = (m*n + m1*n1)/(n + n1)
    vs += vs1
    out.add(k1)
  return out

def statsRank(rxs:dict[str,list[Number]], 
              reverse=False,same=statsSame, eps=0.01) -> dict[str,str]:
  "Sort rxs, recursively split them, stopping when two splits are same."
  # keep per-group mean m and size n; no need to store sum(vs)
  items = [(sum(vs)/len(vs), k, vs, len(vs)) for k, vs in rxs.items() if vs]
  return _statsDiv(sorted(items, reverse=reverse), same, {}, eps, rank=1)[1]

def _statsDiv(groups, same, out, eps, rank=1):
  "Cut and recurse (if we find a cut). Else, use rank=rank, then inc rank."
  def flat(lst): return [x for _, _, xs, _ in lst for x in xs]  # xs is at index 2 now
  cut = _statsCut(groups, eps)
  if cut and not same(flat(groups[:cut]), flat(groups[cut:])):
    return _statsDiv(groups[cut:], same, out, eps,
                     rank=_statsDiv(groups[:cut], same, out, eps, rank)[0])
  for _, k, _, _ in groups: out[k] = rank
  return rank + 1, out

def _statsCut(groups, eps):
  "Cut to maximize difference in means (if cuts differ by more than eps)."
  # totals via m*n (no stored sums needed)
  sum1 = sum(m * n for m, _, _, n in groups)
  n1   = sum(n for _, _, _, n in groups)
  mu   = sum1 / n1
  best = sum0 = n0 = score = 0
  for j, (m, _, _, n) in enumerate(groups[:-1]):
    sum0 += m * n; n0 += n
    sum1 -= m * n; n1 -= n
    mu0, mu1 = sum0 / n0, sum1 / n1
    now = n0 * (mu0 - mu)**2 + n1 * (mu1 - mu)**2
    if abs(mu0 - mu1) > eps and now > score:
      score, best = now, j + 1
  return best

#--------------------------------------------------------------------
def eg__confuse():
  "Stats: discrete calcs for recall, precision etc.."
  # a b c <- got
  # ------. want
  # 5 1   | a
  #   2 1 | b
  #     3 | c
  cf = Confuse()   
  for want,got,n in [
      ("a","a",5),("a","b",1),("b","b",2),("b","c",1),("c","c",3)]:
    for _ in range(n): confuse(cf, want, got)
  xpect = {"a": {'pd':83,  'acc':92, 'pf':0,  'prec':100},
           "b": {'pd':67,  'acc':83, 'pf':11, 'prec':67},
           "c": {'pd':100, 'acc':92, 'pf':11, 'prec':75} }
  for y in confused(cf):
    if y.label != "_OVERALL":
       got = {'pd':y.pd, 'acc':y.acc, 'pf':y.pf, 'prec':y.prec}
       assert xpect[y.label] == got
  [pout(x) for x in confused(cf)]

def eg__stats():
   "Stats: numeric (effect size and significance tests)."
   b4 = [random.gauss(1,1)+ random.gauss(10,2)**0.5
         for _ in range(20)]
   d, out = 0,[]
   while d < 2:
     now = [x+d*random.random() for x in b4]
     out += [f"{d:.2f}" + ("y" if statsSame(b4,now) else "n")]
     d += 0.1
   [print(x) for x in out]

def eg__sk20():
  "Stats: Checking rankings of 20 treatmeents, for increaseing sd"
  def daRx(t):
    if not isinstance(t,(tuple,list)): return str(t)
    return ':'.join(str(x) for x in t)
  n=20
  for sd in [0.1,1,10]:
    for eps in [1E-32,0.05,0.1,0.15,0.2]:
      print("\neps=",eps, "sd=",sd)
      rxs={}
      G=lambda m:[random.gauss(m,sd) for _ in range(n)]
      for i in range(20): 
        if   i<=  4 : rxs[chr(97+i)] = G(10)
        elif i <= 8 : rxs[chr(97+i)] = G(11)
        elif i <=12 : rxs[chr(97+i)] = G(12)
        elif i <=16 : rxs[chr(97+i)] = G(12)
        else        : rxs[chr(97+i)] = G(14)
      out = statsRank(rxs,eps=eps)
      top = ''.join(list(statsTop(rxs,eps=sd*0.35)))
      print("\t",top)
      print("\t",''.join(map(daRx,out.keys())))
      print("\t",''.join([str(x) for x in out.values()]))
