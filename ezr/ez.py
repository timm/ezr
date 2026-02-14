#!/usr/bin/env python3 -B
"""
ez.py: lightweight XAI for optimization, classification, regression
(c) 2025 Tim Menzies, MIT license.

USAGE: python3 ez.py [OPTIONS] [FILE]                          

OPTIONS:
  -b bins=7    Number of bins for numeric discretization
  -B Budget=50 Training sample budget
  -C Check=5   Final evaluation budget
  -k k=1       Bayes low-frequency hack for symbolic attributes
  -l leaf=4    Min rows in tree leaf
  -m m=2       Bayes low-frequency hack for class priors
  -p p=2       Minkowski distance power (1:manhattan, 2:euclidean)
  -s seed=1    Random number seed
  -S Show=30   Tree display width
"""
from math import log,exp,sqrt
import re,sys,random,traceback
BIG=1e32

"""
INPUT: CSV. Row 1 defines columns. Uppercase=numeric, lowercase=symbolic.
  Suffixes: "+" maximize, "-" minimize, "!" class label, "X" ignore.
  Missing values: "?".

API ( Hints: i:instance d:DATA c:COL r:row v:value f:file ):
  OBJ(**d)           Dict subclass with dot-notation access
  csv(f)             Generator yielding parsed rows from CSV file
  cast(s)            Cast string to int, float, bool, or string

  NUM(at,txt)        Numeric column (tracks n, mu, m2)
  SYM(at,txt)        Symbolic column (tracks n, has)
  DATA(items,s)      Dataset: rows + COLS structure
  COLS(names)        Build x/y column lists from header names
  clone(d, rows)     New DATA with same structure, optional rows

  add(i,v)           Update NUM/SYM stats or add row to DATA
  mid(c), spread(c)  Central tendency and diversity for a column
  norm(c,v)          Normalize numeric v to 0..1
  like(c,v,prior)    Likelihood of v in column c
  likes(d,r,n,nh)    Log-likelihood of row r in dataset d

  distx(d,r1,r2)     Minkowski distance between rows over x cols
  disty(d,r)         Distance of row r from heaven over y cols

  TREE(d,rows)       Build regression tree via variance reduction
  treeLeaf(t,r)      Leaf node for row r
  treeNodes(t)       Iterator over (node, level, label) triples
  treeUsed(t)        Set of column names used in tree splits
  treeShow(t)        Print tree with indentation and y stats

TYPE TAGS (.it field routes logic instead of subclassing):
  NUM  SYM  DATA

XAI MECHANISMS:
  Contrast Sets: Isolates "best" rows (sorted by disty, top sqrt(n)).
    Contrasts their attribute ranges against the rest using score().
    Yields simple IF/THEN rules — actionable and human-readable.
  Interpretable Trees: Printed recursively. Indentation = conjunctions.
    Leaves show mid/spread of y. Sorted so best branch prints first.

ARCHITECTURE:
  OBJ-Dict Dualism   Factory fns return OBJ dicts with dot-notation
  Functional Routing .it tag routes logic (no subclass dispatch)
  Config via Docstring  Options regex-parsed from this string at startup
  Reflection Tests   Any eg_* function is auto-runnable via CLI
"""
#---- create ---------------------------------------------------------
def what(s): return NUM if s[0].isupper() else SYM

def COL(at=0,txt=" "): return what(txt)(at=at, txt=txt, goal=txt[-1]!="-")
def NUM(**d): return OBJ(it=NUM, **d, n=0, mu=0, m2=0)
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

#--- update ----------------------------------------------------------
def adds(items, it=None):
  it = it or NUM(); [add(it,item) for item in (items or [])]; return it

def sub(i,v): return add(i,v, -1)

def add(i,v,w=1):
  if v!="?":
    i.n += w
    if i.n <= 0: i.n,i.mu,i.m2 = 0,0,0; return v
    if   SYM  is i.it : i.has[v] = w + i.has.get(v,0)
    elif NUM  is i.it : 
      if i.n <= 0: i.n,i.mu,i.m2 = 0,0,0
      else: d = v-i.mu; i.mu += w*d/i.n; i.m2 += w*d*(v-i.mu)
    elif DATA is i.it :
      if not i.cols: i.cols=COLS(v)
      else:
        i.mids = None
        for col in i.cols.all: add(col, v[col.at], w)
        (i.rows.append if w>0 else i.rows.remove)(v)
  return v

#--- qeury -----------------------------------------------------------
def mid(col): return mode(col) if SYM is col.it else col.mu
def mode(sym): return max(sym.has, key=sym.has.get)
def mids(data):
  data.mids = data.mids or [mid(col) for col in data.cols.all]
  return data.mids

def spread(col): return (ent if SYM is col.it else sd)(col)
def sd(num): return 0 if num.n < 2 else sqrt(max(0,num.m2) / (num.n - 1))
def ent(sym): 
  return -sum(p*log(p,2) for n in sym.has.values() if (p:=n/sym.n)>0)

#---- distance -------------------------------------------------------
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

def furthest(*args): return order(*args)[-1]
def nearest(*args): return order(*args)[0]
def order(data,r1,rows): return sorted(rows,key=lambda r1:distx(data,r1,r2))

#--- bayes ------------------------------------------------------------
def z(num,v): return max(-3, min(3, (v -  num.mu) / (sd(num) + 1/BIG)))
def norm(num,v): return 1 / (1 + exp( -1.7 * z(num,v)))

def bucket(col,v):
   return v if (v=="?" or SYM is col.it) else int(the.bins * norm(col,v))

def like(col, v, prior=0):
  if NUM is col.it: 
    var = sd(col)**2 + 1/BIG
    return (1/sqrt(2*3.14159*var)) * exp(-((v - col.mu)**2)/(2*var))
  else:        
    n = col.has.get(v, 0) + the.k*prior
    return max(1/BIG, n/(col.n + the.k))

def likes(data, row, nall, nh):
  prior = (len(data.rows) + the.m) / (nall + the.m * nh)
  out = log(prior)
  for col in data.cols.x:
    if (v := row[col.at]) != "?": out += log(like(col, v, prior))
  return out

#--- tree -----------------------------------------------------------
def treeSelects(rows, at, fn):
  left, right = [], []
  for r in rows:
    if (v := r[at]) != "?": (left if fn(v) else right).append(r)
  return ((left,right) if len(left)>=the.leaf and len(right)>=the.leaf
          else (None, None))

def treeSplits(col, rows):
  at = col.at
  if SYM is col.it:
    for v in set(r[at] for r in rows if r[at] != "?"):
      left, right = treeSelects(rows, at, lambda x: x == v)
      if left: yield v, left, right
  else:
    vals = sorted(r[at] for r in rows if r[at] != "?")
    if len(vals) >= 2:
      med = vals[len(vals) // 2]
      left, right = treeSelects(rows, at, lambda x: x <= med)
      if left: yield med, left, right

def TREE(data, rows):
  tree = OBJ(y = adds(disty(data, r) for r in rows))
  if len(rows) >= 2 * the.leaf:
    best, bestW = None, BIG
    for c in data.cols.x:
      for cut, left, right in treeSplits(c, rows):
        w = sum(len(s)*sd(adds(disty(data,r) for r in s))
                for s in [left,right])
        if w < bestW:
          best, bestW = (c, cut, left, right), w
    if best:
      c, cut, left, right = best
      tree.update(col=c, cut=cut, left=TREE(data, left),
                                  right=TREE(data, right))
  return tree

def treeLeaf(tree, row):
  if "col" in tree:                          
    v = row[tree.col.at]
    if v == "?": return treeLeaf(tree.left, row)
    kid = (tree.left if (v == tree.cut
                         if SYM is tree.col.it
                         else v <= tree.cut) else tree.right)
    return treeLeaf(kid, row)
  return tree

def treeUsed(tree):
  return {n.col.txt for n,_,_ in treeNodes(tree) if "col" in n}

def treeNodes(tree, lvl=0, pre=""):
  if tree:
    yield tree, lvl, pre
    if "col" in tree:                        
      op = '==' if SYM is tree.col.it else '<='
      no = '!=' if SYM is tree.col.it else '>'
      for kid, txt in sorted([(tree.left, op), (tree.right, no)],
                              key=lambda p: p[0].y.mu):
        yield from treeNodes(kid, lvl+1,
                             f"{tree.col.txt} {txt} {o(tree.cut)}")

def treeShow(tree):                          
  for n, lvl, pre in treeNodes(tree):
    s = f"{'|   '*(lvl-1)}{pre}" if pre else ""
    print(f"{s:{the.Show}} {o(n.y.mu):>6} ({n.y.n})")

#--- lib -------------------------------------------------------------
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
#--- tests ----------------------------------------------------------
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

def eg__tree(f: filename):
  "treeing"
  data = DATA(csv(f))
  data1 = clone(data, shuffle(data.rows)[:the.Budget])
  tree = TREE(data1, data1.rows)
  treeShow(tree)                  
  print(":used", len(treeUsed(tree)), len(data.cols.x))
 
def eg__test(f: filename):
  "testing"
  data = DATA(csv(f))
  half = len(data.rows)//2
  Y = lambda r: disty(data,r)
  b4 = sorted(Y(r) for r in data.rows)
  win = lambda r: int(100*(1-(Y(r)-b4[0])/(b4[half]-b4[0]+1E-6)))
  wins, used = NUM(), 0
  for _ in range(60):
    rows = shuffle(data.rows)
    test, train = rows[half:], rows[:half][:the.Budget]
    tree = TREE(clone(data,train), train)
    used += len(treeUsed(tree))
    test.sort(key=lambda r: treeLeaf(tree,r).y.mu)
    add(wins, win(min(test[:the.Check], key=Y)))
  print(f"{round(wins.mu)} ,sd {round(sd(wins))} ,b4 {o(b4[half])}"
        f" ,lo {o(b4[0])} ,used {int(used/60)} ,B {the.Budget}",
        *[f"{s} {len(a)}" for s,a in
          dict(x=data.cols.x, y=data.cols.y, r=data.rows).items()],
        *f.split("/")[-2:], sep=" ,")
 
#--- main ------------------------------------------------------------
the= OBJ(**{k: cast(v) for k, v in re.findall(r"(\S+)=(\S+)", __doc__)})
random.seed(the.seed)

def main(settings,funs):
  args = iter(sys.argv[1:])
  for s in args:
    if f := funs.get(f"eg_{s[1:].replace('-','_')}"):
      run(f, *[t(next(args)) for t in f.__annotations__.values()])
    else:
      for k in settings:
        if k[0] == s[1]: settings[k] = cast(next(args, ""))

if __name__ == "__main__": main(the,globals())
