
from types import SimpleNamespace as o
import random, math

#----------------------------------------------------------------------------------
BIG = 1e32
def Num(): return o(lo=BIG, hi=-BIG, mu=0, m2=0, n=0, sd=0)
def Sym(): return {}
def isSym(col): return type(col) is dict

def add(col, x):
  if isSym(col): col[x] = 1 + col.get(x, 0)
  elif x != "?":
    col.n += 1
    delta = x - col.mu
    col.mu += delta / col.n
    col.m2 += delta * (x - col.mu)
    col.lo = min(col.lo, x)
    col.hi = max(col.hi, x)
    col.sd = (col.m2 / (col.n - 1 + 1E-32))**0.5

#----------------------------------------------------------------------------------
def Data(src):
   names, *rows = list(src)
   return o(rows=rows, cols=Cols(names,rows))

def Cols(names, rows):
  all, x = {}, {}
  for c, s in enumerate(names):
    col = Sym() if s[0].islower() else Num()
    for r in rows: add(col, r[c])
    all[c] = col
    if s[-1] != "X": x[c] = col
  return o(names=names, all=all, x=x)

#----------------------------------------------------------------------------------
def Tree(data, rows=None, depth=4):
  def go(rows, d):
    if d > 0 and rows:
      if (cuts := [(y.mu, c, *treeBounds(k, col))
                       for c, col in data.cols.x.items()
                       for k, y in treeBins(col, c, rows).items()]):
        best, *_, worst = sorted(cuts)
        for mu, c, lo, hi in [best, worst]:
          yes, no = treeCuts(rows, c, lo, hi)
          leaf = rx(c, yes)
          for subtree in go(no, d - 1):
            yield o(c=c, lo=lo, hi=hi, left=leaf, right=subtree)
  yield from go(rows or data.rows, depth)

def treeBins(col, c, rows):
  out = {}
  for r in rows:
    x = r[c]
    if x != "?":
      k = x if isSym(col) else ("lo" if x < col.mu else "hi")
      out.setdefault(k, []).append(r)
  return {k: rx(c, v) for k, v in out.items()}

def treeCuts(rows, c, lo, hi):
  yes, no = [], []
  for r in rows:
    v = r[c]
    (yes if v == "?" or lo <= v <= hi else no).append(r)
  return yes, no

def treeBounds(k, col):
  return (-BIG, BIG) if isSym(col) else (k, k)

def rx(c, rows):
  col = Num()
  for r in rows:
    x = r[c]
    if x != "?": add(col, x)
  return col

def treeShow(data, t, pre=""):
  if not t: return
  if not hasattr(t, "c"): print(f"{pre}{t.mu:.2f}")
  else:
    name = data.cols.names[t.c]
    if abs(t.lo) < BIG: treeShow(data, t.right, f"{pre}if {name} < {int(t.lo)} then ")
    if abs(t.hi) < BIG: treeShow(data, t.left,  f"{pre}else if {name} >= {int(t.hi)} then ")

def treeBest(trees, rows):
  def predict(t, r):
    while hasattr(t, "c"):
      v = r[t.c]
      t = t.left if v == "?" or t.lo <= v <= t.hi else t.right
    return t.mu
  def score(t):
    return sum((r[-1] - predict(t, r))**2 for r in rows) / len(rows)
  return min(trees, key=score)

#----------------------------------------------------------------------------------
def csv(file):
  with open(file) as f:
    for line in f:
      line = line.strip()
      if line and not line.startswith("#"):
        yield [coerce(x) for x in line.split(",")]

def coerce(x):
  try: return int(x)
  except:
    try: return float(x)
    except: return x.strip()

#----------------------------------------------------------------------------------
if __name__ == "__main__":
  import sys
  random.seed(1)
  file = sys.argv[1] if len(sys.argv) > 1 else "../data/auto93.csv"
  data = Data(csv(file))
  trees = list(Tree(data))
  best = treeBest(trees, data.rows)
  treeShow(data, best)

