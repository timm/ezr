#!/usr/bin/env python3 -B
# <!-- vim: set ts=2 sw=2 sts=2 et: -->
"""
    ezr.py :  an experiment in easier explainable AI. Less is more.    
    (C) 2024 Tim Menzies, timm@ieee.org, BSD-2.    
        
    OPTIONS:    
      -a --any    #todo's to explore             = 100    
      -d --decs   #decimals for showing floats   = 3    
      -f --file   csv file for data              = ../data/misc/auto93.csv    
      -F --Far    how far to seek faraway        = 0.8    
      -k --k      bayes low frequency hack #1    = 1    
      -H --Half   #rows for searching for poles  = 128    
      -l --label  initial number of labelings    = 4    
      -L --Last   max allow labelings            = 30    
      -m --m      bayes low frequency hack #2    = 2    
      -n --n      tinyN                          = 12    
      -N --N      smallN                         = 0.5    
      -p --p      distance function coefficient  = 2    
      -R --Run    start up action method         = help    
      -s --seed   random number seed             = 1234567891    
      -x --xys    max #bins in discretization    = 16    
"""
# (FYI our seed is an 
# [odious, apocalyptic, deficient, pernicious, polite, prime](https://numbersaplenty.com/1234567891) 
# number.)      
import re,ast,sys,math,random,copy,traceback
from fileinput import FileInput as file_or_stdin
from typing import Any as any

#--------- --------- --------- --------- --------- --------- --------- --------- --------
# ## Types

class o:
  "`o` is a Class for quick inits of structs,  and for pretty prints."
  def __init__(i,**d): i.__dict__.update(d)
  def __repr__(i): return i.__class__.__name__+str(show(i.__dict__))

# Other types used in this system.
xy,cols,data,num,sym = o,o,o,o,o
col     = num | sym
number  = float | int
atom    = number | bool | str # and sometimes "?"
row     = list[atom]
rows    = list[row]
classes = dict[str,rows] # `str` is the class name

#--------- --------- --------- --------- --------- --------- --------- --------- --------
# ## Settings

def coerce(s:str) -> atom:
  "Coerces strings to atoms."
  try: return ast.literal_eval(s)
  except Exception:  return s

# Build the global settings variable by parsing the `__doc__` string.
the=o(**{m[1]:coerce(m[2]) for m in re.finditer(r"--(\w+)[^=]*=\s*(\S+)",__doc__)})

# All the settings in `the`  can be updated via command line.   
# For dictionary `d` with key `key`, if command line has `-k X`, then d[key]=coerce(X).
def cli(d:dict):
  "For dictionary key `k`, if command line has `-k X`, then `d[k]=coerce(X)`."
  for k,v in d.items():
    v = str(v)
    for c,arg in enumerate(sys.argv):
      if arg in ["-"+k[0], "--"+k]:
        d[k] = coerce("false" if v=="true" else ("true" if v=="false" else sys.argv[c+1]))

#--------- --------- --------- --------- --------- --------- --------- --------- --------
# ## Structs

# Anything named "_X" is a primitive constructor called by  another constuctor "X".

def _DATA() -> data:
  "DATA stores `rows` (whose columns  are summarized in `cols`)."
  return o(this=DATA, rows=[], cols=None) # cols=None means 'have not read row1 yet'

def _COLS(names: list[str]) -> cols:
  "COLS are factories to make columns. Stores independent/dependent cols `x`/`y` and `all`."
  return o(this=COLS, x=[], y=[], all=[], klass=None, names=names)

def SYM(txt=" ",at=0) -> sym:
  "SYMs incrementally summarizes a stream of symbols."
  return o(this=SYM, txt=txt, at=at, n=0, has={})

def NUM(txt=" ",at=0,has=None) -> num:
  "NUMs incrementally summarizes a stream of numbers."
  return o(this=NUM, txt=txt, at=at, n=0, hi=-1E30, lo=1E30, 
           has=has, rank=0, # if has non-nil, used by the stats package
           mu=0, m2=0, maximize = txt[-1] != "-")

def XY(at,txt,lo,hi=None,ys=None) -> xy:
  "`ys` counts symbols of one column seen between `lo`.. `hi` of another column."
  return o(this=XY,n=0,at=at, txt=txt, lo=lo, hi=hi or lo, ys=ys or {})

#--------- --------- --------- --------- --------- --------- --------- --------- --------
# ## CRUD (= create, read, update, delete
# We don't need to delete (thanks to garbage collection). 
# And "read" is really "read in from some source" and "read out; i.e. query the structs.

# ### Create

def COLS(names: list[str]) -> cols:
  "Create columns (one for each string in `names`)."
  i = _COLS(names)
  i.all = [add2cols(i,n,s) for n,s in enumerate(names)]
  return i

# Rules for column names:    
# (1) Upper case names are NUM.      
# (2) `klass` names ends in '!'.       
# (3) A trailing 'X' denotes 'ignore'.      
# (4)  If not ignoring, then the column is either a dependent goals (held in `cols.y`) or 
#   a independent variable (held in `cols.x`  
# Using those rules,
def add2cols(i:cols, n:int, s:str) -> col:
  "create a NUM or SYM from `s`. Adds it to `x`, `y`, `all` (if appropriate)."
  new = (NUM if s[0].isupper() else SYM)(txt=s, at=n)
  if s[-1] == "!": i.klass = new
  if s[-1] != "X": (i.y if s[-1] in "!+-" else i.x).append(new)
  return new

def DATA(src=None, rank=False) -> data:
  "Adds rows from `src` to a DATA. Summarizes them in `cols`. Maybe sorts the rows."
  i = _DATA()
  [add2data(i,lst) for  lst in src or []]
  if rank: i.rows.sort(key = lambda r:d2h(i,r))
  return i

# ### Update

def add2data(i:data,row1:row) -> None:
  "Update contents of a DATA. Needs `add2col()` or `COLS()`."
  if    i.cols: i.rows.append([add2col(col,x) for col,x in zip(i.cols.all,row1)])
  else: i.cols= COLS(row1)

def adds(i:col, lst:list) -> col:
  "Update a NUM or SYM with many items. Needs `add2col()`."
  [add2col(i,x) for x in lst]
  return i

def add2col(i:col, x:any, n=1) -> any:
  "`n` times, update NUM or SYM with one item. May need `add2num()`."
  if x != "?":
    i.n += n
    if i.this is NUM: add2num(i,x,n)
    else: i.has[x] = i.has.get(x,0) + n
  return x

def add2num(i:num, x:any, n:int) -> None:
  "`n` times, update a NUM with one item."
  i.lo = min(x, i.lo)
  i.hi = max(x, i.hi)
  for _ in range(n):
    if i.has != None: i.has += [x]
    d     = x - i.mu
    i.mu += d / i.n
    i.m2 += d * (x -  i.mu)

def add2xy(i:xy, x: int | float , y:atom) -> None:
  "Update an XY with `x` and `y`."
  if x != "?":
    i.n  += 1
    i.lo =  min(i.lo, xy.lo)
    i.hi =  max(i.hi, xy.hi)
    xy.ys[y] = xy.ys[y].get(y,0) + 1

def xys2xy(*xys : list[xy]) -> xy:
  "Fuse together many XYs into one XY."
  out = XY(xys[0].at, xys[0].txt, xys[0].lo)
  for xy in xys:
    out.n += xy.n
    out.lo =  min(out.lo, xy.lo)
    out.hi =  max(out.hi, xy.hi)
    for y,n in xy.ys.items(): out.ys[y] = out.ys[y].get(y,0) + n
  return out

# ### Read (read in from another source)

# Read rows into a new DATA, guided by an old DATA.
def clone(i:data, inits=[], rank=False) -> data:
  "Copy a DATA (same column structure, with different rows). Optionally, sort it."
  return DATA([i.cols.names] + inits, rank=rank )

# Read rows  from disk.
def csv(file="-") -> row:
  "Iteratively  return `row` from a file, or standard input."
  with file_or_stdin(None if file=="-" else file) as src:
    for line in src:
      line = re.sub(r'([\n\t\r ]|#.*)', '', line)
      if line: yield [coerce(s.strip()) for s in line.split(",")]

# ### Read (read out: query the structs)

def stats(i:data, fun=mid, what:cols=None) -> dict[str,atom]:
  "Stats of some columns (defaults to `fun=mid` of `data.cols.x`), Needs `div()` or `mid()`.""
  return {c.txt:fun(c) for c in what or i.cols.x}

def mid(i:col) -> atom:
  "Middle of a column."
  return i.mu if i.this is NUM else max(i.has, key=i.has.get)

def div(i:col) -> float:
  "Diversity of a column."
  return  (0 if i.n <2 else (i.m2/(i.n-1))**.5) if i.this is NUM else ent(i.has)

def norm(i:num,x) -> float:
  "Normalize `x` to 0..1"
  return x if x=="?" else (x-i.lo)/(i.hi - i.lo - 1E-30)

#--------- --------- --------- --------- --------- --------- --------- --------- --------
# ## Discretization

def discretize(i:col, datas:classes) -> list[xy] ::
  "Find good ranges for the i-th column within `datas`."
  tmp = {}
  [send2xy(i, r[i.at], klass, tmp) for klass,rows1 in datas.items() for r in rows1]
  tmp =  sorted(tmp.values(), key=lambda z:z.lo)
  small = sum(len(rs) for rs in datas.values()) / the.xys
  return tmp if col.this is SYM else merges(tmp, small)

def send2xy(i:col,x:atom, y:str, d:dict) -> None:
  "Store `x,y` in the right part of `d`. Used by `discretize()`."
  if x != "?":
   k = x if col.this is SYM else int(the.xys * norm(i,x))
   k = min(k, the.xys - 1) # so we don't get one lonely item at max
   d[k] = d[k] if k in d else xy(col.at,col.txt,x)
   add2xy(d[k],x,y)

def merges(b4, small):
  "Try merging adjacent items in `b4`. If successful, repeat. Used by `discretize()`.""
  j, now  = 0, []
  while j <  len(b4):
    a = b4[j]
    if j <  len(b4) - 1:
      b = b4[j+1]
      if ab := merge(a,b,small)
        a = ab
        j = j+1  # if i can merge, jump over the merged item
    now += [a]
    j += 1
  return b4 if len(now) == len(b4) else merges(now, small)

def merge(xy1: xy, xy2: xy, small:int) -> xy | None:
  "Return the merge  if the whole is better than the parts. Used  by `merges()`. 
  xy3 = xys2xy(xy1,xy2)
  e1  = ent(xy1.ys)
  e2  = ent(xy2.ys)
  e3  = ent(xys3.ys)
  if n1 <  small or n2 < small or e3 <= (xy.n1*e1 + xy2.n*e2)/n3: return xy3 

#--------- --------- --------- --------- --------- --------- --------- --------- --------
# ## Distances

def d2h(i:data, r:row) -> float:
  "distance to `heaven` (which is the distance of the `y` vals to the best values)."
  n = sum(abs(norm(num,r[num.at]) - num.maximize)**the.p for num in i.cols.y)
  return (n / len(i.cols.y))**(1/the.p)

def dists(i:data, r1:row, r2:row) -> float:
  "Distances between two rows. Needs `dist()`."
  n = sum(dist(c, r1[c.at], r2[c.at])**the.p for c in i.cols.x)
  return (n / len(i.cols.x))**(1/the.p)

def dist(i:col, x:any, y:any) -> float:
  "Distance between two values."
  if  x==y=="?": return 1
  if i.this is SYM: return x != y
  x, y = norm(i,x), norm(i,y)
  x = x if x !="?" else (1 if y<0.5 else 0)
  y = y if y !="?" else (1 if x<0.5 else 0)
  return abs(x-y)

def neighbors(i:data, r1:row, region:rows=None) -> list[row]:
  "Sort the `region` (default=`i.rows`),ascending,  by distance to `r1`."
  return sorted(region or i.rows, key=lambda r2: dists(i,r1,r2))

#--------- --------- --------- --------- --------- --------- --------- --------- --------
# ## Clustering

def halves(i:data, region:rows=None, stop=None, rest=None, evals=1, before=None):
  "Recursively bi-cluster `region`, reursing only down the best half. Needs `half()`."
  region = region or i.rows
  stop = stop or 2*len(region)**the.N
  rest = rest or []
  if len(region) > stop:
    lefts,rights,left  = half(i,region, True, before)
    return halves(i,lefts, stop, rest+rights, evals+1, left)
  else:
    return region,rest,evals

def half(i:data, region:rows, sortp=False, before=None) -> tuple[rows,rows,row]:
  "Split the `region` in half according to each row's distance to two distant points. Needs `twofaraway()`."
  mid = int(len(region) // 2)
  left,right,C = twoFaraway(i, region, sortp=sortp, before=before)
  cos = lambda row1: (dists(i,row1,left)**2 + C**2 - dists(i,row1,right)**2)/(2*C)
  tmp = sorted(region, key=cos)
  return tmp[:mid], tmp[mid:], left

def twoFaraway(i:data, region:rows,before=None, sortp=False) -> tuple[row,row,float]:
  "Find two distant points within the `region`. Needs `faraway()`."
  region = random.choices(region, k=min(the.Half, len(region)))
  x = before or faraway(i, random.choice(region), region)
  y = faraway(i, x, region)
  if sortp and d2h(i,y) < d2h(i,x): x,y = y,x
  return x, y,  dists(i,x,y)

def faraway(i:data, r1:row, region:rows) -> row:
  "Find something far away from `r1` with the `region`."
  farEnough = int( len(region) * the.Far) # to avoid outliers, don't go 100% far away
  return neighbors(i,r1, region)[farEnough]

#--------- --------- --------- --------- --------- --------- --------- --------- --------
# ## Likelihoods

def loglikes(i:data, r:row, nall:int, nh:int) -> float:
  "Likelihood of a `row` belonging to a DATA. Needs `like()`."
  prior = (len(i.rows) + the.k) / (nall + the.k*nh)
  likes = [like(c, r[c.at], prior) for c in i.cols.x if r[c.at] != "?"]
  return sum(math.log(x) for x in likes + [prior] if x>0)

def like(i:col, x:any, prior:float) -> float:
  "Likelihood of `x` belonging to a col. May need `like4num()`."
  return like4num(i,x) if i.this is NUM else (i.has.get(x,0) + the.m*prior) / (i.n+the.m)

def like4num(i:num,x):
  "Likelihood of `x` belonging to a NUM."
  v     = div(i)**2 + 1E-30
  nom   = math.e**(-1*(x - mid(i))**2/(2*v)) + 1E-30
  denom = (2*math.pi*v) **0.5
  return min(1, nom/(denom + 1E-30))

#--------- --------- --------- --------- --------- --------- --------- --------- --------
# ## Sequential model optimization

def smo(i:data, score=lambda B,R: B-R):
  "Sequential model optimization."
  def ranked(lst:rows) -> rows:
    "sort `lst` by distance to heaven"
    return sorted(lst, key = lambda r:d2h(i,r))

  def guess(todo:rows, done:rows) -> rows:
    "Divide `done` into `best`,`rest`. use those to guess the order of unlabelled rows."
    cut  = int(.5 + len(done) ** the.N)
    best = clone(i, done[:cut])
    rest = clone(i, done[cut:])
    key  = lambda r: score(loglikes(best, r, len(done), 2),
                           loglikes(rest, r, len(done), 2))
    random.shuffle(todo) # optimization: only sort a random subset of todo 
    return sorted(todo[:the.any], key=key, reverse=True) + todo[the.any:]

  def smo1(todo:rows, done:rows) -> rows:
    "Guess the `top`  unlabeled row, add that to `done`, resort `done`, and repeat"
    for _ in range(the.Last - the.label):
      if len(todo) < 3: break
      top,*todo = guess(todo, done)
      done += [top]
      done = ranked(done)
    return done

  random.shuffle(i.rows) # remove any  bias from older runs
  return smo1(i.rows[the.label:], ranked(i.rows[:the.label]))

#--------- --------- --------- --------- --------- --------- --------- --------- ---------
# ## Misc Functions

def ent(d:dict) -> float:
  "Entropy of a distribution."
  N = sum(v for v in d.values())
  return -sum(v/N*math.log(v/N,2) for v in d.values())

def bore(d,best=True,BEST=1,REST=1):
  "Score a distribution by how often it selects for `best`."
  b,r = 1E-30,1E-30
  for k,v in d.items():
    if k==best: b += v
    else      : r += v
  b,r = b/BEST, r/REST
  return b**2/(b+r) # support * probability

def show(x:any) -> any:
  "Some pretty-print rules."
  it = type(x)
  if it == float:  return round(x,the.decs)
  if it == list:   return [show(v) for v in x]
  if it == dict:   return "("+' '.join([f":{k} {show(v)}" for k,v in x.items()])+")"
  if it == o:      return show(x.__dict__)
  if it == str:    return '"'+str(x)+'"'
  if callable(x):  return x.__name__
  return x

def btw(*args, **kwargs):
  "Print to standard error, flush standard error, do not print newlines."
  print(*args, file=sys.stderr, end="", flush=True, **kwargs)

#--------- --------- --------- --------- --------- --------- --------- --------- ---------
# ## Main

def main() -> None: 
  "Update `the` from the command line; call the start-up command `the.Run`."
  cli(the.__dict__); run(the.Run)

def run(s:str) -> int:
  "Reset the seed. Run `eg[s]()`. Afterwards, restore old settings. Return '1' on failure."
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
  return out

#--------- --------- --------- --------- --------- --------- --------- --------- ---------
# ## Start-up Actions
# `./ezr.py -R xx` with execute `eg.xx()` at start-up time.

class eg:
  "Store all the start up actions"
  def all():
    "Run all actions. Return to OS a count of failing actions (those returning `False`.."
    sys.exit(sum(run(s)==False for s in dir(eg) if s[0] !="_" and s !=  "all"))

  def help():
    "Print help."
    print(re.sub(r"\n    ","\n",__doc__))
    print("Start-up commands:")
    [print(f"  -R {k:15} {getattr(eg,k).__doc__}") for k in dir(eg) if k[0] !=  "_"]

  def the(): 
    "Show settings."
    print(the)

  def csv(): 
    "Print some of the csv rows."
    [print(x) for i,x in enumerate(csv(the.file)) if i%50==0]

  def cols():
    "Demo of column generation."
    [print(show(col)) for col in 
       COLS(["Clndrs","Volume","HpX","Model","origin","Lbs-","Acc+","Mpg+"]).all]

  def num():
    "Show mid and div from NUMbers."
    n= adds(NUM(),range(100))
    print(show(dict(div=div(n), mid=mid(n))))

  def sym():
    "Show mid and div from SYMbols."
    s= adds(SYM(),"aaaabbc")
    print(show(dict(div=div(s), mid=mid(s))))

  def datas():
    "Show sorted rows from a DATA."
    data1= DATA(csv(the.file), rank=True)
    print(show(stats(data1, what=data1.cols.y)))
    print(data1.cols.names)
    for i,row in enumerate(data1.rows):
      if i % 40 == 0: print(i,"\t",row)

  def clone():
    "Check that clones have same structure as original."
    data1= DATA(csv(the.file), rank=True)
    print(show(stats(data1)))
    print(show(stats(clone(data1, data1.rows))))

  def loglike():
    "Show some bayes calcs."
    data1= DATA(csv(the.file))
    print(show(sorted(loglikes(data1,row,1000,2)
                      for i,row in enumerate(data1.rows) if i%10==0)))

  def dists():
    "Show some distance calcs."
    data1= DATA(csv(the.file))
    print(show(sorted(dists(data1, data1.rows[0], row)
                      for i,row in enumerate(data1.rows) if i%10==0)))
    for _ in range(5):
      print("")
      x,y,C,=twoFaraway(data1,data1.rows)
      print(x,C);print(y)

  def halves():
    "Halve the data."
    data1= DATA(csv(the.file))
    a,b,_ = half(data1,data1.rows)
    print(len(a), len(b))
    best,rest,n = halves(data1,stop=4)
    print(n,d2h(data1,best[0]))

  def smo():
    "Optimize something."
    d= DATA(csv(the.file))
    print(show(d.cols.all[1]))
    print(">",len(d.rows))
    best = smo(d)
    print(len(best),d2h(d, best[0]))

  def profileSmo():
    "Example of profiling."
    import cProfile
    import pstats
    cProfile.run('smo(data(csv(the.file)))','/tmp/out1')
    p = pstats.Stats('/tmp/out1')
    p.sort_stats('time').print_stats(20)

  def smo20():
    "Run smo 20 times."
    d= DATA(src=csv(the.file))
    b4=adds(NUM(), [d2h(d,row) for row in d.rows])
    now=adds(NUM(), [d2h(d, smo(d)[0]) for _ in range(20)])
    sep=",\t"
    print("mid",show(mid(b4)), show(mid(now)),show(b4.lo),sep=sep,end=sep)
    print("div",show(div(b4)), show(div(now)),sep=sep,end=sep)
    print(the.file)

#--------- --------- --------- --------- --------- --------- --------- --------- ---------
if __name__ == "__main__": main()



