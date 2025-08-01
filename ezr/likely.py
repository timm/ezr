#!/usr/bin/env python3 -B
from like import *
from dist import *

#--------------------------------------------------------------------
def likely(data:Data, rows=None) -> List[Row]:
  """x,xy = rows with 'x' and 'xy' knowledge.
  Find the thing in x most likely to be best. Add to xy. Repeat."""
  rows = rows or data.rows
  x   = clone(data, shuffle(rows[:]))
  xy, best, rest = clone(data), clone(data), clone(data)
  # label anything
  for _ in range(the.Any):
    add(xy, sub(x, x.rows.pop()))
  # divide lablled items into best and rest
  xy.rows = distysort(xy)
  n = round(the.Any**.5)
  adds(xy.rows[:n], best)
  adds(xy.rows[n:], rest)
  # loop
  fn = likely1 if the.acq=="klass" else likelier
  while x.n > 2 and xy.n < the.Build:
    add(xy, add(best, sub(x, fn(best, rest, x))))
    if best.n > (xy.n**.5):
      best.rows = distysort(xy,best.rows)
      while best.n > (xy.n**.5):
        add(rest, sub(best, best.rows.pop(-1)))
  return distysort(xy)

def likely1(best:Data, rest:Data, x:Data) -> Row:
  "Remove from `x' any 1 thing more best-ish than rest-ish."
  shuffle(x.rows)
  j, nall = 0, best.n + rest.n
  for i,row in enumerate(x.rows[:the.Few*2]):
    if likes(best,row,nall,2) > likes(rest,row,nall,2):
      j = i; break
  return x.rows.pop(j)

def likelier(best:Data, rest:Data, x:Data) -> Row:
  "Sort 'x by the.acq, remove first from 'x'. Return first."
  e, nall = math.e, best.n + rest.n
  p = nall/the.Build
  q = {'xploit':0, 'xplor':1}.get(the.acq, 1-p)
  def _fn(row):
    b,r = e**likes(best,row,nall,2), e**likes(rest,row,nall,2)
    if the.acq=="bore": return b*b/(r+1e-32)
    return (b + r*q) / abs(b*q - r + 1e-32)

  first, *lst = sorted(x.rows[:the.Few*2], key=_fn, reverse=True)
  x.rows = lst[:the.Few] + x.rows[the.Few*2:] + lst[the.Few:] 
  return first

#--------------------------------------------------------------------
def eg__bayes():
  "like: check we can find row likelihoods"
  data = Data(csv(the.file))
  assert all(-30 <= likes(data,t) <= 0 for t in data.rows)
  print(sorted([round(likes(data,t),2) for t in data.rows])[::20])

def eg__inc():
  "like: check we can incremental add and remove data"
  d1 = Data(csv(the.file))
  d2 = clone(d1)
  x  = d2.cols.x[1]
  for row in d1.rows:
    add(d2,row)
    if d2.n==100:  
      mu1,sd1 = x.mu,x.sd ; print("asIs",mu1,sd1)
  for row in d1.rows[::-1]:
    if d2.n==100: 
      mu2,sd2 = x.mu,x.sd ; print("toBe",mu2,sd2)
      assert abs(mu2 - mu1) < 1.01 and abs(sd2 - sd1) < 1.01
    sub(d2,row,zap=True)

def eg__likely():
  "like: try different acqusition functions"
  data = Data(csv(the.file))
  b4   = adds(disty(data,r) for r in data.rows)
  R    = lambda n: int(100*n)
  win  = lambda n: R((1 - (n - b4.lo) / (b4.mu - b4.lo)))
  rxs  = dict(klass=Num(),xploit=Num(),xplor=Num(),adapt=Num())
  for acq,log in rxs.items():
    the.acq = acq
    adds((disty(data, likely(data)[0]) for _ in range(20)), log)
  zero=rxs["klass"]
  print(*map(win,[zero.mu] + [log.mu for s,log in rxs.items() if s != "klass"]),
        the.file)

#--------------------------------------------------------------------
def eg__all()             : mainAll(globals())
def eg__list()            : mainList(globals())
def eg_h()                : print(helpstring)
if __name__ == "__main__" : main(globals())
