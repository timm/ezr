#!/usr/bin/env python3 -B
"""
ezr.py: minimal XAI for multi-objective reasoning
(c) 2026 Tim Menzies <timm@ieee.org> MIT license

Options:

  -P=2       minkowski coefficient
  -Start=4   acquire: initial random labels
  -Stop=50   acquire: total labelling budget
  -Few=128   max train rows
  -Leaf=4    tree: min rows in any leaf
  -Check=5   holdout: top picks to label
  -k=1       bayes: rare klass hack
  -m=2       bayes: rare evidence hack
  -Klass=$MOOT/classify/diabetes.csv  classify demo data
  -Repeats=30  klass: number of train/test splits
  -Seed=1234567891  random number seed
  -File=$MOOT/optimize/misc/auto93.csv
"""

# pylint: disable=bad-indentation,invalid-name
# pylint: disable=missing-function-docstring
# pylint: disable=multiple-statements,multiple-imports
# pylint: disable=unnecessary-lambda-assignment
# pylint: disable=inconsistent-return-statements
# pylint: disable=dangerous-default-value
# pylint: disable=broad-exception-caught
# pylint: disable=unidiomatic-typecheck

import os, random, re, sys, traceback
from math import exp, log, log2, pi, sqrt
from types import SimpleNamespace as o

def atom(s,bools={'True': True, 'False': False}):
  try: return int(s)
  except ValueError:
    try: return float(s)
    except ValueError:
      s = s.strip()
      return bools.get(s, s)

pat = r"(\w+)=(\S+)"
the = o(**{k: atom(v) for k,v in re.findall(pat, __doc__ or "")})
defaults = o(**vars(the))

def csv(file):
  file = file.replace("$MOOT", os.environ.get("MOOT")
                      or os.path.expanduser("~/gits/moot"), 1)
  with open(file, encoding="utf-8") as f:
    return [tuple(atom(x) for x in line.split(","))
            for line in f if line.strip()]

