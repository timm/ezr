"""Classify: NB vs Tree vs ZeroR (90/10 split, 20 reps, asserts > ZeroR)."""
from conftest import *
from ezr import *
from tree import treeGrow, treeLeaf
from stats import confused

def _nbBatch(train_rows, test_rows, header, klass_at):
  h, all = {}, Data([header])
  for r in train_rows:
    want = r[klass_at]
    if want not in h: h[want] = clone(all)
    add(all, add(h[want], r))
  cf = {}
  for r in test_rows:
    want = r[klass_at]
    got = max(h, key=lambda k: likes(h[k], r, len(all.rows), len(h)))
    cf.setdefault(want, {}); cf[want][got] = cf[want].get(got, 0) + 1
  return cf

def _treeBatch(d, train_rows, test_rows, klass_at):
  klass = lambda r: r[klass_at]
  t = treeGrow(d, train_rows, klass=klass, y=Sym)
  cf = {}
  for r in test_rows:
    want = r[klass_at]
    got = mid(treeLeaf(t, r).ynum)
    cf.setdefault(want, {}); cf[want][got] = cf[want].get(got, 0) + 1
  return cf

def _mergeCf(a, b):
  for w in b:
    a.setdefault(w, {})
    for g, n in b[w].items(): a[w][g] = a[w].get(g, 0) + n
  return a

def _accuracy(cf):
  total = sum(cf[w][g] for w in cf for g in cf[w])
  correct = sum(cf[w].get(w, 0) for w in cf)
  return correct / (total or 1e-32)

def _zeroR(train_rows, test_rows, klass_at):
  counts = {}
  for r in train_rows: counts[r[klass_at]] = counts.get(r[klass_at], 0) + 1
  majority = max(counts, key=counts.get)
  hits = sum(1 for r in test_rows if r[klass_at] == majority)
  return hits / (len(test_rows) or 1e-32)

def _runClassify(file, reps=20, frac=0.9):
  rows = list(csv(str(file)))
  header, body = rows[0], rows[1:]
  d = Data(csv(str(file)))
  klass_at = d.cols.klass.at
  nb_cf, tr_cf, zr = {}, {}, []
  import random
  for i in range(reps):
    random.seed(the.seed + i)
    shuffled = body[:]; random.shuffle(shuffled)
    split = int(frac * len(shuffled))
    train, test = shuffled[:split], shuffled[split:]
    _mergeCf(nb_cf, _nbBatch(train, test, header, klass_at))
    _mergeCf(tr_cf, _treeBatch(d, train, test, klass_at))
    zr.append(_zeroR(train, test, klass_at))
  return _accuracy(nb_cf), _accuracy(tr_cf), sum(zr)/len(zr)

def test_classify_diabetes():
  if not EGCLASS2.exists(): import pytest; pytest.skip("no diabetes.csv")
  nb, tr, zr = _runClassify(EGCLASS2)
  print(f"\ndiabetes: ZeroR={zr:.3f} NB={nb:.3f} Tree={tr:.3f}")
  assert nb > zr, f"NB ({nb:.3f}) <= ZeroR ({zr:.3f})"
  assert tr > zr, f"Tree ({tr:.3f}) <= ZeroR ({zr:.3f})"

def test_classify_soybean():
  if not EGCLASS1.exists(): import pytest; pytest.skip("no soybean.csv")
  nb, tr, zr = _runClassify(EGCLASS1)
  print(f"\nsoybean: ZeroR={zr:.3f} NB={nb:.3f} Tree={tr:.3f}")
  assert nb > zr, f"NB ({nb:.3f}) <= ZeroR ({zr:.3f})"
  assert tr > zr, f"Tree ({tr:.3f}) <= ZeroR ({zr:.3f})"
