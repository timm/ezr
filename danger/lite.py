#!/usr/bin/env python3 -B 
"""
ezr.py: lightweight incremental multi-objective optimization   
(c) 2025, Tim Menzies <timm@ieee.org>, MIT license   
   
    -A  Any=4             on init, how many initial guesses?   
    -B  Budget=30         when growing theory, how many labels?   
    -C  Check=5           budget for checking learned model
    -D  Delta=smed        required effect size test for cliff's delta
    -F  Few=128           sample size of data random sampling  
    -K  Ks=0.95           confidence for Kolmogorovâ€"Smirnov test
    -l  leaf=3            min items in tree leaves
    -p  p=2               distance co-efficient
    -s  seed=1234567891   random number seed   
    -f  file=../../moot/optimize/misc/auto93.csv    data file 
    -h                     show help   
"""
from types import SimpleNamespace as o
from typing import Any,List,Iterator
import random, time, math, sys, re

Number = int|float
Atom   = Number|str|bool
Row    = List[Atom]

big    = 1e32

#--------------------------------------------------------------------
def label(row): 
  "Return the row as its own label"
  return row

#--------------------------------------------------------------------
def Num(at=0,s=" "): 
  "Create a numeric column summarizer"
  return o(it=Num, at=at, txt=s, n=0, mu=0, m2=0, sd=0, 
           hi=-big, lo=big, more = 0 if s[-1] == "-" else 1)

def Sym(at=0,s=" "): 
  "Create a symbolic column summarizer"
  return o(it=Sym, at=at, txt=s, n=0, has={})

def Cols(names : List[str]) -> o:
  "Create column summaries from column names"
  all=[(Num if s[0].isupper() else Sym)(c,s) for c,s in enumerate(names)]
  klass=None
  for col in all: 
    if col.txt[-1]=="!": klass=col
  return o(it=Cols, names = names, all = all, klass = klass,
           x = [col for col in all if col.txt[-1] not in "X-+"],
           y = [col for col in all if col.txt[-1] in "-+"])

def Data(src) -> o:
  "Create data structure from source rows"
  src = iter(src)
  return adds(src, o(it=Data, n=0, mid=None, rows=[], kids=[], ys=None,
                     cols=Cols(next(src)))) # kids=[], how=[], ys=None))

def clone(data:Data, rows=None) -> o:
  "Create new Data with same columns but different rows"
  return adds(rows or [], Data([data.cols.names]))

#--------------------------------------------------------------------
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
  if x.it is Sym: x.has[v] = inc + x.has.get(v,0)
  elif x.it is Num:
    x.n += inc
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
    x.n += inc
    if inc > 0: x.rows += [v]
    elif zap: x.rows.remove(v) # slow for long rows
    [add(col, v[col.at], inc) for col in x.cols.all]
  return v

#--------------------------------------------------------------------
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

#--------------------------------------------------------------------
def dist(src) -> float:
  "Calculate Minkowski distance"
  d,n = 0,0
  for v in src: n,d = n+1, d + v**the.p;
  return (d/n) ** (1/the.p)

def disty(data:Data, row:Row) -> float:
  "Distance from row to best y-values"
  return dist(abs(norm(c, row[c.at]) - c.more) for c in data.cols.y)

def distysort(data:Data,rows=None) -> List[Row]:
  "Sort rows by distance to best y-values"
  return sorted(rows or data.rows, key=lambda r: disty(data,r))

def distx(data:Data, row1:Row, row2:Row) -> float:
  "Distance between two rows using x-values"
  def _aha(col, a,b):
    if a==b=="?": return 1
    if col.it is Sym: return a != b
    a,b = norm(col,a), norm(col,b)
    a = a if a != "?" else (0 if b>0.5 else 1)
    b = b if b != "?" else (0 if a>0.5 else 1)
    return abs(a - b)
  return dist(_aha(col, row1[col.at], row2[col.at])  
              for col in data.cols.x)

#--------------------------------------------------------------------
def likely(data:Data, rows=None) -> List[Row]:
  "Find the thing in x most likely to be best. Add to xy. Repeat."
  rows = rows or data.rows
  x   = clone(data, shuffle(rows[:]))
  xy, best, rest = clone(data), clone(data), clone(data)

  # label anything
  for _ in range(the.Any): add(xy, label(sub(x, x.rows.pop())))

  # divide lablled items into best and rest
  xy.rows = distysort(xy); n = round(the.Any**.5)
  adds(xy.rows[:n], best); adds(xy.rows[n:], rest)

  # loop, labelling the best guess
  while x.n > 2 and xy.n < the.Budget:
    add(xy, add(best, sub(x, label(guess(xy, best, rest, x)))))
    if best.n > (xy.n**.5):
      best.rows = distysort(xy,best.rows)
      while best.n > (xy.n**.5):
        add(rest, sub(best, best.rows.pop(-1)))
  return distysort(xy)

def guess(xy, best:Data, rest:Data, x:Data) -> Row:
  "Remove from `x' any 1 thing more best-ish than rest-ish."
  for _ in range(the.Few):
    row = x.rows[ i := random.randrange(x.n) ]
    if distx(xy, mids(best), row) < distx(xy, mids(rest), row):
      return x.rows.pop(i)
  return x.rows.pop()

#--------------------------------------------------------------------
def distKpp(data, rows=None, k=20, few=None):
  "Return key centroids usually separated by distance D^2."
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

#--------------------------------------------------------------------
treeOps = {'<=' : lambda x,y: x <= y, 
           '==' : lambda x,y:x == y, 
           '>'  : lambda x,y:x > y}

def treeSelects(row:Row, op:str, at:int, y:Atom) -> bool: 
  "Have we selected this row?"
  return (x := row[at]) == "?" or treeOps[op](x, y)

def Tree(data:Data, Klass=Num, Y=None, how=None) -> Data:
  "Create regression tree."
  Y = Y or (lambda row: disty(data, row))
  data.kids, data.how = [], how
  data.ys = adds(Y(row) for row in data.rows)
  if len(data.rows) >= the.leaf:
    hows = [how for col in data.cols.x 
            if (how := treeCuts(col,data.rows,Y,Klass))]
    if hows:
      for how1 in min(hows, key=lambda c: c.div).hows:
        rows1 = [r for r in data.rows if treeSelects(r, *how1)]
        if the.leaf <= len(rows1) < len(data.rows):
          data.kids += [Tree(clone(data,rows1), Klass, Y, how1)]
  return data

def treeCuts(col:o, rows:list[Row], Y:callable, Klass:callable) -> o:
  "Divide a col into ranges."
  def _sym(sym):
    d, n = {}, 0
    for row in rows:
      if (x := row[col.at]) != "?":
        n += 1
        d[x] = d.get(x) or Klass()
        add(d[x], Y(row))
    return o(div = sum(c.n/n * div(c) for c in d.values()),
             hows = [("==",col.at,x) for x in d])

  def _num(num):
    out, b4, lhs, rhs = None, None, Klass(), Klass()
    xys = [(row[col.at], add(rhs, Y(row))) # add returns the "y" value
           for row in rows if row[col.at] != "?"]
    for x, y in sorted(xys, key=lambda z: z[0]):
      if x != b4 and the.leaf <= lhs.n <= len(xys) - the.leaf:
        now = (lhs.n * lhs.sd + rhs.n * rhs.sd) / len(xys)
        if not out or now < out.div:
          out = o(div=now, hows=[("<=",col.at,b4), (">",col.at,b4)])
      add(lhs, sub(rhs, y))
      b4 = x
    return out

  return (_sym if col.it is Sym else _num)(col)

#--------------------------------------------------------------------
def treeNodes(data:Data, lvl=0, key=None) -> Data:
  "iterate over all treeNodes"
  yield lvl, data
  for j in sorted(data.kids, key=key) if key else data.kids:
    yield from treeNodes(j,lvl + 1, key)

def treeLeaf(data:Data, row:Row, lvl=0) -> Data:
  "Select a matching leaf"
  for j in data.kids:
    if treeSelects(row, *j.how): return treeLeaf(j,row,lvl+1)
  return data

def treeShow(data:Data, key=lambda d: d.ys.mu) -> None:
  "Display tree with #rows and win% columns"
  ats = {}
  print(f"{'#rows':>6} {'win':>4}")
  for lvl, d in treeNodes(data, key=key):
    if lvl == 0: continue
    op, at, y = d.how
    name = data.cols.names[at]
    indent = '|  ' * (lvl - 1)
    expl = f"if {name} {op} {y}"
    score = int(100 * (1 - (d.ys.mu - data.ys.lo) /
             (data.ys.mu - data.ys.lo + 1e-32)))
    leaf = ";" if not d.kids else ""
    print(f"{d.ys.n:6} {score:4}    {indent}{expl}{leaf}")
    ats[at] = 1
  used = [data.cols.names[at] for at in sorted(ats)]
  print(len(data.cols.x), len(used), ', '.join(used))

#--------------------------------------------------------------------
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

def shuffle(lst:List) -> List:
  "shuffle a list, in place"
  random.shuffle(lst); return lst

def main(settings : o, funs: dict[str,callable]) -> o:
  "from command line, update config find functions to call"
  for n,s in enumerate(sys.argv):
    if (fn := funs.get(f"eg{s.replace('-', '_')}")):
      random.seed(settings.seed); fn()
    else:
      for key in vars(settings):
        if s=="-"+key[0]: 
          settings.__dict__[key] = coerce(sys.argv[n+1])

#---------------------------------------------------------------------
def eg__ezr(repeats=20):
  "Example function demonstrating the optimization workflow"
  data = Data(csv(the.file))
  b4  = adds(disty(data,row) for row in data.rows)
  now = adds(ezr1(data,b4,shuffle(data.rows)) for _ in range(1))
  print(the.Budget, now.mu)

def ezr1(data, b4, rows):
   win    = lambda v: int(100*(1 - (v - b4.lo)/(b4.mu - b4.lo)))
   best   = lambda rows: win(disty(data, distysort(data,rows)[0]))
   half   = len(data.rows)//2
   train, holdout = data.rows[:half], data.rows[half:]
   labels = likely(clone(data,train))
   tree   = Tree(clone(data,labels))
   treeShow(tree)
   for row in holdout: print(row); print(treeLeaf(data,row).ys.mu)
   #some   = sorted(holdout,
   #                key=lambda row: treeLeaf(tree,row).ys.mu)[the.Check]
   #  return best(some)
   #print(best(some))
   return 10
#
the = o(**{k:coerce(v) for k,v in re.findall(r"(\w+)=(\S+)",__doc__)})
if __name__ == "__main__": main(the, globals())

# #!/usr/bin/env python3 -B 
# """
# ezr.py: lightweight incremental multi-objective optimization   
# (c) 2025, Tim Menzies <timm@ieee.org>, MIT license   
#
#     -A  Any=4             on init, how many initial guesses?   
#     -B  Budget=30         when growing theory, how many labels?   
#     -C  Check=5           budget for checking learned model
#     -D  Delta=smed        required effect size test for cliff's delta
#     -F  Few=128           sample size of data random sampling  
#     -K  Ks=0.95           confidence for Kolmogorov–Smirnov test
#     -l  leaf=3            min items in tree leaves
#     -p  p=2               distance co-efficient
#     -s  seed=1234567891   random number seed   
#     -f  file=../../moot/optimize/misc/auto93.csv    data file 
#     -h                     show help   
# """
# from types import SimpleNamespace as o
# from typing import Any,List,Iterator
# import random, time, math, sys, re
#
# Number = int|float
# Atom   = Number|str|bool
# Row    = List[Atom]
#
# big    = 1e32
#
# #--------------------------------------------------------------------
# def label(row): return row
#
# #--------------------------------------------------------------------
# def Num(i=0,s=" "): 
#   return o(it=Num, i=i, txt=s, n=0, mu=0, m2=0, sd=0, hi=-big, lo=big,
#            more = 0 if s[-1] == "-" else 1)
#
# def Sym(i=0,s=" "): 
#   return o(it=Sym, i=i, txt=s, n=0, has={})
#
# def Cols(names : List[str]) -> o:
#   all=[(Num if s[0].isupper() else Sym)(c,s) for c,s in enumerate(names)]
#   klass=None
#   for col in all: 
#     if col.txt[-1]=="!": klass=col
#   return o(it=Cols, names = names, all = all, klass = klass,
#            x = [col for col in all if col.txt[-1] not in "X-+"],
#            y = [col for col in all if col.txt[-1] in "-+"])
#
# def Data(src) -> o:
#   src = iter(src)
#   return adds(src, o(it=Data, n=0, mid=None, rows=[], cols=Cols(next(src))))
#
# def clone(data:Data, rows=None) -> o:
#   return adds(rows or [], Data([data.cols.names]))
#
# #--------------------------------------------------------------------
# def adds(src, it=None) -> o:
#   it = it or Num()
#   [add(it,x) for x in src]
#   return it
#
# def sub(x:o, v:Any, zap=False) -> Any: 
#   return add(x,v,-1,zap)
#
# def add(x: o, v:Any, inc=1, zap=False) -> Any:
#   "incrementally update Syms,Nums or Datas"
#   if v == "?": return v
#   if x.it is Sym: x.has[v] = inc + x.has.get(v,0)
#   elif x.it is Num:
#     x.n += inc
#     x.lo, x.hi = min(v, x.lo), max(v, x.hi)
#     if inc < 0 and x.n < 2:
#       x.sd = x.m2 = x.mu = x.n = 0
#     else:
#       d     = v - x.mu
#       x.mu += inc * (d / x.n)
#       x.m2 += inc * (d * (v - x.mu))
#       x.sd  = 0 if x.n < 2 else (max(0,x.m2)/(x.n-1))**.5
#   elif x.it is Data:
#     x.mid = None
#     x.n += inc
#     if inc > 0: x.rows += [v]
#     elif zap: x.rows.remove(v) # slow for long rows
#     [add(col, v[col.i], inc) for col in x.cols.all]
#   return v
#
# #--------------------------------------------------------------------
# def norm(num:Num, v:float) -> float:  
#   return  v if v=="?" else (v - num.lo) / (num.hi - num.lo + 1E-32)
#
# def mids(data: Data) -> Row:
#   data.mid = data.mid or [mid(col) for col in data.cols.all]
#   return data.mid
#
# def mid(col: o) -> Atom:
#   return max(col.has, key=col.has.get) if col.it is Sym else col.mu
#
# #--------------------------------------------------------------------
# def dist(src) -> float:
#   d,n = 0,0
#   for v in src: n,d = n+1, d + v**the.p;
#   return (d/n) ** (1/the.p)
#
# def disty(data:Data, row:Row) -> float:
#   return dist(abs(norm(c, row[c.i]) - c.more) for c in data.cols.y)
#
# def distysort(data:Data,rows=None) -> List[Row]:
#   return sorted(rows or data.rows, key=lambda r: disty(data,r))
#
# def distx(data:Data, row1:Row, row2:Row) -> float:
#   def _aha(col, a,b):
#     if a==b=="?": return 1
#     if col.it is Sym: return a != b
#     a,b = norm(col,a), norm(col,b)
#     a = a if a != "?" else (0 if b>0.5 else 1)
#     b = b if b != "?" else (0 if a>0.5 else 1)
#     return abs(a - b)
#   return dist(_aha(col, row1[col.i], row2[col.i])  
#               for col in data.cols.x)
#
# #--------------------------------------------------------------------
# def likely(data:Data, rows=None) -> List[Row]:
#   """x,xy = rows with 'x' and 'xy' knowledge.
#   Find the thing in x most likely to be best. Add to xy. Repeat."""
#   rows = rows or data.rows
#   x   = clone(data, shuffle(rows[:]))
#   xy, best, rest = clone(data), clone(data), clone(data)
#
#   # label anything
#   for _ in range(the.Any): add(xy, label(sub(x, x.rows.pop())))
#
#   # divide lablled items into best and rest
#   xy.rows = distysort(xy); n = round(the.Any**.5)
#   adds(xy.rows[:n], best); adds(xy.rows[n:], rest)
#
#   # loop, labelling the best guess
#   while x.n > 2 and xy.n < the.Budget:
#     add(xy, add(best, sub(x, label(guess(xy, best, rest, x)))))
#     if best.n > (xy.n**.5):
#       best.rows = distysort(xy,best.rows)
#       while best.n > (xy.n**.5):
#         add(rest, sub(best, best.rows.pop(-1)))
#   return distysort(xy)
#
# def guess(xy, best:Data, rest:Data, x:Data) -> Row:
#   "Remove from `x' any 1 thing more best-ish than rest-ish."
#   for _ in range(the.Few):
#     row = x.rows[ i := random.randrange(x.n) ]
#     if distx(xy, mids(best), row) < distx(xy, mids(rest), row):
#       return x.rows.pop(i)
#   return x.rows.pop()
#
# #--------------------------------------------------------------------
# def distKpp(data, rows=None, k=20, few=None):
#   "Return key centroids usually separated by distance D^2."
#   few = few or the.Few
#   rows = rows or data.rows[:]
#   random.shuffle(rows)
#   out = [rows[0]]
#   while len(out) < k:
#     tmp = random.sample(rows, min(few,len(data.rows)))
#     ws  = [min(distx(data, r, c)**2 for c in out) for r in tmp]
#     p   = sum(ws) * random.random()
#     for j, w in enumerate(ws):
#       if (p := p - w) <= 0: 
#           out += [tmp[j]]; break
#   return out
#
# #--------------------------------------------------------------------
# treeOps = {'<=' : lambda x,y: x <= y, 
#            '==' : lambda x,y:x == y, 
#            '>'  : lambda x,y:x > y}
#
# def treeSelects(row:Row, op:str, at:int, y:Atom) -> bool: 
#   "Have we selected this row?"
#   return (x := row[at]) == "?" or treeOps[op](x, y)
#
# def Tree(data:Data, Klass=Num, Y=None, how=None) -> Data:
#   "Create regression tree."
#   Y = Y or (lambda row: disty(data, row))
#   data.kids, data.how = [], how
#   data.ys = adds(Y(row) for row in data.rows)
#   if len(data.rows) >= the.leaf:
#     hows = [how for col in data.cols.x 
#             if (how := treeCuts(col,data.rows,Y,Klass))]
#     if hows:
#       for how1 in min(hows, key=lambda c: c.div).hows:
#         rows1 = [r for r in data.rows if treeSelects(r, *how1)]
#         if the.leaf <= len(rows1) < len(data.rows):
#           data.kids += [Tree(clone(data,rows1), Klass, Y, how1)]
#   return data
#
# def treeCuts(col:o, rows:list[Row], Y:callable, Klass:callable) -> o:
#   "Divide a col into ranges."
#   def _sym(sym):
#     d, n = {}, 0
#     for row in rows:
#       if (x := row[col.at]) != "?":
#         n += 1
#         d[x] = d.get(x) or Klass()
#         add(d[x], Y(row))
#     return o(div = sum(c.n/n * div(c) for c in d.values()),
#              hows = [("==",col.at,x) for x in d])
#
#   def _num(num):
#     out, b4, lhs, rhs = None, None, Klass(), Klass()
#     xys = [(row[col.at], add(rhs, Y(row))) # add returns the "y" value
#            for row in rows if row[col.at] != "?"]
#     for x, y in sorted(xys, key=lambda z: z[0]):
#       if x != b4 and the.leaf <= lhs.n <= len(xys) - the.leaf:
#         now = (lhs.n * lhs.sd + rhs.n * rhs.sd) / len(xys)
#         if not out or now < out.div:
#           out = o(div=now, hows=[("<=",col.at,b4), (">",col.at,b4)])
#       add(lhs, sub(rhs, y))
#       b4 = x
#     return out
#
#   return (_sym if col.it is Sym else _num)(col)
#
# #--------------------------------------------------------------------
# def treeNodes(data:Data, lvl=0, key=None) -> Data:
#   "iterate over all treeNodes"
#   yield lvl, data
#   for j in sorted(data.kids, key=key) if key else data.kids:
#     yield from treeNodes(j,lvl + 1, key)
#
# def treeLeaf(data:Data, row:Row) -> Data:
#   "Select a matching leaf"
#   for j in data.kids or []:
#     if treeSelects(row, *j.how): return treeLeaf(j,row)
#   return data
#
# def treeShow(data:Data, key=lambda d: d.ys.mu) -> None:
#   "Display tree with #rows and win% columns"
#   ats = {}
#   print(f"{'#rows':>6} {'win':>4}")
#   for lvl, d in treeNodes(data, key=key):
#     if lvl == 0: continue
#     op, at, y = d.how
#     name = data.cols.names[at]
#     indent = '|  ' * (lvl - 1)
#     expl = f"if {name} {op} {y}"
#     score = int(100 * (1 - (d.ys.mu - data.ys.lo) /
#              (data.ys.mu - data.ys.lo + 1e-32)))
#     leaf = ";" if not d.kids else ""
#     print(f"{d.ys.n:6} {score:4}    {indent}{expl}{leaf}")
#     ats[at] = 1
#   used = [data.cols.names[at] for at in sorted(ats)]
#   print(len(data.cols.x), len(used), ', '.join(used))
#
# #--------------------------------------------------------------------
# def fyi(s, end=""):
#   "write the standard error (defaults to no new line)"
#   print(s, file=sys.stderr, flush=True, end=end)
#
# def coerce(s:str) -> Atom:
#   "coerce a string to int, float, bool, or trimmed string"
#   for fn in [int,float]:
#     try: return fn(s)
#     except Exception as _: pass
#   s = s.strip()
#   return {'True':True,'False':False}.get(s,s)
#
# def csv(file: str ) -> Iterator[Row]:
#   "Returns rows of a csv file."
#   with open(file,encoding="utf-8") as f:
#     for line in f:
#       if (line := line.split("%")[0]):
#         yield [coerce(s) for s in line.split(",")]
#
# def shuffle(lst:List) -> List:
#   "shuffle a list, in place"
#   random.shuffle(lst); return lst
#
# def main(settings : o, funs: dict[str,callable]) -> o:
#   "from command line, update config find functions to call"
#   for n,s in enumerate(sys.argv):
#     if (fn := funs.get(f"eg{s.replace('-', '_')}")):
#       random.seed(settings.seed); fn()
#     else:
#       for key in vars(settings):
#         if s=="-"+key[0]: 
#           settings.__dict__[key] = coerce(sys.argv[n+1])
#
# #---------------------------------------------------------------------
# def eg__ezr():
#   data = Data(csv(the.file))
#   half = len(data.rows)//2
#   train, holdout = data.rows[:half], data.rows[half:]
#   labels = likely(clone(data,train)))
#   tree = Tree(labels)
#
#
#
# the = o(**{k:coerce(v) for k,v in re.findall(r"(\w+)=(\S+)",__doc__)})
# if __name__ == "__main__": main(the, globals())
