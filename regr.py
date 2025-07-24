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
 return o(at=at,txt=txt,lo=BIG,hi=-BIG,mu=0,n=0,
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
def distPoles(data):
  out, east = [], random.choice(data.rows)
  for _ in range(the.Poles):
    west = random.choice(data.rows)
    out += [(east, west, distx(data,east,west))]
    east = west
  return out

def disty(data,row):
  d = sum(abs(norm(c,row[c.at]) - c.goal)**the.p for c in data.cols.y)
  return (d / len(data.cols.y))**(1/the.p)

def distx(data,r1,r2):
  def _dist(col):
    a = r1[col.at]
    b = r2[col.at]
    if a==b=="?": return 1
    if isSym(col): return a != b
    a,b = norm(col,a), norm(col,b)
    a = a if a != "?" else (0 if b > .5 else 1)
    b = b if b != "?" else (0 if a > .5 else 1)
    return abs(a - b)

  d = sum(_dist(col)**the.p for col in data.cols.x)
  return (d / len(data.cols.x))**(1/the.p)

def distInterpolate(data,row,east,west,c):
  a = distx(data,row,east)
  b = distx(data,row,west)
  x = (a*a + c*c - b*b) / (2*c + 1/BIG) / (c + 1/BIG)
  y1,y2 = disty(data,east), disty(data,west)
  return y1 + x*(y2 - y1)

def distGuessY(data,row,poles): 
  return sum(distInterpolate(data,row,*p) for p in poles)/len(poles)

#---------------------------------------------------------------------
def eg_h(): print(__doc__)

def eg__data():
  for col in dataRead(the.file).cols.all: print(col)

def eg__int():
  data = dataRead(the.file)
  _eg__int(data)

def _eg__int(data):
  poles = distPoles(data)
  repeats=32
  acc=0
  n=0
  Guess=lambda r: distGuessY(data,r,poles)
  Y=lambda r: disty(data,r)
  for __ in range(32):
    random.shuffle(data.rows)
    for _ in range(repeats):
       a=b=None
       while a==b:
         a,b=random.choices(data.rows,k=2)
       d=1
       if Y(a) >= d*Y(b):  n+=1; acc += Guess(a)>=d*Guess(b)
       if Y(a) <  Y(b)/d:  n+=1; acc += Guess(a)<Guess(b)/d
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
