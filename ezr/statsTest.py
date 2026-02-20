#!/usr/bin/env python3 -B
"""tests.py: corner cases for stats.py"""
import random
from stats import Confuse, confuse, confused, same, top

def banner(s): print(f"\n{'='*40}\n{s}")
def show_cf(cf):
  for c in confused(cf):
    print(f"  {c.label:>10}  pd={c.pd:3}  pf={c.pf:3}  prec={c.prec:3}  acc={c.acc:3}")

# ---- confuse demos --------------------------------------------------

def eg_perfect():
  "always right: tp=all, fn=fp=0"
  banner("perfect classifier")
  cf = Confuse()
  for _ in range(40): confuse(cf, "yes", "yes")
  for _ in range(10): confuse(cf, "no",  "no")
  show_cf(cf)

def eg_worst():
  "always wrong: all fn/fp, tp=0"
  banner("worst classifier (always wrong)")
  cf = Confuse()
  for _ in range(40): confuse(cf, "yes", "no")
  for _ in range(10): confuse(cf, "no",  "yes")
  show_cf(cf)

def eg_imbalanced():
  "1 positive in 99: recall vs precision tradeoff"
  banner("imbalanced (1% positive)")
  cf = Confuse()
  confuse(cf, "pos", "pos")          # 1 true positive
  confuse(cf, "pos", "neg")          # 1 false negative
  for _ in range(98): confuse(cf, "neg", "neg")
  show_cf(cf)

def eg_multiclass():
  "3-class: see per-class and _OVERALL"
  banner("multi-class (A/B/C)")
  cf = Confuse()
  random.seed(1)
  labels = ["A"]*40 + ["B"]*35 + ["C"]*25
  for want in labels:
    got = want if random.random() < 0.7 else random.choice(["A","B","C"])
    confuse(cf, want, got)
  show_cf(cf)

# ---- same/top demos -------------------------------------------------

def eg_identical():
  "same list twice: must return True"
  banner("same: identical lists")
  x = list(range(20))
  print("  identical:", same(x, x[:]))

def eg_shifted():
  "same: shifted mean, should differ"
  banner("same: shifted mean")
  x = list(range(20))
  y = [v + 5 for v in x]
  print("  shift+5  :", same(x, y))
  y2 = [v + 0.5 for v in x]
  print("  shift+0.5:", same(x, y2))   # borderline

def eg_spread():
  "same mean, very different spread"
  banner("same: equal mean, different spread")
  import statistics
  x = [10]*20
  y = list(range(1, 21))
  print(f"  x mu={statistics.mean(x)} sd=0  y mu={statistics.mean(y):.1f} sd={statistics.stdev(y):.1f}")
  print("  same?", same(x, y))

def eg_small_n():
  "tiny lists: n=3 stress-tests ks threshold"
  banner("same: tiny lists (n=3)")
  print("  [1,2,3] vs [1,2,3]:", same([1,2,3],[1,2,3]))
  print("  [1,2,3] vs [7,8,9]:", same([1,2,3],[7,8,9]))

def eg_top_all_same():
  "top: all treatments identical -> returns all"
  banner("top: all identical treatments")
  rxs = {k: list(range(20)) for k in "ABC"}
  print("  winners:", top(rxs))

def eg_top_one_winner():
  "top: one treatment clearly best"
  banner("top: one clear winner")
  rxs = {"good": [1,2,3,4,5]*4,
         "bad1": [10,11,12,13,14]*4,
         "bad2": [15,16,17,18,19]*4}
  print("  winners:", top(rxs))

def eg_top_tied():
  "top: two treatments tied at top"
  banner("top: two tied winners")
  rxs = {"A": [1,2,3,4,5]*4,
         "B": [1,2,3,4,5]*4,   # same as A
         "C": [10,11,12,13,14]*4}
  print("  winners:", top(rxs))

def eg_weibull():
  "top: random weibull stress test (expect small winner set)"
  banner("top: 20 weibull treatments, n=20 each")
  from stats import weibulls
  random.seed(1)
  winners = weibulls()
  print(f"  {len(winners)} winners from 20: {winners}")

# ---- main -----------------------------------------------------------
if __name__ == "__main__":
  for name,fn in list(globals().items()):
    if name.startswith("eg_"):
      fn()
