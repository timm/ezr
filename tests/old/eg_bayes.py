import sys; sys.path.insert(0, "../src")

from data import Data
from dist import ydist
from lib import lines,doc,csv,cat,go,o
from bayes import like,acquires
from example import EXAMPLE

def eg__bayes(file):
  data = Data(csv(doc(file) if file else lines(EXAMPLE)))
  print(cat(sorted([like(data,row,2,1000) for row in data._rows[::5]])))

def eg__lite(file):
  data = Data(csv(doc(file) if file else lines(EXAMPLE)))
  b4   = [ydist(data, row) for row in data._rows][::8]
  now  = [ydist(data, acquires(data).best._rows[0]) for _ in range(12)]
  print(o(b4=sorted(b4)))
  print(o(now=sorted(now)))


go(globals())
