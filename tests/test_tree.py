"""Tree learner: tree, see (with active learn seed), funny, plan."""
from conftest import *
from ezr import *
from tree import treeGrow, treeShow, treeLeaf, treePlan
from acquire import acquire

def test_tree():
  _, d_train, _ = ready(EGOPT1)
  t = treeGrow(d_train, d_train.rows)
  treeShow(t)
  assert t.left is not None and t.right is not None

def test_see():
  _, d_train, _ = ready(EGOPT1)
  lab = acquire(d_train)
  t = treeGrow(d_train, lab.rows)
  treeShow(t)
  assert t.left is not None

def test_funny():
  d, d_train, test = ready(EGOPT1)
  t = treeGrow(d_train, d_train.rows)
  rows_seen = 0
  for r in sorted(test, key=lambda r: disty(d_train, r))[:10]:
    lf = treeLeaf(t, r); rows_seen += 1
  assert rows_seen > 0

def test_plan():
  d, d_train, _ = ready(EGOPT1)
  t = treeGrow(d_train, d_train.rows)
  here = treeLeaf(t, max(d.rows, key=lambda r: disty(d, r)))
  plans = sorted(treePlan(t, here))
  assert plans, "treePlan produced no counterfactuals"
  assert all(dy > 0 for dy, _, _ in plans)
