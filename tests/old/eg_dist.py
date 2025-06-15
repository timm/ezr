
import sys; sys.path.insert(0, "../src")
from about import o,the
from data import Data,Num
from lib import go,csv,doc,cat
from dist import xdist,ydist,kpp,ydists

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

go(globals())

