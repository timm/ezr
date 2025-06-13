from about import o,the
from data  import Sym,clone
from adds  import add,sub
from lib   import big
from dist  import ydists



def acquired(data):
  a = acquires(data,stop = the.Stop - the.Test)
  t = tree(clone(data, a.best._rows + a.rest._rows))
  return sorted(a.test, key=lambda z:leaf(t,z).ys.mu)[:the.Test]


