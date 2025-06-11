
import sys; sys.path.insert(0, "../src")

import random
from about import the
from adds import add,sub
from lib import go,csv,doc,cat
from dist import ydist,ydists
from landscape import fastmaps
from data import Data

def eg__fastmap():
  data = Data(csv(doc(the.file)))
  one = lambda: ydist(data, ydists(data,fastmaps(data))[0])
  print(cat(sorted(one() for _ in range(20))))

go(num=eg__fastmap))

