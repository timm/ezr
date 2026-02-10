#!/usr/bin/env python3 -B
"""
ezr.py: easy AI tools
(c) 2025 Tim Menzies, MIT license

Options:
   -b bins=5    Number of bins
   -B Budget=50 Initial sampling budget
   -C Check=5   final evalaution budget
   -l leaf=4    Min examples in leaf of tree
   -p p=2       Distance coeffecient
   -s seed=1    Random number seed
   -S Show=30   Tree display width"""
#from .tools import helper
from math import log,exp,sqrt
import re,sys,random,traceback
BIG=1e32

#---------------------------------------------------------------------
# Create
def what(s): return NUM if s[0].isupper() else SYM

def COL(at=0,txt=" "): return what(txt)(at=at, txt=txt, goal=txt[-1]!="-")
def NUM(**d): return OBJ(it=NUM, **d, n=0, mu=0, m2=0, low={}, hi={})
def SYM(**d): return OBJ(it=SYM, **d, n=0, has={})

def DATA(items=None,s=""):
 return adds(items, OBJ(it=DATA, n=0, s=s, rows=[], cols=None, mids=None))

def COLS(names):
  cols= [COL(at=n,txt=s) for n,s in enumerate(names)]
  return OBJ(it=COLS, names=names, all=cols,
             x= [c for c in cols if c.txt[-1] not in "-+!X"],
             y= [c for c in cols if c.txt[-1]     in "-+!" ])

def clone(data, rows=None):
  return DATA([data.cols.names] + (rows or []))

#---------------------------------------------------------------------
# Update
def adds(items, it=None):
  it = it or NUM(); [add(it,item) for item in (items or [])]; return it

def sub(i,v): return add(i,v, -1)

def add(i,v,w=1):
  if v!="?":
    i.n += w
    if   SYM  is i.it : i.has[v] = w + i.has.get(v,0)
    elif NUM  is i.it : d = v-i.mu; i.mu += w*d/i.n; i.m2 += w*d*(v-i.mu)
    elif DATA is i.it :
      if not i.cols: i.cols=COLS(v)
      else:
        i.mids = None
        for col in i.cols.all: add(col, v[col.at], w)
        (i.rows.append if w>0 else i.rows.remove)(v)
  return v

#---------------------------------------------------------------------
# Query
def mid(col): return mode(col) if SYM is col.it else col.mu
def mode(sym): return max(sym.has, key=sym.has.get)
def mids(data):
  data.mids = data.mids or [mid(col) for col in data.cols.all]
  return data.mids

def spread(col): return (ent if SYM is col.it else sd)(col)
def sd(num): return 0 if num.n < 2 else sqrt(max(0,num.m2) / (num.n - 1))
def ent(sym): return -sum(p*log(p,2) for n in sym.has.values() if (p:=n/sym.n)>0)

def z(num,v): return max(-3, min(3, (v -  num.mu) / (sd(num) + 1/BIG)))
def norm(num,v): return 1 / (1 + exp( -1.7 * z(num,v)))

def bucket(col,v):
   if v=="?" or SYM is col.it: return v
   b = int(the.bins * norm(col,v))
   col.low[b] = min(v, col.low.get(b,BIG)) # remember lowest value
   col.hi[b]  = max(v, col.hi.get(b,-BIG)) # remember lowest value
   return b

#---------------------------------------------------------------------
# distance
def minkowski(items):
  n,d = 0,0
  for item in items: n, d = n+1, d+item ** the.p
  return 0 if n==0 else (d / n) ** (1 / the.p)

def disty(data, row):
  return minkowski((norm(y,row[y.at]) - y.goal) for y in data.cols.y)

def distx(data,row1,row2):
  return minkowski(aha(x, row1[x.at], row2[x.at]) for x in data.cols.x)

def aha(col,u,v):
  if u==v=="?": return 1
  if SYM is col.it : return u != v
  u,v = norm(col,u), norm(col,v)
  u = u if u != "?" else (0 if v>0.5 else 1)
  v = v if v != "?" else (0 if u>0.5 else 1)
  return abs(u - v)

def furthest(*args): return around(*args)[-1]
def nearest(*args): return around(*args)[0]

def around(data,row,rows):
  return sorted(rows,key=lambda other:distx(data,row,other))

#---------------------------------------------------------------------
# discretization, breaking nums on, at max, the.bins number of chops
def score(N,n,mu,sd1):  return BIG if n< the.leaf else sd1

def bestcut(data, rows):
  d = {c.at: {} for c in data.cols.x}
  total = {c.at: NUM() for c in data.cols.x}
  for r in rows:
    y = disty(data, r)
    for c in data.cols.x:
      if (b := bucket(c, r[c.at])) != "?":
        if b not in d[c.at]: d[c.at][b] = NUM()
        add(d[c.at][b], y)
        add(total[c.at], y)
  return min((cut for c in data.cols.x
                for cut in cuts(len(rows), c,
                                sorted(d[c.at].items()), total[c.at])),
           default=None)

def cuts(n, col, bins, total):
  if SYM is col.it:
    for b, num in bins:
      yield score(n, num.n, num.mu, sd(num)), col.at, b
  else:
    lhs = NUM()
    n = total.n
    for b, num in bins[:-1]:
      lhs = merge(lhs, num)
      rhs = unmerge(total, lhs)
      mu  = (lhs.n*lhs.mu  + rhs.n*rhs.mu)  / n 
      s   = (lhs.n*sd(lhs) + rhs.n*sd(rhs)) / n 
      yield score(n, total.n, mu, s), col.at, b

def unmerge(num1, num2): return merge(num1,num2,w=-1)

def merge(num1, num2, w=1):
  out = NUM()
  out.n = num1.n + w * num2.n
  if out.n <= 0: return NUM()
  out.mu = (num1.n * num1.mu + w * num2.n * num2.mu) / out.n
  if num1.n == 0: out.m2 = num2.m2
  else:
    d = out.mu - num2.mu
    out.m2 = num1.m2 + w * (num2.m2 + d * d * out.n * num2.n / num1.n)
  return out

 #---------------------------------------------------------------------
# tree
def Tree(data, uses=None):
  uses = uses or set()
  def grow(rows):
    at, b, kids = None, None, {}
    if len(rows) > the.leaf :
      if cut := bestcut(data, rows):
        _,at,b = cut
        yes,no,col = [],[],data.cols.all[at]
        for row in rows:
          (yes if selects(col, row, b) else no).append(row)
        if yes and no:
          if len(yes) >= the.leaf: kids[True] = grow(yes)
          if len(no) >= the.leaf: kids[False] = grow(no)
          if kids: uses.add(at)
    return OBJ(root=data, kids=kids, at=at, bucket=b,
               x = mids(clone(data,rows)),
               y = adds(disty(data,row) for row in rows))
  return grow(data.rows), uses

def selects(col, row, b):
  bucket_val = bucket(col, row[col.at])
  if bucket_val == "?": return False  
  return bucket_val == b if SYM is col.it else bucket_val <= b

def treeLeaf(t, row):
  if not t or not t.kids: return t  
  col = t.root.cols.all[t.at]
  kid = t.kids.get(bucket(col, row[col.at]) == t.bucket)
  return treeLeaf(kid, row) if kid else t  

def treeShow(t):
  def show(n, lvl, pre):
    if not n: return
    g = [n.x[c.at] for c in n.root.cols.y]
    print(f"{('| '*(lvl-1)+pre):{the.Show}}: ",end="")
    print(f"{o(n.y.mu):6} : {n.y.n:4} : {o(g)}")
    if n.kids:
      for k in sorted(n.kids, key=lambda k: n.kids[k].y.mu):
        c, b = n.root.cols.all[n.at], n.bucket
        show(n.kids[k], lvl+1, showCol(c, b, k))
  ys = ', '.join([y.txt for y in t.root.cols.y])
  print(f"{'':{the.Show}}  Score       N   [{ys}]"); show(t, 0, "")

def showCol(col, bucket, left):
  if SYM is col.it:
    return f"{col.txt} {'==' if left else '!='} {bucket}"
  val = col.low.get(bucket+1, col.hi.get(bucket, '?'))
  return f"{col.txt} {'<' if left else '>='} {o(val)}"

#--------------------------------------------------------------------
# lib

def clip(v,lo,hi): return max(lo, min(hi, v))

def shuffle(lst): random.shuffle(lst); return lst

def o(t):
  match t:
    case _ if type(t) is type(o): return t.__name__
    case dict(): return "{" + " ".join(f":{k} {o(t[k])}" for k in t) + "}"
    case float(): return f"{int(t)}" if int(t) == t else f"{t:.2f}"
    case list(): return "[" + ", ".join(o(x) for x in t) + "]"
    case tuple(): return "(" + ", ".join(o(x) for x in t) + ")"
    case _: return str(t)

class OBJ(dict):
  __getattr__,__setattr__,__repr__ = dict.__getitem__,dict.__setitem__,o

def gauss(mu,sd1):
  return mu + 2 * sd1 * (sum(random.random() for _ in range(3)) - 1.5)

def pick(d,n):
  n *= random.random()
  for k,v in d.items():
    if (n := n-v) <= 0: return k

CASTS = [int,float,lambda s: {"true":1,"false":0}.get(s.lower(),s)]

def cast(s):
  for f in CASTS:
    try: return f(s)
    except ValueError: ...

def csv(f):
  with open(f,encoding="utf-8") as file:
    for s in file:
      if s:=s.strip(): yield [cast(x.strip()) for x in s.split(",")]

#---------------------------------------------------------------------
# cli
def run(f,*args):
  random.seed(the.seed)
  try: f(*args)
  except Exception: traceback.print_exc()

def filename(s): return s

def eg_h():
  "Show help."
  print(__doc__)
  for k, fun in globals().items():
    if k.startswith("eg_"):
     s = re.sub('^_','-',k[3:])
     print(f"   -{s:<12}{fun.__doc__.strip()}")

def eg__all(f:filename):
  "Run all examples."
  for k, fun in globals().items():
    if k.startswith("eg_") and k!= "eg__all":
      print("\n#---------",k)
      run(fun,f) if fun.__annotations__.values() else run(fun)

def eg__the():
  "Show config."
  print(the)

def eg_s(n:int):
  "Set random number seed."
  the.seed=n; random.seed(n)

def eg__csv(f:filename) :
  "Example: csv reader."
  [print(row) for row in list(csv(f))[::40]]

def eg__syms():
  "Example: SYMs summaries."
  syms = adds("aaaabbc",SYM())
  print(o(x:=ent(syms))); assert abs(1.379-x) < .05

def eg__nums():
  "Example: NUMs summaries."
  nums = adds(gauss(10, 1) for _ in range(1000))
  print(OBJ(mu=nums.mu, sd=sd(nums)))
  assert abs(10 - nums.mu) < .05 and abs(1 - sd(nums)) < .05

def eg__data(f:filename):
  "asds"
  data = DATA(csv(f))
  print(*data.cols.names)
  print("x",*data.cols.x,sep="\n")
  print("y",*data.cols.y,sep="\n")

def eg__ys(f:filename):
  "asds"
  data = DATA(csv(f))
  print(*data.cols.names)
  print(o(mids(data)))
  for row in sorted(data.rows, key=lambda row: disty(data, row))[::40]:
    print(*row,*[bucket(col,row[col.at]) for col in data.cols.y],
          round(disty(data,row),2))

def eg__tree(f:filename):
  "treeing"
  data = DATA(csv(f))
  data1 = clone(data, shuffle(data.rows)[:the.Budget])
  tree,_ = Tree(data1)
  treeShow(tree)

def eg__test(f:filename):
  "testing"
  data = DATA(csv(f))
  half  = len(data.rows)//2
  Y    = lambda row: disty(data,row)
  b4   = sorted(Y(row) for row in data.rows)
  win  = lambda r: int(100 * (1 - (Y(r)-b4[0]) / (b4[half]-b4[0] + 1/BIG)))
  wins = NUM()
  for _ in range(60):
    rows = shuffle(data.rows)
    test, train = rows[half:], rows[:half][:the.Budget]
    tree,_ = Tree(clone(data,train))
    test.sort(key=lambda row: treeLeaf(tree,row).y.mu)
    add(wins, win(min(test[:the.Check], key=Y)))
  print(f"{round(wins.mu)} ,sd {round(sd(wins))} ,b4 {o(b4[half])} ,lo {o(b4[0])}",
        f" ,B {the.Budget}",
        *[f"{s} {len(a)}" for s,a in
          dict(x=data.cols.x, y=data.cols.y, r=data.rows).items()],
        *f.split("/")[-2:], sep=" ,")

#--------------------------------------------------------------------
the= OBJ(**{k: cast(v) for k, v in re.findall(r"(\S+)=(\S+)", __doc__)})
random.seed(the.seed)

def main():
  args = iter(sys.argv[1:])
  for s in args:
    if f := globals().get(f"eg_{s[1:].replace('-','_')}"):
      run(f, *[t(next(args)) for t in f.__annotations__.values()])
    else:
      for k in the:
        if k[0] == s[1]: the[k] = cast(next(args, ""))

if __name__ == "__main__": main()
