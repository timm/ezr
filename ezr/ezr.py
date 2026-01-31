#!/usr/bin/env python3 -B
"""
ezr.py: easy AI tools
(c) 2025 Tim Menzies, MIT license

Options:
   -b bins=5    Number of bins
   -B Budget=50 Initial sampling budget 
   -C Check=5   final evalaution budget
   -l leaf=2    Min examples in leaf of tree
   -p p=2       Distance coeffecient
   -s seed=1    Random number seed
   -S Show=30   Tree display width"""
from math import log,exp,sqrt
import re,sys,random,traceback
BIG=1e32

#-------------------------------------------------------------------------------
# Create
def what(s): return NUM if s[0].isupper else SYM

def COL(at=0,txt=" "): return what(txt)(at=at, txt=txt, goal=txt[-1]!="-")
def NUM(**d): return OBJ(it=NUM, **d, n=0, mu=0, m2=0)
def SYM(**d): return OBJ(it=SYM, **d, n=0, has={})

def DATA(items=[],s=""): return adds(items,OBJ(it=DATA,s=s,rows=[],cols=None))

def COLS(names):
  cols= [COL(at=n,txt=s) for n,s in enumerate(names)]
  return OBJ(it=COLS, names=names, all=cols,
             x= [c for c in cols if c.txt[-1] not in "-+!X"],
             y= [c for c in cols if c.txt[-1]     in "-+!" ])

def clone(data, rows=[]): return DATA([data.cols.names] + rows)

#-------------------------------------------------------------------------------
# Update
def adds(items, it=None):
  it = it or NUM(); [add(it,item) for item in items]; return it

def add(i,v):
  if DATA is i.it : 
     if not i.cols: i.cols=COLS(v)
     else: i.rows += [[add(c,v[c.at]) for c in i.cols.all]]
  elif v != "?":
    i.n += 1
    if SYM is i.it : i.has[v] = 1 + i.has.get(v,0)
    if NUM is i.it : d = v - i.mu; i.mu += d/i.n; i.m2 += d*(v - i.mu)
  return v

#-------------------------------------------------------------------------------
# Query
def score(num):
  return BIG if num.n < the.leaf else num.mu + sd(num) /(sqrt(num.n) + 1/BIG)

def mids(data):  return [mid(col) for col in data.cols.all]
def mid(col): return mode(col) if SYM is col.it else col.mu
def mode(sym): return max(sym.has, key=sym.has.get)

def spread(col): return (ent if SYM is col.it else sd)(col)
def sd(num): return 0 if num.n < 2 else sqrt(num.m2 / (num.n - 1))
def ent(sym): return -sum(p*log(p,2) for n in sym.has.values() if (p:=n/sym.n)>0)

def z(num,v): return (v -  num.mu) / (sd(num) + 1/BIG)
def norm(num,v): return 1 / (1 + exp( -1.7 * clip(z(num,v),-3,3)))
def bucket(num,v): return int(the.bins * norm(num, v))

#-------------------------------------------------------------------------------
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

def around(data,row,rows): return sorted(rows,key=lambda r:distx(data,row,r))

#------------------------------------------------------------------------------
# lib

def clip(v,lo,hi): max(lo, min(hi, v))

def shuffle(lst): random.shuffle(lst); return lst

def o(t):
  match t:
    case _ if type(t) is type(o): return t.__doc__
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
    if (n := n-v) <= 0: break
  return k

def cast(s, BOOL={"true": True, "false": False}):
  try: return int(s)
  except ValueError:
    try: return float(s)
    except ValueError: return BOOL.get(s, s)

def csv(f):
  with open(f) as file:
    for s in file: yield [cast(x) for x in s.split(",")]

#-------------------------------------------------------------------------------
# cli
def run(f,*args):
  random.seed(the.seed)
  try: f(*args)
  except Exception: traceback.print_exc()

def filename(s): return s

def eg_h():
  "Show help."
  print(__doc__)
  for k, v in globals().items():
    if k.startswith("eg_"): 
     print(f"   -{re.sub(f'^_','-',k[3:]):<12}{v.__doc__.strip()}")

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
  syms = adds("aaaabbc",SYM()); print(o(x:=ent(syms))); assert abs(1.379-x) < .05

def eg__nums():
  "Example: NUMs summaries."
  nums = adds(gauss(10, 1) for _ in range(1000))
  print(OBJ(mu=nums.mu, sd=sd(nums)))
  assert abs(10 - nums.mu) < .05 and abs(1 - sd(nums)) < .05

def eg__ys(f:filename):
  "asds"
  data = DATA(csv(f))
  print(*data.cols.names)
  print(o(mids(data)))
  for row in sorted(data.rows, key=lambda r: disty(data, r))[::40]:
    print(*row,*[bucket(col,row[col.at]) for col in data.cols.y],
          round(disty(data,row),2))

def eg__tree(f:filename):
  ""
  data = DATA(csv(f))
  data1 = clone(data, shuffle(data.rows)[:50])
  tree,_ = Tree(data1)
  treeShow(tree)

def eg__test(f:filename):
  ""
  data = DATA(csv(filename))
  mid  = len(data.rows)//2
  Y    = lambda r: disty(data,r)
  b4   = sorted(Y(r) for r in data.rows)
  win  = lambda r: int(100 * (1 - (Y(r)  - b4[0]) / (b4[mid] - b4[0] + 1/BIG)))
  wins = NUM()
  for _ in range(60):
    rows = shuffle(data.rows)
    test, train = rows[mid:], rows[:mid][:the.Budget]
    tree,_ = Tree(clone(data,train))
    test.sort(key=lambda r: treeLeaf(tree,r).y.mu)
    add(wins, win(min(test[:the.Check], key=Y)))
  print(f"{round(wins.mu)} ,sd {round(sd(wins))} ,b4 {o(b4[mid])} ,lo {o(b4[0])}",
        *[f"{s} {len(a)}" for s,a in 
          dict(x=data.cols.x, y=data.cols.y, r=data.rows).items()],
        *filename.split("/")[-2:], sep=" ,")

#------------------------------------------------------------------------------
the= OBJ(**{k: cast(v) for k, v in re.findall(r"(\S+)=(\S+)", __doc__)})
random.seed(the.seed)

if __name__ == "__main__":
  args = iter(sys.argv[1:])
  for s in args:
    print(s)
    if f := globals().get(f"eg_{s[1:]}"):
      print(f)
      run(f, *[t(next(args)) for t in f.__annotations__.values()])
    elif s[1:] in the: 
      print(3)
      the[s[1:]] = cast(next(args, ""))
