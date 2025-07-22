#!/usr/bin/env python3 -B
"""
fft.py, multi objective tree building   
(c) 2025, Tim Menzies <timm@ieee.org>, MIT license   
   
Options:  
 -s random seed    seed=1234567891    
 -f data file      file=../moot/regression/auto93.csv   
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
BIG = 1e32
def Num(at=0,txt=""): return o(at=at,txt=txt,lo=BIG, hi= -BIG, mu=0, n=0)
def Sym(at=0,txt=""): return o(at=at,txt=txt,has={})
def Data()          : return o(rows=[], cols=[])

def isSym(col): return "has" in col.__dict__
def isData(col): return "rows" in col.__dict__

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
  for x in src: it = it or Num(); add(it,x)
  return it 
  
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
def Tree(data, depth=4):
  def _go(data1, d):  
    sub=False
    if d > 0 and len(data1.rows)>2:
      if cuts := [cut for col in data1.cols.x
                      for cut in treeCuts(data1, col, data1.rows)]:
        best, *_, worst = sorted(cuts)
        for _, c, (xlo, xhi), leaf in [best, worst]:
          yes, no = treeKids(data1.rows, c, xlo, xhi)
          for subtree in _go(dataClone(data1, no), d - 1):
            sub=True
            yield o(c=c, lo=xlo, hi=xhi, left=leaf, right=subtree)
    if not sub:
      yield adds([row[data.cols.klass.at] for row in data1.rows])
  yield from _go(data, depth)

def treeCuts(data, col, rows):
  ys = {}
  for row in rows:
    x, y = row[col.at], row[data.cols.klass.at]
    if x == "?": continue
    k = x if isSym(col) else x <= col.mu  
    if k not in ys: ys[k] = Num()
    add(ys[k], y)
  return [
   (ys[k].mu, # what to sort on
    col.at,        
    (k,k) if isSym(col) else ((-BIG,col.mu) if k else (col.mu,BIG)),
    ys[k]) for k in ys]
 
def treeKids(rows, c, xlo, xhi):
  yes, no, maybe = [], [], []
  for row in rows:
    v=row[c]
    (maybe if v=="?" else yes if xlo <= v <=xhi else no).append(row)
  (yes if len(yes) > len(no) else no).extend(maybe)
  return yes, no

def treeShow(data, t):
  if not hasattr(t, "c"): print(f"{t.mu:.2f}")
  else:
    name = data.cols.all[t.c].txt
    if   t.lo == t.hi:      txt= f"{name} == {t.hi}"
    elif abs(t.lo) == -BIG: txt= f"{name} <= {t.hi:.3f}"
    else:                   txt= f"{name} >= {t.lo:.3f}"
    print(f"if {txt} then {t.left.mu} else")
    treeShow(data,t.right) 

def treeTune(trees, rows):
  def _predict(t, row):
    while hasattr(t, "c"):
      t = t.left if row[t.c]=="?" or t.lo<=row[t.c]<=t.hi else t.right
    return t.mu
  def _score(t):
    return sum((row[-1]-_predict(t,row))**2 for row in rows) / len(rows)
  return min(trees, key=_score)

#---------------------------------------------------------------------
def eg_h(): print(__doc__)

def eg__data():
  for col in dataRead(the.file).cols.all: print(col)

def eg__tune():
  data = dataRead(the.file)
  trees = list(Tree(data))
  best = treeTune(trees, data.rows)
  treeShow(data, best)

if __name__ == "__main__": 
  for n, arg in enumerate(sys.argv):
    for k in the.__dict__:
      if arg == "-" + k[0]: 
        the.__dict__[k] = coerce(sys.argv[n+1])
    if (fn := globals().get(f"eg{arg.replace('-', '_')}")):
      random.seed(the.seed)
      fn() 
