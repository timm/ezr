#!/usr/bin/env python3 -B 
from data import *

#--------------------------------------------------------------------
def dist(src) -> float:
  "general distance function"
  d,n = 0,0
  for v in src: n,d = n+1, d + v**the.p;
  return (d/n) ** (1/the.p)

def disty(data:Data, row:Row) -> float:
  "distance of row to best goal values"
  return dist(abs(norm(c, row[c.at]) - c.more) for c in data.cols.y)

def distysort(data:Data,rows=None) -> List[Row]:
  "sort rows by distance to best goal values"
  return sorted(rows or data.rows, key=lambda r: disty(data,r))

def distx(data, row1, row2):
  "Distance between independent values of two rows."
  def _aha(col, a,b):
    if a==b=="?": return 1
    if col.it is Sym: return a != b
    a,b = norm(col,a), norm(col,b)
    a = a if a != "?" else (0 if b>0.5 else 1)
    b = b if b != "?" else (0 if a>0.5 else 1)
    return abs(a-b)
  return dist(_aha(col, row1[col.at], row2[col.at])  
              for col in data.cols.x)

def daBest(data,rows=None):
  "find the best from rows, report its disty"
  rows = rows or data.rows
  Y=lambda r: disty(data,r)
  return Y(sorted(rows, key=Y)[0])

#--------------------------------------------------------------------
def distKpp(data, rows=None, k=20, few=None):
  "Return key centroids usually separated by distance D^2."
  few = few or the.Few
  rows = rows or data.rows[:]
  random.shuffle(rows)
  out = [rows[0]]
  while len(out) < k:
    tmp = random.sample(rows, few)
    ws  = [min(distx(data, r, c)**2 for c in out) for r in tmp]
    p   = sum(ws) * random.random()
    for j, w in enumerate(ws):
      if (p := p - w) <= 0: 
          out += [tmp[j]]; break
  return out

def distKmeans(data, rows=None, n=10, out=None, err=1, **key):
  "Return key centroids within data."
  rows = rows or data.rows
  centroids = [mids(d) for d in out] if out else distKpp(data,rows,**key)
  d,err1 = {},0
  for row in rows:
    col = min(centroids, key=lambda crow: distx(data,crow,row))
    err1 += distx(data,col,row) / len(rows)
    d[id(col)] = d.get(id(col)) or clone(data)
    add(d[id(col)],row)
  print(f'err={err1:.3f}')
  return (out if (n==1 or abs(err - err1) <= 0.01) else
          distKmeans(data, rows, n-1, d.values(), err=err1,**key))

def distProject(data,row,east,west,c=None):
  "Map row along a line east -> west."
  D = lambda r1,r2 : distx(data,r1,r2)
  c = c or D(east,west)  
  a,b = D(row,east), D(row,west)
  return (a*a +c*c - b*b)/(2*c + 1e-32)

def distFastmap(data,rows=None):
  "Sort rows along a line between 2 distant points."
  rows = rows or data.rows
  X = lambda r1,r2:distx(data,r1,r2)
  anywhere, *few = random.choices(rows, k=the.Few)
  here  = max(few, key= lambda r: X(anywhere,r))
  there = max(few, key= lambda r: X(here,r))
  c     = X(here,there)
  return sorted(rows, key=lambda r: distProject(data,r,here,there,c))

def distFastermap(data,rows, sway1=False):
  "Prune half the rows furthest from best distant pair."
  random.shuffle(rows)
  nolabel = rows[the.Any:]
  labels = clone(data, rows[:the.Any])
  Y  = lambda r: disty(labels,r)
  while len(labels.rows) < the.Build and len(nolabel) >= 2: 
    east, *rest, west = distFastmap(data,nolabel)
    add(labels, east)
    add(labels, west)
    n = len(rest)//2
    nolabel = nolabel[:n] if Y(east) < Y(west) else nolabel[n:]
    if not sway1 and len(nolabel) < 2:
      nolabel= [r for r in rows if r not in labels.rows]
      random.shuffle(nolabel)
  labels.rows.sort(key=Y)
  return o(labels= labels,
           nolabels= [r for r in rows if r not in labels.rows])

#-------------------------------------------------------------------
def eg__distx():
  "Dist: check x distance calcs."
  data = Data(csv(the.file))
  r1= data.rows[0]
  ds= sorted([distx(data,r1,r2) for r2 in data.rows])
  print(', '.join(f"{x:.2f}" for x in ds[::20]))
  assert all(0 <= x <= 1 for x in ds)

def eg__disty():
  "Dist: check y distance calcs."
  data = Data(csv(the.file))
  data.rows.sort(key=lambda row: disty(data,row))
  assert all(0 <= disty(data,r) <= 1 for r in data.rows)
  print(', '.join(data.cols.names))
  print("top4:");   [print("\t",row) for row in data.rows[:4]]
  print("worst4:"); [print("\t",row) for row in data.rows[-4:]]

def eg__irisKpp(): 
  "Dist: check Kmeans++ centroids on iris."
  src = csv("../../moot/classify/iris.csv")
  [print(r) for r in distKpp(Data(src),k=10)]

def eg__irisK(): 
  "Dist: check Kmeans on iris."
  src = csv("../../moot/classify/iris.csv")
  for data in distKmeans(Data(src),k=10):
    print(', '.join([out(x) for x in mids(data)])) 

def eg__fmap():
  "Dist:  diversity-based optimziation with fast map."
  data = Data(csv(the.file))
  for few in [32,64,128,256,512]:
    the.Few = few
    print(few)
    n=adds(daBest(data, 
             distFastermap(data,data.rows).labels.rows) 
                for _ in range(20))
    print("\t",n.mu,n.sd)

#--------------------------------------------------------------------
def eg__all()             : mainAll(globals())
def eg__list()            : mainList(globals())
def eg_h()                : print(helpstring)
if __name__ == "__main__" : main(globals())
