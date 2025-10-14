#!/usr/bin/env python3 -B 
from math import sqrt
import traceback, random, time, sys, re
from types import simplenamespace as obj

the=obj(Budget=30, Check=5, Delta='smed', Ks=.95, seed=42,
        file="../moot/optimize/misc/auto93.csv")

BIG = 1e32

### Constructors ------------------------------------------------------
def Num(at=0,s=" "): return o(it=Num, at=at, txt=s, n=0, mu=0, m2=0, sd=0, 
                              hi=-big, lo=big, best=s[-1] != "-")

def Sym(at=0,s=" "): return o(it=Sym, at=at, txt=s, n=0, has={})

def Cols(names):
  all = [(Num if s[0].isupper() else Sym)(i,s) for i,s in enumerate(names)]
  return obj(it=Cols, names=names, all=all,
             y = [col for col in all if col.txt[-1]     in "-+"],
             x = [col for col in all if col.txt[-1] not in "-+X"])

def Data(src):
  src = iter(src)
  return adds(src, o(it=Data, n=0, rows=[], cols=Cols(next(src)))) 

def clone(data:Data, rows=None) -> o:
  return adds(rows or [], Data([data.cols.names]))

### Update -----------------------------------------------------------
def adds(src, it=None) -> o:
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
def main(data):
  n = len(data)//2
  train, holdout = data.rows[:n], data.rows[n:]
  model = rules(data,train)

def rules(data,rows):
  Y = lambda r: disty(data,r)
  n = int(sqrt(length(rows)))
  rows = rows.sort(key=Y)

def bestRangeSym(i, j):
  n = i.n + j.n
  return max((i.has.get(k,0) - j.has.get(k,0))/n, i.at, k, k)
             for k in i.has + j.has)[1:]

def bestRangeNum(i, j):
  if i.mu > j.mu: i, j = j, i
  cdf = lambda t, x: 1/(1 + exp(-1.704*(x - t.mu)/t.sd))
  if i.sd == j.sd: 
    x = (i.mu + j.mu) / 2
    return cdf(i, x), i.at, -BIG, x
  a = j.sd**2 - i.sd**2
  b = 2*(i.mu*j.sd**2 - j.mu*i.sd**2)
  c = j.mu**2*i.sd**2 - i.mu**2*j.sd**2 + 2*i.sd**2*j.sd**2*sqrt(j.sd/i.sd)
  d = sqrt(b**2 - 4*a*c)
  x1, x2 = (-b - d)/(2*a), (-b + d)/(2*a)
  lo = x1 if cdf(i, x1) >= .05 else -BIG
  hi = x2 if cdf(i, x2) <= .95 else BIG
  return cdf(i, hi) - cdf(i, lo), i.at, lo, hi

# ## Misc data functions ----------------------------------------------
def norm(num:Num, v:float) -> float:  
  "Normalize a value to 0..1 range"
  return  v if v=="?" else (v - num.lo) / (num.hi - num.lo + 1E-32)

# ## Distance Calcs ---------------------------------------------------
def dist(src):
  d,n = 0,0
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

# ## Tree Generation ----------------------------------------------------
def selects(row, op, at, y): 
  if (x:=row[at]) == "?" : return True
  if op == "<="          : return x <= y
  if op == "=="          : return x == y
  if op == ">"           : return x > y

def Tree(data, rows=None, Y=None, Klass=Num, how=None):
  "Create tree from list of lists"
  rows = rows or data.rows
  Y    = Y or (lambda row: disty(data,row))
  tree = o(rows=rows, how=how, kids=[], 
           mu=mid(adds(Y(r) for r in rows)))
  if len(rows) >= the.leaf:
    spread, cuts = min(treeCuts(c,rows,Y,Klass) for c in data.cols.x)
    if spread < big:
      for cut in cuts:
        subset = [r for r in rows if treeSelects(r, *cut)]
        if the.leaf <= len(subset) < len(rows):
          tree.kids += [Tree(data, subset, Y, Klass, cut)]
  return tree

def treeCuts(col, rows, Y:callable, Klass:callable):
  "Return best cut for column at position 'at'"
  xys = sorted([(r[col.at], Y(r)) for r in rows if r[col.at] != "?"])
  return (_symCuts if col.it is Sym else _numCuts)(col.at,xys,Y,Klass)

def _symCuts(at,xys,Y,Klass) -> (float, list[Op]):
  "Cuts for symbolic column."
  d = {}
  for x, y in xys:
    d[x] = d.get(x) or Klass()
    add(d[x], y)
  here = sum(ys.n/len(xys) * div(ys) for ys in d.values())
  return here, [("==", at, x) for x in d]

def _numCuts(at,xys,Y,Klass) -> (float, list[Op]):
  "Cuts for numeric columns."
  spread, cuts, left, right = big, [], Klass(), Klass()
  [add(right,y) for _, y in xys]
  for i, (x, y) in enumerate(xys[:-1]):
    add(left, sub(right, y))
    if x != xys[i+1][0]:
      if the.leaf <= i < len(xys) - the.leaf:
        now = (left.n*div(left) + right.n*div(right)) / (left.n+right.n)
        if now < spread:
          spread = now
          cuts = [("<=", at, x), (">", at, x)]
  return spread, cuts

# ## Tree Processing -------------------------------------------------
def treeLeaf(tree, row):
  "Find which leaf a row belongs to"
  for kid in tree.kids:
    if treeSelects(row, *kid.how): return treeLeaf(kid, row)
  return tree

def treeNodes(tree, lvl=0):
  "Iterate over all tree nodes"
  yield lvl, tree
  for kid in sorted(tree.kids, key=lambda kid: kid.mu):
    yield from treeNodes(kid, lvl + 1)

def treeShow(data,tree,win=None):
  "Display tree structure with Y means"
  win = win or (lambda v:int(100*v))
  n   = {s:0 for s in data.cols.names}
  for lvl, node in treeNodes(tree):
    if lvl == 0: continue
    op, at, y = node.how
    indent = '|  ' * (lvl - 1)
    rule = f"if {data.cols.names[at]} {op} {y}"
    n[data.cols.names[at]] += 1
    leaf = ";" if not node.kids else ""
    print(f"n:{len(node.rows):4}   win:{win(node.mu):5}     ",end="")
    print(f"{indent}{rule}{leaf}")
  print("\nUsed: ",*sorted([k for k in n.keys() if n[k]>0],
                           key=lambda k: -n[k]))

# ## Misc Utils ------------------------------------------------------
def fyi(s, end=""):
  "write the standard error (defaults to no new line)"
  print(s, file=sys.stderr, flush=True, end=end)

def coerce(s:str) -> Atom:
  "coerce a string to int, float, bool, or trimmed string"
  for fn in [int,float]:
    try: return fn(s)
    except Exception as _: pass
  s = s.strip()
  return {'True':True,'False':False}.get(s,s)

def csv(file: str ) -> Iterator[Row]:
  "Returns rows of a csv file."
  with open(file,encoding="utf-8") as f:
    for line in f:
      if (line := line.split("%")[0]):
        yield [coerce(s) for s in line.split(",")]

def shuffle(lst:list) -> list:
  "shuffle a list, in place"
  random.shuffle(lst); return lst

def main(settings : o, funs: dict[str,callable]) -> o:
  "from command line, update config find functions to call"
  for n,s in enumerate(sys.argv):
    if (fn := funs.get(f"eg{s.replace('-', '_')}")):
      try: 
        random.seed(settings.seed); fn()
      except Exception as e: 
        print("Error:", e); traceback.print_exc()
    else:
      for key in vars(settings):
        if s=="-"+key[0]: 
          settings.__dict__[key] = coerce(sys.argv[n+1])

# ## Demos ------------------------------------------------------------
def eg__demo():
  "The usual run"
  data = Data(csv(the.file))
  print("\nFile:\t",the.file)
  print("Rows:\t",len(data.rows))
  print("X:\t",len(data.cols.x))
  print("Y:\t",len(data.cols.y),*[c.txt for c in data.cols.y])
  print(" ")
  b4   = adds(disty(data,row) for row in data.rows)
  win  = lambda v: int(100*(1 - (v - b4.lo)/(b4.mu - b4.lo)))
  best = lambda rows: win(disty(data, distysort(data,rows)[0]))
  half = len(data.rows) // 2
  data.rows = shuffle(data.rows)
  train, holdout = data.rows[:half], data.rows[half:]
  labels = likely(clone(data, train))
  tree   = Tree(clone(data, labels))
  treeShow(data, tree,win)
  print("Best train:",best(labels), "hold-out:",
         best(sorted(holdout, 
              key=lambda row: treeLeaf(tree,row).mu)[:the.Check]))

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
  if callable(x)      : x= x.__name__
  elif type(x) is obj : x= "{"+" ".join(f":{k} {o(x[k])}" for k in vars(x))+"}"
  return str(x)

def same(x:list[Qty], y:list[Qty],Ks=0.95,Delta="smed") -> bool: 
  "True if x,y indistinguishable and differ by just a small effect."
  x, y = sorted(x), sorted(y)
  n, m = len(x), len(y)
  def _cliffs():
    "How frequently are x items are gt,lt than y items?"
    gt = sum(a > b for a in x for b in y)
    lt = sum(a < b for a in x for b in y)
    return abs(gt - lt) / (n * m)
  def _ks():
    "Return max distance between cdf."
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
          the.__dict__[key] = coerce(sys.argv[n+1])
  main()
