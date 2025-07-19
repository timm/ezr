#!/usr/bin/env python3 -B
import random, sys
from math import log
from types import SimpleNamespace as o

BIG = 1e32
Sym = dict
def Num(): return o(lo=BIG, hi=-BIG,mu=0,m2=0,n=0,sd=0) 

the = o(bins=7,
        p=2, 
        Projections=8, 
        seed=1234567890, 
        file="../moot/optimize/misc/auto93.csv")

def Data(src):
  head, *rows = list(src)
  data  = _data(head, rows)
  poles = projections(data)
  for row in rows: 
    row[-1] = sum(interpolate(data,row,*pole) for pole in poles)/len(poles)
  return data

def _data(names,rows):
  w,x,y,all = {},{},{},{}
  for c, s in enumerate(names):
    col = Sym if s[0].islower() else Num)()
    [add(col,v) for row in rows if (v:=row[c]) != "?"]
    all[c] = col
    if s[-1] != "X":
      w[c] = s[-1] == "+"
      (y if s[-1] in "!+-" else x)[c] = col 
  return o(rows=rows, cols=o(names=names, w=w, x=x, y=y, all=all))

def add(col, v):
  if type(col) is Sym: col[v] = 1 + col.get(v,0)
  else:
    v       = float(v)
    col.n  += 1
    d       = v - col.mu
    col.mu += 1 * (d / col.n)
    col.m2 += 1 * (d * (v - col.mu))
    col.sd  = (col.m2/(col.n - 1 - 1/BIG))**.5
    col.lo  = min(v, col.lo)
    col.hi  = max(v, col.hi)
  return v

def size(col): return sum(col.values()) if type(col) is Sym else col.n 
def mid(col) : return mode(col          if type(col) is Sym else col.mu 
def div(col):  return ent(col)          if type(col) is Sym else col.sd

def mode(d): return max(d, key=d.get)
def ent(d) : N=size(); return -sum(p*log(p,2) for n in d.values() if (p:=n/N)>0)

#------------------------------------------------------------------------------
def minkowski(src):
  d,n = 0,0
  for v in src: n,d = n+1, d + v**the.p
  return (d/n) ** (1/the.p)

def ydist(data,row):
  return minkowski(abs(norm(row[y], *col) - data.cols.w[y]) 
                   for y,col in data.cols.y.items())

def xdist(data, row1, row2):
  return minkowski(_xdist(row1[x], row2[x], col) 
                   for x,col in data.cols.x.items())
   
def _xdist(x1, x2, col):
  if x1==x2=="?": return 1
  if type(col) is Sym: return x1 != x2
  x1,x2 = norm(x1,*col), norm(x2,*col)
  x1    = x1 if x1 != "?" else (0 if x2>0.5 else 1)
  x2    = x2 if x2 != "?" else (0 if x1>0.5 else 1)
  return abs(x1-x2)

def norm(x,lo,hi): 
  return (x - lo) / (hi - lo + 1/BIG)

def cosine(data,row,best,rest,c):
  a,b = xdist(data, row, best), xdist(data, row, rest)
  return (a*a + c*c - b*b)/(2*c + 1/BIG)

def interpolate(data,row,best,rest,c):
  x = cosine(data,row,best,rest,c) 
  y1,y2 = ydist(data,best), ydist(data,rest)
  return y1 + x/c * (y2-y1) 

def projections(data):
  poles = []
  for _ in range(the.Projections):
    best,rest = random.sample(data.rows, k=2)
    if ydist(data,best) > ydist(data,rest):
      best,rest = rest,best
    poles += [(best, rest, xdist(data,best, rest))]
  return poles

#------------------------------------------------------------------------------
def rx(c, rows):
  out = Num(); [add(out, row[c]) for row in rows if row[c] != "?"]; return out.mu

def selects(rows, c, lo, hi):
  yes, no = [], []
  for row in rows:
    v = row[c]
    if v == "?" or lo <= v <= hi: yes.append(row)
    if v == "?" or not (lo <= v <= hi): no.append(row)
  return yes, no

def fft(data, rows, depth=4):
  if depth > 0 and rows:
    if (cuts := [cut for c, col in data.cols.x.items() 
                 for cut in fftCuts(col, c, rows, type(col) is Sym)]):
      best, *_, worst = sorted(cuts)
      yield _fftRecurse(data, rows, depth, True, *best)
      yield _fftRecurse(data, rows, depth, False,*worst)

def fftCuts(col, c, rows, sym):
  bins, unknowns = {}, []
  for row in rows:
    v = row[c]
    if v == "?": unknowns.append(row); continue
    k =v if sym else v <= col.mu
    bins[k] = bins.get(k) or Num()
    add(bins[k], row[-1])
  [add(bin, row[-1]) for row in unknowns for bin in bins.values()]
  for k, y in bins.items():
    if sym: lo = hi = k
    else:   lo, hi = (-BIG, col.mu) if k else (col.mu, BIG)
    yield (y.mu, c,lo,hi)

def _fftRecurse(data, rows, depth, exiting, mu,c,lo,hi):
  mu, c, lo, hi = cut
  yes, no = selects(rows, c, lo, hi)
  leaf = o(stats=rx(c, yes if exiting else no))
  rest = no if exiting else yes
  if depth == 1: return leaf
  return o(c=c, lo=lo, hi=hi, left=leaf, right=fft(data, rest, depth - 1))

def predict(t, row):
  while hasattr(t, "c"):
    v = row[t.c]
    t = t.left        if v == "?" or t.lo <= v <= t.hi else (
        next(t.right) if hasattr(t.right, "__iter__")  else t.right)
  return t.stats

def showFFT(t, lvl=0):
  if not hasattr(t, "c"): return print("  " * lvl + f"=> {t.stats:.2f}")
  print("  " * lvl + f"if {t.c} in [{t.lo:.2f}, {t.hi:.2f}] then")
  showFFT(t.left, lvl + 1)
  print("  " * lvl + "else")
  for r in (t.right if hasattr(t.right, "__iter__") else [t.right]):
    showFFT(r, lvl + 1)

   """
x<1  x>1          y==a y==b y==c
10   1              3   8    20

worst split  y==c
best split x>1

exit on worst = 0
exit on best = 0

left is alwaus e xit.
"""
def csv(file):
  n = -1
  with open(file,encoding="utf-8") as f:
    for line in f:
      if (line := line.split("%")[0]):
        n += 1
        suffix = "scoreX" if n==0 else 0
        yield [s.strip() for s in line.split(",")] + [suffix]

r3=lambda n:round(n,3)

def eg__the(): print(the)

def eg__xdata(): 
  data = Data(csv(the.file))
  print(sorted([r3(xdist(data,r,data.rows[0])) for r in data.rows])[::10])
  print(sorted([r3(ydist(data,r)) for r in data.rows])[::10])

def eg__data(): 
  for p in [1,2,4,8]:
    the.Projections = p
    data = Data(csv(the.file))
    gy = [(row[-1],ydist(data,row)) for row in data.rows]
    r=0
    for _ in range(1000):
      a =random.choice(gy)
      b =random.choice(gy)
      if a[0] > b[0]: a,b=b,a
      r += a[1] < b[1]
    print(f"{r/1000:.2f} ", end="",flush=True)
  print(the.file)

def eg__one():
  S = lambda rows: len(rows)
  data = [
    ['age', 'color', 'INCOME!', 'BUYS+'],
    [25, 'red', 50, 'yes'],
    [30, 'blue', 60, 'no'],
    [20, 'red', 70, 'yes'],
    [40, 'green', 80, 'no']]
  trees = grow(data, S, d=2)
  best  = max(trees, key=lambda t: S([predict(t, r) for r in data[1:]]))
  preds = [predict(best, r) for r in data[1:]]

def cli(d):
  for i,arg in enumerate(sys.argv): 
    if (fn := globals().get(f"eg{arg.replace('-', '_')}")):
      random.seed(d['seed'])
      fn()
    else:
      for k,b4 in d.items():
        if arg == "-"+k[0]: 
          new = b4==True and "False" or b4==False and "True" or sys.argv[i+1]
          d[k] = type(b4)(new)
   
random.seed(the.seed)
if __name__=="__main__": 
  cli(the.__dict__)
