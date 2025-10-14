#!/usr/bin/env python3 -B 
from math import sqrt, exp, log
import traceback, fileinput, random, time, sys, re

class obj(dict):
    __getattr__ = dict.__getitem__;
    __setattr__ = dict.__setitem__
    __repr__    = lambda i: o(i)

the=obj(Budget=30, Check=5, Delta='smed', Ks=.95, seed=42, p=2,
        file="../../moot/optimize/misc/auto93.csv")

BIG = 1e32

### Constructors ------------------------------------------------------
def Num(at=0,s=" "): return obj(it=Num, at=at, txt=s, n=0, mu=0, m2=0, sd=0, 
                                lo=BIG, hi=-BIG, best=s[-1] != "-")

def Sym(at=0,s=" "): return obj(it=Sym, at=at, txt=s, n=0, has={})

def Cols(names):
  all = [(Num if s[0].isupper() else Sym)(i,s) for i,s in enumerate(names)]
  return obj(it=Cols, names=names, all=all,
             y = [col for col in all if col.txt[-1]     in "-+"],
             x = [col for col in all if col.txt[-1] not in "-+X"])

def Data(src):
  src = iter(src)
  return adds(src, obj(it=Data, n=0, rows=[], cols=Cols(next(src)))) 

def clone(data:Data, rows=None):
  return adds(rows or [], Data([data.cols.names]))

### Update -----------------------------------------------------------
def adds(src, it=None):
  it = it or Num()
  [add(it,x) for x in src]
  return it

def add(x, v):
  if v == "?": return v
  x.n += 1
  if x.it is Sym: 
    x.has[v] = 1 + x.has.get(v,0)
  elif x.it is Num:
    x.lo, x.hi = min(v, x.lo), max(v, x.hi)
    d     = v - x.mu
    x.mu += 1 * (d / x.n)
    x.m2 += 1 * (d * (v - x.mu))
    x.sd  = 0 if x.n < 2 else (max(0,x.m2)/(x.n-1))**.5
  elif x.it is Data:
    x.rows += [v]
    [add(col, v[col.at]) for col in x.cols.all]

# ## Misc data functions ----------------------------------------------
# ## Misc data functions ----------------------------------------------
def norm(num:Num, v:float) -> float:  
  "Normalize a value to 0..1 range"
  return  v if v=="?" else (v - num.lo) / (num.hi - num.lo + 1E-32)

# ## Distance Calcs ---------------------------------------------------
def dist(src):
  d,n = 0,1/BIG
  for v in src: n,d = n+1, d + v**the.p;
  return (d/n) ** (1/the.p)

def disty(data, row):
  return dist(abs(norm(c, row[c.at]) - c.best) for c in data.cols.y)

def distx(data, row1, row2):
  def fn(col, a,b):
    if a==b=="?": return 1
    if col.it is Sym: return a != b
    a,b = norm(col,a), norm(col,b)
    a = a if a != "?" else (0 if b>0.5 else 1)
    b = b if b != "?" else (0 if a>0.5 else 1)
    return abs(a - b)
  return dist(fn(c, row1[c.at], row2[c.at])  for c in data.cols.x)

### Rule Generation ----------------------------------------------------
def selects(row, op, at, y): 
  if (x:=row[at]) == "?" : return True
  if op == "<="          : return x <= y
  if op == "=="          : return x == y
  if op == ">"           : return x > y

def main(data):
  n = len(data.rows)//2
  train, holdout = data.rows[:n], data.rows[n:]
  model = rules(data, train, int(sqrt(len(train))))

def rules(data,rows,n):
  Y = lambda r: disty(data,r)
  rows.sort(key=Y)
  best,rest = clone(data, rows[:n]), clone(data,rows[n:])
  for i,j in zip(best.cols.x, rest.cols.x):
    print((bestSym if i.it is Sym else bestNum)(i,j),i.at,i.txt)

def bestSym(i, j):
  n = i.n + j.n
  return max(((i.has.get(k,0) - j.has.get(k,0))/n, k, k)
             for k in (i.has | j.has))[1:]

def bestNum(i, j):
  assert i.mu < j.mu, f"bad range"
  x = (i.mu + j.mu) / 2
  if i.mu + 3*i.sd >= j.mu - 3*j.sd:  # triangles overlap
    h_i = 1 / (i.sd * sqrt(2 * 3.14159)) # max height of i (at mu)
    h_j = 1 / (j.sd * sqrt(2 * 3.14159)) # max height of j (at mu)
    m_i = -h_i / (3*i.sd) # rise/run
    m_j =  h_j / (3*j.sd) # rise/run
    # where the falling line from i's peak meets the rising line to j's peak.
    tmp = (m_i*i.mu - h_i - m_j*(j.mu - 3*j.sd)) / (m_i - m_j)
    if i.mu <= tmp <= j.mu:
      x = tmp
  return 1/(1 + exp(-1.704*(x - i.mu)/i.sd)),  -BIG, x
 
#------------------------------------------------------------------------------
def csv(file=None):
  for line in fileinput.input(files=file if file else '-'):
    if (line := line.split("%")[0]):
      yield [coerce(s.strip()) for s in line.split(",")]

def coerce(s):
  try: return int(s)
  except:
    try: return float(s)
    except: return {'True':True, 'False':False}.get(s,s)

def oo(x): print(o(x)); return x

def o(x):
  it = type(x)
  if callable(x)   : x= x.__name__
  elif it is float : x= int(x) if x % 1 == 0 else round(x,3)
  elif it is obj   : x= "{"+" ".join(f":{k} {o(x[k])}" for k in x)+"}"
  return str(x)

def same(x, y,Ks=0.95,Delta="smed"): 
  "True if x,y indistinguishable and differ by just a small effect."
  x, y = sorted(x), sorted(y)
  n, m = len(x), len(y)
  def _cliffs():  # How frequently are x items are gt,lt than y items?
    gt = sum(a > b for a in x for b in y)
    lt = sum(a < b for a in x for b in y)
    return abs(gt - lt) / (n * m)
  def _ks(): # Return max distance between cdf.
    xs = sorted(x + y)
    fx = [sum(a <= v for a in x)/n for v in xs]
    fy = [sum(a <= v for a in y)/m for v in xs]
    return max(abs(v1 - v2) for v1, v2 in zip(fx, fy))
  ks    = {0.1:1.22, 0.05:1.36, 0.01:1.63}[round(1 - Ks,2)]
  cliffs= {'small':0.11,'smed':0.195,'medium':0.28,'large':0.43}[Delta]
  return _cliffs() <= cliffs and _ks() <= ks * ((n + m)/(n * m))**0.5

#------------------------------------------------------------------------------
random.seed(the.seed)
if __name__=="__main__" and len(sys.argv) > 1:
  if __name__ == "__main__" and len(sys.argv) > 1:
    for n, s in enumerate(sys.argv):
      for key in vars(the):
        if s[0] == "-" and s == f"-{key[0]}":
          the[key] = coerce(sys.argv[n+1])
  main(Data(csv(the.file)))
