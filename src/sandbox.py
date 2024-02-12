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
import math
huge = sys.maxsize
tiny = 1 / huge

class obj:
  def __init__(i,**d): i.__dict__.update(d)
  def __repr__(i)    : return i.__class__.__name__ +str(i.__dict__)

the = obj(bins=8)

def COL(obj):
  def __init__(i,at=0,txt=" "):
    i.n = 0; i.at = at; i.txt = txt, 
    i.goalp  = txt[-1] in "+-!", 
    i.heaven = 0 if txt[-1] == "-" else 1

class SYM(obj):
  def __init__(i,**kw): super().__init__(**kw); i.has = {}
  def add(i,x): i.n += 1; i.has[x] = 1 + i.has.get(x,0)
  def bin(i,x): return x 
  def ent(i)  : return -sum(v/i.n*math.log(v/n,2) for _,v in i.has.items() if v>0)

def NUM(obj):
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

  def bin(i,x):
    n = (i.hi - i.lo)/the.bins
    return x if x=="?" else min(the.bins-1, int((x - i.lo) / n))

class ROW(obj):
  def __init__(i,lst, data): i.cells,i.data,i.bins = lst,data,[]

  def bins(i):
    i.bins = [col.bin(x) for col,x in zip(data.cols,i.cells)]

class DATA(obj):
  def __init__(i,lsts=[],order=False)
    head,*rows = list(lsts) 
    i.cols = [(NUM if s[-1].isupper() else SYM)(s,n) for s,n in enumerate(head)]
    i.rows = []
    [i.add(row) for row in rows] 
    if order: i.ordered()

  def add(i,row): 
    row = row if isinstance(row,Row) else ROW(row,i)
    i.rows += [row] 
    [col.add(x) for x,col in zip(row,i.cols) if x != "?"]

  def clone(i, rows=[], order=False):
    return DATA([[col.txt for col in i.col]] + rows, order=order)


