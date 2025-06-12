from about import o,the
from lib import big,shuffle
from dist import ydist,xdist,xdists,ydists 
from data import clone

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
  todo,done = [],[]
  while len(done) <= the.Build - 2:
    todo = todo if len(todo) > 2 else shuffle(data._rows[:])
    a, *todo, b = fastmap(data, todo)
    done += [a,b]
    mid   = len(todo)//2
    todo  = todo[:mid] if ydist(data,a) < ydist(data,b) else todo[mid:]
  return o(best=clone(data, done), test=todo)



