#!/usr/bin/env python3 -B
"""
n2m.py: tiny AI. multi objective, explainable, AI
(c) 2025 Tim Menzies, <timm@ieee.org>. MIT license

Options, with (defaults):

  -f   file       : data name (../../moot/optimize/misc/auto93.csv)
  -r   rseed      : set random number rseed (123456781)
  -R   Rnd        : round floats in pretty print (2)
  -F   Few        : a few rows to explore (128)
  -l   leaf       : tree learning: min leaf size (2)
  -p   p          : distance calcs: set Minkowski coefficient (2)

Bayes:
  -k   k          : bayes hack for rare classes (1)
  -m   m          : bayes hack for rare attributes (2)

Active learning:
  -a   acq        : xploit or xplore or adapt (xploit)  
  -A   Assume     : on init, how many initial guesses? (4)
  -B   Build      : when growing theory, how many labels? (20)
  -C   Check      : when testing, how many checks? (5)

Stats:
  -S   Signif     : significance threshold (0.95)
  -b   bootstrap  : num. bootstrap samples (512)
  -C   Cliffs     : effect size threshold (0.197)
 """

import traceback,random,math,sys,re
sys.dont_write_bytecode = True 

BIG=1E32
isa=isinstance

class o:
  "Mutatable struct. Named slots. Dot slot access. With pretty print."
  __init__ = lambda i, **d: i.__dict__.update(**d)
  __repr__ = lambda i: see(i.__dict__)

def atom(x):
  "Coerce string to int,float, bool, string"
  for fn in (int, float):
    try: return fn(x)
    except: pass
  x = x.strip()
  return x == "true" if x in ("true", "false") else x

the = o(**{k:atom(v) for k,v in
           re.findall(r"-\w+\s+(\w+)[^\(]*\(\s*([^)]+)\)", __doc__)})

# Sample data ----------------------------------------------------------------

EXAMPLE="""
Max_spout, hashing, Spliters, Counters, Throughput+, Latency-
1        , off    , 1       , 1       , 4255.3     , 2.5621
1        , on     , 1       , 3       , 4160.1     , 2.6057
1        , off    , 1       , 6       , 4089.5     , 2.55
1        , on     , 1       , 9       , 4156.9     , 2.5688
1        , on     , 1       , 12      , 4013.8     , 2.5474
1        , off    , 1       , 15      , 4194.1     , 2.5676
1        , on     , 1       , 18      , 3964.2     , 2.5503
1        , off    , 2       , 1       , 4294.7     , 4.7793
1        , on     , 2       , 3       , 4343.6     , 2.381
1        , off    , 2       , 6       , 4423.6     , 2.3538
1        , on     , 2       , 9       , 4369.6     , 2.4306
1        , off    , 2       , 12      , 4288.1     , 2.3965
1        , on     , 2       , 15      , 4291.2     , 2.4462
1        , off    , 2       , 18      , 4236.2     , 2.4647
1        , on     , 3       , 1       , 4980.3     , 2.1598
1        , off    , 3       , 3       , 5058.6     , 3.5506
1        , on     , 3       , 6       , 4836.7     , 2.1283
1        , off    , 3       , 9       , 4786.9     , 2.1468
1        , on     , 3       , 12      , 4528.8     , 3.0358
1        , off    , 3       , 15      , 4767.6     , 2.2173
1        , on     , 3       , 18      , 4949.1     , 2.1277
1        , off    , 6       , 1       , 4904.2     , 2.1626
1        , on     , 6       , 3       , 5151       , 2.0815
1        , off    , 6       , 6       , 4847.1     , 2.1376
1        , on     , 6       , 9       , 4891.9     , 2.1503
1        , off    , 6       , 12      , 4871       , 2.2277
1        , on     , 6       , 15      , 4645.8     , 2.1468
1        , off    , 6       , 18      , 4688.1     , 2.2277
10       , on     , 1       , 1       , 8226.1     , 13.733
10       , off    , 1       , 3       , 12697      , 9.2121
10       , on     , 1       , 6       , 14870      , 8.1247
10       , off    , 1       , 9       , 14807      , 7.5491
10       , on     , 1       , 12      , 15374      , 7.1335
10       , off    , 1       , 15      , 16019      , 7.3717
10       , on     , 1       , 18      , 15103      , 7.3965
10       , on     , 2       , 3       , 14169      , 8.1471
10       , off    , 2       , 6       , 18462      , 6.481
10       , off    , 2       , 12      , 20233      , 5.7734
10       , on     , 2       , 15      , 19505      , 5.6023
10       , on     , 3       , 1       , 8219.4     , 13.865
10       , off    , 3       , 3       , 14591      , 7.6695
10       , off    , 3       , 9       , 17161      , 6.5827
10       , on     , 3       , 12      , 17130      , 6.2694
10       , on     , 3       , 18      , 16140      , 7.2948
10       , on     , 6       , 3       , 16238      , 7.0838
10       , off    , 6       , 6       , 20089      , 5.2988
10       , on     , 6       , 9       , 20066      , 5.0202
10       , on     , 6       , 15      , 19157      , 5.0006
100      , off    , 1       , 9       , 18652      , 62.08
100      , on     , 1       , 12      , 20872      , 55.886
100      , off    , 1       , 15      , 19875      , 53.539
100      , off    , 2       , 1       , 8746       , 117.57
100      , off    , 2       , 6       , 20814      , 53.103
100      , off    , 2       , 12      , 26373      , 40.169
100      , on     , 2       , 15      , 25948      , 46.001
100      , off    , 2       , 18      , 25565      , 39.447
100      , off    , 3       , 3       , 16941      , 65.185
100      , on     , 3       , 12      , 20821      , 56.731
100      , on     , 3       , 18      , 21234      , 53.927
100      , off    , 6       , 1       , 9214.4     , 116.13
100      , on     , 6       , 3       , 20359      , 55.501
100      , on     , 6       , 9       , 23142      , 37.915
100      , off    , 6       , 12      , 24892      , 41.478
100      , on     , 6       , 15      , 23675      , 32.286
1000     , on     , 1       , 1       , 10038      , 1063.6
1000     , off    , 1       , 3       , 20050      , 553.74
1000     , on     , 1       , 6       , 22015      , 511.62
1000     , on     , 1       , 12      , 21808      , 470.82
1000     , off    , 1       , 15      , 23497      , 439.35
1000     , off    , 2       , 1       , 8666.8     , 1239.5
1000     , on     , 2       , 3       , 22289      , 518.71
1000     , on     , 2       , 9       , 28129      , 398.1
1000     , off    , 2       , 12      , 32399      , 332.68
1000     , on     , 3       , 1       , 9973.9     , 1105.8
1000     , off    , 3       , 3       , 19036      , 595.91
"""
#------------------------------------------------------------------
class Summary(o): pass

#----------------
class Sym(Summary):
  def __init__(i, inits=[], at=0, txt=""):
    i.n   = 0     ## items kept
    i.at  = at    ## column position 
    i.txt = txt   ## column name
    i.has = {}    ## counts of symbols seen
    i.adds(inits)

#----------------
class Num(Summary):
  def __init__(i, inits=[], at=0, txt="", rank=0):
     i.n = i.mu = i.m2 = i.sd = 0    ## items kept  
     i.at   = at   ## column position
     i.txt  = txt  ## column name
     i.hi   = -BIG ## biggest seen
     i.lo   =  BIG ## smallest seen
     i.rank = rank ## used only by stats
     i.heaven = 0 if  txt.endswith("-") else 1 ## goal. 0,1=min,max
     i.adds(inits)

  def norm(i,v): 
    "Normalize 0..1 for min..max."
    return v if v=="?" else (v-i.lo)/(i.hi-i.lo+1/BIG)

#-----------------
class Data(Summary):
  def __init__(i,inits=[]):
    inits   = iter(inits)
    cols    = _cols(next(inits))
    i.n     = 0            ## items kept
    i._rows = []           ## rows
    i.cols  = cols         ## summaries of rows
    i.adds(inits)

  def clone(i, inits=[]):
    "Make a new Data with same structre as self."
    return Data([i.cols.names]+inits)

def _cols(names):
  "Factory. List[str] -> Dict[str, List[ Sym | Num ]]"
  cols= o(names = names, ## all the column names
          klass = None,  ## Target for classification
          all   = [],    ## all columns
          x     = [],    ## also, hold independents here
          y     = [])    ## also, hold dependent here
  cols.all = [_col(at,name,cols) for at,name in enumerate(cols.names)]
  return cols

def _col(at,name,cols): 
  col = (Num if name[0].isupper() else Sym)(txt=name, at=at) 
  if name[-1] != "X":
    if name[-1] == "!": cols.klass = col
    (cols.y if name[-1] in "+-" else cols.x).append(col)
  return col 

#------------------------------------------------------------------
_last = None
def bind(fn=None, doc=None):
  """Make fn a method of the class of the first arg. This lets me
  group toether in the code related methods from different classes.
  Kind of like extend methosd in C#/Kotlin or open class methods 
  in Ruby, or any methods in Julia or Lua"""
  def D(f):
    global _last; _last = f.__doc__ = doc or _last
    if (c := next(iter(f.__annotations__.values()), None)): 
      setattr(c, f.__name__, f)
    return f
  return D(fn) if callable(fn) else D

#------------------
@bind("Update")
def add(i:Summary,v, inc=1, zap=False):
  if v != "?":
    i.n += inc
    i._add(v,inc,zap) # implemented by subclass 
  return v

@bind("Do many updates")
def adds(i:Summary, lst=[]): [i.add(x) for x in lst]; return i

@bind("'sub' is just a negative `add`")
def sub(i:Summary, v, inc= -1,zap=False): return i.add(v,inc,zap)

#--------------------------------------------
@bind("Internal methods to update a Summary")
def _add(i:Sym,s,inc,_):
  i.has[s] = i.has.get(s,0) + inc

@bind
def _add(i:Num,n, inc, _):
  i.lo, i.hi = min(n,i.lo), max(n,i.hi)
  if inc < 0 and i.n < 2: 
    i.sd = i.m2 = i.mu = i.n = 0
  else:
    d     = n - i.mu
    i.mu += inc * (d / i.n)
    i.m2 += inc * (d * (n - i.mu))
    i.sd  = 0 if i.n <= 2 else (max(0,i.m2)/(i.n-1))**.5

@bind
def _add(i:Data,row,inc,zap):  
  if inc > 0 : i._rows.append(row) 
  elif zap   : i._rows.remove(row) # slow for large lists
  for col in i.cols.all: col.add(row[col.at], inc)

#-----------------------
@bind("Central tendancy.")
def mid(i:Num) : return i.mu

@bind
def mid(i:Sym): return max(i.has, key=i.has.get)

@bind
def mid(i:Data) : return [c.mid() for c in i.cols.all]

#--------------------------------------
@bind("Deviation from central tendancy.")
def spread(i:Num) : return i.sd

@bind
def spread(i:Sym):
  d = i.has
  return -sum(p*math.log(p,2) for v in d.values() if (p:=v/i.n) > 0)

@bind
def spread(i:Data): return [c.spread() for c in i.cols.all]

#-------------------------------------------------------------------
@bind("Distance between numeric or symbolic atoms.")

def _dist(vs):
  "Minkowski distance."
  s, n = 0, 1/BIG
  for x in vs:
    n += 1
    s += abs(x)**the.p
  return (s / n)**(1/the.p)

@bind("Distance between 2 things")
def xdist(_:Sym, u,v):
  return 1 if u=="?" and v=="?" else u !=v

@bind
def xdist(i:Num, u,v):
  if u=="?" and v=="?": return 1
  u = i.norm(u)
  v = i.norm(v)
  u = u if u != "?" else (0 if v > .5 else 1)
  v = v if v != "?" else (0 if u > .5 else 1)
  return abs(u - v)

@bind
def xdist(i:Data,r1,r2): 
  return _dist(c.xdist(r1[c.at], r2[c.at]) for c in i.cols.x)

@bind("Return rows, sorted by xdist to row r1.")
def xdists(i:Data, r1, rows=None):
  return sorted(rows or i._rows, key=lambda r2: i.xdist(r1,r2))

@bind("Distance dependent variables to heaven.")
def ydist(i:Data,row):
  return _dist((c.norm(row[c.at]) - c.heaven) for c in i.cols.y)

@bind("Return rows, sorted by ydist to heaven.")
def ydists(i:Data, rows=None):
  return sorted(rows or i._rows, key=lambda row: i.ydist(row))

@bind("Find k centroids d**2 away from existing centoids.")
def kpp(i:Data, k=None, rows=None):
  row, *rows = shuffle(rows or i._rows)[:the.Few]
  out = [row]
  while len(out) < (k or the.Build):
     ws = [min(i.xdist(r, c)**2 for c in out) for r in rows]
     out.append(random.choices(rows, weights=ws)[0])
  return out

def kmeans(i, rows, centroids, n=10):
  errs = []
  for _ in range(n):
    new, err = {}, 0
    for row in rows:
      c = min(centroids, key=lambda z: i.xdist(z, row))
      now = new[id(c)] = new.get(id(c)) or i.clone()
      now.add(row)
      err += i.xdist(row, c)
    errs += [err / len(rows)]
    centroids = [new[k].mid() for k in new]
  return centroids, errs

#-----------------------------------------------------------------
class Abcd:
  def __init__(i, a=0): i.a, i.b, i.c, i.d = a, 0, 0, 0
  def add(i, want, got, x):
    if x == want:   i.d += (got == want); i.b += (got != want)
    else:           i.c += (got == x);    i.a += (got != x)
    p = lambda y, z: int(100 * y / (z or 1e-32))
    i.pd   = p(i.d,       i.d + i.b)
    i.pf   = p(i.c,       i.c + i.a)
    i.prec = p(i.d,       i.d + i.c)
    i.acc  = p(i.d + i.a, i.a + i.b + i.c + i.d)

def abcds(want, got, state=None):
  state = state or o(stats={}, total=0)
  for L in (want, got):
    state.stats[L] = state.stats.get(L) or Abcd(state.total)
  for x, s in state.stats.items():
    s.add(want, got, x)
  state.total += 1
  return state

def same(a, b): 
  return cliffs(a, b) and bootstrap(a, b)

#--------------------------------------------------------------------
def same(cliff=None, n=None, conf=None):
  n     = n or the.bootstrap
  conf  = conf or the.Boots
  cliff = cliff or the.Cliifs
  return lambda xs,ys:cliffs(xs,ys,cliff) and bootstrap(xs,ys,n,conf)

def cliffs(xs,ys, cliff):
  "Effect size. Tb1 of doi.org/10.3102/10769986025002101"
  n,lt,gt = 0,0,0
  for x in xs:
    for y in ys:
      n += 1
      if x > y: gt += 1
      if x < y: lt += 1
  return abs(lt - gt)/n  < cliff # 0.197)  #med=.28, small=.11

# Non-parametric significance test from 
# Chp20,doi.org/10.1201/9780429246593. Distributions are the same 
# if, often, we `_see` differences just by chance. We center both 
# samples around the combined mean to simulate what data might look 
# like if vals1 and vals2 came from the same population.
def bootstrap(xs, ys, bootstrap,conf):
  _see = lambda i,j: abs(i.mu - j.mu) / (
                     (i.sd**2/i.n + j.sd**2/j.n)**.5 +1E-32)
  x,y,z = Num(xs+ys), Num(xs), Num(ys)
  yhat  = [y1 - mid(y) + mid(x) for y1 in xs]
  zhat  = [z1 - mid(z) + mid(x) for z1 in ys]
  n     = 0
  for _ in range(bootstrap):
    n += _see(Num(random.choices(yhat, k=len(yhat))),
              Num(random.choices(zhat, k=len(zhat)))) > _see(y,z)
  return n / bootstrap >= (1- conf)

def sk(rxs, same, eps=0, reverse=False):
  "Dict[key,List[float]] -> List[Num(key,rank,mu,sd)]" 
  def _cut(items):
    cut  = None
    N    = sum(num.n for num, _ in items)
    M    = sum(num.mu * num.n for num, _ in items) / N
    best = s1 = n1 = 0
    for j, (num, _) in enumerate(items[:-1]):
      n, s   = num.n, num.mu * num.n
      n1, s1 = n1 + n, s1 + s
      m1     = s1 / n1
      n2     = N - n1
      m2     = (M * N - s1) / n2
      gain   = (n1 * (m1 - M)**2 + n2 * (m2 - M)**2) / N
      if abs(m1 - m2) > eps and gain > best:
        best, cut = gain, j+1
    return cut

  def _div(items, rank=0):
    if (cut := _cut(items)) is not None:
      L, R = items[:cut], items[cut:]
      a    = [x for _, vals in L for x in vals]
      b    = [x for _, vals in R for x in vals]
      if not same(a, b):
        return _div(R, _div(L, rank) + 1)
    for num, _ in items:
      num.rank = rank
    return rank

  nums = sorted([(Num(vals, txt=k),vals) for k,vals in rxs.items()],
                key=lambda x: x[0].mu, reverse=reverse)
  _div(nums)
  return [num for num, _ in nums]

#-----------------------------------------------------------------
ops = {'<=' : lambda x,y: x <= y,
       "==" : lambda x,y: x == y,
       '>'  : lambda x,y: x >  y}

def selects(row,op,at,y): x=row[at]; return x=="?" or ops[op](x,y) 

@bind("what cuts most reduces spread?")
def cuts(i:Sym,rows,Y,Klass): 
  n,d = 0,{}
  for row in rows:
    if (x := row[i.at]) != "?":
      n = n + 1
      d[x] = d[x] if x in d else Klass()
      add(d[x], Y(row))
  return o(div = sum(c.n/n * spread(c) for c in d.values()),
           hows = [("==",i.at, k) for k,_ in d.items()])

@bind
def cuts(i:Num,rows,Y,Klass):
  out = None
  b4, lhs, rhs = None, Klass(), Klass()
  xys = [(r[i.at], add(rhs, Y(r))) for r in rows if r[i.at] != "?"]
  for x, y in sorted(xys, key=lambda xy: xy[0]):
    if x != b4:
      if the.leaf <= lhs.n <= len(xys) - the.leaf:
        now = (lhs.n * lhs.sd + rhs.n * rhs.sd) / len(xys)
        if not out or now < out.div:
          out= o(div=now,hows=[("<=",i.at,b4), (">",i.at,b4)])
    add(lhs, sub(rhs,y))
    b4 = x
  return out

@bind("Split data on best cut. Recurse on each split.")
def tree(i:Data, Klass=Num, Y=None, how=None):
  Y      = Y or (lambda row: ydist(i,row))
  i.kids = []
  i.how  = how
  i.ys   = Num(Y(row) for row in i._rows)
  if i.n >= the.leaf:
    tmp = [x for c in i.cols.x if (x := c.cuts(i._rows,Y,Klass))]    
    if tmp:
      for how1 in min(tmp,   key=lambda cut: cut.div).hows:
        #for how1 in sorted(tmp, key=lambda cut: cut.div)[0].hows:
        rows1 = [row for row in i._rows if selects(row, *how1)]
        if the.leaf <= len(rows1) < i.n:
          i.kids += [i.tree(i.clone(rows1), Klass, Y, how1)]  
  return i

@bind(" Iterate over all nodes.")
def nodes(i:Data , lvl=0, key=None): 
  yield lvl, i
  for j in (sorted(i.kids, key=key) if key else i.kids):
    yield from j.nodes(lvl + 1, key=key)

@bind(" Return leaf selected by row.")
def leaf(i:Data,row):
  for j in i.kids or []:
    if selects(row, *j.how): 
      return j.leaf(row)
  return i

@bind("Show Tree")
def showTree(i:Data, key=lambda d: d.ys.mu):
  s, ats = i.ys, {}
  win = lambda x: int(100 * (1 - ((x - s.lo) / (s.mu-s.lo+1e-32))))
  print(f"{'d2h':>4} {'win':>4} {'n':>4}")
  print(f"{'----':>4} {'----':>4} {'----':>4}")
  for lvl, data in i.nodes(key=key):
    leafp = not data.kids
    op, at, y = data.how if lvl else ('', '', '')
    name = i.cols.all[at].txt if lvl else ''
    expl = f"{name} {op} {y}" if lvl else ''
    indent = '|  ' * (lvl - 1)
    print(f"{data.ys.mu:4.2f} {win(data.ys.mu):4} {data.n:4}    "
          f"{indent}{expl}{';' if leafp else ''}")
    if lvl: ats[at] = 1
  print(', '.join(i.cols.names[at] for at in sorted(ats)))

# # Pretty print a tree
# def show(data, key=lambda z:z.ys.mu):
#   stats = data.ys
#   win = lambda x: int(100*(1 - ((x-stats.lo)/(stats.mu - stats.lo))))
#   print(f"{'d2h':>4} {'win':>4} {'n':>4}  ")
#   print(f"{'----':>4} {'----':>4} {'----':>4}  ")
#   ats={}
#   for lvl, node in nodes(data, key=key):
#     leafp = len(node.kids)==0
#     post = ";" if leafp else ""
#     xplain = ""
#     if lvl > 0:
#       op,at,y = node.how
#       ats[at] = 1
#       xplain = f"{data.cols.all[at].txt} {op} {y}"
#     indent = (lvl - 1) * "|  "
#     print(f"{node.ys.mu:4.2f} {win(node.ys.mu):4} {node.n:4}    "
#           f"{indent}{xplain}{post}")
#   print(', '.join(sorted([data.cols.names[at] for at in ats])))
#
#-----------------------------------------------------------------
def shuffle(lst):
  random.shuffle(lst)
  return lst

def csv(src):
  for line in src:
    if line:
      yield [atom(x) for x in line.strip().split(',')]

lines=lambda s: (line for line in s.splitlines())

def doc(file):
  with open(file, "r") as f:
    for line in f: yield(line)

def say(v): print(see(v)); return v

def see(v):
  "Converts most things to strings."
  it = type(v)
  if it is float : return _cF(v) 
  if it is dict  : return _cD(v)
  if callable(v) : return v.__name__ + "()"
  if it is list  : return "{" + ", ".join(map(see, v)) + "}"
  if hasattr(v,"__dict__"): 
    return v.__class__.__name__ + see(v.__dict__)
  return str(v)

def _c(k) : return not (isa(k,str) and k[0] == "_")
def _cD(v): return see([f":{k} {see(v[k])}" for k in v if _c(k)])
def _cF(v): return str(int(v)) if v==int(v) else f"{v:.{the.Rnd}g}"

#--------------------------------------------------------------------
def cli(d):
  for k, v in d.items():
    for c, arg in enumerate(sys.argv):
      if arg == "-" + k[0]:
        d[k] = atom("False" if str(v) == "True" else (
                    "True" if str(v) == "False" else (
                    sys.argv[c+1] if c<len(sys.argv)-1 else str(v))))

def run(fn,x=None):
  try:  
    print("\n# "+(fn.__doc__ or ""))
    random.seed(the.rseed)
    fn(x)
  except Exception as _:
    tb = traceback.format_exc().splitlines()[4:]
    return sys.stdout.write(
            "\n".join([f"\033[31m{x}\033[0m" for x in tb])+"\n")

def main(fns):
  cli(the.__dict__)
  for i, s in enumerate(sys.argv[1:]):
    if fn := fns.get("eg" + s.replace("-", "_")):
      x = None if i==len(sys.argv[1:]) - 1 else atom(sys.argv[i+2])
      run(fn, x)
