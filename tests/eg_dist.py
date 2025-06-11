
import sys; sys.path.insert(0, "../src")
from about import the
from data import Data
from aux import go,csv,doc,cat
from dist import xdist,ydist,kpp,ydists

def eg__dist():
  data = Data(csv(doc(the.file)))
  row1 = data._rows[0]
  assert all(0 <= xdist(data,row1,row2) <= 1 for row2 in data._rows)
  assert all(0 <= ydist(data,row2) <= 1      for row2 in data._rows)
  lst = ydists(data)
  [print(round(ydist(data,row),2), row) for row in lst[:3] + lst[-3:]]

def eg__diversitySampling():
  data = Data(csv(doc(the.file)))
  one = lambda: ydist(data, ydists(data,kpp(data))[0])
  print(cat(sorted(one() for _ in range(20))))

go(dist=eg__dist, 
   div=eg__diversitySampling)

