"""
Explore a `todo` set, within fewest queries to labels:

1. Label and move a few `initial` items to a `done`.
2. Sort the `done` into sqrt(n) `best` and `rest`.
3. Build a model that reports likelihood `b,r` of an item being in `best` or `rest`. 
4. Sort `todo` by `-b/r`. 
5. From that sorted `todo` space,   
   (a) delete the last `forget` percent (e.g. 20%);    
   (b) move  the first item into `done`.
6. Goto step 2.
"""
import sys,math
from collections import Counter
from fileinput import FileInput as file_or_stdin 

big = 1E30
tiny = 1/big

class OBJ:
  def __init__(i,**d) : i.__dict__.update(d)
  def __repr__(i)     : return i.__class__.__name__+'{'+str(i.__dict__)+'}'

the = OBJ(k=1, m=2, bins=8, file="../data/auto93.csv")
#----------------------------------------------------------------------------------------
class BIN(OBJ):
  def __init__(i,at,lo):  i.at,i.lo,i.hi,i.ys = at,lo,lo,Counter()  

  def add(i,x,y):
    i.lo = min(x, i.lo)
    i.hi = max(x, i.hi)
    i.ys[y] += 1

  def merge(i,j,xpect):
    if i.at == j.at:
      k     = BIN(at=i.at, lo=min(i.lo,j.lo), hi=max(i.hi,j.hi), ys=i.ys+j.ys)
      ei,ni = entropy(i.ys)
      ej,nj = entropy(j.ys)
      ek,nk = entropy(k.ys)
      if ni < xpect or nj < xpect: return k
      if ek <= (ni*ei + nj*ej)/nk  : return k

  def selects(i,lst): 
    return  lst[i.at]=="?" or i.lo <= lst[i.at] <= i.hi
#----------------------------------------------------------------------------------------
class COL(OBJ):
  def __init__(i,at=0,txt=" "): i.n,i.at,i.txt = 0,at,txt

  def bins(i,pos,neg):
    d, xpect = {}, (len(pos)+len(neg))/the.bins
    def send2bin(x,y):
      if x != "?":
        k = i.bin(x)
        if k not in d: d[k] = BIN(i.at,x)
        d[k].add(x,y)
    [send2bin(row[i.at],y) for y,rows in [("+",pos),("-",neg)] for row in rows] 
    return i._bins(sorted(d.values(), key=lambda z:z.lo), xpect)
#----------------------------------------------------------------------------------------
class SYM(COL):
  def __init__(i,*kw): super().__init__(**kw); i.has = {}
  def add(i,x):
    if x != "?":
      i.n += 1
      i.has[x] = i.has.get(x,0) + 1
 
  def _bins(i,bins,_)  : return bins
  def bin(i,x)         : return x
  def div(i)           : return entropy(i.has)
  def like(i,x,m,prior): return (i.has.get(x, 0) + m*prior) / (i.n + m)
  def mid(i)           : return max(i.has, key=i.has.get)
#----------------------------------------------------------------------------------------
class NUM(COL):
  def __init__(i,*kw): 
    super().__init__(**kw); i.mu,i.m2 = 0,0
    i.heaven = 0 if i.txt[-1]=="-" else 1

  def add(i,x):
    if x != "?":
      i.n += 1
      d = x - i.mu
      i.mu += d/i.n
      i.m2 += d * (x -  i.mu)

  def _bins(i, bins, xpect): return merges(bins,merge=lambda x,y:x.merge(y,xpect))
  def bin(i,x): 
    tmp = int(the.bins * i.norm(x))
    return the.bins - 1 if tmp==the.bins else tmp 
  
  def d2h(i,x) : return abs(i.norm(x) - i.heaven)
  def div(i)   : return  0 if i.n < 2 else (i.m2 / (i.n - 1))**.5
  def mid(i)   : return i.mu
  def norm(i,x): return x=="?" and x or (x - i.lo) / (i.hi - i.lo + tiny)   

  def like(i, x, *_):
    v     = i.div()**2 + tiny
    nom   = math.e**(-1*(x - i.mu)**2/(2*v)) + tiny
    denom = (2*math.pi*v)**.5
    return min(1, nom/(denom + tiny))
#----------------------------------------------------------------------------------------
class COLS(OBJ):
  def __init__(i,names):
    i.x,i.y,i.all,i.names,i.klass = [],[],[],names,None
    for at,txt in enumerate(names):
      a,z = txt[0], txt[-1]
      col = (NUM if a.isupper() else SYM)(at=at,txt=txt)
      i.all.append(col)
      if z != "X":
        (i.y if z in "!+-" else i.x).append(col)
        if z == "!": i.klass= col

  def add(i,lst):
    [col.add(lst[col.at]) for col in i.all if lst[col.at] != "?"]; return lst
#----------------------------------------------------------------------------------------
class DATA(OBJ):
  def __init__(i,src=[],order=False,fun=None):
    i.rows, i.cols = [],[]
    [i.add(lst,fun) for lst in src]

  def add(i,lst,fun=None):
    if i.cols: 
      if fun: fun(i,lst)
      i.rows += [i.cols.add(lst)]
    else: 
      i.cols = COLS(lst)

  def clone(i,lst=[],ordered=False):
    return DATA([i.cols.names]+lst)
  
  def d2h(i, lst):
    d = sum(col.d2h( lst[col.at] )**2 for col in i.cols.y)
    return (d/len(i.cols.y))**.5

  def loglike(i, lst, nall, nh, m,k):
    prior = (len(i.rows) + k) / (nall + k*nh)
    likes = [c.like(lst[c.at],m,prior) for c in i.cols.x if lst[c.at] != "?"]
    return sum(math.log(x) for x in likes + [prior] if x>0)
  
  def order(i):
    i.rows = sorted(i.rows, key=i.d2h)
    return i.rows
#----------------------------------------------------------------------------------------
class NB(OBJ):
  def __init__(i): i.nall, i.datas = 0,{}

  def loglike(i,data,lst):
    return data.loglike(lst, i.nall, len(i.datas), the.m, the.k)

  def run(i,data,lst):
    klass = lst[data.cols.klass.at]
    i.nall += 1
    if klass not in i.datas: i.datas[klass] =  data.clone()
    i.datas[klass].add(lst)
#----------------------------------------------------------------------------------------
def entropy(d):
  N = sum(n for n in d.values()if n>0)
  return -sum(n/N*math.log(n/N,2) for n in d.values() if n>0), N

def merges(b4, merge):
  "Bottom up clustering. While we can merge adjacent items, merge then repeat."
  j, now, most, repeat  = 0, [], len(b4), False 
  while j <  most:
    a = b4[j] 
    if j <  most - 1: 
      if tmp := merge(a, b4[j+1]):  
        a, j, repeat = tmp, j+1, True  # skip merged item, search down rest of list
    now += [a]
    j += 1
  return merges(now, merge) if repeat else b4 

def coerce(s):
  try: return ast.literal_eval(s) # <1>
  except Exception:  return s

def csv(file=None):
  with file_or_stdin(file) as src:
    for line in src:
      line = re.sub(r'([\n\t\r"\’ ]|#.*)', '', line)
      if line: yield [coerce(s.strip()) for s in line.split(",")]
#----------------------------------------------------------------------------------------
class MAIN:
  def opt(): print(the)

  def data(): 
   d=DATA(csv(the.file))
   print(d.cols.x[1].div()) 

  def rows():
    d=DATA(csv(the.file))
    print(sorted(round(d.loglike(row,len(d.rows),1, the.m, the.k),3) for row in d.rows)[::50])

if __name__=="__main__" and len(sys.argv) > 1: 
	getattr(MAIN, sys.argv[1], MAIN.opt)()
