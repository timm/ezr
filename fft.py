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
def Data(): return o(rows=[], cols=[])
def Sym(at=0,txt=""): return o(at=at,txt=txt,has={},w=1)
def Num(at=0,txt=" "): return o(at=at,txt=txt,lo=BIG,hi=-BIG,
                                mu=0,n=0,goal=0 if txt[0]=="-" else 1)

def isNum(col) : return hasattr(col, "mu") 
def isSym(col) : return hasattr(col, "has")
def isData(col): return hasattr(col, "rows")

def add(it, v):
  if v=="?": return v
  if isSym(it): it.has[v] = 1 + it.has.get(v, 0)
  elif isData(it):
    if it.cols: it.rows.append([add(c,v[c.at]) for c in it.cols.all])
    else: it.cols = dataHeader(v)
  else:
    it.n  += 1
    delta   = v - it.mu
    it.mu += delta / it.n
    it.lo  = min(it.lo, v)
    it.hi  = max(it.hi, v)
  return v

def adds(src,it=None):
  it = it or Num()
  for x in src: add(it,x)
  return it 

def norm(col, v): 
  return v if v=="?" or type(col) is Sym else (
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
  d = sum(abs(norm(c,row[c.at]) - c.goal)**the.p for c in data.cols.y)
  return (d / len(data.cols.y))**(1/the.p)

def distx(data,r1,r2):
  def _dist(col):
    a = r1[col.at]
    b = r2[col.at]
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
def Tree(data, Guess, depth=the.depth):
  def _go(data1, d):  
    sub = False
    if d <= depth:
      if cuts := [cut for col in data1.cols.x 
                  for cut in treeCuts(data1, col, data1.rows, Guess)]:
        best, *_, worst = sorted(cuts)
        for how, (_, c, (xlo, xhi), leaf) in enumerate([worst, best]):
          yes, no = treeKids(data1.rows, c, xlo, xhi)
          if len(yes) > len(data.rows)**.33:
            for subtree in _go(dataClone(data1, no), d + 1):
              sub = True
              yield o(c=c, lo=xlo, hi=xhi, left=leaf, 
                           bias=how, right=subtree)
    if not sub:
      yield adds([Guess(row) for row in data1.rows])
  yield from _go(data, 1)

def treeCuts(data, col, rows, Guess):
  ys = {}
  for row in rows:
    x, y = row[col.at], Guess(row)
    if x == "?": continue
    k = x if isSym(col) else x <= col.mu  
    if k not in ys: ys[k] = Num()
    add(ys[k], y)
  return [
    (ys[k].mu, 
     col.at,
     (k,k) if isSym(col) else ((-BIG,col.mu) if k else (col.mu,BIG)),
     ys[k]) for k in ys]

def treeKids(rows, c, xlo, xhi):
  yes, no, maybe = [], [], []
  for row in rows:
    v = row[c]
    (maybe if v == "?" else yes if xlo <= v <= xhi else no).append(row)
  (yes if len(yes) > len(no) else no).extend(maybe)
  return yes, no

def treeShow(data, t, last=1):
  if not hasattr(t, "c"): print(f"{1-last} : {t.n:>4} : {t.mu:.2f}")
  else:
    name = data.cols.all[t.c].txt
    if   t.lo == t.hi:      txt = f"{name} == {t.hi}"
    elif abs(t.hi) == BIG:  txt = f"{name} >= {t.lo:.3f}"
    else:                   txt = f"{name} <= {t.hi:.3f}"
    print(f"{t.bias} : {t.left.n:>4} : ", end="")
    print(f"if {txt} then {t.left.mu:.3f} else")
    treeShow(data, t.right, t.bias)

def treePredict(t, row):
  while hasattr(t, "c"):
    t = t.left if row[t.c]=="?" or t.lo<=row[t.c]<=t.hi else t.right
  return t.mu

def treeTune(trees, rows, Guess):
  def _score(t): 
    return sum(abs(Guess(r)-treePredict(t,r)) for r in rows)/len(rows)
  return min(trees, key=_score)

# def Tree(data, depth=the.depth):
#   def _go(data1, d):  
#     sub=False
#     if d <= the.depth :
#       if cuts := [cut for col in data1.cols.x
#                       for cut in treeCuts(data1, col, data1.rows)]:
#         best, *_, worst = sorted(cuts)
#         for how,(_, c, (xlo, xhi), leaf) in enumerate([worst,best]):
#           yes, no = treeKids(data1.rows, c, xlo, xhi)
#           if len(yes) > len(data.rows)**.33:
#             for subtree in _go(dataClone(data1, no), d + 1):
#               sub=True
#               yield o(c=c, lo=xlo, hi=xhi, left=leaf,
#                       bias=how,right=subtree)
#     if not sub:
#       yield adds([row[data.cols.klass.at] for row in data1.rows])
#   yield from _go(data, 1)
#
# def treeCuts(data, col, rows):
#   ys = {}
#   for row in rows:
#     x, y = row[col.at], row[data.cols.klass.at]
#     if x == "?": continue
#     k = x if isSym(col) else x <= col.mu  
#     if k not in ys: ys[k] = Num()
#     add(ys[k], y)
#   return [
#    (ys[k].mu, # what to sort on
#     col.at,        
#     (k,k) if isSym(col) else ((-BIG,col.mu) if k else (col.mu,BIG)),
#     ys[k]) for k in ys]
#
# def treeKids(rows, c, xlo, xhi):
#   yes, no, maybe = [], [], []
#   for row in rows:
#     v=row[c]
#     (maybe if v=="?" else yes if xlo <= v <=xhi else no).append(row)
#   (yes if len(yes) > len(no) else no).extend(maybe)
#   return yes, no
#
# def treeShow(data, t,last=1):
#   if not hasattr(t, "c"): print(f"{1-last} : {t.n:>4} : {t.mu:.2f}")
#   else:
#     name = data.cols.all[t.c].txt
#     if   t.lo == t.hi:      txt= f"{name} == {t.hi}"
#     elif abs(t.hi) == BIG : txt= f"{name} >= {t.lo:.3f}"
#     else:                   txt= f"{name} <= {t.hi:.3f}"
#     print(f"{t.bias} : {t.left.n:>4} : if {txt} then {t.left.mu:.3f} else")
#     treeShow(data,t.right,t.bias) 
#
# def treePredict(t, row):
#   while hasattr(t, "c"):
#     t = t.left if row[t.c]=="?" or t.lo<=row[t.c]<=t.hi else t.right
#   return t.mu
#
# def treeTune(trees, rows):
#   def _score(t):
#     return sum(abs(row[-1]-treePredict(t,row)) for row in rows) / len(rows)
#   return min(trees, key=_score)
#
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
