import sys; sys.path.insert(0, "../src")

from about import o,the
from aux import go,csv,doc,cat
from dist import ydist
from landscape import fastmaps
from data import Data,Num

def eg__fastmap():
  data = Data(csv(doc(the.file)))
  b4   = Num(ydist(data,row) for row in data._rows)
  one  = lambda : ydist(data, fastmaps(data).best._rows[0])
  print(o(mu=b4.mu,
          lo=b4.lo,
          vals= cat(sorted(one() for _ in range(20)))))

go(fmap=eg__fastmap)

