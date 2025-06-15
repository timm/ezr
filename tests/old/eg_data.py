import sys; sys.path.insert(0, "../src")

import random,math
from data import o,go,cat,csv,doc,the,atom,Cols,Num,Sym
from aux import go

# need an eg to reports stats... show you can walk around the data model
def eg__o(_):
  print(o(name="alan", age=41, p=math.pi))

def eg__the(_):
  print(the)

def eg__csv(_):
  s,n = 0,0
  for i,row in enumerate(csv(doc(the.file))): 
    if not i % 20: print(row)
    assert len(row)==6
    if type(row[0]) is str: s += 1
    if type(row[0]) in [int,float]: n += 1
  assert s==1 and n==100
def eg__cols(_):
  ":         : List[str] --> columns"
  cols = Cols(["name","Age","Salary+"])
  for what,lst in (("x", cols.x), ("y",cols.y)):
    print("\n"+what)
    [print("\t"+cat(one)) for one in lst]

def eg__num(_):
  num=Num([random.gauss(10,2) for _ in range(1000)])
  assert 10 < mid(num) < 10.2 and 2 < spread(num) < 2.1

def eg__sym(_):
  sym = Sym("aaaabbc")
  assert "a"==mid(sym) and 1.3 < spread(sym) < 1.4

def eg__data(_):
  data = Data(csv(doc(the.file)))
  print(data.n)
  print("X"); [print("  ",col) for col in data.cols.x]
  print("Y"); [print("  ",col) for col in data.cols.y]

def eg__addSub(_):
  data1 = Data(csv(doc(the.file)))
  data2 = clone(data1)
  for row in data1._rows:
    add(data2,row)
    if len(data2._rows)==100: 
      mids    = mid(data2)
      spreads = spread(data2)
  for row in data1._rows[::-1]:
    if len(data2._rows)==100: 
      assert sum((a-b) for a,b in zip(mids, mid(data2))) < 0.1
      assert sum((a-b) for a,b in zip(spreads, spread(data2))) < 0.1
      return
    sub(data2, row, purge=True)


def eg__dist(_):
  data = Data(csv(doc(the.file)))
  row1 = data._rows[0]
  Y    = lambda r     : round(ydist(data,r),2)
  X    = lambda r1,r2 : xdist(data,r1,r2)
  assert all(0 <= Y(row)       <= 1 for row  in data._rows)
  assert all(0 <= X(row1,row2) <= 1 for row2 in data._rows)
  tmp = sorted(data._rows,key=Y)
  [print(Y(r), r) for r in tmp[:3] + tmp[-3:]]

def eg__kpp(_):
  data = Data(csv(doc(the.file)))
  Y    = lambda r: ydist(data,r)
  one  = lambda  : Y(min(kpp(data), key=Y))
  b4   = Num(Y(r) for r in data._rows)
  print("kpp ",o(mu   = b4.mu, lo=b4.lo, 
                 vals = [sorted(one() for _ in range(20))]))

go(the, atom, globals())
