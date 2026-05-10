"""Acquire: active learning — assert wins > random baseline."""
from conftest import *
from ezr import *
from acquire import acquire, acquireWithCentroid, acquireWithBayes
from tree import treeGrow, treeLeaf
import random

def test_acquire():
  d0 = Data(csv(str(EGOPT1)))
  w1, w2, w_rand = Num(), Num(), Num()
  win = wins(d0)
  for _ in range(20):
    d, d_train, test_rows = ready(d0)
    lab = acquire(d_train)
    t = treeGrow(d_train, lab.rows)
    guess = sorted(test_rows, key=lambda r: mid(treeLeaf(t, r).ynum))
    add(w1, win(min(lab.rows[:the.learn.check], key=lambda r: disty(d_train, r))))
    add(w2, win(min(guess[:the.learn.check],     key=lambda r: disty(d_train, r))))
    add(w_rand, win(min(sample(test_rows, the.learn.check), key=lambda r: disty(d_train, r))))
  print(f":train {int(mid(w1))} :test {int(mid(w2))} :rand {int(mid(w_rand))}")
  assert mid(w1) > mid(w_rand), f"acquire train ({mid(w1):.1f}) <= random ({mid(w_rand):.1f})"
  assert mid(w2) > mid(w_rand), f"acquire test ({mid(w2):.1f}) <= random ({mid(w_rand):.1f})"

def test_acquire_compare_strategies():
  d = Data(csv(str(EGOPT1)))
  W = wins(d)
  Y = lambda r: disty(d, r)
  out = {}
  for _ in range(20):
    random.shuffle(d.rows)
    n = len(d.rows) // 2
    test = d.rows[n:]
    train = d.rows[:n][:the.few]
    lab1 = train[:the.learn.budget]
    lab2 = acquire(clone(d, train))
    lab3 = acquire(clone(d, train), acquireWithCentroid)
    for how, lab in (("rand", lab1), ("bayes", lab2.rows), ("near", lab3.rows)):
      d2    = clone(d, lab)
      tree2 = treeGrow(d2, d2.rows)
      guess = sorted(test, key=lambda r: mid(treeLeaf(tree2, r).ynum))
      out[how] = out.get(how) or Num()
      add(out[how], W(sorted(guess[:the.learn.check], key=Y)[0]))
  for how, num in out.items(): print(int(mid(num)), how, end=" ")
  print()
  assert mid(out["bayes"]) > mid(out["rand"]), \
    f"bayes ({mid(out['bayes']):.1f}) <= rand ({mid(out['rand']):.1f})"
  assert mid(out["near"]) > mid(out["rand"]), \
    f"near ({mid(out['near']):.1f}) <= rand ({mid(out['rand']):.1f})"
