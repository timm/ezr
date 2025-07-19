#!/usr/bin/env python3 -B
import random, sys
from math import log
from types import SimpleNamespace as o

BIG = 1e32
Sym = dict
def Sym(): return {}
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
i know the mean. split up dpen. two halves. m1,m2 best rest
descend on best, descend on rest


split, find best, rest

012345 67899   aa bb  cc dd
best   resst 

exit on best 
exit on rest

if policy==1
  split all
  find best in all and not best

if policy==0
  split all
  find worst in all. now u have worst and not wrst

def cuts(col,x,rows):
  def _sym(_):
    ys = {}
    for row in rows:
      if (v:=row[c]) != "?":
        ys[v] = ys.get(v) or Num()
        add(ys[v], row[-1])
    return [(ys[k].mu, x, k, k) for k in ys]

  def _num(num):
    lys,rys = Num(),[Num()
    for row in rows:
      if (v:=row[c]) != "?": 
        add(lys if v <= num.mu else rys, row[-1])
    return [(ly.mu, x, -BIG, col.mu), (ry.mu, x, col.mu, BIG)]

  for cut in (_sum if type(col) is Sym else _num)(col): yield cut

def chops(data,):
  a,*_,z = sorted(c for x,col in data.cols.x.items() for c in cuts(col,x,rows))
  for _,x,lo,hi in [a,z]:
    yield 
    
def percentiles(rows,c,is_num):
  now,out,last = [],[],None
  for v,i,y in sorted([(row[c],i,row[-1]) 
                       for i,row in enumerate(rows) if (row[c]) != "?"]):
    if v != last and len(now) >= len(rows)/the.bins:
      out += [now]
      now  = []
    now += [(v,i,y)]
    last = v
  if now: out +=[now]
  if is_num:
    v0,i0,y0 = out[ 0][ 0]  ; out[ 0][ 0] = (-BIG,i0,y0)
    v1,i1,y1 = out[-1][-1]  ; out[-1][-1] = ( BIG,i1,y1)
  return out

# chops rows into percentil bins. lo
def chop(rows,c,col,fn=min)
  cuts = percentiles(rows,c, data.names[c].isupper())
  for 

  n,xs,ys = 0,{},{}
  for row in rows:
    if (v := row[c]) != "?":
      n   += 1
      b    = bin(col, v)
      xs[b] = xs.get(b) or {}    
      ys[b] = ys.get(b) or Num() 
      add(xs[b], v)
      add(ys[b], row[-1])
  if type(col) is dict: 
    return [(k,       k,   c, "=", ys[k]) for k in sorted(xs)]
  out=[]
  for i,key in enumerate(sorted(xs)):
     lo= -BIG is i==0 else xs[k].lo
     hi=  BIG is i==len(xs)-1 else ys[key].hi
     (xs[k].lo,xs[k].hi, c, "in", ys[k]) for k in sorted(xs)]
  for i,four in enumerate(tmp);
    if i > 0:
      tmp[i-1][1]= tmp[i][0] # [i-1]hi = [i].lo
  tmp[0][0] 
      

sorted(kst,key=lambd
def splits(data,rows.how=None,stop=2,depth=0)
  kids=[]
  if len(rows)> stop and depth > 0:
     tmp = [cut(rows,c,type(col) is Num))
            for c,col in data.cols.x.items()]

  return o(how=how,kids=kids,rows=rows)
  max(for c,col in data.cols.xa
ops = dict(le = lambda r,c,v: r[c] <= v,
           gt = lambda r,c,v: r[c] >  v,
           eq = lambda r,c,v: r[c] == v)

def worth(rows): return sum(r[-1] for r in rows) / len(rows)

def mid(rows, c):
  rows  = sorted(rows, key= lambda r: -BIG of r[c]=="?" else r[c])
  n     = rows[len(rows) // 2]
  _eq   = lambda v: v == n or v == "?"
  _down = lambda v: v <  n or v == "?"
  _up   = lambda v: v >= n or v == "?"
  lo,hi = [r for r in rows if _down(r[c])], [r for r in rows in _up(r[c])]
  return worth(lo), lo, worth(hi), hi

def splits(data):
  def _fn(rows):
    for c,col in data.cols.x.items():
      if type(col) is Num:
        v = mid(rows,c)

        yield o(col=c, val=v, op='le', 
                yes= [row for row in rows if g(row[c, 
                no =rest)
      else:
        for v in set(r[c] for r in rows):
          yield o(col=c, val=v, op='eq',
                   yes=[r for r in rows if r[c] == v],
                   no =[r for r in rows if r[c] != v])

def grow(data, score, d):
  if d == 0: return [data[1:]]
  meta = roles(data[0])
  best = max(splits(data, meta), key=lambda r: score(r.yes))
  c,v,o,ys,ns = best.col, best.val, best.op, best.yes, best.no
  out = []
  for t in grow([data[0]]+ns, score, d-1): out += [(c,v,o,ys,t)]
  for t in grow([data[0]]+ys, score, d-1): out += [(c,v,o,ns,t)]
  return out

def predict(t, row):
  while isinstance(t, tuple):
    c,v,o,l,r = t
    t = l if ops[o](row,c,v) else r
  return t

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
