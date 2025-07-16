#!/usr/bin/env python3 -B
import random, sys
from types import SimpleNamespace as o

Sym = dict
Num = tuple #(lo,hi)
BIG  = 1e32
the  = o(p=2, seed=1234567890, Projections=8,
         file="../moot/optimize/misc/auto93.csv")

def Data(src):
  head, *rows = list(src)
  data  = _data(head, rows)
  poles = projections(data)
  for row in rows: score(data,row,poles)
  return data

def _data(names,rows):
  w,x,y,all = {},{},{},{}
  for c, s in enumerate(names):
    col = _col(c, rows, s[0].islower())
    all[c] = col
    if s[-1] != "X":
      w[c] = s[-1] == "+"
      (y if s[-1] in "!+-" else x)[c] = col 
  return o(rows=rows, cols=o(names=names, w=w, x=x, y=y, all=all))

def _col(c, rows, is_sym=True):
  counts, lo, hi = {}, BIG, -BIG
  for row in rows:
    if (v:=row[c]) != "?": 
      if is_sym: 
        counts[v] = 1 + counts.get(v,0)
      else : 
        v = row[c] = float(v)
        lo, hi = min(v,lo), max(v,hi)
  return counts if is_sym else (lo, hi)

#------------------------------------------------------------------------------
def minkowski(src):
  d,n = 0,0
  for v in src: n,d = n+1, d + v**the.p
  return (d/n) ** (1/the.p)

def ydist(data,row):
  return minkowski(abs(norm(row[c], *col) - data.cols.w[c]) 
                   for c,col in data.cols.y.items())

def xdist(data, row1, row2):
  return minkowski(_xdist(col, row1[c], row2[c]) 
                   for c,col in data.cols.x.items())
   
def _xdist(col, a,b):
  if a==b=="?": return 1
  if type(col) is Sym: return a != b
  a,b = norm(a,*col), norm(b,*col)
  a = a if a != "?" else (0 if b>0.5 else 1)
  b = b if b != "?" else (0 if a>0.5 else 1)
  return abs(a-b)

def norm(x,lo,hi,*_): 
  return (x - lo) / (hi - lo + 1/BIG)

def cosine(data,row,best,rest,c):
  a,b = xdist(data, row, best), xdist(data, row, rest)
  return (a*a + c*c - b*b)/(2*c + 1/BIG)

def score(data,row,poles):
  row[-1] = sum(cosine(data,row,*pole) < 0.1 for pole in poles)/len(poles)

def projections(data):
  poles = []
  for _ in range(the.Projections):
    best,rest = random.sample(data.rows, k=2)
    if ydist(data,best) > ydist(data,rest):
      best,rest = rest,best
    poles += [(best, rest, xdist(data,best, rest))]
  return poles

#------------------------------------------------------------------------------
# ops = dict(le = lambda r,c,v: r[c] <= v,
#            gt = lambda r,c,v: r[c] >  v,
#            eq = lambda r,c,v: r[c] == v)
#
# lt = lambda c,x: (lambda row: row[c]<x)
#
# def mid(data,rows,c):
#   s = sorted(rows, key=); n = len(s)
#   return s[n//2] if n%2 else (s[n//2-1] + s[n//2])/2
#
# def roles(head):
#   n,s,x,y = set(),set(),set(),set()
#   for i,txt in enumerate(head):
#     if isinstance(txt,str):
#       (n if txt[-1].isupper() else s).add(i)
#       (y if txt[-1] in "!+-" else x).add(i)
#   return o(nums=n, syms=s, x=x, y=y)
#
# def splits(data, meta):
#   head, rows = data[0], data[1:]
#   for c in meta.x:
#     if c in meta.nums:
#       v = median([r[c] for r in rows])
#       yield o(col=c, val=v, op='le',
#                yes=[r for r in rows if r[c] <= v],
#                no =[r for r in rows if r[c] >  v])
#     else:
#       for v in set(r[c] for r in rows):
#         yield o(col=c, val=v, op='eq',
#                  yes=[r for r in rows if r[c] == v],
#                  no =[r for r in rows if r[c] != v])
#
# def grow(data, score, d):
#   if d == 0: return [data[1:]]
#   meta = roles(data[0])
#   best = max(splits(data, meta), key=lambda r: score(r.yes))
#   c,v,o,ys,ns = best.col, best.val, best.op, best.yes, best.no
#   out = []
#   for t in grow([data[0]]+ns, score, d-1): out += [(c,v,o,ys,t)]
#   for t in grow([data[0]]+ys, score, d-1): out += [(c,v,o,ns,t)]
#   return out
#
# def predict(t, row):
#   while isinstance(t, tuple):
#     c,v,o,l,r = t
#     t = l if ops[o](row,c,v) else r
#   return t
#
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
  data = Data(csv(the.file))
  for x,y in sorted([(r3(row[-1]),r3(ydist(data,row))) for row in data.rows]):
      print(x,y)

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
