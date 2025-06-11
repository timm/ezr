import sys; sys.path.insert(0, "../src")

import random
from about import the
from adds import add,sub
from lib import cli,csv,doc
from query import spread,mid
from data import clone,Num,Sym,Data


def eg__num():
  num=Num([random.gauss(10,2) for _ in range(1000)])
  assert 10 < mid(num) < 10.2 and 2 < spread(num) < 2.1

def eg__sym():
  sym = Sym("aaaabbc")
  assert "a"==mid(sym) and 1.3 < spread(sym) < 1.4

def eg__data():
  data = Data(csv(doc(the.file)))
  print(data.n)
  print("X"); [print("  ",col) for col in data.cols.x]
  print("Y"); [print("  ",col) for col in data.cols.y]

def eg__addSub():
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

cli(dict(num=eg__num, sym=eg__sym, 
         data=eg__data, addsub=eg__addSub))

