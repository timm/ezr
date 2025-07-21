"""
FFT Recursive Tree Generator

This script reads tabular data and builds Fast and Frugal Trees
(FFTs) by recursively partitioning the rows based on value splits.
It evaluates and selects the best-performing tree using squared
error on the target column.  The tree is built using minimal code
and a recursive structure, with an emphasis on readability.

Sections:
 1. Imports and Constants
 2. CSV Reader and Coercion 
 3. Data Types and Stats
 4. Data Preparation
 5. Binning and Row Selection 
 6. FFT Tree Builder
 7. FFT Display and Midpoint
 8. Best Tree Selection

Run:
  $ python fft.py [file=path] [depth=4]

Settings:
  file=../moot/optimize/misc/auto93.csv
  depth=4
  seed=1
"""

# 1. Imports and Constants
import random,sys,re
from copy import deepcopy
from types import SimpleNamespace as o

BIG = 1E32

def settings():
  d = {m[1]: coerce(m[2]) for m in re.finditer(r"(\w+)=([^\s]+)", __doc__)}
  for arg in sys.argv[1:]:
    k,v = arg.split("=")
    d[k] = coerce(v)
  return o(**d)

# 2. CSV Reader and Coercion
def coerce(s):
  for fn in [int, float]:
    try: return fn(s)
    except: pass
  s = s.strip()
  return {'True': True, 'False': False}.get(s, s)

def csv(file):
  with open(file) as f:
    for line in f:
      line = line.split("#")[0].strip()
      if line: yield [coerce(s) for s in line.split(",")]

# 3. Data Types and Stats
def isSym(col): return isinstance(col, dict)

def Sym(): return {}

def Num(): return o(lo=BIG, hi=-BIG, mu=0, m2=0, n=0, sd=0)

def add(n,x):
  n.n += 1; d = x - n.mu
  n.mu += d/n.n
  n.m2 += d*(x - n.mu)
  n.sd = (n.m2/(n.n - 1 - 1/BIG))**.5 if n.n > 1 else 0
  n.lo, n.hi = min(x,n.lo), max(x,n.hi)
  return x

# 4. Data Preparation
def _data(names, rows):
  all,x = {},{}
  for c,s in enumerate(names):
    col = Sym() if s[0].islower() else Num()
    for row in rows:
      val = row[c]
      if isSym(col): col[val] = 1 + col.get(val, 0)
      elif val != "?": add(col, val)
    all[c] = col
    if s[-1] != "X": x[c] = col
  return o(names=names, all=all, x=x)

def Data(src):
  src = list(src)
  return o(rows=src[1:], cols=_data(src[0], src[1:]))

def rx(c,rows):
  n = Num()
  for r in rows:
    v = r[c]
    if v != "?": add(n,v)
  return n

# 5. Binning and Row Selection
def bounds(k,col):
  return (k,k) if isSym(col) else (
         (-BIG,col.mu) if k else (col.mu,BIG))

def yesno(rows,c,lo,hi):
  y,n = [],[]
  for r in rows:
    v = r[c]
    (y if v=="?" or lo<=v<=hi else n).append(r)
  return y,n

def bins(col,c,rows):
  b,u = {},[]
  for r in rows:
    v = r[c]
    (u if v=="?" else 
     b.setdefault(v if isSym(col) else v<=col.mu, [])).append(r)
  for k in b: b[k].extend(u)
  return {k:rx(-1,v) for k,v in b.items()}

# 6. FFT Tree Builder
def fft(data, rows=None, depth=4):
  out = []
  rows = rows or data.rows
  def go(rows, d):
    if d == 0 or not rows: return None
    cuts = [(y.mu, c, *bounds(k, col))
            for c, col in data.cols.x.items()
            for k, y in bins(col, c, rows).items()]
    if not cuts: return None
    best, *_, worst = sorted(cuts)
    for mu, c, lo, hi in [best, worst]:
      yes, no = yesno(rows, c, lo, hi)
      leaf = rx(c, yes)
      rest = no
      subtree = go(rest, d - 1)
      node = o(c=c, lo=lo, hi=hi, left=leaf, right=subtree)
      out.append(deepcopy(node))  # Append completed tree

  go(None, rows, depth)
  return out

# 7. FFT Display and Midpoint
def mid(col): return max(col, key=col.get) if isSym(col) else col.mu

def fftShow(data, t, prefix=""):
  if not t: return
  if not hasattr(t, "c"): print(f"{prefix}{mid(t):.2f}")
  else:
    name = data.cols.names[t.c]
    if abs(t.lo) < BIG:
      fftShow(data, t.right, 
              f"{prefix}if {name} < {int(t.lo)} then ")
    if abs(t.hi) < BIG:
      fftShow(data, t.left,  
              f"{prefix}else if {name} >= {int(t.hi)} then ")

# 8. Best Tree Selection
def bestfft(ffts, rows):
  def predict(t,r):
    while hasattr(t, "c"):
      v = r[t.c]
      t = t.left if v=="?" or t.lo <= v <= t.hi else t.right
    return t.mu
  def score(t):
    return sum((r[-1]-predict(t,r))**2 for r in rows)/len(rows)
  return min(ffts, key=score)

# Entry Point
if __name__ == "__main__":
  the = settings()
  random.seed(the.seed)
  data = Data(csv(the.file))
  trees = fft(data, depth=the.depth)
  best = bestfft(trees, data.rows)
  fftShow(data, best)
