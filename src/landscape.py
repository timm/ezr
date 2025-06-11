from about import the
from aux import big,shuffle
from dist import ydist,xdist,xdists,ydists 

def project(data, row, a, b, C=None):
  C =  C or xdist(data,a,b)
  A,B = xdist(data,row,a), xdist(data,row,b)
  return (A*A + C*C - B*B) / (C+C + 1/big)

def fastmap(data, rows):
  one,*tmp = shuffle(rows)[:the.Few]
  far = int(0.9 *len(tmp))
  a   = xdists(data, one, tmp)[far]; 
  b   = xdists(data, a,   tmp)[far]
  C   = xdist(data,a,b)
  return sorted(rows, key = lambda r: project(data,r,a,b,C))

def fastmaps(data):
  done, todo = [], data._rows[:]
  while len(todo) > 2 and len(done) <= the.Build-2:
    a, *todo, b = fastmap(data, todo)
    mid = len(todo)//2
    todo= todo[mid:] if ydist(data,a) > ydist(data,b) else todo[:mid]
    done += [a,b]
  return ydists(data, done), todo
