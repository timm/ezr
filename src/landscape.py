from about import the
from lib import big,shuffle
from dist import ydist,xdist,xdists,ydists 

def project(data, row, a, b, C=None):
  C = C or xdist(data,a,b)
  A,B = xdist(data,row,a), xdist(data,row,b)
  return (A*A + C*C - B*B) / (C + 1/big)

def fastmap(data, rows, b4=None):
  one,*tmp = rows[:the.Few]
  one = b4 if b4 else one
  far = int(0.9 *len(tmp))
  a   = xdists(data, one, tmp)[far]
  b   = xdists(data, a,   tmp)[far]
  C   = xdist(data, a,b)
  return sorted(rows, reverse = ydist(data,a) > ydist(data,b),
                      key = lambda r: abs(project(data,r,a,b,C)))

def fastmaps(data, build=None):
  todo = shuffle(data._rows)
  stop = build or the.Build
  done = []
  while len(todo)>2 and n < stop-2:
    n = n+2
    a,b,*todo = fastmap(data,shuffle(todo))[len(todo)//2]
    done += [a,b]
  return ydists(data,done), todo
