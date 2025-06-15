# How probable is it that  `v` belongs to a column?
import math
from data import o,the,clone,Sym,add,sub,BIG,shuffle

def pdf(col,v, prior=0):
  "Return probability that `v` belongs to `col`."
  if col.it is Sym:
    return (col.has.get(v,0) + the.m*prior) / (col.n + the.m + 1/BIG)
  sd = col.sd or 1 / BIG
  var = 2 * sd * sd
  z = (v - col.mu) ** 2 / var
  return min(1, max(0, math.exp(-z) / (2 * math.pi * var) ** 0.5))

def like(data, row, nall=2, nh=100):
  "Report how much `data` like `row`."
  prior = (data.n + the.k) / (nall + the.k*nh)
  t = [pdf(c,v,prior) for c in data.cols.x if (v:=row[c.at]) != "?"]
  return sum(math.log(n) for n in t + [prior] if n>0)    

def acquires(data, stop=None):
  "Split rows to best,rest. Label row that's e.g. max best/rest. Repeat."
  def _acquire(row):
    "Using a two class classifier to guess how good is `row`."
    p   = n/the.Build
    e   = math.e
    b,r = e**like(best,row,n,2), e**like(rest,row,n,2)
    q   = 0 if the.acq=="xploit" else (1 if the.acq=="xplor" else 1-p)
    return (b + r*q) / abs(b*q - r + 1/BIG)

  # set up
  Y         = lambda row: ydist(data,row)
  rows      = shuffle(data._rows)
  stop      = the.Build if stop is None else stop
  n         = the.Assume
  todo      = rows[n:]
  bestrest  = clone(data, rows[:n])
  done      = sorted(ydists(bestrest)
  cut       = round(n**the.guess)
  best,rest = clone(data, done[:cut]), clone(data, done[cut:])

  # incremental model update
  while len(todo) > 2 and n < stop:
    n    += 1
    hi,*lo= sorted(todo[:the.Few*2], key=_acquire, reverse=True)
    todo = lo[:the.Few] + todo[the.Few*2:] + lo[the.Few:] 
    add(bestrest, add(best, hi))
    best._rows.sort(key=Y)
    if len(best._rows) >= round(n**the.guess):
      add(rest, sub(best, best._rows.pop(-1))) 
  return o(best=best, rest=rest, test=todo)
