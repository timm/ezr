import math,sys
huge = sys.maxsize
tiny = 1 / huge

class obj:
  def __init__(i,**d): i.__dict__.update(d)
  def __repr__(i)    : return i.__class__.__name__ +str(i.__dict__)

the = obj(bins=8)

def nth(n): return lambda lst: lst[n] == "?"

def d2h(i,row):
    for col in i.ys.values():
      n +=1
      d += (abs(col.norm(row[col.at]) - col.heaven)**2
    return (d/n)**.5

def first(a): return a[0]
def second(a): return a[1]
def lt(x,y):  return x < y
def gt(x,y):  return x > y

def cells(col, rows, klass):
  return [(row[col.at],klass,row) for row in rows if row[col.at] != "?"]

def fft(i,rowss):
  lst = sorted(rows in rows],key=i.d2h)
  n   = int(.5 + len(lst)**.5)
  for col in i.xs:
    for rule in fft1(4,sorted(cells(col,lst[:n],True) + cells(col,lst[n:],False))):
      yield rule

def fft1(depth,xyr):
  if depth < 0:
    lhs,rhs,cut = {}, {}, xyr[int(len(xyr)//2)][0]
    for x,k,_ in xyr: rhs[x] = rhs.get(x,0) + 1
    for n,(x,k,_) in enumerate(xyr):
      lhs[x]  = lhs.get(x,0) + 1
      rhs[x] += 1
      n1      = n + 1
      n2      = len(xyr) - n1
      tmp     = (n1*ent(lhs) + n2*ent(rhs))/(n1+n2)
      if tmp < most: most,cut = tmp,n
    if cut:
      left, right = xyr[:cut], xyr[cut:]
  
    
  
  lo, op, cut    = huge, lt, lst[int(len(lst)//2)][1]
  s1, s2 =  0, sum(first(x) for x in lst)
  for d,x in lst:
    s1 += d
    s2 -= d
    if s1 < s2 and s1 < lo: lo,op,cut = s1,lt,x
    if s2 < s1 and s2 < lo: lo,op,cut = s2,gt,x
  return lo,op,cut


  (x(row),y) for y,rows in rowss.items() for row in rows],
               key=lambda xy:xy[0])
  lefts,rights,lhs,rhs = 0,len(xys),dict(),dict()
  for _,y in xys: rhs[y] = rhs.get(y,0) + 1
  least,cut = huge,None
  for x,y in enumerate(xys): 
    lefts  += 1; lhs[y] = lhs.get(y,0) + 1
    rights -= 1; rhs[y] -= 1
    tmp     = (lefts*ent(lhs) + rights*ent(rhs)) / (lefts + rights)
    if tmp < least: least,cut = tmp,x

def ent(d):
  n = sum(d.values())
  return - sum(v/n*math.log(v/n,2) for v in d.values() if v>0)

   1 2 3 4 5 6 6 7
   a a a   a
         b b b b b

  lst = sorted([x(r) for r in rows if x(r) != "?"])
  for x in lst: 
    if x1 != "?": c2[x1] += 1


def COL(obj):
  def __init__(i,at=0,txt=" "):
    i.n = 0; i.at = at; i.txt = txt,
    i.heaven = 0 if txt[-1] == "-" else 1
    i.goalp  = txt[-1] in "+-!",

class SYM(obj):
  def __init__(i,**kw): COL.__init__(**kw); i.has = {}
  def add(i,x): i.n += 1; i.has[x] = 1 + i.has.get(x,0)
  def bin(i,x): return x
  def ent(i)  : return -sum(v/i.n*math.log(v/i.n,2) for _,v in i.has.items() if v>0)

def NUM(obj):
  def __init__(i,**kw):
    COL.__init__(**kw)
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

  def bin(i,x):
    width = (i.hi - i.lo)/the.bins
    return x if x=="?" else min(the.bins-1, int((x - i.lo) / width))

class ROW(obj):
  def __init__(i,lst, data): i.cells,i.data  = lst,data

  def bin(i): i.bins = [col.bin(x) for col,x in zip(i.data.cols,i.cells)]

class DATA(obj):
  def __init__(i,lsts=[],order=False):
    head,*rows = list(lsts)
    i.cols = [(NUM if s[-1].isupper() else SYM)(s,n) for s,n in enumerate(head)] 
    i.rows = []
    [i.add(row) for row in rows]
    if order: i.ordered()

  def add(i,row):
    row = row if isinstance(row,ROW) else ROW(row,i)
    i.rows += [row]
    [col.add(x) for x,col in zip(row.cells,i.cols) if x != "?"]

  def clone(i, rows=[], order=False):
    return DATA([[col.txt for col in i.cols]] + rows, order=order)
