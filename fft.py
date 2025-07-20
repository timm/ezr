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
    col = (Sym if s[0].islower() else Num)()
    [add(col, row[c]) for row in rows]
    all[c] = col
    if s[-1] != "X":
      w[c] = s[-1] == "+"
      (y if s[-1] in "!+-" else x)[c] = col 
  return o(rows=rows, cols=o(names=names, w=w, x=x, y=y, all=all))

def add(col, v):
  if v != "?":
    if type(col) is Sym: col[v] = 1 + col.get(v,0)
    else:
      col.n  += 1
      d       = v - col.mu
      col.mu += 1 * (d / col.n)
      col.m2 += 1 * (d * (v - col.mu))
      col.sd  = (col.m2/(col.n - 1 - 1/BIG))**.5
      col.lo  = min(v, col.lo)
      col.hi  = max(v, col.hi)
  return v

def size(col): return sum(col.values()) if type(col) is Sym else col.n 
def div(col):  return entropy(col)      if type(col) is Sym else col.sd

def mode(d)   : return max(d, key=d.get)
def entropy(d): N=size(); return -sum(p*log(p,2) for n in d.values() if (p:=n/N)>0)

def mid(col):
  if isinstance(col, dict): return mode(col)
  if hasattr(col, "mu"):    return col.mu
  if isinstance(col, (int, float)): return col
  return 0  # fallback

#------------------------------------------------------------------------------
def minkowski(src):
  d,n = 0,0
  for v in src: n,d = n+1, d + v**the.p
  return (d/n) ** (1/the.p)

def ydist(data,row):
  return minkowski(abs(norm(col,row[y]) - data.cols.w[y]) 
                   for y,col in data.cols.y.items())

def xdist(data, row1, row2):
  return minkowski(_xdist(col,row1[x], row2[x]) 
                   for x,col in data.cols.x.items())
   
def _xdist(col,x1, x2):
  if x1==x2=="?": return 1
  if type(col) is Sym: return x1 != x2
  x1,x2 = norm(col, x1), norm(col, x2)
  x1    = x1 if x1 != "?" else (0 if x2>0.5 else 1)
  x2    = x2 if x2 != "?" else (0 if x1>0.5 else 1)
  return abs(x1-x2)

def norm(col,x):
  return (x - col.lo) / (col.hi - col.lo + 1/BIG)

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
  out = Num()
  for r in rows:
    v = r[c]
    if v != "?": add(out, v)
  return out

def selects(rows, c, lo, hi):
  yes, no = [], []
  for row in rows:
    v = row[c]
    if v == "?" or lo <= v <= hi: yes.append(row)
    if v == "?" or not (lo <= v <= hi): no.append(row)
  return yes, no

def fft(data, rows=None, depth=4):
  rows = rows or data.rows
  if depth > 0 and rows:
    if (cuts := [cut for c, col in data.cols.x.items() 
                 for cut in fftCuts(col, c, rows, type(col) is Sym)]):
      best, *_, worst = sorted(cuts)
      yield from fftRecurse(data, rows, depth, True, *best)
      yield from fftRecurse(data, rows, depth, False,*worst)

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

def fftRecurse(data, rows, depth, exiting, mu,c,lo,hi):
  yes, no = selects(rows, c, lo, hi)
  leaf = rx(c, yes if exiting else no)
  rest = no        if exiting else yes
  if depth==1: 
    yield leaf
  else:
    for right in fft(data,rest,depth-1):
      yield o(c=c, lo=lo, hi=hi, left=leaf, right=right)

def fftPredict(t, row):
  while hasattr(t, "c"):
    v = row[t.c]
    t = t.left        if v == "?" or t.lo <= v <= t.hi else (
        next(t.right) if hasattr(t.right, "__iter__")  else t.right)
  return t.stats

def fftShow(data, t, seen=None, prefix=""):
  seen = seen or set()
  def show(x): return f"{int(x):.0f}" if abs(x) >= 1 else f"{x:.2f}"
  while hasattr(t, "c"):
    if t.c in seen:
      print(f"{prefix}# skipped redundant test on {data.cols.names[t.c]}")
      break
    seen.add(t.c)
    name = data.cols.names[t.c]
    if abs(t.lo) < 1e31:
      print(f"{prefix}if {name} < {show(t.lo)} then", end=" ")
      fftShow(data, t.right, seen.copy(), prefix + "  ")
    if abs(t.hi) < 1e31:
      print(f"{prefix}else if {name} >= {show(t.hi)} then", end=" ")
      t = t.left
      continue
    return
  print(f"{prefix}{mid(t):.2f}")

def coerce(s):
  for fn in [int,float]:
    try: return fn(s)
    except Exception as _: pass
  s = s.strip()
  return {'True':True,'False':False}.get(s,s)

def csv(file):
  n = -1
  with open(file,encoding="utf-8") as f:
    for line in f:
      if (line := line.split("%")[0]):
        n += 1
        suffix = "scoreX" if n==0 else 0
        yield [coerce(s.strip()) for s in line.split(",")] + [suffix]

r3=lambda n:round(n,3)

def eg__the(): print(the)

def eg__xdata(): 
  data = Data(csv(the.file))
  print(sorted([r3(xdist(data,r,data.rows[0])) for r in data.rows])[::10])
  print(sorted([r3(ydist(data,r)) for r in data.rows])[::10])

def eg__data(): 
  for p in [4,8,12,16]:
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

def eg__fft():
  data = Data(csv(the.file))
  for tree in fft(data, depth=3): print(""); fftShow(data,tree)
  
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
