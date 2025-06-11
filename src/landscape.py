from about import the
from lib import big,shuffle
from dist import ydist,xdist,xdists,ydists 

def project(data, row, a, b, C=None):
  C = C or xdist(data,a,b)
  A,B = xdist(data,row,a), xdist(data,row,b)
  return (A*A + C*C - B*B) / (C+C + 1/big)

def fastmap(data, rows):
  one,*tmp = shuffle(rows[:the.Few])
  far = int(0.9 *len(tmp))
  a   = xdists(data, one, tmp)[far]; 
  b   = xdists(data, a,   tmp)[far]
  C   = xdist(data, a,b)
  rows.remove(a)
  rows.remove(b)
  return a,b,sorted(rows, reverse = ydist(data,a) > ydist(data,b),
                          key = lambda r: project(data,r,a,b,C))

def fastmaps(data, build=None):
  todo = shuffle(data._rows[:])
  stop = build or the.Build
  done = []
  while len(todo)>2 and len(done) < stop-2:
    a,b,todo = fastmap(data,todo)
    done += [a,b]
    todo  = todo[:len(todo)//2]
  return done, todo
