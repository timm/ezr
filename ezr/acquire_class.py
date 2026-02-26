#!/usr/bin/env python3 -B
"""acquire.py: active learning via sequential model-based acquisition
(c) 2026 Tim Menzies timm@ieee.org, MIT license"""
import random
from math import sqrt
from ez_class import Data, adds, csv, says, Row, shuffle, the, main, filename

choice = random.choice

def clone(d:Data, rows:list=[]) -> Data:
  return Data([d.cols.names] + rows)

def nearer(seen:Data, best:Data, rest:Data, r:Row) -> float:
  return seen.distx(best.mid(), r) - seen.distx(rest.mid(), r)

def likelier(seen:Data, best:Data, rest:Data, r:Row) -> float:
  return rest.like(r, len(seen.rows), 2) - best.like(r, len(seen.rows), 2)

def acquire(seen:Data, best:Data, rest:Data,
            unseen:Data, scorer=nearer, eager=True) -> Row:
  if eager:
    return min(unseen.rows, key=lambda r: scorer(seen, best, rest, r))
  for _ in range(len(unseen.rows)):
    r = choice(unseen.rows)
    if scorer(seen, best, rest, r) < 0: break
  return r

def guess(d:Data, Any=4, Budget=50, label=lambda r:r, **kwargs) -> Data:
  rows   = shuffle(d.rows[:])
  unseen = clone(d, rows[Any:][:the.Few])
  seen   = clone(d, rows[:Any])
  seen.rows.sort(key=(Y := lambda r: seen.disty(r)))
  n      = round(sqrt(Any))
  best   = clone(d, seen.rows[:n])
  rest   = clone(d, seen.rows[n:])
  while len(unseen.rows) > 2 and len(seen.rows) < Budget:
    seen.add(
      best.add(
        label(
          unseen.sub(
            acquire(seen, best, rest, unseen, **kwargs)))))
    if len(best.rows) > sqrt(len(seen.rows)):
      best.rows.sort(key=Y)
      while len(best.rows) > sqrt(len(seen.rows)):
        rest.add(best.sub(best.rows[-1]))
  return clone(d, sorted(seen.rows, key=Y))

def win(d:Data) -> callable:
  b4    = sorted(d.disty(r) for r in d.rows)
  lo,med = b4[0], b4[len(b4)//2]
  return lambda r: int(100*(1 - (d.disty(r) - lo)/(med - lo + 1E-6)))

def eg__data(f:filename):
  "compare acquisition strategies across 20 runs"
  d     = Data(csv(f))
  score = win(d)
  for eager in [False, True]:
    for fn in [nearer, likelier]:
      tmp = [score(guess(d, scorer=fn, eager=eager).rows[0]) for _ in range(20)]
      says(sorted(tmp) + [eager, fn.__name__], w=3)

if __name__ == "__main__": main(globals())
