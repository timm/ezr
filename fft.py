from types import SimpleNamespace as o

the = o(p=2)
Sym, Num = dict, tuple

def Col(c, rows, nump=True):
  d, lo, hi, d = {}, 1e32, -1e32
  for row in rows:
    if (v:=row[c]) != "?": 
      if nump : lo, hi = min(v,lo), max(v,hi) 
      else    : d[v] = d.get(v,0) + 1
  return (lo,hi) if nump else d 

def Data(names,*rows):
  w,x,y,all = {},{},{},{}
  for c, s in enumerate(names):
    new = Col(c, rows, s[0].isupper())
    all[c] = new
    if s[-1] != "X":
      w[c] = s[-1] == "+"
      (y if s[-1] in "!+-" else x)[c] = new
  return o(rows=rows, cols=o(names=names, w=w, x=x, y=y, all=all))

#------------------------------------------------------------------------------
def minkowski(src):
  d,n = 0,0
  for v in src: n,d = n+1, d + v**the.p
  return (d/n) ** (1/the.p)

def ydist(data,row):
  return minkowski(abs(norm(row[c], *col) - data.cols.w[c]) 
                   for c,col in data.cols.y.items())

def xdist(data, row1, row2):
  return minkowski(_dist1(col, row1[c], row2[c]) 
                   for c,col in data.cols.x.items())
   
def _xdist1(col, a,b):
  if a==b=="?": return 1
  if type(col) is Sym: return a != b
  a,b = norm(a,*col), norm(b,*col)
  a = a if a != "?" else (0 if b>0.5 else 1)
  b = b if b != "?" else (0 if a>0.5 else 1)
  return abs(a-b)

def norm(x,lo,hi): return 0 if x == "?" else (x - lo) / (hi - lo + 1e-32)

def estiamte(data,row,east,west,c):
  a,b = xdist(data, row,east), xdist(data,row,west)
  return (a*a +c*c - b*b)/(2*c + 1e-32) < 0.5

def estimates(data,row,poles):
  return sum(estiamte(data,row,*pole) for pole in poles)/len(poles)

#------------------------------------------------------------------------------
ops = dict(le = lambda r,c,v: r[c] <= v,
           gt = lambda r,c,v: r[c] >  v,
           eq = lambda r,c,v: r[c] == v)

lt = lambda c: (lambda row: row[c])

def mid(data,rows,c):
  s = sorted(rows, key=); n = len(s)
  return s[n//2] if n%2 else (s[n//2-1] + s[n//2])/2

def roles(head):
  n,s,x,y = set(),set(),set(),set()
  for i,txt in enumerate(head):
    if isinstance(txt,str):
      (n if txt[-1].isupper() else s).add(i)
      (y if txt[-1] in "!+-" else x).add(i)
  return o(nums=n, syms=s, x=x, y=y)

def splits(data, meta):
  head, rows = data[0], data[1:]
  for c in meta.x:
    if c in meta.nums:
      v = median([r[c] for r in rows])
      yield o(col=c, val=v, op='le',
               yes=[r for r in rows if r[c] <= v],
               no =[r for r in rows if r[c] >  v])
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
  with open(file,encoding="utf-8") as f:
    for line in f:
      if (line := line.split("%")[0]):
        yield [coerce(val.strip()) for val in line.split(",")]

def coerce(s):
  for fn in [int,float]:
    try: return fn(s)
    except Exception as _: pass
  s = s.strip()
  return {'True':True,'False':False}.get(s,s)

S = lambda rows: len(rows)
data = [
  ['age', 'color', 'INCOME!', 'BUYS+'],
  [25, 'red', 50, 'yes'],
  [30, 'blue', 60, 'no'],
  [20, 'red', 70, 'yes'],
  [40, 'green', 80, 'no']
]

trees = grow(data, S, d=2)
best  = max(trees, key=lambda t: S([predict(t, r) for r in data[1:]]))
preds = [predict(best, r) for r in data[1:]]

