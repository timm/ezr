#!/usr/bin/env python3 -B
"""acquire.py: active learning via sequential model-based acquisition
(c) 2026 Tim Menzies timm@ieee.org, MIT license"""
import random
from math import sqrt
from ez_class import Data,csv,Row,shuffle,the,main,filename,eg_s
from tree_class import evaluate, random_trainer, clone

choice = random.choice

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

def guess(d:Data, rows:list, Any=4, Budget=None, 
          scorer=nearer, eager=True, label=lambda r:r) -> list[Row]:
  """Active learner that returns trained rows"""
  Budget = Budget or the.Budget
  rows   = shuffle(rows[:])
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
            acquire(seen, best, rest, unseen, scorer=scorer, eager=eager)))))
    if len(best.rows) > sqrt(len(seen.rows)):
      best.rows.sort(key=Y)
      while len(best.rows) > sqrt(len(seen.rows)):
        rest.add(best.sub(best.rows[-1]))
  return sorted(seen.rows, key=Y)

# Create trainer wrappers for evaluate()
def guess_lazy_nearer(d:Data, rows:list) -> list[Row]:
  return guess(d, rows, scorer=nearer, eager=False)
guess_lazy_nearer.__name__ = "guess_lazy_nearer"

def guess_lazy_likelier(d:Data, rows:list) -> list[Row]:
  return guess(d, rows, scorer=likelier, eager=False)
guess_lazy_likelier.__name__ = "guess_lazy_likelier"

def guess_eager_nearer(d:Data, rows:list) -> list[Row]:
  return guess(d, rows, scorer=nearer, eager=True)
guess_eager_nearer.__name__ = "guess_eager_nearer"

def guess_eager_likelier(d:Data, rows:list) -> list[Row]:
  return guess(d, rows, scorer=likelier, eager=True)
guess_eager_likelier.__name__ = "guess_eager_likelier"

#---- demos -----------------------------------------------------------
def eg__compare(f:filename):
  "compare all trainers: random + 4 guess strategies"
  print("")
  d = Data(csv(f))
  for trainer in [random_trainer, 
                  guess_lazy_nearer, guess_lazy_likelier,
                  guess_eager_nearer, guess_eager_likelier]:
    evaluate(d, trainer, file=f)

if __name__ == "__main__": main(globals())
