"""Stats: same, bestRanks, confused."""
from conftest import *
from ezr import *
from stats import same, bestRanks, confused

def test_same_obviously_same():
  xs = [10, 20, 30, 40, 50]
  ys = [11, 19, 31, 39, 51]
  assert same(xs, ys, eps=0.5)

def test_same_obviously_different():
  xs = [1, 2, 3, 4, 5]
  ys = [100, 200, 300, 400, 500]
  assert not same(xs, ys, eps=0.5)

def test_bestRanks_picks_lowest_median():
  d = {"good": [1, 2, 3], "bad": [100, 200, 300]}
  best = bestRanks(d)
  assert "good" in best
  assert "bad" not in best

def test_confused_simple():
  cf = {"a": {"a": 80, "b": 20},
        "b": {"a": 10, "b": 90}}
  out = confused(cf)
  labels = [s.label.strip() for s in out]
  assert labels == ["a", "b"]
  for s in out:
    assert 0 <= s.acc <= 100
    assert s.tp + s.fn + s.fp + s.tn == 200
