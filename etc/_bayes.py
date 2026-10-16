#!/usr/bin/env python3 -B
# vim: set et sw=2 ts=2 sts=2 cc=75 :
"""
_bayes.py: the naive bayes half of cmp_bayes_lgbm, so it can run under
pypy.  LightGBM is a C extension and will not load there, so the two
learners have to be timed in separate interpreters.  Prints json.

Usage: pypy3 _bayes.py FILE SHUFFLES TRAIN
"""
import os, sys, json, time, random

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import min as m

def main(file, n, train):
  t = m.Tbl(m.csv(file))
  klass = lambda row: str(row.raw[t.cols.klass.at])
  acc, c = [], time.time()
  for seed in range(n):
    rows = t.rows[:]
    random.Random(seed).shuffle(rows)    # same order as the lgbm side
    k = int(train * len(rows))
    tr, te = rows[:k], rows[k:]
    fit = m.clone(t, tr)
    m.bins(fit)
    guess = m.nb(fit, fit.rows, klass)
    acc += [100 * sum(guess(m.binRow(fit, r)) == klass(r)
                      for r in te) / len(te)]
  print(json.dumps(dict(acc=acc, secs=time.time() - c, rows=len(t.rows))))

if __name__ == "__main__":
  main(sys.argv[1], int(sys.argv[2]), float(sys.argv[3]))
