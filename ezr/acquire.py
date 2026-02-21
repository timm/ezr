#!/usr/bin/env python3 -B
import sys, random
from ez2 import Data, add, sub, adds, clone, csv, says
from ez2 import disty, distx, likes, mids, shuffle, the
choice=random.choice

def nearer(xy, best, rest, r):
  return distx(xy, mids(best), r) - distx(xy, mids(rest), r)

def likelier(xy, best, rest, r):
  return likes(rest, r, xy.n, 2) - likes(best, r, xy.n, 2)

def acquire(xy, best, rest, x, scorer=nearer, eager=True):
  if eager: 
    return min(x.rows[:the.Few], key=lambda r: scorer(xy,best,rest,r))
  for m in range(the.Few):
    r = choice(x.rows)
    if scorer(xy, best, rest, r) < 0: break
  return r

def guess(d, Any=4, Budget=50, label=lambda r:r, **kwargs):
  rows = shuffle(d.rows[:])
  x    = clone(d, rows[Any:])
  xy   = clone(d, rows[:Any])
  xy.rows.sort(key= (Y := lambda r: disty(xy, r)))
  n    = round(Any**0.5)
  best = adds(xy.rows[:n], clone(d))
  rest = adds(xy.rows[n:], clone(d))
  while x.n > 2 and xy.n < Budget:
    add(xy, add(best, sub(x, label(acquire(xy,best,rest,x, **kwargs)))))
    if best.n > xy.n**.5:
      best.rows.sort(key = Y)
      while best.n > xy.n**.5:
        add(rest, sub(best, best.rows[-1]))
  return clone(d, sorted(xy.rows, key = Y))

def win(d):
  b4 = sorted(disty(d, r) for r in d.rows)
  lo, med = b4[0], b4[len(b4)//2]
  return lambda r: int(100*(1-(disty(d,r)-lo)/(med-lo+1E-6)))

if __name__ == "__main__":
  random.seed(float(sys.argv[1]))
  d = Data(csv(sys.argv[2]))
  score = win(d)
  for eager in [False, True]:
    for scorer in [nearer, likelier]:
      tmp = sorted(score(guess(d, scorer=scorer, eager=eager).rows[0])
                   for _ in range(20))
      says(tmp + [eager, scorer.__name__], w=3)
