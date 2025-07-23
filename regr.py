#!/usr/bin/env python3 -B
"""
reggr.py, multi objective tree building   
(c) 2025, Tim Menzies <timm@ieee.org>, MIT license   
   
Options:  
 -s random seed      seed=1234567891    
 -P number of poles  Poles=4
 -p dist coeffecient p=2
 -f data file        file=../moot/optimize/misc/auto93.csv   
"""
from types import SimpleNamespace as o
import random, math, sys, re

def coerce(z):
  try: return int(z)
  except:
    try: return float(z)
    except: 
      z = z.strip()
      return {'True':True, 'False':False}.get(z,z)

the= o(**{k:coerce(v) for k,v in re.findall(r"(\w+)=(\S+)", __doc__)})

#---------------------------------------------------------------------
BIG = 1E30
def Data()            : return o(rows=[], cols=[])
def Sym(at=0,txt="")  : return o(at=at,txt=txt,has={},w=1)
def Num(at=0,txt=" ") : 
 return o(at=at,txt=txt,lo=BIG,hi=-BIG,mu=0,n=0,w=1,
          goal= 0 if txt[0]=="-" else 1)

def isNum(col) : return "mu"   in col.__dict__
def isSym(col) : return "has"  in col.__dict__
def isData(col): return "rows" in col.__dict__

def add(it, v):
  if v=="?": return v
  if isSym(it): it.has[v] = 1 + it.has.get(v, 0)
  elif isData(it):
    if it.cols: it.rows.append([add(c,v[c.at]) for c in it.cols.all])
    else: it.cols = dataHeader(v)
  else:
    it.n  += 1
    delta   = v - it.mu
    it.mu += delta / it.n
    it.lo  = min(it.lo, v)
    it.hi  = max(it.hi, v)
  return v

def adds(src,it=None):
  it = it or Num()
  for x in src: add(it,x)
  return it 
  
def norm(col, v): 
  return v if v=="?" or type(col) is Sym else (
        (v-col.lo)/(col.hi-col.lo + 1/BIG))

#---------------------------------------------------------------------
def dataClone(data, rows=[]):
  return adds([[col.txt for col in data.cols.all]] + rows, Data())

def dataHeader(names):
  cols = o(all=[], x=[], y=[], klass=None)
  for c,s in enumerate(names):
    col = Num(c, s) if s[0].isupper() else Sym(c, s)
    cols.all += [col]
    if s[-1] == "X": continue
    if s[-1] == "!": cols.klass = col
    (cols.y if s[-1] in "!-+" else cols.x).append(col)
  return cols

def dataRead(file):
  data = Data()
  with open(file) as f:
    for line in f:
      line = line.strip()
      if line and not line.startswith("#"):
        add(data, [coerce(x) for x in line.split(",")])
  return data

#---------------------------------------------------------------------
def dist(src):
  d,n = 0,0
  for v in src: n,d = n+1, d + v**the.p
  return (d/n) ** (1/the.p)

def disty(data, row):
  return dist(abs(norm(c, row[c.at]) - c.goal) for c in data.cols.y)

def distx(data, row1, row2):
  return dist(distCol(c, row1[c.at], row2[c.at]) for c in data.cols.x)

def distCol(col, a,b):
  if a==b=="?": return 1
  if isSym(col) : return a != b
  a,b = norm(col,a), norm(col,b)
  a = a if a != "?" else (0 if b>0.5 else 1)
  b = b if b != "?" else (0 if a>0.5 else 1)
  return col.w*abs(a-b)

def distProject(data,row,east,west,c=None):
  D = lambda r1,r2 : distx(data,r1,r2)
  c = c or D(east,west)  
  a,b = D(row,east), D(row,west)
  return (a*a +c*c - b*b)/(2*c + 1e-32)

def distInterpolate(data,row,east,west,c=None):
  x = distProject(data,row,east,west,c) / (c + 1/BIG)
  y1,y2 = disty(data,east), disty(data,west)
  return y1 + x*(y2 - y1)

def distPoles(data):
  out = []
  for _ in range(the.Poles):
    east,west = random.choices(data.rows,k=2)
    c = distx(data,east,west)
    out += [(east,west,c)]
  return out

def distGuessY(data,row,poles):
  y = 0
  for pole in poles:
     y += distInterpolate(data,row,*pole)
  return y/len(poles)

def distWeights(data, poles, n=1000):
  Y     = lambda r: distGuessY(data, r,poles)
  tmp   = {col.at:1e-32 for col in data.cols.x}
  for _ in range(n):
    a,b = random.sample(data.rows,2)
    dY  = abs(Y(a) - Y(b))
    dX  = distx(data,a,b)
    for c in data.cols.x:
      tmp[c.at] += dY / (dX + 1e-32) 
  s = sum(tmp.values())
  for col in data.cols.x: col.w = tmp[col.at]/s

#---------------------------------------------------------------------
def eg_h(): print(__doc__)

def eg__data():
  for col in dataRead(the.file).cols.all: print(col)

def eg__int():
  data = dataRead(the.file)
  _eg__int(data)

def _eg__int(data):
  poles = distPoles(data)
  repeats=1000
  acc=0
  n=0
  Guess=lambda r: distGuessY(data,r,poles)
  Y=lambda r: disty(data,r)
  for _ in range(repeats):
     a=b=None
     while a==b:
       a,b=random.choices(data.rows,k=2)
     d=0.95
     if Y(a) >= d*Y(b):  n+=1; acc += Guess(a)>=d*Guess(b)
     if Y(a) < Y(b)/d:  n+=1; acc += Guess(a)<Guess(b)/d
  print(f"{acc/n:.2f}")

def eg__weights(): 
  print(" ")
  data = dataRead(the.file)
  _eg__int(data)
  distWeights(data,distPoles(data))
  print([col.w for col in data.cols.x])
  _eg__int(data)

if __name__ == "__main__": 
  for n, arg in enumerate(sys.argv):
    for k in the.__dict__:
      if arg == "-" + k[0]: 
        the.__dict__[k] = coerce(sys.argv[n+1])
    if (fn := globals().get(f"eg{arg.replace('-', '_')}")):
      random.seed(the.seed)
      fn() 
