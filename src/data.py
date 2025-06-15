"""
core: a tiny tool for classification and regression
(c) 2025 Tim Menzies, <timm@ieee.org>. MIT license

Options:
  -f file     data name (../../moot/optimize/misc/auto93.csv)
  -r rseed    set random number rseed (123456781)
  -F Few      a few rows to explore (128)
  -K K        neighborhood size (3)
  -p p        distance calcs: set Minkowski coefficient (2)
 """
# Must: functions, not classes; max line length = 68 chars
# Should: functions 5 lines or less
import random,math,sys,re
sys.dont_write_bytecode = True

#-- utils ---------------------------------------------------------
BIG=1E32

def cat(v):
  "Pretty print most things."
  if callable(v) : return v.__name__ + "()"
  it = type(v)
  if it is float : return str(int(v)) if v == int(v) else f"{v:.3g}"
  if it is list  : return "{" + ", ".join(map(cat, v)) + "}"
  if it is dict  : return cat([f":{k} {cat(v[k])}" for k in v
                              if not k.startswith("_")])
  return str(v)

class o:
  "Easy init a mutated struct with named slots and x.slot access."
  __init__ = lambda i, **d: i.__dict__.update(**d)
  __repr__ = lambda i: cat(i.__dict__)

def atom(x):
  "Coerce string to int,float, bool, string"
  for fn in (int, float):
    try: return fn(x)
    except: pass
  x = x.strip()
  return x == "true" if x in ("true", "false") else x

def doc(file):
  "Iterate thorugh all lines in a file."
  with open(file, 'r', newline='', encoding='utf-8') as f:
    for line in f: yield line

def csv(src):
  "Iterate thorugh all lines in a src."
  for line in src:
    if (line := line.strip()) and not line.startswith("#"):
      yield [atom(s) for s in line.strip().split(',')]
       
def settings(txt):
  "Extract flag=default from strings like our doc string"
  seen = {}
  for k,v in re.findall(r"-\w+\s+(\w+)[^\(]*\(\s*([^)]+)\)",txt):
    assert k not in seen, f"duplicate flag for setting '{k}'"
    seen[k] = atom(v)
  return o(**seen)

def adds(lst,i): 
  "Bulk addits."
  [add(i,x) for x in lst]; return i

def shuffle(lst):
  "Return lst, with contents shuffled in place."
  random.shuffle(lst)
  return lst

def uniform(lst,k,fn):
  "Return average."
  return sum(fn(x) for x in lst[:k])/ len(lst)

def triangle(lst,k,fn):
 "Sort by d, take first k, return weighted v scores ranks."
 wts = [k - i for i in range(k)]
 return sum(w*fn(x) for x,w in zip(lst[:k],wts)) / sum(wts)

class Abcd:
  def __init__(i, a): 
    i.a = a; i.b = i.c = i.d = i.pd = i.pf = i.prec = i.acc = 0
  def add(i, want, got, x):
    if x==want: i.d += got==want; i.b += got!=want
    else:       i.c += got==x;    i.a += got!=x
    a,b,c,d = i.a,i.b,i.c,i.d
    p       = lambda z: int(100*z)
    i.pd    = p(d / (b + d + 1e-32))
    i.pf    = p(c / (a + c + 1e-32))
    i.prec  = p(d / (c + d + 1e-32))
    i.acc   = p((a + d) / (a + b + c + d + 1e-32))

def abcds(got, want, this=None):
  this = this or dict(n=0,stats={})
  for x in [want, got]:
    this["stats"][x] = this["stats"].get(x) or Abcd(this["n"])
  this["n"] += 1
  for x,s in this["stats"].items():
    s.add(want,got,x)
  return this

#--structs -------------------------------------------------------
def Num(inits=[],at=0, txt="", rank=0):
  "Summary of numeric columns."
  return adds(inits, o(it   =Num,
                       n    = 0,    ## items seen  
                       at   = at,   ## column position
                       txt  = txt,  ## column name
                       mu   = 0,    ## mean
                       sd   = 0,    ## standard deviation
                       m2   = 0,    ## second moment
                       hi   = -BIG, ## biggest seen
                       lo   =  BIG, ## smallest seen
                       rank = rank, ## used only by stats
                       more = not txt.endswith("-")))

def Sym( inits=[], at=0, txt=" "):
  "Summary of symbolic columns."
  return adds(inits, o(it  = Sym, 
                       n   = 0,     ## items see
                       at  = at,    ## column position 
                       txt = txt,   ## column name
                       has = {}))   ## counts of symbols seen

def Data(inits): 
  "Data stores rows and columns."
  inits = iter(inits)
  cols  = _cols(next(inits))
  return adds(inits.o(it    = Data, 
                      n     = 0,     ## items seen
                      _rows = [],    ## rows
                      cols  = cols)) ## summaries of rows

def _cols(names):
  "Factory. List[str] -> Dict[str, List[ Sym | Num ]]"
  all, x, y, klass = [], [], [], None
  for c, s in enumerate(names):
    col = (Num if s[0].isupper() else Sym)(at=c, txt=s)
    all += [col]
    if s[-1] != "X":
      if s[-1] == "!": klass = col
      (y if s[-1] in "+-" else x).append(col)
  return o(names = names,           ## all the column names
           klass = klass,           ## Target for classification
           all   = all,             ## all columns
           x     = x,               ## also, hold independents here
           y     = y)               ## also, hold dependent here

# -- update -------------------------------------------------------
def sub(i,v,purge=False): 
  "Subtraction is just addition, with a negative increment."
  return add(i, v, inc= -1, purge=purge)

def add(i, v, inc=1, purge=False): # -> v
  "For inc additions; add `v` to `i`. Skip unknowns. Return v."
  if v == "?": return v 
  i.n += inc
  if   i.it is Num: _num(i,v,inc)
  elif i.it is Sym: _sym(i,v,inc)
  else: # i.it is Data
    if inc > 0: i._rows.append(v)
    elif purge: i._rows.remove(v) # only on explicit purge
    for col in i.cols.all: add(col, v[col.at], inc)
  return v

def _num(num,n,inc): 
  "To udpate Num, update mu,sd,m2,lo,hi."
  num.lo, num.hi = min(n,num.lo), max(n,num.hi)
  if inc < 0 and num.n < 2: 
    num.sd = num.m2 = num.mu = num.n = 0
  else:
    d       = n - num.mu
    num.mu += inc * (d / num.n)
    num.m2 += inc * (d * (n - num.mu))
    num.sd  = 0 if num.n <= 2 else (max(0,num.m2)/(num.n-1))**.5

def _sym(sym,s,inc): 
  "To update Syms, update symbol counts."
  sym.has[s] = inc + sym.has.get(s,0)

# -- query helpers ----------------------------------------------
def mid(i):
  "Central tendancy."
  return [mid(c) for c in i.cols.all] if i.it is Data else (
         i.mu if i.it is Num else mode(i.has))

def spread(i):
  "Deviation from central tendancy."
  return [mid(c) for c in i.cols.all] if i.it is Data else (
         i.sd if i.it is Num else ent(i.has, i.n))

def mode(d): 
  "Key with higehst value."
  return max(d, key=d.get)

def ent(d, n): 
  "Key with higehst value."
  return -sum((p := v/n) * math.log(p, 2) for v in d.values() if v)

# -- distance helpers ----------------------------------------------
def norm(num, v): 
  return v if v=="?" else (v - num.lo) / (num.hi - num.lo + 1/BIG)

def dist(vs):
  "Minkowski distance." 
  n, s = 0, 0
  for x in vs:
    n += 1
    s += abs(x)**the.p
  return (s / n)**(1/the.p)

def ydist(data, row): 
  "Distance to goal (1 for maximize, 0 for minimze)"
  return dist(abs(norm(c, row[c.at]) - c.more) for c in data.cols.y)

def ydists(data, rows=None):
  "Return all rows, sorted by ydis tto goals."
  return sorted(rows or data._rows, key=lambda row: ydist(data,row))

def xdists(data, row1, rows=None):
  "Return all rows, sorted by xdist to row1."
  return sorted(rows or data._rows, 
                key=lambda row2: xdist(data,row1,row2))
  
def xdist(data, row1, row2):  
  "Distance between independent attributes."
  return dist(_xdist(c, row1[c.at], row2[c.at]) for c in data.cols.x)

def _xdist(col,u,v):
  "Distance between numeric or symbolic atoms."
  if u=="?" and v=="?": return 1 
  if col.it is Sym: return u!=v  #1=different, 0=same 
  u = norm(col,u)
  v = norm(col,v)
  u = u if u != "?" else (0 if v > .5 else 1)
  v = v if v != "?" else (0 if u > .5 else 1)
  return abs(u - v) 

def kpp(data, k=None, rows=None):
  "Find k centroids d**2 away from existing centoids."
  row, *rows = shuffle(rows or data._rows)[:the.Few]
  out = [row]
  while len(out) < (k or the.Build):
     ws = [min(xdist(data,r, c)**2 for c in out) for r in rows]
     out.append(random.choices(rows, weights=ws)[0])
  return out

# -- setup --------------------------------------------------------
the = settings(__doc__)
random.seed(the.rseed)

def main(data):
  klass = data.cols.klass.at
  shuffle(data._rows)
  centroids = kpp(data)
  for row in data._rows():
    got   = xdists(data,row, centroids)[klass]
    want  = row[klass]
    acc  += got != want
  return acc
