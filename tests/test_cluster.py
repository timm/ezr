"""Clustering: kmeans, kpp, rhalf benchmarks."""
from conftest import *
from ezr import *
from cluster import kmeans, kpp, rhalf, neighbors
from time import perf_counter_ns as now

def _clustering(d0, build, near=1, fast=False, repeats=10):
  t_build, t_apply, err = 0, 0, 0
  for _ in range(repeats):
    d, train, test = ready(d0)
    predict = lambda rs: (sum(disty(train, r) for r in rs) / len(rs) if rs else 0)
    t_1 = now(); ds = build(train); t_2 = now()
    t_build += t_2 - t_1
    for r in test:
      near_rs = neighbors(train, r, ds, near=near, fast=fast)
      err += abs(disty(d, r) - predict(near_rs)) / len(test)
    t_apply += now() - t_2
  return err / repeats

def test_cluster_kmeans():
  d = Data(csv(str(EGOPT1)))
  err = _clustering(d, lambda d1: kmeans(d1, k=10), repeats=3)
  baseline = _clustering(d, lambda d1: [d1], repeats=3)
  assert err <= baseline * 1.5, f"kmeans err {err:.3f} >> baseline {baseline:.3f}"

def test_cluster_rhalf():
  d = Data(csv(str(EGOPT1)))
  err = _clustering(d, lambda d1: rhalf(d1, k=10), repeats=3)
  baseline = _clustering(d, lambda d1: [d1], repeats=3)
  assert err <= baseline * 1.5, f"rhalf err {err:.3f} >> baseline {baseline:.3f}"

def test_cluster_kpp():
  d = Data(csv(str(EGOPT1)))
  cents = kpp(d, k=10)
  assert len(cents) == 10
