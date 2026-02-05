#!/usr/bin/env python3 
"""
ezr.py (v0.5): lightweight XAI for multi-objective optimization   
(c) 2025, Tim Menzies <timm@ieee.org>, MIT license      
[code](https://github.com/timm/ezr) :: 
[data](https://github.com/timm/moot)    

Options:
   
    -a  acq=near          label with (near|xploit|xplor|bore|adapt)
    -A  Any=4             on init, how many initial guesses?   
    -B  Budget=30         when growing theory, how many labels?   
    -C  Check=5           budget for checking learned model
    -D  Delta=smed        effect size test for cliff's delta
    -F  Few=128           sample size of data random sampling  
    -K  Ks=0.95           confidence for Kolmogorovâ€"Smirnov test
    -l  leaf=3            min items in tree leaves
    -m  m=1               Bayes low frequency param
    -p  p=2               distance co-efficient
    -s  seed=1234567891   random number seed   
    -f  file=../moot/optimize/misc/auto93.csv    data file 
    -h                     show help   

"""
from types import SimpleNamespace as o
from typing import Any, Iterator
import traceback, random, time, math, sys, re
   
sys.dont_write_bytecode = True
    
Qty  = int | float
Atom = Qty | str | bool
Row  = list[Atom]
Op   = (str,int,Atom)
    
big = 1e32

# ## Labeling ----------------------------------------------------------
def label(row:Row) -> Row: 
  "Stub. Ensure a row is labelled."
  return row

# ## Constructors ------------------------------------------------------
def Num(at=0,s=" "): 
  "Create a numeric column summarizer"
  return o(it=Num, at=at, txt=s, n=0, mu=0, m2=0, sd=0, 
           hi=-big, lo=big, best = 0 if s[-1] == "-" else 1)

def Sym(at=0,s=" "): 
  "Create a symbolic column summarizer"
  return o(it=Sym, at=at, txt=s, n=0, has={})

def Cols(names : list[str]) -> o:
  "Create column summaries from column names"
  all=[(Num if s[0].isupper() else Sym)(c,s) 
        for c,s in enumerate(names)]
  klass=None
  for col in all: 
    if col.txt[-1]=="!": klass=col
  return o(it=Cols, names = names, all = all, klass = klass,
           x = [col for col in all if col.txt[-1] not in "X-+"],
           y = [col for col in all if col.txt[-1] in "-+"])

def Data(src) -> o:
  "Create data structure from source rows"
  src = iter(src)
  return adds(src, o(it=Data, n=0, mid=None, rows=[], kids=[], 
                     ys=None, cols=Cols(next(src)))) 

def clone(data:Data, rows=None) -> o:
  "Create new Data with same columns but different rows"
  return adds(rows or [], Data([data.cols.names]))

# ## Update -----------------------------------------------------------
def adds(src, it=None) -> o:
  "Add multiple items to a summarizer"
  it = it or Num()
  [add(it,x) for x in src]
  return it

def sub(x:o, v:Any, zap=False) -> Any: 
  "Remove value from summarizer"
  return add(x,v,-1,zap)

def add(x: o, v:Any, inc=1, zap=False) -> Any:
  "incrementally update Syms,Nums or Datas"
  if v == "?": return v
  x.n += inc
  if   x.it is Sym: x.has[v] = inc + x.has.get(v,0)
  elif x.it is Num:
    x.lo, x.hi = min(v, x.lo), max(v, x.hi)
    if inc < 0 and x.n < 2:
      x.sd = x.m2 = x.mu = x.n = 0
    else:
      d     = v - x.mu
      x.mu += inc * (d / x.n)
      x.m2 += inc * (d * (v - x.mu))
      x.sd  = 0 if x.n < 2 else (max(0,x.m2)/(x.n-1))**.5
  elif x.it is Data:
    x.mid = None
    if inc > 0: x.rows += [v]
    elif zap: x.rows.remove(v) # slow for long rows
    [add(col, v[col.at], inc) for col in x.cols.all]
  return v

# ## Misc data functions ----------------------------------------------
def norm(num:Num, v:float) -> float:  
  "Normalize a value to 0..1 range"
  return  v if v=="?" else (v - num.lo) / (num.hi - num.lo + 1E-32)

def mids(data: Data) -> Row:
  "Get central tendencies of all columns"
  data.mid = data.mid or [mid(col) for col in data.cols.all]
  return data.mid

def mid(col: o) -> Atom:
  "Get central tendency of one column"
  return max(col.has, key=col.has.get) if col.it is Sym else col.mu

def divs(data:Data) -> float:
  "Return the central tendency for each column."
  return [div(col) for col in data.cols.all]

def div(col:o) -> float:
  "Return the central tendnacy for one column."
  if col.it is Num: return col.sd
  vs = col.has.values()
  N  = sum(vs)
  return -sum(p*math.log(p,2) for n in vs if (p:=n/N) > 0)

# ## Distance Calcs ---------------------------------------------------
def dist(src) -> float:
  "Calculate Minkowski distance"
  d,n = 0,0
  for v in src: n,d = n+1, d + v**the.p;
  return (d/n) ** (1/the.p)

def disty(data:Data, row:Row) -> float:
  "Distance from row to best y-values"
  return dist(abs(norm(c, row[c.at]) - c.best) for c in data.cols.y)

def distysort(data:Data,rows=None) -> list[Row]:
  "Sort rows by distance to best y-values"
  return sorted(rows or data.rows, key=lambda r: disty(data,r))

def distx(data:Data, row1:Row, row2:Row) -> float:
  "Distance between two rows using x-values"
  return dist(_aha(c, row1[c.at], row2[c.at])  for c in data.cols.x)

def _aha(col, a,b):
  "David Aha's distance function."
  if a==b=="?": return 1
  if col.it is Sym: return a != b
  a,b = norm(col,a), norm(col,b)
  a = a if a != "?" else (0 if b>0.5 else 1)
  b = b if b != "?" else (0 if a>0.5 else 1)
  return abs(a - b)

# ## Clustering --------------------------------------------------------
def distKpp(data, rows=None, k=20, few=None): #\n{100}#
  "Return centroids separated by distance squared (ish)"
  few = few or the.Few
  rows = rows or data.rows[:]
  random.shuffle(rows)
  out = [rows[0]]
  while len(out) < k:
    tmp = random.sample(rows, min(few,len(data.rows)))
    ws  = [min(distx(data, r, c)**2 for c in out) for r in tmp]
    p   = sum(ws) * random.random()
    for j, w in enumerate(ws):
      if (p := p - w) <= 0: 
          out += [tmp[j]]; break
  return out

def distProject(data,row,east,west,c=None):
  "Map row along a line east -> west."
  D = lambda r1,r2 : distx(data,r1,r2)
  c = c or D(east,west)  
  a,b = D(row,east), D(row,west)
  return (a*a +c*c - b*b)/(2*c + 1e-32)

def distFastmap(data,rows=None):
  "Sort rows along a line between 2 distant points."
  rows = rows or data.rows
  X = lambda r1,r2:distx(data,r1,r2)
  anywhere, *few = random.choices(rows, k=the.Few)
  here  = max(few, key= lambda r: X(anywhere,r))
  there = max(few, key= lambda r: X(here,r))
  c     = X(here,there)
  return sorted(rows, key=lambda r: distProject(data,r,here,there,c))

def distFastermap(data,rows=None, sway2=True):
  "Prune half the rows furthest from best distant pair."
  rows = shuffle(rows or data.rows)
  raw  = rows[the.Any:]
  out  = clone(data, rows[:the.Any])
  Y    = lambda r: disty(out,r)
  while len(out.rows) < the.Budget and len(raw) >= 2: 
    east, *rest, west = distFastmap(data,raw)
    add(out, east)
    add(out, west)
    n   = len(rest)//2
    raw = raw[:n] if Y(east) < Y(west) else raw[n:]
    if sway2 and len(raw) < 2:
      raw = shuffle([r for r in rows if r not in out.rows])
  return sorted(out.rows, key=Y)

# ## Likelihood -------------------------------------------------------
def like(i:o, v:Any, prior=0) -> float :
  "log probability of 'v' belong to the distribution in 'i'"
  if i.it is Sym:
    tmp = ((i.has.get(v,0) + the.m*prior) 
           / (sum(i.has.values())+the.m+1e-32))
    return math.log(max(tmp, 1e-32))
  else:
    ## Next Line added to resolve cases where i.sd == 0
    if i.sd == 0: return 0 if v == i.mu else 1E-32
    
    var = i.sd * i.sd + 1E-32
    log_nom = -1 * (v - i.mu) ** 2 / (2 * var)
    log_denom = 0.5 * math.log(2 * math.pi * var)
    return log_nom - log_denom

def likes(data:Data, row:Row, nall=100, nh=2) -> float:
  "How much does this DATA like row?"
  prior = data.n / (nall + 1e-32)
  log_prior = math.log(max(prior, 1e-32))
  tmp = [like(c, row[c.at]) for c in data.cols.x if row[c.at] != "?"]
  return log_prior + sum(tmp)    

# ## Active Learning --------------------------------------------------
def likely(data:Data, rows=None) -> list[Row]:
  "Find an 'x' most likely to be best. Add to xy. Repeat."
  rows = rows or data.rows
  x   = clone(data, shuffle(rows[:]))
  xy, best, rest = clone(data), clone(data), clone(data)

  # label anything
  for _ in range(the.Any): add(xy, label(sub(x, x.rows.pop())))

  # divide lablled items into best and rest
  xy.rows = distysort(xy); n = round(the.Any**.5)
  adds(xy.rows[:n], best); adds(xy.rows[n:], rest)

  # loop, labelling the best guess
  guess = nearer if the.acq=="near" else likelier
  while x.n > 2 and xy.n < the.Budget:
    add(xy, add(best, sub(x, label(guess(xy, best, rest, x)))))
    if best.n > (xy.n**.5):
      best.rows = distysort(xy,best.rows)
      while best.n > (xy.n**.5):
        add(rest, sub(best, best.rows.pop(-1)))
  return distysort(xy)

def nearer(xy, best:Data, rest:Data, x:Data) -> Row:
  "Remove from `x' any 1 thing more best-ish than rest-ish."
  for _ in range(the.Few):
    row = x.rows[ i := random.randrange(x.n) ]
    if distx(xy, mids(best), row) < distx(xy, mids(rest), row):
      return x.rows.pop(i)
  return x.rows.pop()

def likelier(_, best:Data, rest:Data, x:Data) -> Row:
  "Sort 'x by the.acq, remove first from 'x'. Return first."
  e, nall = math.e, best.n + rest.n
  p = nall/the.Budget
  q = {'xploit':0, 'xplor':1}.get(the.acq, 1-p)
  def _fn(row):
    b,r = e**likes(best,row,nall,2), e**likes(rest,row,nall,2)
    if the.acq=="bore": return b*b/(r+1e-32)
    return (b + r*q) / abs(b*q - r + 1e-32)
  first, *lst = sorted(x.rows[:the.Few*2], key=_fn, reverse=True)
  x.rows = lst[:the.Few] + x.rows[the.Few*2:] + lst[the.Few:] 
  return first

# ## Tree Generation ----------------------------------------------------
def treeSelects(row:Row, op:str, at:int, y:Atom) -> bool: 
  "Have we selected this row?"
  if (x:=row[at]) == "?" : return True
  if op == "<="          : return x <= y
  if op == "=="          : return x == y
  if op == ">"           : return x > y

  ## Adding Next line to support binary splits
  if op == "!="          : return x != y

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

# def _symCuts(at,xys,Y,Klass) -> (float, list[Op]):
#   "Cuts for symbolic column."
#   d = {}
#   for x, y in xys:
#     d[x] = d.get(x) or Klass()
#     add(d[x], y)
#   print(d)
#   input()
#   here = sum(ys.n/len(xys) * div(ys) for ys in d.values())
#   return here, [("==", at, x) for x in d]

## Re-writing _symCuts to return binary splits
def _symCuts(at, xys, Y, Klass) -> (float, list[Op]):
    "Cuts for symbolic column (binary split)."
    unique_vals = set(x for x, _ in xys)
    spread, cuts = big, []
    for val in unique_vals:
        left, right = Klass(), Klass()
        [add(left if x == val else right, y) for x, y in xys]
        if left.n >= the.leaf and right.n >= the.leaf:
            now = (left.n * div(left) + right.n * div(right)) / (left.n + right.n)
            if now < spread:
                spread, cuts = now, [("==", at, val), ("!=", at, val)]      
    return spread, cuts


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

def ezrmain():
  "top-level call"
  main(the,globals()); random.seed(the.seed); eg__demo()

# ## Start-up ---------------------------------------------------------
the = o(**{k:coerce(v) for k,v in re.findall(r"(\w+)=(\S+)",__doc__)})
if __name__ == "__main__": ezrmain();