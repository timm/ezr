#!/usr/bin/env python3 -B
"""acquire.py: active learning via Bayes or centroid acquisition."""
from ezr import *

def acquireWithBayes(data, best, rest, row):
  """Score: rest - best likelihood."""
  n = len(best.rows) + len(rest.rows)
  return likes(rest, row, n, 2) - likes(best, row, n, 2)

def acquireWithCentroid(data, best, rest, row):
  """Score: dist(best) - dist(rest)."""
  return (distx(data, row, mids(best)) -
          distx(data, row, mids(rest)))

def warm_start(data, rows, label):
  """Init lab/best/rest from start rows."""
  lab = clone(data, rows[:the.learn.start])
  lab.rows.sort(key=lambda row: disty(lab, label(data, row)))
  n = int(sqrt(len(lab.rows)))
  return (lab,
          clone(data, lab.rows[:n]),
          clone(data, lab.rows[n:]),
          rows[the.learn.start:])

def dont_let_Best_grow_too_big(best, rest, lab):
  """Cap best at sqrt(|lab|); evict worst."""
  if len(best.rows) > sqrt(len(lab.rows)):
    best.rows.sort(key=lambda row: disty(lab, row))
    rest.rows.append(
      add(rest.cols, sub(best.cols, best.rows.pop())))

def acquire(data, score=acquireWithCentroid,
            label=lambda _, row: row):
  """Active learning. Returns labeled Data."""
  rows = data.rows[:]
  shuffle(rows)
  lab, best, rest, unlab = warm_start(data, rows[:the.few], label)
  fn = lambda row: score(lab, best, rest, row)
  for _ in range(the.learn.budget):
    if not unlab: break
    pickr, *unlab = sorted(unlab, key=fn)
    add(lab, add(best, label(data, pickr)))
    dont_let_Best_grow_too_big(best, rest, lab)
  lab.rows.sort(key=lambda r: disty(lab, r))
  return lab

def cli(argv):
  """Run acquire on FILE; print top-check labeled rows by d2h."""
  if not argv: print("usage: ezr acquire FILE [--learn.budget=50 ...]"); return
  d0 = Data(csv(argv[0]))
  win = wins(d0)
  lab = acquire(d0)
  best = sorted(lab.rows, key=lambda r: disty(lab, r))[:the.learn.check]
  print(f":budget {the.learn.budget} :check {the.learn.check}")
  for r in best:
    print(f"  win={win(r):>4}  d2h={disty(lab, r):.3f}  {r}")

if __name__ == "__main__":
  cli(sys.argv[1:])
