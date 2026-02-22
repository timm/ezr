#!/usr/bin/env python3 -B
import sys, random
from math import sqrt
from ez2 import Data, add, sub, adds, clone, csv, says, Row
from ez2 import disty, distx, likes, main, mids, shuffle, the
from ez2 import eg__the, eg_s
choice = random.choice

def nearer(seen:Data, best:Data, rest:Data, r:Row) -> bool:
  return distx(seen, mids(best), r) - distx(seen, mids(rest), r)

def likelier(seen:Data, best:Data, rest:Data, r:Row) -> bool:
  return likes(rest, r, seen.n, 2) - likes(best, r, seen.n, 2)

def acquire(seen:Data, best:Data, rest:Data, 
            unseen:Data, scorer=nearer, eager=True) -> Row:
  if eager: 
    return min(unseen.rows, key=lambda r: scorer(seen,best,rest,r))
  for m in range(unseen.n):
    r = choice(unseen.rows)
    if scorer(seen, best, rest, r) < 0: break
  return r

def guess(d:Data, Any=4, Budget=50, label=lambda r:r, **kwargs) -> Data:
  rows   = shuffle(d.rows[:])
  unseen = clone(d, rows[Any:][:the.Few])
  seen   = clone(d, rows[:Any])
  seen.rows.sort(key= (Y := lambda r: disty(seen, r)))
  n      = round(sqrt(Any))
  best   = adds(seen.rows[:n], clone(d))
  rest   = adds(seen.rows[n:], clone(d))
  while unseen.n > 2 and seen.n < Budget:
    add(seen,
      add(best,
        label(
          sub(unseen, 
            acquire(seen, best, rest, unseen, **kwargs)))))
    if best.n > sqrt(seen.n):
      best.rows.sort(key = Y)
      while best.n > sqrt(seen.n):
        add(rest, 
          sub(best, best.rows[-1]))
  return clone(d, sorted(seen.rows, key = Y))

def win(d:Data) -> callable:
  b4 = sorted(disty(d, r) for r in d.rows)
  lo, med = b4[0], b4[len(b4)//2]
  return lambda r: int(100*(1 - (disty(d,r) - lo)/(med - lo + 1E-6)))

def eg__four(file:str):
  d = Data(csv(file))
  score = win(d)
  for eager in [False, True]:
    for fn in [nearer, likelier]:
      tmp= [score(guess(d,scorer=fn,eager=eager).rows[0]) for _ in range(20)]
      says(sorted(tmp) + [eager, fn.__name__], w=3)

if __name__ == "__main__": main(globals())
