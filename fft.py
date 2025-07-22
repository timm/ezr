#!/usr/bin/env python3 -B
"""
fft.py, multi objective tree building   
(c) 2025, Tim Menzies <timm@ieee.org>, MIT license   
   
Options:  
 -s random seed    seed=1234567891    
 -f data file      file=../moot/optimize/misc/auto93.csv   
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

the = o( **{k: coerce(v) for k,v in re.findall(r"(\w+)=(\S+)", __doc__)} ) 

#----------------------------------------------------------------------------------
BIG = 1e32
def Num(): return o(lo = BIG, hi = -BIG, mu=0, m2=0, n=0, sd=0)
def Sym(): return {}
def isSym(col): return type(col) is dict

def add(col, v):
  if v == "?": return v
  if isSym(col): col[v] = 1 + col.get(v, 0)
  else:
    col.n  += 1
    delta   = v - col.mu
    col.mu += delta / col.n
    col.m2 += delta * (v - col.mu)
    col.lo  = min(col.lo, v)
    col.hi  = max(col.hi, v)
    col.sd  = (col.m2 / (col.n - 1 + 1E-32))**0.5
  return v

#----------------------------------------------------------------------------------
def Data(src=[]):
  data = o(rows=[], cols=None)
  for row in src: dataAdd(data, row)
  return data

def dataAdd(data, row):
  if data.cols : data.rows.append([add(col,row[c]) for c,col in data.cols.all])
  else: data.cols = dataHeader(row)

def dataClone(data, rows=[]):
  return Data([data.cols.names] + rows)

def dataHeader(names):
  cols = o(names=names, all=[], x={}, y={}, klass=None)
  for c,s in enumerate(names):
    cols.all += [Num() if s[0].isupper() else Sym()]
    if s[-1] == "X": continue
    if s[-1] == "!": cols.klass = c
    if s[-1] == "-": cols.all[-1].goal = 0
    (cols.y if s[-1] in "!-+" else cols.x)[c] = cols.all[-1]
  return cols

def dataRead(file):
  data = Data()
  with open(file) as f:
    for line in f:
      line = line.strip()
      if line and not line.startswith("#"):
        dataAdd(data, [coerce(x) for x in line.split(",")])
  return data

#-------------------------------------------------------------------------------
def Tree(data, depth=4):
  def _go(data1, d):  
    if d > 0 and data1.rows:
      if cuts := [cut for c, col in data1.cols.x.items()
                      for cut    in treeCuts(data1, col, c, data1.rows)]:
        best, *_, worst = sorted(cuts)
        for _, c, (xlo, xhi), leaf in [best, worst]:
          yes, no = treeKids(data1.rows, c, xlo, xhi)
          for subtree in _go(dataClone(data1, no), d - 1):
            yield o(c=c, lo=xlo, hi=xhi, left=leaf, right=subtree)
  yield from _go(data, depth)

def treeCuts(data, col, c, rows):
  ys = {}
  for row in rows:
    x, y = row[c], row[data.cols.klass]
    if x == "?": continue
    k = x if isSym(col) else x <= col.mu  
    if k not in ys: ys[k] = Num()
    add(ys[k], y)
  return [(ys[k].mu,
           c,
           (k,k) if isSym(col) else ((-BIG,col.mu) if k else (col.mu,BIG)),
           ys[k]) for k in ys]
 
def treeKids(rows, c, xlo, xhi):
  yes, no, maybe = [], [], []
  for row in rows:
    v=row[c]
    (maybe if v=="?" else yes if xlo <= v <=xhi else no).append(row)
  (yes if len(yes) > len(no) else no).extend(maybe)
  return yes, no

def treeShow(data, t, pre=""):
  if not t: return
  if not hasattr(t, "c"): print(f"{pre}{t.mu:.2f}")
  else:
    name = data.cols.names[t.c]
    if abs(t.lo) < BIG: treeShow(data, t.right, 
                                 f"{pre}if {name} < {int(t.lo)} then ")
    if abs(t.hi) < BIG: treeShow(data, t.left,  
                                 f"{pre}else if {name} >= {int(t.hi)} then ")

def treeTune(trees, rows):
  def _predict(t, row):
    while hasattr(t, "c"):
      t = t.left if row[t.c] == "?" or t.lo <= row[t.c] <= t.hi else t.right
    return t.mu
  def _score(t):
    return sum((r[-1] - _predict(t, row))**2 for row in rows) / len(rows)
  return min(trees, key=_score)

#-------------------------------------------------------------------------------
def eg_h(): print(__doc__)

def eg__eg():
  data = dataRead(file)
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
      fn() $ sddssffsdfsd 
