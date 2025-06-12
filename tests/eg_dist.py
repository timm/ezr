
import sys; sys.path.insert(0, "../src")
from about import o,the
from data import Data,Num
from aux import go,csv,doc,cat
from dist import xdist,ydist,kpp,ydists

def eg__dist(_):
  data = Data(csv(doc(the.file)))
  row1 = data._rows[0]
  assert all(0 <= xdist(data,row1,row2) <= 1 for row2 in data._rows)
  assert all(0 <= ydist(data,row2) <= 1      for row2 in data._rows)
  lst = ydists(data)
  [print(round(ydist(data,row),2), row) for row in lst[:3] + lst[-3:]]

def eg__div(_):
  data = Data(csv(doc(the.file)))
  b4   = Num(ydist(data,row) for row in data._rows)
  one = lambda: ydist(data, ydists(data,kpp(data))[0])
  print("div ",o(mu=b4.mu, lo=b4.lo,
                 vals= cat(sorted(one() for _ in range(20)))))

go(globals())

