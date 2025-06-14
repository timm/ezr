
import sys; sys.path.insert(0, "../src")

from about import the
from data import Data,Num,clone
from tree import tree,leaf,show
from dist import ydist
from lib import doc,csv,go,o
from bayes import acquires

def eg__tree(_):
  data = Data(csv(doc(the.file)))
  Y = lambda row: round(ydist(data,row),2)
  ys=Num(Y(row) for row in data._rows)
  print(the.file)
  a = acquires(data)
  print(Y(a.best._rows[0]))
  print(o(mu=ys.mu, lo=ys.lo))
  t = tree(clone(data, a.best._rows + a.rest._rows))
  show(t)
  guesses = sorted(a.test, key=lambda z:leaf(t,z).ys.mu)[:the.Check]
  guess = min(guesses, key=Y)
  print(Y(guess), guess)

go(globals())
