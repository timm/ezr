# How probable is it that  `v` belongs to a column?
from data import Sym,clone,add
from aux import big
from about import o,the
import random,math

def pdf(col,v, prior=0):
  "Return probability that `v` belongs to `col`."
  if col.it is Sym:
    return (col.has.get(v,0) + the.m*prior) / (col.n + the.m + 1/big)
  sd = col.sd or 1 / big
  var = 2 * sd * sd
  z = (v - col.mu) ** 2 / var
  return min(1, max(0, math.exp(-z) / (2 * math.pi * var) ** 0.5))

def like(data, row, nall=2, nh=100):
  "Report how much `data` like `row`."
  prior = (data.n + the.k) / (nall + the.k*nh)
  tmp = [pdf(c,row[c.at],prior) 
         for c in data.cols.x if row[c.at] != "?"]
  return sum(math.log(n) for n in tmp + [prior] if n>0)    

def likes(datas, row):
  "Return the `data` in `datas` that likes `row` the most."
  n = sum(data.n for data in datas)
  return max(datas, key=lambda data: like(data, row, n, len(datas)))

def acquires(data, start=None, stop=None, guess=None, few=None):
  "Split rows to best,rest. Label row that's e.g. max best/rest. Repeat."
  def _acquire(b, r, acq="xploit", p=1):
    b,r = math.e**b, math.e**r
    q   = 0 if acq=="xploit" else (1 if acq=="xplor" else 1-p)
    return (b + r*q) / abs(b*q - r + 1/big)
  def _guess(row):
    return _acquire(like(best,row,n,2), like(rest,row,n,2), the.Acq, n/the.Stop)

  start = the.Assume if start is None else start
  stop = the.Build if stop is None else stop
  guess = the.guess if guess is None else guess
  few = the.Few if few is None else few
  random.shuffle(data._rows)
  n         = start
  todo      = data._rows[n:]
  bestrest  = clone(data, data._rows[:n])
  done      = ydists(bestrest)
  cut       = round(n**guess)
  best      = clone(data, done[:cut])
  rest      = clone(data, done[cut:])
  while len(todo) > 2 and n < stop:
    n      += 1
    hi, *lo = sorted(todo[:few*2], # just sort a few? then 100 times faster
                    key=_guess, reverse=True)
    todo    = lo[:few] + todo[few*2:] + lo[few:]
    add(bestrest, add(best, hi))
    best._rows = ysort(bestrest)
    if len(best._rows) >= round(n**guess):
      add(rest, # if incremental update, then runs 100 times faster
        sub(best,  
            best._rows.pop(-1))) 
  return o(best=best, rest=rest, test=todo)

def acquired(data):
  a = acquires(data,stop = the.Stop - the.Test)
  t = tree(clone(data, a.best._rows + a.rest._rows))
  return sorted(a.test, key=lambda z:leaf(t,z).ys.mu)[:the.Test]


