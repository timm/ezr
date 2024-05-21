#!/usr/bin/env python3 -B
# <!-- vim: set ts=2 sw=2 sts=2 et: -->
# Settings can be updated via command line.   
# e.g. `./ezr.py -s $RANDOM` sets `the.seed` to a random value set by operating system.
"""
ezr.py :  experiment in easier explainable AI. Less is more.
(C) 2024 Tim Menzies, timm@ieee.org, BSD-2.

OPTIONS:
  -a --any     #todo's to explore             = 100
  -b --bins    max #bins in discretization    = 16
  -d --decs    #decimals for showing floats   = 3
  -f --file    csv file for data              = ../data/misc/auto93.csv
  -F --Far     how far to seek faraway        = 0.8
  -k --k       bayes low frequency hack #1    = 1
  -H --Half    #rows for searching for poles  = 128
  -l --label   initial number of labelings    = 4
  -L --Last    max allow labelings            = 30
  -m --m       bayes low frequency hack #2    = 2
  -n --n       tinyN                          = 12
  -N --N       smallN                         = 0.5
  -p --p       distance function coefficient  = 2
  -R --Run     start up action method         = help
  -s --seed    random number seed             = 1234567891
"""
# (FYI our seed is odious, pernicious, apocalyptic, deficient, and prime.)      
import re,ast,sys,math,random,copy,traceback
from fileinput import FileInput as file_or_stdin
from typing import Any,NewType 
from typing_extensions import Literal

#--------- --------- --------- --------- --------- --------- --------- --------- --------
# ## Types
atom    = NewType('atom',    float|int|bool|str) 
row     = NewType('row',     list[atom])
rows    = NewType('rows',    list[row])
classes = NewType('classes', dict[str, # `str` is the class name
                                  rows])

class o:
  "Class for quick inits of structs, and pretty prints."
  def __init__(i,**d): i.__dict__.update(d)
  def __repr__(i): return i.__class__.__name__+str(show(i.__dict__))

bin,cols,data = NewType('bin',o),NewType('cols',o),NewType('data',o)
num,sym       = NewType('num',o),NewType('sym',o)
col           = NewType('col', num|sym)

def coerce(s:str) -> atom:
  "coerces strings to atoms"
  try: return ast.literal_eval(s)
  except Exception:  return s

# Build the globals by parsing the `__doc__` string.
the=o(**{m[1]:coerce(m[2]) for m in re.finditer(r"--(\w+)[^=]*=\s*(\S+)",__doc__)})

#--------- --------- --------- --------- --------- --------- --------- --------- --------
# ## Structs
def _DATA() -> data:
  "primitive constructor: stores `rows` (whose columns  are summarized in `cols`)."
  return o(rows=[], cols=[])

def _COLS(names: list[str]) -> cols:
  """primitive constructor: a factory that makes, and stores, `all` the columns.
  (and the  independent and dependent cols are also held in `x` and ``y`"""
  return o(x=[], y=[], all=[], klass=None, names=names)

def _SYM(txt=" ",at=0) -> sym:
  "primitive constructor: incrementally summarizes a stream of symbols."
  return o(isNum=False, txt=txt, at=at, n=0, has={})

def _NUM(txt=" ",at=0,has=None) -> num:
  "primitive constructor: incremental summarizes a stream of numbers."
  return o(isNum=True,  txt=txt, at=at, n=0, hi=-1E30, lo=1E30, 
           has=has, rank=0, # if has non-nil, used by the stats package
           mu=0, m2=0, maximize = txt[-1] != "-")

def _BIN(at,txt,lo,hi=None,ys=None) -> bin:
  """primitive constructor: `ys` holds a count of the symbols seen in one column
  between the `lo` and `hi` of another column."""
  return o(n=0,at=at, txt=txt, lo=lo, hi=hi or lo, ys=ys or {})

#--------- --------- --------- --------- --------- --------- --------- --------- --------
# ## Constructors
# Here are the constructors that just call the primitive constructors.
NUM, SYM, BIN = _NUM, _SYM, _BIN

# Herea re the other constructors.
def COLS(names: list[str]) -> cols:
  "Constructor. Create columns (one for each string in `names`)."
  i = _COLS(names)
  i.all = [add2cols(i,n,s) for n,s in enumerate(names)]
  return i

def add2cols(i:cols, n:int, s:str) -> None:
  """Upper case names are NUM.  The `klass` name ends in '!'.  A trailing
  'X' denotes 'ignore'.  If not ignoring, then the column is either
  a dependent goals (held in `cols.y`) or a independent variable (held
  in `cols.x`)."""
  new = (NUM if s[0].isupper() else SYM)(txt=s, at=n)
  if s[-1] == "!": i.klass = new
  if s[-1] != "X": (i.y if s[-1] in "!+-" else i.x).append(new)
  return new

def DATA(src=None, rank=False) -> data:
  """ Constructor. `src` can be any iterator that returns a list of values (e.g. some 
  list, or the `csv` iterator, shown below, that reads rows from a csv file)."""
  i = _DATA()
  [add2data(i,lst) for  lst in src or []]
  if rank: i.rows.sort(key = lambda lst:d2h(i,lst))
  return i

def clone(i:data, inits=[], rank=False) -> data:
  """Copy a structure (same column structure, but with different rows).
  Optionally, the rows in the new structure can be sorted."""
  return DATA([i.cols.names] + inits, rank=rank )

#--------- --------- --------- --------- --------- --------- --------- --------- ---------
# ## Update
def add2data(i:data,row1:row) -> None:
  "update contents of a DATA"
  if    i.cols: i.rows.append([add2col(col,x) for col,x in zip(i.cols.all,row1)])
  else: i.cols= cols(row1)

def adds(i:col, lst:list) -> col:
   "Update a NUM or SYM with many items."
   [add2col(i,x) for x in lst]
   return i

def add2col(i:col, x:Any, n=1) -> Any:
  "`n` times, update NUM or SYM with one item."
  if x != "?":
    i.n += n
    if i.isNum: add2num(i,x,n)
    else: i.has[x] = i.has.get(x,0) + n
  return x

def add2num(i:num, x:Any, n:int) -> None:
  "`n` times, update a NUM with one item."
  i.lo = min(x, i.lo)
  i.hi = max(x, i.hi)
  for _ in range(n):
    if i.has != None: i.has += [x]
    d       = x - i.mu
    i.mu += d / i.n
    i.m2 += d * (x -  i.mu)

#--------- --------- --------- --------- --------- --------- --------- --------- --------
# ## Queries
def mid(i:col) -> atom:
  "middle of a column"
  return i.mu if i.isNum else max(i.has, key=i.has.get)

def mids(i:data, cols=None) -> dict[str,atom]:
  "middle of some columns (defaults to `data.cols.x`)"
  return {i.txt:mid(col) for col in cols or i.cols.x}

def div(i:col) -> float:
  "diversity of a column"
  return  (0 if i.n <2 else (i.m2/(i.n-1))**.5) if i.isNum else ent(i.has)[0]

def divs(i:data, cols=None) -> dict[str,float]:
  "diversity of some columns (defaults to `data.cols.x`)"
  return {col.txt:div(col) for col in cols or i.cols.x}

def norm(i:num,x) -> float:
  "normalize `x` to 0..1"
  return x if x=="?" else (x-i.lo)/(i.hi - i.lo - 1E-30)

#--------- --------- --------- --------- --------- --------- --------- --------- --------
# Discretization
#
# def bins2bin(bins):
#   out    = BIN(bins[0].at, bins[0].txt, bins[0].lo)
#   for bin in bins:
#     out.lo =  min(out.lo, bin.lo)
#     out.hi =  max(out.hi, bin.hi)
#     for y,n in bin.ys.items: bin.ys[y] = bin.ys[y].get(y,0) + n
#   return out
#
# def merge(bin1,bin2):
#   bin3 = bins2bin([bin1,bin2])
#   e1,n1 = ent(bin1.ys)
#   e2,n2 = ent(bin2.ys)
#   e3,n3 = ent(bins3.ys)
#   if n1 <  small or n2 < small : return bin3 # merge if bins too small
#   if e3 <= (n1*e1 + n2*e2)/n3  : return bin3 # merge if parts are more complex
#
# def bins(col, classes, small=None)
#   out = binsDivide(ccol,classes)
#   if not col.isNum: return out
#   small= small or (sum(len(row) for rows in classes.values)) / the.bins
#   rewrunaut = merges(out, merge=lambda x,y:merge(x,y,small)
#   
# def binsDivide(col, classes):
#   d = {}
#   [_send2bin(col,row[col.at],y,d) for y,rows in classes.items() for row in rows]
#   return sorted(d.values, key=lambda z:z.lo)
#
# def _send2bin(col,x,y,d):
#   if x != "?":
#      k = _bin(col,x)
#      it = d[k] = d[k] if k in d else BIN(col.at,col.txt,x)
#      it.lo = min(it.lo, x)
#      it.hi = max(it.hi, x)
#      it.ys[y] = it.ys.get(y,0) + 1
#
# def _bin(col,x):
#   return min(the.bins - 1, int(the.bins * norm(col,x)) if col.isNum else x
#
# def _merges(b4, mergeFun):
#   j, now  = 0, []
#   while j <  len(b4):
#     x = b4[j]
#     if j <  len(b4) - 1:
#       y = b4[j+1]
#       if xy := mergeFun(x, y):
#         x = xy
#         j = j+1  # if i can merge, jump over the merged item
#     now += [x]
#     j += 1
#   return b4 if len(now) == len(b4) else _merges(now, mergeFun)
#
#
#
    # --  small = small or (sum(len(lst) for lst in classes.values())/the.bins))
#--------- --------- --------- --------- --------- --------- --------- --------- --------
# ## Distances

def d2h(i:data, row1:row) -> float:
  "distance to `heaven` (which is the distance of the `y` vals to the best values)"
  n = sum(abs(norm(num,row1[num.at]) - num.maximize)**the.p for num in i.cols.y)
  return (n / len(i.cols.y))**(1/the.p)

def dists(i:data, row1:row, row2:row) -> float:
  "distances between two rows"
  n = sum(dist(col, row1[col.at], row2[col.at])**the.p for col in i.cols.x)
  return (n / len(data.cols.x))**(1/the.p)

def dist(i:col, x:any, y:amy) -> float:
  "distance between two values"
  if  x==y=="?": return 1
  if not i.isNum: return x != y
  x, y = norm(i,x), norm(i,y)
  x = x if x !="?" else (1 if y<0.5 else 0)
  y = y if y !="?" else (1 if x<0.5 else 0)
  return abs(x-y)

def neighbors(i:data,row1:row, rows=None) : list[row]:
  "return `rows`, sorted ascending by distance to `row1"
  return sorted(rows or data.rows, key=lambda row2: dists(i,row1,row2))

#--------- --------- --------- --------- --------- --------- --------- --------- --------
# ## Clusters
def faraway(data,row,rows):
  far = int( len(rows) * the.Far)
  return neighbors(data,row,rows)[far]

def twoFaraway(data,rows=None,before=None, sortp=False):
  rows = rows or data.rows
  x = before or faraway(data, random.choice(rows), rows)
  y = faraway(data, x, rows)
  if sortp and d2h(data,y) < d2h(data,x): x,y = y,x
  return x, y,  dists(data,x,y)

def half(data,rows,sortp=False,before=None):
  def D(r1,r2): return dists(data,r1, r2)
  mid = int(len(rows) // 2)
  left,right,C = twoFaraway(data, random.choices(rows, k=min(the.Half, len(rows))),
                            sortp=sortp, before=before)
  tmp = sorted(rows, key=lambda row: (D(row,left)**2 + C**2 - D(row,right)**2)/(2*C))
  return tmp[:mid], tmp[mid:], left

def halves(data, rows=None, stop=None, rest=None, evals=1, before=None):
  rows = rows or data.rows
  stop = stop or 2*len(rows)**the.N
  rest = rest or []
  if len(rows) > stop:
    lefts,rights,left  = half(data,rows, True, before)
    return halves(data,lefts, stop, rest+rights, evals+1, left)
  else:
    return rows,rest,evals

#--------- --------- --------- --------- --------- --------- --------- --------- --------
# ## Likelihoods

# Likelihood of a `row` belonging to a `data`.
def loglikes(data, row, nall, nh):
  prior = (len(data.rows) + the.k) / (nall + the.k*nh)
  likes = [like(col,row[col.at],prior) for col in data.cols.x if row[col.at] != "?"]
  return sum(math.log(x) for x in likes + [prior] if x>0)

# Likelihood of `x` belonging to a `col`.
def like(col, x, prior):
  return like4num(col,x) if col.isNum else like4sym(col,x,prior)

def like4sym(sym,x,prior): return (sym.has.get(x, 0) + the.m*prior) / (sym.n + the.m)

def like4num(num,x):
  v     = div(num)**2 + 1E-30
  nom   = math.e**(-1*(x - mid(num))**2/(2*v)) + 1E-30
  denom = (2*math.pi*v) **0.5
  return min(1, nom/(denom + 1E-30))

#--------- --------- --------- --------- --------- --------- --------- --------- --------
# ## Sequential model optimization
# Assumes we can access everyone's indepent variables much cheaper than the dependent
# variables 

def smo(data, score=lambda B,R: B-R):
  def guess(todo, done):
    cut  = int(.5 + len(done) ** the.N)
    best = clone(data, done[:cut])
    rest = clone(data, done[cut:])
    key  = lambda row: score(loglikes(best, row, len(done), 2),
                             loglikes(rest, row, len(done), 2))
    random.shuffle(todo)
    return sorted(todo[:the.any], key=key, reverse=True) + todo[the.any:]

  def smo1(todo, done):
    for i in range(the.Last - the.label):
      if len(todo) < 3: break
      top,*todo = guess(todo, done)
      done += [top]
      done = clone(data, done, rank=True).rows # done is now resorted
    return done

  random.shuffle(data.rows)
  return smo1(data.rows[the.label:], clone(data, data.rows[:the.label], rank=True).rows)

#--------- --------- --------- --------- --------- --------- --------- --------- ---------
def ent(d):
  N = sum(v for v in d.values() if v > 0)
  return -sum(v/N*math.log(v/N,2) for v in d.values() if v > 0),N

def sumDicts(dicts):
  out={}
  for one in dicts:
    for k,v in one.items(): out[k] = out.get(k,0) + v
  return out

def bore(d,goal=True,B=1,R=1):
  best,rest = 1E-30,1E-30
  for k,v in d.items():
    if k==goal: best += v
    else: rest += v
  best,rest = best/B, rest/R
  return best**2/(best+rest)

def show(x):
  it = type(x)
  if it == float:  return round(x,the.decs)
  if it == list:   return [show(v) for v in x]
  if it == dict:   return "("+' '.join([f":{k} {show(v)}" for k,v in x.items()])+")"
  if it == o:      return show(x.__dict__)
  if it == str:    return '"'+str(x)+'"'
  if callable(x):  return x.__name__
  return x

def csv(file=None):
  with file_or_stdin(file) as src:
    for line in src:
      line = re.sub(r'([\n\t\r ]|#.*)', '', line)
      if line: yield [coerce(s.strip()) for s in line.split(",")]

def cli(d):
  for k,v in d.items():
    v = str(v)
    for c,arg in enumerate(sys.argv):
      if arg in ["-"+k[0], "--"+k]:
        d[k] = coerce("false" if v=="true" else ("true" if v=="false" else sys.argv[c+1]))

def btw(*args, **kwargs):
    print(*args, file=sys.stderr, end="", flush=True, **kwargs)
#--------- --------- --------- --------- --------- --------- --------- --------- ---------
def main(): cli(the.__dict__); run(the.Run)

def run(s):
  def run1():
    try:
      return getattr(eg, s)()
    except Exception:
      print(traceback.format_exc())
      return False
  reset = {k:v for k,v in the.__dict__.items()}
  random.seed(the.seed)
  out = run1()
  for k,v in reset.items(): the.__dict__[k]=v
  return out==False

class eg:
  def all(): sys.exit(sum(run(s) for s in dir(eg) if s[0] !="_" and s !=  "all"))

  def help():
    print(__doc__)
    print("Start-up commands:")
    [print(f"  -R {k} ") for k in sorted(dir(eg)) if k[0] !=  "_"]

  def the(): print(the)

  def csv(): [print(x) for i,x in enumerate(csv(the.file)) if i%50==0]

  def cols():
    [print(col) for col in 
       cols(["Clndrs","Volume","HpX","Model","origin","Lbs-","Acc+","Mpg+"]).all]

  def num():
    n= adds(NUM(),range(100))
    print(dict(div=div(n), mid=mid(n)))

  def sym():
    s= adds(SYM(),"aaaabbc")
    print(dict(div=div(s), mid=mid(s)))

  def clone():
    data1= data(csv(the.file), rank=True)
    print(show(mids(data1)))
    print(show(mids(clone(data1, data1.rows))))

  def datas():
    data1= data(csv(the.file), rank=True)
    print(show(mids(data1, cols=data1.cols.y)))
    print(data1.cols.names)
    for i,row in enumerate(data1.rows):
      if i % 40 == 0: print(i,"\t",row)

  def loglike():
    data1= data(csv(the.file))
    print(show(sorted(loglikes(data1,row,1000,2)
                      for i,row in enumerate(data1.rows) if i%10==0)))

  def dists():
    data1= data(csv(the.file))
    print(show(sorted(dists(data1, data1.rows[0], row)
                      for i,row in enumerate(data1.rows) if i%10==0)))
    for _ in range(10):
      print("")
      x,y,C,=twoFaraway(data1)
      print(x,C);print(y)

  def halves():
    data1= data(csv(the.file))
    a,b,_ = half(data1,data1.rows)
    print(len(a), len(b))
    best,rest,n = halves(data1,stop=4)
    print(n,d2h(data1,best[0]))

  def smo():
    d= data(csv(the.file))
    print(">",len(d.rows))
    best = smo(d)
    print(len(best),d2h(d, best[0]))

  def profileSmo():
    import cProfile
    import pstats
    cProfile.run('smo(data(csv(the.file)))','/tmp/out1')
    p = pstats.Stats('/tmp/out1')
    p.sort_stats('time').print_stats(20)

  def smo20():
    "modify to show # evals"
    d= data(src=csv(the.file))
    b4=adds(NUM(), [d2h(d,row) for row in d.rows])
    now=adds(NUM(), [d2h(d, smo(d)[0]) for _ in range(20)])
    sep=",\t"
    print("mid",show(mid(b4)), show(mid(now)),show(b4.lo),sep=sep,end=sep)
    print("div",show(div(b4)), show(div(now)),sep=sep,end=sep)
    print(the.file)
#--------- --------- --------- --------- --------- --------- --------- --------- ---------
if __name__ == "__main__": main()

