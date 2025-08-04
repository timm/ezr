#!/usr/bin/env python3 -B
"""
fft.py, multi objective tree building   
(c) 2025, Tim Menzies <timm@ieee.org>, MIT license   
   
Options:  
 -s  random seed            seed=1234567891    
 -d  depth of tree          depth=5
 -P  number of poles        Poles=20
 -p  distance coeffecient   p=2
 -f  data file              
     file=../moot/optimize/misc/auto93.csv   
"""
from types import SimpleNamespace as o
import random, math, sys, re

def coerce(z):
  try: return int(z)
  except:
    try: return float(z)
    except: 
      z = z.strip()
      return {'True':True, 'False':False}.get(z,z)

the= o(**{k:coerce(v) for k,v in re.findall(r"(\w+)=(\S+)", __doc__)})

#---------------------------------------------------------------------
BIG = 1E30
def Data(): return o(it=Data,rows=[], cols=[])
def Sym(i=0,txt=""): return o(it=Sym,i=i,txt=txt,has={},w=1)
def Num(i=0,txt=" "): return o(it=Num, i=i,txt=txt,lo=BIG,hi=-BIG,
                                mu=0,n=0,m2=0,sd=0,
                                goal=0 if txt[0]=="-" else 1)

def sub(x:o, v:Any, zap=False) -> Any: 
  "subtraction is just adding -1"
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
    x.n += inc
    if inc > 0: x.rows += [v]
    elif zap: x.rows.remove(v) # slow for long rows
    [add(col, v[col.i],inc) for col in x.cols.all]
  return v

def adds(src,it=None):
  it = it or Num()
  for x in src: add(it,x)
  return it 

def norm(col, v): 
  return v if v=="?" or col.it is Sym else (
         (v-col.lo)/(col.hi-col.lo + 1/BIG))
 
#---------------------------------------------------------------------
def dataClone(data, rows=[]):
  return adds([[col.txt for col in data.cols.all]] + rows, Data())

def dataHeader(names):
  cols = o(all=[], x=[], y=[], klass=None)
  for c,s in enumerate(names):
    col = Num(c, s) if s[0].isupper() else Sym(c, s)
    cols.all += [col]
    if s[-1] == "X": continue
    if s[-1] == "!": cols.klass = col
    (cols.y if s[-1] in "!-+" else cols.x).append(col)
  return cols

def dataRead(file):
  data = Data()
  with open(file) as f:
    for line in f:
      line = line.strip()
      if line and not line.startswith("#"):
        add(data, [coerce(x) for x in line.split(",")])
  return data

#---------------------------------------------------------------------
def distPoles(data):
  out, east = [], random.choice(data.rows)
  for _ in range(the.Poles):
    west = random.choice(data.rows)
    out += [(east, west, distx(data,east,west))]
    east = west
  return out

def disty(data,row):
  d = sum(abs(norm(c,row[c.i]) - c.goal)**the.p for c in data.cols.y)
  return (d / len(data.cols.y))**(1/the.p)

def distx(data,r1,r2):
  def _dist(col):
    a = r1[col.i]
    b = r2[col.i]
    if a==b=="?": return 1
    if isSym(col): return a != b
    a,b = norm(col,a), norm(col,b)
    a = a if a != "?" else (0 if b > .5 else 1)
    b = b if b != "?" else (0 if a > .5 else 1)
    return abs(a - b)

  d = sum(_dist(col)**the.p for col in data.cols.x)
  return (d / len(data.cols.x))**(1/the.p)

def distInterpolate(data,row,east,west,c):
  a = distx(data,row,east)
  b = distx(data,row,west)
  x = (a*a + c*c - b*b) / (2*c + 1/BIG) / (c + 1/BIG)
  y1,y2 = disty(data,east), disty(data,west)
  return y1 + x*(y2 - y1)

def distGuessY(data,row,poles): 
  return sum(distInterpolate(data,row,*p) for p in poles) / len(poles)

#---------------------------------------------------------------------
def treeCuts(rows, col, klass):
  return (treeCutsSym if isSym(col) else treeCutsNum)(rows, col, klass)

def treeCutsSym(rows, col, klass):
  buckets = {}
  for r in rows:
    x = r[col.i]
    if x != "?":
      buckets.setdefault(x, []).append(r)
  for sym, bucket in buckets.items():
    mid = distGuessY(bucket)
    yield (mid, col.i, (sym, sym), o(mid=mid, n=len(bucket)))

def treeCutsNum(rows, col, klass, BIG=1e32):
  xrows = sorted((x, r) for r in rows if (x := r[col.i]) != "?")
  n = len(xrows)
  if n < 2:
    return
  xr, xl = Num(), Num()
  for x, _ in xrows: xr.add(x)
  eps, cohen = math.sqrt(n), xr.sd * 0.34
  best = (BIG, None)
  for i, (x, r) in enumerate(xrows[:-1]):
    xr.sub(x); xl.add(x)
    if xl.n > eps and xr.n > eps and abs(xl.mu - xr.mu) >= cohen:
      score = (xl.n * div(xl) + xr.n * div(xr)) / n
      if score < best[0]:
        best = (score, (i, x))
  if best[1]:
    i, x = best[1]
    y1 = distGuessY([r for _, r in xrows[:i]])
    y2 = distGuessY([r for _, r in xrows[i:]])
    yield (y1, col.i, (-BIG, x), o(mid=y1, n=i))
    yield (y2, col.i, (x, BIG), o(mid=y2, n=n - i))


def Tree(data, Guess, depth=the.depth):
  def _go(data1, d):
    sub = False
    if d <= depth:
      cuts = [cut for col in data1.cols.x
                   for cut in treeCuts(data1.rows, col, data1.cols.klass)]
      if cuts:
        best, *_, worst = sorted(cuts)
        for how, (_, c, (lo, hi), leaf) in enumerate([worst, best]):
          yes, no = treeKids(data1.rows, c, lo, hi)
          if len(yes) > len(data.rows) ** .33:
            for subtree in _go(dataClone(data1, no), d + 1):
              sub = True
              yield o(c=c, lo=lo, hi=hi,
                      left=leaf, bias=how, right=subtree)
    if not sub:
      mid = distGuessY(data1.rows)
      yield o(mid=mid, n=len(data1.rows))
  yield from _go(data, 1)

def treeShow(data, t, last=1):
  if not hasattr(t, "c"):
    print(f"{1-last} : {t.n:>4} : {t.mid:.2f}")
  else:
    name = data.cols.all[t.c].txt
    if t.lo == t.hi: txt = f"{name} == {t.hi}"
    elif abs(t.hi) == BIG: txt = f"{name} >= {t.lo:.3f}"
    else: txt = f"{name} <= {t.hi:.3f}"
    print(f"{t.bias} : {t.left.n:>4} : if {txt} then {t.left.mid:.3f} else")
    treeShow(data, t.right, t.bias)


def treeKids(rows, c, xlo, xhi):
  yes, no, maybe = [], [], []
  for row in rows:
    v = row[c]
    (maybe if v == "?" else yes if xlo <= v <= xhi else no).append(row)
  (yes if len(yes) > len(no) else no).extend(maybe)
  return yes, no
def treePredict(t, row):
  while hasattr(t, "c"):
    t = t.left if row[t.c]=="?" or t.lo<=row[t.c]<=t.hi else t.right
  return t.mu

def treeTune(trees, rows, Guess):
  def _score(t): 
    return sum(abs(Guess(r)-treePredict(t,r)) for r in rows)/len(rows)
  return min(trees, key=_score)

#---------------------------------------------------------------------
def eg_h(): print(__doc__)

def eg__data():
  for col in dataRead(the.file).cols.all: print(col)

def eg__tune():
  data = dataRead(the.file)
  poles = distPoles(data)
  Guess = lambda row: distGuessY(data, row, poles)
  trees = list(Tree(data,Guess))
  best = treeTune(trees,data.rows,Guess)
  treeShow(data,best)

def eg__tunes():
  d0 = dataRead(the.file)
  poles = distPoles(d0)
  Guess = lambda row: distGuessY(d0, row, poles)

  Y = lambda row: disty(d0, row)
  stats = adds([Y(r) for r in d0.rows])

  n = len(d0.rows)//2
  rand, fft = Num(), Num()
  for _ in range(20):
    random.shuffle(d0.rows)
    add(rand, Y(sorted(d0.rows[:10], key=Y)[0]))
    train, test = dataClone(d0, d0.rows[:n]), dataClone(d0, d0.rows[n:])
    trees = list(Tree(train, Guess))
    best = treeTune(trees, train.rows, Guess)
    rows = sorted(test.rows, key=lambda r: treePredict(best, r))[:10]
    add(fft, Y(sorted(rows, key=Y)[0]))

  winFft  = 1 - (fft.mu - stats.lo) / (stats.mu - stats.lo)
  winRand = 1 - (rand.mu - stats.lo) / (stats.mu - stats.lo)
  print(f"mu0 {stats.mu:.2f} lo {stats.lo:.2f} out {fft.mu:.2f} winF {winFft:.2f}",end="")
  print(f" muF {fft.mu:.2f} winR {winRand:.2f} muR {rand.mu:.2f}",the.file)

if __name__ == "__main__": 
  for n, arg in enumerate(sys.argv):
    for k in the.__dict__:
      if arg == "-" + k[0]: 
        the.__dict__[k] = coerce(sys.argv[n+1])
    if (fn := globals().get(f"eg{arg.replace('-', '_')}")):
      random.seed(the.seed)
      fn() 
