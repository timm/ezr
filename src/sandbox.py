# import random
# from math import *
# def phi(x):
#   return (1.0 + erf(x / sqrt(2.0))) / 2.0
#
# def pc(n):
#   w = 6/n
#   def xy(i): x= -3 + i*w; return [x,phi(x),0]
#   lst = [xy(i) for i in range(n+1)]
#   for i,three in enumerate(lst):
#     if i > 0:
#       three[2] = lst[i][1] - lst[i-1][1]
#   [print([round(x,3) for x in three],sep="\t")
#    for three in lst]
#
# pc(30)
import random,math,sys 
huge = sys.maxsize
tiny = 1 / huge

class obj:
  def __init__(i,**d): i.__dict__.update(d)
  def __repr__(i)    : return i.__class__.__name__ +str(i.__dict__)

the = obj(bins=8,seed=31210,data="../data/auto93.csv")

class COL(obj):
  def make(s,n):  return (NUM if s[0].isupper else SYM)(s,n)

  def __init__(i,txt=" ",at=0):
    i.n = 0; i.at = at; i.txt = txt
    i.heaven = -1 if txt[-1] == "-" else 1
    i.isGoal = txt[-1] in "+-!"

  def adds(i,lst): [i.add(x) for x in lst];return i

  def bins(i,rowss):
    return i.bins1(sorted([(row[i.at], klass) 
                           for klass,rows in rowss.items() 
                           for row in rows if row[i.at] != "?"]))

class SYM(COL):
  def __init__(i,**kw): super().__init__(**kw); i.has = {}
  def add(i,x): i.n += 1; i.has[x] = 1 + i.has.get(x,0)
  def norm(i,x): return x
  def ent(i)  : return -sum(v/i.n*math.log(v/i.n,2) for _,v in i.has.items() if v>0)
  def bin1(i,xys,goal):
    c={}
    for x,y in xys:   
      k = y==goal
      c[k] = c.get(k,{})
      c[k][x] = c[k].get(x,0) + 1
    return sorted([(ent(c[k]),k) for k in c])[0] 

class NUM(COL):
  def __init__(i,**kw):
    super().__init__(**kw)
    i.mu,i.m2,i.sd,i.lo,i.hi = 0,0,0, huge, -huge

  def add(i,x):
    if x != "?":
      i.n  += 1
      i.lo  = min(x,i.lo)
      i.hi  = max(x,i.hi)
      delta = x - i.mu
      i.mu += delta / i.n
      i.m2 += delta * (x -  i.mu)
      i.sd  = 0 if i.n < 2 else (i.m2 / (i.n - 1))**.5

  def norm(i,x): return x=="?" and x or (x - i.lo) / (i.hi - i.lo + tiny)

  def bins1(i,xys,goal):
    n1,n2,c1,c2 = 0,len(xys),{},{}
    for x,y in xys:   
      k = y==goal
      c2[k] = c2.get(k,0) + 1
    small,min = len(xys)**.5, ent(c2) 
    for n,(x,y) in enumerate(xys):
      n2    -= 1; n1 += 1
      c2[y] -= 1; c1[y] = c1.get(y,0) + 1
      if n1>small and n2>small and x!=xys[n+1][0]:
        e=(n1*ent(c1) + n2*ent(c2))/(n1+n2)
        if e < min:
          min,cut = e,x 
    return (min,cut)

class DATA(obj):
  def __init__(i,lsts=[],order=False):
    head,*rows = list(lsts)
    i.cols = [COL.make(s,n) for n,s in enumerate(head)]
    i.ys   = {col.at:col for col in i.cols if col.isGoal}
    i.rows = []
    [i.add(row) for row in rows]
    if order: i.rows = sorted(i.rows, key=i.d2h)

  def add(i,row): 
    i.rows += [row]
    [col.add(x) for x,col in zip(row.cells,i.cols) if x != "?"]

  def clone(i, rows=[], order=False):
    return DATA([[col.txt for col in i.cols]] + rows, order=order)

  def d2h(i,row):
    n,d=0,0
    for col in i.ys.values():
      d += abs(col.norm(row[col.at]) - col.heaven)**2
      n += 1
    return (d/n)**.5

#-----------------------------------------------------
def ent(d):
  n = sum(d.values())
  return - sum(v/n*math.log(v/n,2) for v in d.values() if v>0)

def coerce(s):
  try: return ast.literal_eval(s)
  except Exception: return s

def csv(file=None):
  with file_or_stdin(file) as src:
    for line in src:
      line = re.sub(r'([\n\t\r"\’ ]|#.*)', '', line)
      if line: yield [coerce(s.strip()) for s in line.split(",")]

#-----------------------------------------------------     make saved
      
class Eg: 
  def all():
    sys.exit(sum(1 if getattr(Eg,s)()==False else 0 
                 for s in dir(Eg) if s[0] !="_" and s !="all"))
    
  def nums():  
    assert 6.61  < NUM().adds([x**.5 for x in range(100)]).mu  < 6.62
    assert 13.31 < NUM().adds([46,	69	,32,	60,	52	,41]).sd < 13.32

if __name__ == "__main__":  
  random.seed(the.seed)
  getattr(Eg, next(iter(sys.argv), 1), Eg.all)()