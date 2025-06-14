# How probable is it that  `v` belongs to a column?
from about import o,the
from data  import Sym,clone
from adds  import add,sub
from lib   import big
from dist  import ydists
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
  def _guess(row):
    "Using a two class classifier to guess how good is `row`."
    p   =n/the.Build
    b,r = like(best,row,n,2), like(rest,row,n,2)
    b,r = math.e**b, math.e**r
    q   = 0 if the.acq=="xploit" else (1 if the.acq=="xplor" else 1-p)
    return (b + r*q) / abs(b*q - r + 1/big)

  # initlaizations
  start = the.Assume if start is None else start
  stop = the.Build if stop is None else stop
  guess = the.guess if guess is None else guess
  few = the.Few if few is None else few
  
  # set up
  random.shuffle(data._rows)
  n         = start
  todo      = data._rows[n:]
  bestrest  = clone(data, data._rows[:n])
  done      = ydists(bestrest)
  cut       = round(n**guess)
  best      = clone(data, done[:cut])
  rest      = clone(data, done[cut:])

  # incremental model update
  while len(todo) > 2 and n < stop:
    n     += 1
    hi,*lo= sorted(todo[:few*2],# 100 times faster if only sort few 
                   key=_guess, reverse=True)
    todo = lo[:few]+todo[few*2:]+lo[few:] #give other rows a chance
    add(bestrest, add(best, hi))
    best._rows = ydists(bestrest)
    if len(best._rows) >= round(n**guess):
      add(rest, # 100 times faster if incremental update
        sub(best,  
            best._rows.pop(-1))) 
  return o(best=best, rest=rest, test=todo)
