#!/usr/bin/env python3 -B
# <!-- vim: set ts=2 sw=2 sts=2 et: -->
"""
ezr.py : an experiment in easier AI. Less is more.
(C) 2024 Tim Menzies, timm@ieee.org, BSD-2.

OPTIONS:
  -a --any     #todo's to explore             = 100
  -d --decs    #decimals for showing floats   = 3
  -f --file    csv file for data              = ../data/misc/auto93.csv
  -F --Far     how far to seek faraway        = 0.8
  -k --k       bayes low frequency hack #1    = 1
  -H --Half    #rows for searching for poles  = 128
  -l --label   initial number of labelings    = 4
  -L --Last    max allow labellings           = 30
  -m --m       bayes low frequency hack #2    = 2
  -n  --n      tinyN                          = 12
  -N --N       smallN                         = 0.5
  -p --p       distance function coefficient  = 2
  -R --Run     start up action method         = help
  -s --seed    random number seed             = 1234567891
"""
# (FYI our seed is odious, pernicious, apocalyptic, deficient, and prime.)      
# The above settings. Can be updated via command line.   
# e.g. `./ezr.py -s $RANDOM` sets `the.seed` to a random value set by operating system.

#<br clear=left><hr>  
# ## Setting up
import re,ast,sys,math,random,copy,traceback
from fileinput import FileInput as file_or_stdin

# Class for quick inits of named structs, and pretty prints.
class o:
  def __init__(i,**d): i.__dict__.update(d)
  def __repr__(i): return i.__class__.__name__+str(show(i.__dict__))

def coerce(s):
  try: return ast.literal_eval(s) # <1>
  except Exception:  return s

the=o(**{m[1]:coerce(m[2]) for m in re.finditer(r"--(\w+)[^=]*=\s*(\S+)",__doc__)})

#--------- --------- --------- --------- --------- --------- --------- --------- --------
# ## Structs

# DATA stores rows, which are summarized in column headers.
def DATA(): return o(rows=[], cols=[])

# COLS is a factory that makes, and stores, the columns (`x,y` are the indepednet and depednet
# columns, `all` stores everything, `klass` is the class column).
def COLS(lst): return o(x=[], y=[], all=[], klass=None, names=lst)

# SYMs summarize a stream of symbols.
def SYM(txt=" ",at=0): return o(isNum=False, txt=txt, at=at, n=0, has={})

# NUMs summarize a stream of numbers.
# A trailing "-" or "+" denotes a numeric goal we need to minimize or maximize to 0 or 1.
def NUM(txt=" ",at=0,has=None):
  return o(isNum=True,  txt=txt, at=at, n=0, hi=-1E30, lo=1E30, 
           has=has, rank=0, # if has non-nil, used by the stats package
           mu=0, m2=0, maximize = txt[-1] != "-")

#--------- --------- --------- --------- --------- --------- --------- --------- --------
# ## Constructors

# Create columns (one for each string in `names`).
def cols(names):
  cols1 = COLS(names)
  cols1.all = [_cols(cols1,n,s) for n,s in enumerate(names)]
  return cols1

# Upper case names are NUM.  
# The `klass` name ends in "!".   
# A trailing "X" denotes "ignore".  
# If not ignoring, then the column is 
# either a dependent goals (held in `cols.y`) or a independent variable (held in `cols.x`).
def _cols(cols1, n, s):
  col = (NUM if s[0].isupper() else SYM)(txt=s, at=n)
  if s[-1] == "!": cols1.klass = col
  if s[-1] != "X": (cols1.y if s[-1] in "!+-" else cols1.x).append(col)
  return col

# Create data. `src` can be any iterator that returns a list of values 
# (e.g. some list, or the `csv` iterator, shown below, that reads rows from a csv file).
def data(src=None, rank=False):
  data1=DATA()
  [append(data1,lst) for  lst in src or []]
  if rank: data1.rows.sort(key = lambda lst:d2h(data1,lst))
  return data1

# Copy a structure (same column structure, but with different rows).
# Optionally, the rows in the new structure can be sorted.
def clone(data1, inits=[], rank=False):
  return data([data1.cols.names] + inits, rank=rank )

#--------- --------- --------- --------- --------- --------- --------- --------- ---------
# ## Update

# Update DATA.
def append(data,row1):
  if    data.cols: data.rows.append([add(col,x) for col,x in zip(data.cols.all,row1)])
  else: data.cols= cols(row1)

# Update NUMs and SYMs with many items.
def adds(col,lst): [add(col,x) for x in lst]; return col

# Update NUMs and SYMs with one item.
def add(col,x,n=1):
  if x!="?":
    col.n += n
    (_add2num if col.isNum else _add2sym)(col,x,n)
  return x

def _add2sym(sym,x,n): sym.has[x] = sym.has.get(x,0) + n

# Update NUMs using Welford's on-line 
# [algorithm](https://en.wikipedia.org/wiki/Algorithms_for_calculating_variance).
def _add2num(num,x,n):
  num.lo = min(x, num.lo)
  num.hi = max(x, num.hi)
  for _ in range(n):
    if num.has: num.has += [x]
    d       = x - num.mu
    num.mu += d / num.n
    num.m2 += d * (x -  num.mu)

#--------- --------- --------- --------- --------- --------- --------- --------- --------
# ## Queries

# Middle of a column.
def mid(col):
  return col.mu if col.isNum else max(col.has, key=col.has.get)

# Middle of some columns (defaults to `data.cols.x`).
def mids(data, cols=None):
  return {col.txt:mid(col) for col in cols or data.cols.x}

# Diversity of a column.
def div(col):
  return  (0 if col.n <2 else (col.m2/(col.n-1))**.5) if col.isNum else ent(col.has)

# Diverstiy of some columns (defaults to `data.cols.x`).
def divs(data, cols=None): return {col.txt:div(col) for col in cols or data.cols.x}

# Normalize `x` to 0..1
def norm(num,x): return x if x=="?" else (x-num.lo)/(num.hi - num.lo - 1E-30)


#--------- --------- --------- --------- --------- --------- --------- --------- --------
# ## Distances

# Distance to `heaven` (which is the distance of the `y` vals to the best values).
def d2h(data,row):
  n = sum(abs(norm(num,row[num.at]) - num.maximize)**the.p for num in data.cols.y)
  return (n / len(data.cols.y))**(1/the.p)

# Distances between two rows
def dists(data,row1,row2):
  n = sum(dist(col, row1[col.at], row2[col.at])**the.p for col in data.cols.x)
  return (n / len(data.cols.x))**(1/the.p)

# Distance between two values
def dist(col,x,y):
  if  x==y=="?": return 1
  if not col.isNum: return x != y
  x, y = norm(col,x), norm(col,y)
  x = x if x !="?" else (1 if y<0.5 else 0)
  y = y if y !="?" else (1 if x<0.5 else 0)
  return abs(x-y)

def neighbors(data,row1, rows=None):
  return sorted(rows or data.rows, key=lambda row2: dists(data,row1,row2))

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
  return -sum(v/N*math.log(v/N,2) for v in d.values() if v > 0)

def value(d,goal=True):
  b,r,n = 1E-30,1E-30,1E-30
  for k,v in d.items():
    n += v
    if k==goal: b += v
    else: r += v
  b,r = b/n, r/n
  return b**2/(b+r)

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
      if arg == "-"+k[0]:
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

