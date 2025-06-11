import random
from about import the
from lib import big,shuffle
from dist import ydist,xdist,xdists

def project(data, row, a, b, C=None):
  C = C or xdist(data,a,b)
  A,B = xdist(data,row,a), xdist(data,row,b)
  return (A*A + C*C - B*B) / (C + 1/big)

def fastmap(data, rows):
  one, *some = shuffle(rows)
  some = some[:the.Few]
  far  = int(0.9 *len(some))
  a    = xdists(data, one, some)[far]
  b    = xdists(data, a, some)[far]
  C    = xdist(data, a,b)
  return sorted(rows, reverse = ydist(data,a) > ydist(data,b),
                      key = lambda r: abs(project(data,r,a,b,C)))

def fastmaps(data, stop=None):
  rows = shuffle(data._rows)
  while len(rows)>2 and n < (stop or the.Stop):
    n=n+2
    a,b,*todo = fastmap(data,done,todo)
    done += [a,b]
    todo = todo[:int(len(todo)*.66)]
  return done
