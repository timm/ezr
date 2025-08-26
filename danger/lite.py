#!/usr/bin/env python3 -B 
"""
ezr0.py: lightweight incremental multi-objective optimization   
(c) 2025, Tim Menzies <timm@ieee.org>, MIT license   
   
    -A  Any=4              on init, how many initial guesses?   
    -B  Budget=50          when growing theory, how many labels?   
    -D  Delta=smed         required effect size test for cliff's delta
    -F  Few=128            sample size of data random sampling  
    -K  Ks=0.95            confidence for Kolmogorov–Smirnov test
    -p  p=2                distance co-efficient
    -s  seed=1234567891    random number seed   
    -f  file=../../moot/optimize/misc/auto93.csv  data file 
    -h                     show help   
"""
from types import SimpleNamespace as o
from typing import Any,List,Iterator
import random, math, sys, re

the = o(**{k:v for k,v in re.findall(r"(\w+)=(\S+)",__doc__)})

Number = int|float
Atom   = Number|str|bool
Row    = List[Atom]
big    = 1e32

#--------------------------------------------------------------------
def label(row): return row
#--------------------------------------------------------------------
def Num(i=0,s=" "): 
  return o(it=Num, i=i, txt=s, n=0, mu=0, m2=0, sd=0, hi=-big, lo=big,
           more = 0 if s[-1] == "-" else 1)

def Sym(i=0,s=" "): 
  return o(it=Sym, i=i, txt=s, n=0, has={})

def Cols(names : List[str]) -> o:
  all=[(Num if s[0].isupper() else Sym)(c,s) for c,s in enumerate(names)]
  return o(it=Cols, names = names, all = all,
           x = [col for col in all if col.txt[-1] not in "X-+"],
           y = [col for col in all if col.txt[-1] in "-+"])

def Data(src) -> o:
  src = iter(src)
  return adds(src, o(it=Data, n=0, mid=None, rows=[], cols=Cols(next(src))))

def clone(data:Data, rows=None) -> o:
  return adds(rows or [], Data([data.cols.names]))

#--------------------------------------------------------------------
def adds(src, it=None) -> o:
  it = it or Num()
  [add(it,x) for x in src]
  return it

def sub(x:o, v:Any, zap=False) -> Any: 
  return add(x,v,-1,zap)

def add(x: o, v:Any, inc=1, zap=False) -> Any:
  "incrementally update Syms,Nums or Datas"
  if v == "?": return v
  if x.it is Sym: x.has[v] = inc + x.has.get(v,0)
  elif x.it is Num:
    x.n += inc
    x.lo, x.hi = min(v, x.lo), max(v, x.hi)
    if inc < 0 and x.n < 2:
      x.sd = x.m2 = x.mu = x.n = 0
    else:
      d     = v - x.mu
      x.mu += inc * (d / x.n)
      x.m2 += inc * (d * (v - x.mu))
      x.sd  = 0 if x.n < 2 else (max(0,x.m2)/(x.n-1))**.5
  elif x.it is Data:
    x.mid = None
    x.n += inc
    if inc > 0: x.rows += [v]
    elif zap: x.rows.remove(v) # slow for long rows
    [add(col, v[col.i], inc) for col in x.cols.all]
  return v

#--------------------------------------------------------------------
def norm(num:Num, v:float) -> float:  
  return  v if v=="?" else (v - num.lo) / (num.hi - num.lo + 1E-32)

def mids(data: Data) -> Row:
  data.mid = data.mid or [mid(col) for col in data.cols.all]
  return data.mid

def mid(col: o) -> Atom:
  return max(col.has, key=col.has.get) if col.it is Sym else col.mu

#--------------------------------------------------------------------
def dist(src) -> float:
  d,n = 0,0
  for v in src: n,d = n+1, d + v**the.p;
  return (d/n) ** (1/the.p)

def disty(data:Data, row:Row) -> float:
  return dist(abs(norm(c, row[c.i]) - c.more) for c in data.cols.y)

def distysort(data:Data,rows=None) -> List[Row]:
  return sorted(rows or data.rows, key=lambda r: disty(data,r))

def distx(data:Data, row1:Row, row2:Row) -> float:
  def _aha(col, a,b):
    if a==b=="?": return 1
    if col.it is Sym: return a != b
    a,b = norm(col,a), norm(col,b)
    a = a if a != "?" else (0 if b>0.5 else 1)
    b = b if b != "?" else (0 if a>0.5 else 1)
    return abs(a - b)
  return dist(_aha(col, row1[col.i], row2[col.i])  
              for col in data.cols.x)

#--------------------------------------------------------------------
def likely(data:Data, rows=None) -> List[Row]:
  """x,xy = rows with 'x' and 'xy' knowledge.
  Find the thing in x most likely to be best. Add to xy. Repeat."""
  rows = rows or data.rows
  x   = clone(data, shuffle(rows[:]))
  xy, best, rest = clone(data), clone(data), clone(data)

  # label anything
  for _ in range(the.Any): add(xy, label(sub(x, x.rows.pop())))

  # divide lablled items into best and rest
  xy.rows = distysort(xy); n = round(the.Any**.5)
  adds(xy.rows[:n], best); adds(xy.rows[n:], rest)

  # loop, labelling the best guess
  while x.n > 2 and xy.n < the.Budget:
    add(xy, add(best, sub(x, label(guess(xy, best, rest, x)))))
    if best.n > (xy.n**.5):
      best.rows = distysort(xy,best.rows)
      while best.n > (xy.n**.5):
        add(rest, sub(best, best.rows.pop(-1)))
  return distysort(xy)

def guess(xy, best:Data, rest:Data, x:Data) -> Row:
  "Remove from `x' any 1 thing more best-ish than rest-ish."
  for _ in range(the.Few):
    row = x.rows[ i := random.randrange(x.n) ]
    if distx(xy, mids(best), row) < distx(xy, mids(rest), row):
      return x.rows.pop(i)
  return x.rows.pop()

#--------------------------------------------------------------------
def distKpp(data, rows=None, k=20, few=None):
  "Return key centroids usually separated by distance D^2."
  few = few or the.Few
  rows = rows or data.rows[:]
  random.shuffle(rows)
  out = [rows[0]]
  while len(out) < k:
    tmp = random.sample(rows, min(few,len(data.rows)))
    ws  = [min(distx(data, r, c)**2 for c in out) for r in tmp]
    p   = sum(ws) * random.random()
    for j, w in enumerate(ws):
      if (p := p - w) <= 0: 
          out += [tmp[j]]; break
  return out

#--------------------------------------------------------------------
def fyi(s):
  print(s, file=sys.stderr, flush=True, end="")

def atom(s:str) -> o:
  for fn in [int,float]:
    try: return fn(s)
    except Exception as _: pass
  s = s.strip()
  return {'True':True,'False':False}.get(s,s)

def csv(file: str ) -> Iterator[Row]:
  with open(file,encoding="utf-8") as f:
    for line in f:
      if (line := line.split("%")[0]):
        yield [atom(s.strip()) for s in line.split(",")]

def shuffle(lst:List):
  random.shuffle(lst)
  return lst

def main(funs: dict[str,callable]) -> None:
  "from command line, update config find functions to call"
  for n,arg in enumerate(sys.argv):
    if (fn := funs.get(f"eg{arg.replace('-', '_')}")):
      random.seed(the.seed); fn()
    else:
      for key in vars(the):
        if arg=="-"+key[0]: the.__dict__[key] = atom(sys.argv[n+1])

#--------------------------------------------------------------------
def statsSame(x:list[Number], y:list[Number]) -> bool: 
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

  ks    = {0.1:1.22, 0.05:1.36, 0.01:1.63}[round(1 - the.Ks,2)]
  cliffs= {'small':0.11,'smed':0.195,'medium':0.28,'large':0.43}[the.Delta]
  return _cliffs() <= cliffs and _ks() <= ks * ((n + m)/(n * m))**0.5

def statsTop(rxs:dict[str,list[Number]], 
             reverse=False, same=statsSame, eps=0.01) -> set:
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
    if not (cut > 0 and not same(left, right)): break
    its = its[:cut]
  return {k for _, _, k, _ in its}

#--------------------------------------------------------------------
def eg__10(): worker(range(10,11,10))
def eg__20(): worker(range(10,21,10))
def eg__40(): worker(range(10,41,10))
def eg__80(): worker(range(10,81,10))

def worker(budgets, repeats=20):
  data = Data(csv(the.file))
  b4   = adds(disty(data,r) for r in data.rows)
  win  = lambda r: int(100*(1 - (disty(data,r) - b4.lo)/(b4.mu - b4.lo)))
  out  = {}
  for b in budgets:
    fyi(".")
    the.Budget = b
    rxs = dict(rand = lambda: random.sample(data.rows, k=b),
               kpp  = lambda: distKpp(data,            k=b),
               near = lambda: likely(data))
    for k,fun in rxs.items():
      out[f"{k}{b}"] = [win(distysort(data,fun())[0]) for _ in range(repeats)]
  eps  = adds(x for k in out for x in out[k]).sd * 0.35
  best = list(statsTop(out, reverse=True, eps = eps))
  mu   = adds(x for k in best for x in out[k]).mu
  print(int(mu), re.sub(".*/","",the.file), *best, sep=", ")
    
#--------------------------------------------------------------------
for k,v in the.__dict__.items(): the.__dict__[k] = atom(v)
if __name__ == "__main__": main(globals())
