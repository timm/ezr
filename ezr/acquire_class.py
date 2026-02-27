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
  Budget = Budget or the.Budget
  rows   = shuffle(rows[:])
  unseen = clone(d, rows[Any:][:the.Few])
  seen   = clone(d, rows[:Any]).sorty()
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
      rest.add(
        best.sub(
          best.sorty().rows[-1]))
  return seen.sorty().rows

#---- demos -----------------------------------------------------------
def eg__compare(f:filename):
  "compare all trainers: random + 4 guess strategies"
  def lazy_nearer(d,rs):   return guess(d,rs,scorer=nearer,  eager=False)
  def lazy_likelier(d,rs): return guess(d,rs,scorer=likelier,eager=False)
  def eager_nearer(d,rs):  return guess(d,rs,scorer=nearer,  eager=True)
  def eager_likelier(d,rs):return guess(d,rs,scorer=likelier,eager=True)
  print("")
  d = Data(csv(f))
  for trainer in [random_trainer, 
                  lazy_nearer, lazy_likelier,
                  eager_nearer, eager_likelier]:
    evaluate(d, trainer, file=f)

if __name__ == "__main__": main(globals())
