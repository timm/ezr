#!/usr/bin/env python3 -B
"""
vsmin.py: ezr.py's acquire versus min.py's one-shot holdout.
Same budget, one shared ruler.  Delta is 0 if `same`.
(c) 2026 Tim Menzies <timm@ieee.org> MIT license

Flags are ezr.py's: -Stop (budget), -Check, -Repeats, -Seed,
-File.  min.py's Budget/Check are set to match.

Both arms return one row; both rows are scored by the SAME
wins() ruler, built once off the whole table.  So the only
thing the delta measures is which row each program found.
"""
# pylint: disable=bad-indentation,multiple-statements
# pylint: disable=invalid-name,wildcard-import
# pylint: disable=unused-wildcard-import
import os, sys, random  # pylint: disable=C0410
import min as minpy     # `as` so builtin min() survives
import ezr
from ezr import *

the.Eps = 0.35                 # cohen's absolute floor, in score points
the._defaults.update(Eps=the.Eps)

def mu(xs: NUMS) -> float:
  "Mean."
  return sum(xs) / len(xs)

def arms(tbl: TBL) -> tuple[NUMS, NUMS]:
  "One score per seed, per arm, on one shared ruler."
  w = wins(tbl)                          # the shared ruler
  minpy.the.Budget, minpy.the.Check = the.Stop, the.Check
  d = minpy.Tbl(minpy.csv(the.File))    # min's own table
  a, b = [], []
  for i in range(the.Repeats):
    s = the.Seed + i                     # same seed, both arms
    random.seed(s)
    a += [w(holdout(tbl, acquire))]      # ezr.py, end to end
    minpy.the.Seed = s                   # holdout() seeds itself
    b += [w(minpy.holdout(d)[0])]         # min.py, end to end
  return a, b

def eg_min() -> None:
  "ezr versus min, same budget.  0 if the same."
  tbl  = Tbl(csv(the.File))
  a, b = arms(tbl)
  d    = 0 if same(a, b, eps=the.Eps) else round(mu(a) - mu(b))
  print(f"{round(mu(a)):>4} {round(mu(b)):>4} {d:>4}"
        f" {os.path.basename(the.File)}")

if __name__ == "__main__":
  _av = sys.argv[1:]
  while _av:
    _s = _av.pop(0)
    if   _s[:2] == "--":  run(eg_min)
    elif _s[1:] in the:   the[_s[1:]] = atom(_av.pop(0))
    else: print(f"unknown arg: {_s}")
