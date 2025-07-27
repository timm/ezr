#!/usr/bin/env python3 -B
"""
y.py:  multi objective planner
(col) 2025, Tim Menzies <timm@ieee.org>, MIT license

 -B  Build=24        when growing theory, how many labels?
 -C  Check=5         when testing, how many checks?
 -F  Few=128         sub-sample size for distances
 -b  bins=7          number of bins
 -l  leaf=2          treeNodes in tree leaves
 -p  p=2             distance calculation coefficient
 -s  seed=1234567891 random number seed
 -f  file=../moot/optimize/misc/auto93.csv
                     path to CSV file

 -h                  show help
 --list              list all examples
 --X                 run example X
 --all               run all examples
"""
import random, math, sys, re

def coerce(s):
  for fn in [int,float]:
    try: return fn(s)
    except Exception as _: pass
  s = s.strip()
  return {'True':True,'False':False}.get(s,s)

class o:
  __init__ = lambda i,**d: i.__dict__.update(**d)
  __repr__ = lambda i:"{" + (' '.join(
                      [f":{k} {show(v)}" for k,v in i.__dict__.items() 
                       if str(k)[0] != "_"])) + "}"

def show(x): 
  if type(x) is type(show): return x.__name__
  if type(x) is float: return int(x) if x==int(x) else f"{x:.3f}" 
  return str(x)

the = o(**{k:coerce(v) for k,v in re.findall(r"(\w+)=(\S+)",__doc__)})

#---------------------------------------------------------------------
def Sym(at=0,txt="" ): return o(it=Sym, at=at, txt=txt, has={})
def Num(at=0,txt=" "): return o(it=Num, at=at, txt=txt, lo=1e32, 
                                mu=0, m2=0, sd=0, n=0, hi=-1e32, 
                                goal= 0 if str(txt)[-1]=="-" else 1)

def Data(str):
  return adds(str, o(it=Data, rows=[], cols=None))

def Cols(names):
  all, x, y, klass = [], [], [], None
  for c,s in enumerate(names):
    all += [(Num if s[0].isupper() else Sym)(c,s)]
    if s[-1] == "X": continue
    if s[-1] == "!": klass= all[-1]
    (y if s[-1] in "!-+" else x).append( all[-1] )
  return o(it=Cols, names=names, all=all, x=x, y=y, klass=klass)

def dataClone(data, src=[]): return adds(src, Data([data.cols.names]))

def add(x, v, inc=1):
  def _sym(): 
    x.has[v] = x.has.get(v,0) + inc
  def _data():
    if    x.cols: x.rows += [[add(c, v[c.at]) for c in x.cols.all]]
    else: x.cols = Cols(v)
  def _num():
    x.n  += 1
    x.lo  = min(v, x.lo)
    x.hi  = max(v, x.hi)
    if inc < 0 and x.n < 2:
      x.sd = x.m2 = x.mu = x.n = 0
    else:
      d     = v - x.mu
      x.mu += inc * (d / x.n)
      x.m2 += inc * (d * (v - x.mu))
      x.sd  = 0 if x.n < 2 else (max(0,x.m2)/(x.n-1))**.5
  #-----------
  if v != "?": 
    _num() if x.it is Num else _sym() if x.it is Sym else _data()
  return v

def norm(col, v): 
  return v if v=="?" or col.it is Sym else (v-col.lo)/(col.hi-col.lo + 1E-32)

#--------------------------------------------------------------------
def dist(src):
  "Generalized Minkowski distance with a variable power p."
  d,n = 0,0
  for v in src: n,d = n+1, d + v**the.p
  return (d/n) ** (1/the.p)

def disty(data, row):
  "Distance between goals and heaven."
  return dist(abs(norm(c, row[c.at]) - c.goal) for c in data.cols.y)

def distx(data, row1, row2):
  def _aha(col, a,b):
    if a==b=="?": return 1
    if col.it is Sym: return a != b
    a,b = norm(col,a), norm(col,b)
    a = a if a != "?" else (0 if b>0.5 else 1)
    b = b if b != "?" else (0 if a>0.5 else 1)
    return abs(a-b)
  #----------------
  return dist(_aha(c, row1[c.at], row2[c.at])  for c in data.cols.x)

def distProject(data,row,east,west,c=None):
  "Map row along a line east -> west."
  D = lambda r1,r2 : distx(data,r1,r2)
  c = c or D(east,west)  
  a,b = D(row,east), D(row,west)
  return (a*a +c*c - b*b)/(2*c + 1e-32)

def distFastmap(data, rows=None):
  "Sort rows along a line between 2 distant points."
  rows = rows or data.rows
  X = lambda r1,r2: distx(data,r1,r2)
  anywhere, *few = random.choices(rows, k=the.Few)
  here  = max(few, key= lambda r: X(anywhere,r))
  there = max(few, key= lambda r: X(here,r))
  c     = X(here,there)
  return sorted(rows, key=lambda r: distProject(data,r,here,there,c))

def adds(src, it=None):
  it = it or Num()
  [add(it,x) for x in src]
  return it

def csv(file):
  with open(file,encoding="utf-8") as f:
    for line in f:
      if (line := line.split("%")[0]):
        yield [coerce(s.strip()) for s in line.split(",")]

#--------------------------------------------------------------------
# _|_  ._   _    _  
#  |_  |   (/_  (/_ 

treeOps = {'<=' : lambda x,y: x <= y, 
           '==' : lambda x,y:x == y, 
           '>'  : lambda x,y:x > y}

def treeSelects(row,op,at,y): 
  "Have we selected this row?"
  return (x := row[at]) == "?" or treeOps[op](x, y)

def Tree(data, Klass=Num, Y=None, how=None):
  "Create regression tree."
  Y = Y or (lambda row: disty(data, row))
  data.kids, data.how = [], how
  data.ys = adds(Y(row) for row in data.rows)
  if len(data.rows) >= the.leaf:
    hows = [how for col in data.cols.x
            if (how := treeCuts(col, data.rows, col.at, Y, Klass))]
    if hows:
      for how1 in min(hows, key=lambda c: c.div).hows:
        rows1 = [r for r in data.rows if treeSelects(r, *how1)]
        if the.leaf <= len(rows1) < len(data.rows):
          data.kids += [Tree(dataClone(data,rows1), Klass, Y, how1)]
  return data

def treeCuts(col, rows, at, Y, Klass):
  "Divide a col into ranges."
  def _sym(sym):
    d, n = {}, 0
    for row in rows:
      if (x := row[at]) != "?":
        n += 1
        d[x] = d.get(x) or Klass()
        add(d[x], Y(row))
    return o(div = sum(c.n/n * div(c) for c in d.values()),
             hows = [("==",at,x) for x in d])
  
  def _num(num):
    out, b4, lhs, rhs = None, None, Klass(), Klass()
    xys = [(row[at], add(rhs, Y(row))) # add returns the "y" value
           for row in rows if row[at] != "?"]
    for x, y in sorted(xys, key=lambda z: z[0]):
      if x != b4 and the.leaf <= lhs.n <= len(xys) - the.leaf:
        now = (lhs.n * lhs.sd + rhs.n * rhs.sd) / len(xys)
        if not out or now < out.div:
          out = o(div=now, hows=[("<=",at,b4), (">",at,b4)])
      add(lhs, add(rhs, y, -1))
      b4 = x
    return out

  return (_sym if type(col) is Sym else _num)(col)

def treeNodes(data, lvl=0, key=None):
  "iterate over all treeNodes"
  yield lvl, data
  for j in sorted(data.kids, key=key) if key else data.kids:
    yield from treeNodes(j,lvl + 1, key)

def treeLeaf(data, row):
  "Select a matching leaf"
  for j in data.kids or []:
    if treeSelects(row, *j.how): return treeLeaf(j,row)
  return data

def treeShow(data, key=lambda d: d.ys.mu):
  "Display tree"
  print(f"{'d2h':>4} {'win':>4} {'n':>4}")
  print(f"{'----':>4} {'----':>4} {'----':>4}")
  s, ats = data.ys, {}
  win = lambda x: int(100 * (1-(x-data.ys.lo) / 
                             (data.ys.mu-data.ys.lo+1e-32)))
  for lvl, d in treeNodes(data,key=key):
    op, at, y = d.how if lvl else ('', '', '')
    name = data.cols.names[at] if lvl else ''
    expl = f"{name} {op} {y}" if lvl else ''
    indent = '|  ' * (lvl - 1)
    line = f"{d.ys.mu:4.2f} {win(d.ys.mu):4} {len(d.rows):4}    " \
           f"{indent}{expl}{';' if not d.kids else ''}"
    print(line)
    if lvl: ats[at] = 1
  used = [data.cols.names[at] for at in sorted(ats)]
  print(len(data.cols.x), len(used), ', '.join(used))

#---------------------------------------------------------------------
def daBest(data,rows): 
  Y = lambda row: disty(data, row)
  return Y(sorted(rows or data.rows, key=Y)[0])

def myLeaves(tree, rows):
  return sorted(rows, key=lambda r: treeLeaf(tree,r).ys.mu)

def eg_h(): print(__doc__)

def eg__the(): print(the)

def eg__num(): print(adds(random.gauss(10,1) for _ in range(100)))

def eg__data(): 
  data = Data(csv(the.file))
  [print(c) for c in data.cols.all]

def eg__tree():
  data = Data(csv(the.file))
  R = lambda n: int(100*n)
  out2, out2s = [],[]
  for _ in range(20):
    random.shuffle(data.rows)
    n = len(data.rows)//2
    rows1, rows2 = data.rows[:n], data.rows[n:]
    data0  = dataClone(data,rows1)
    data1  = dataClone(data, random.choices(rows1, k=the.Build))
    tree1  = Tree(data1)
    rows1s = distFastmap(data0)
    n      = len(rows1s)//the.Build
    tree1s = Tree(dataClone(data, rows1s[::n]))
  
    data2  = dataClone(data,rows2)
    stats2 = adds(disty(data2,row) for row in rows2)
    win2   = lambda n: 100*(1 - (n - stats2.lo)/(stats2.mu - stats2.lo))
  
    guess2 = daBest(data2, myLeaves(tree1,  rows2)[:the.Check])
    guess2s= daBest(data2, myLeaves(tree1s, rows2)[:the.Check])
    out2  += [int(win2(guess2))]
    out2s += [int(win2(guess2s))]
  print(sorted(out2))
  print(sorted(out2s))

if __name__ == "__main__":
  for n,arg in enumerate(sys.argv):
    if (fn := globals().get(f"eg{arg.replace('-', '_')}")):
      random.seed(the.seed)
      fn() 
    else:
      for key in the.__dict__:
        if arg == "-"+key[0]: the[key] = coerce(sys.argv[n+1])
