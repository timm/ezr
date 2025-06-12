import sys; sys.path.insert(0, "../src")

from about import o,the
from dist import ydist
from data import Data,Num
from landscape import fastmaps
from aux import go,csv,doc,cat

def eg__fastmap(_):
  data = Data(csv(doc(the.file)))
  b4   = Num(ydist(data,row) for row in data._rows)
  one  = lambda : ydist(data, fastmaps(data).best._rows[0])
  print("fmap",o(mu=b4.mu, lo=b4.lo,
                 vals= cat(sorted(one() for _ in range(20)))))

go(globals())

