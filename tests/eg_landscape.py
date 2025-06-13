import sys; sys.path.insert(0, "../src")

from about import o,the
from dist import ydist,ydists
from data import Data,Num
from landscape import fastmaps
from lib import go,csv,doc,cat

def eg__fastmap(_):
  data = Data(csv(doc(the.file)))
  Y    = lambda r: ydist(data,r)
  b4   = Num(Y(r) for r in data._rows)
  one  = lambda : Y(min(fastmaps(data).best._rows, key=Y))
  print("fmap",o(mu=b4.mu, lo=b4.lo,
                 vals= sorted(one() for _ in range(20))))

go(globals())

