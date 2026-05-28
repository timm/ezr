#!/usr/bin/env python3 -B
"""cli.py: ezr command-line + eg_* demos and tests.

Usage:
  ezr [--key=val ...] CMD [args]
  ezr --list           list all eg_* commands
  ezr --help           show this help

CMD is the name after `eg_`. Examples:
  ezr classify ~/gits/moot/classify/diabetes.csv
  ezr tree     ~/gits/moot/optimize/misc/auto93.csv
  ezr search de ~/gits/moot/optimize/misc/auto93.csv
  ezr --learn.budget=256 acquire ~/gits/moot/optimize/misc/auto93.csv
  ezr test_core
  ezr test_acquire
"""
import sys, random, traceback
from pathlib import Path
from ezr import *

# ---- Default data files (override via args) ----
EGOPT1   = Path.home() / "gits/moot/optimize/misc/auto93.csv"
EGCLASS1 = Path.home() / "gits/moot/classify/soybean.csv"
EGCLASS2 = Path.home() / "gits/moot/classify/diabetes.csv"
EGCNB    = Path.home() / "gits/moot/text_mining/reading/processed/Hall.csv"
EGTXT    = Path.home() / "gits/moot/text_mining/reading/raw/Hall.csv"

def ready(file):
  """Shuffle, split data into (full, train, test_rows)."""
  d = file if Data == type(file) else Data(csv(str(file)))
  random.shuffle(d.rows)
  half = len(d.rows) // 2
  return (d, clone(d, d.rows[:half][:the.few]), d.rows[half:])

def need(f):
  """Return path string if exists, else None."""
  p = Path(f)
  if not p.exists():
    print(f"missing: {f}"); return None
  return str(p)

# ============================================================
# App demos (one per app)
# ============================================================

def eg_classify(*argv):
  """Incremental NB on FILE; print confusion matrix raw counts."""
  if not argv: print("usage: ezr classify FILE"); return
  cf = classify(csv(argv[0])) or {}
  for want in sorted(cf):
    for got in sorted(cf[want]):
      print(f"  :want {want:<24} :got {got:<24} :n {cf[want][got]}")

def eg_tree(*argv):
  """Grow regression tree on FILE, show structure."""
  if not argv: print("usage: ezr tree FILE"); return
  d = Data(csv(argv[0]))
  treeShow(treeGrow(d, d.rows))

def eg_cluster(*argv):
  """kmeans++ + kmeans on FILE, one row per cluster."""
  if not argv: print("usage: ezr cluster FILE [--k=10]"); return
  d = Data(csv(argv[0]))
  cents = kpp(d, k=10)
  ds = kmeans(d, k=10, cents=cents)
  for c in ds:
    print(f"  :n {len(c.rows):>4}  :centroid {o(mids(c))}")

def eg_search(*argv):
  """ezr search {sa|ls|de} FILE — run search, report energy trace."""
  if len(argv) < 2: print("usage: ezr search {sa|ls|de} FILE"); return
  algo, file = argv[0], argv[1]
  d0 = Data(csv(file))
  shuffle(d0.rows)
  known = clone(d0, d0.rows[:50])
  srch  = clone(d0, d0.rows[50:])
  oracle = lambda r: oracleNearest(known, r)
  fns = {"sa": lambda: sa(srch, oracle, restarts=100),
         "ls": lambda: ls(srch, oracle),
         "de": lambda: de(srch, oracle)}
  if algo not in fns: print(f"unknown: {algo}"); return
  print(f"{'evals':>6} {'energy':>7}")
  for h, e, _ in fns[algo](): print(f"  {h:4}   {o(e):>5}")

def eg_acquire(*argv):
  """Active learning on FILE; print top-check labeled rows by d2h."""
  if not argv: print("usage: ezr acquire FILE [--learn.budget=50]"); return
  d0 = Data(csv(argv[0]))
  win = wins(d0)
  lab = acquire(d0)
  best = sorted(lab.rows, key=lambda r: disty(lab, r))[:the.learn.check]
  print(f":budget {the.learn.budget} :check {the.learn.check}")
  for r in best:
    print(f"  :win {win(r):>4}  :d2h {disty(lab, r):.3f}  {r}")

def eg_textmine(*argv):
  """CNB text mining on FILE."""
  if not argv: print("usage: ezr textmine FILE"); return
  f = need(argv[0])
  if f: tmActive(f)

def eg_stats(*argv):
  """Tiny demo of same/bestRanks/confused."""
  print(":same    ", same([1,2,3,4,5], [1.1,2,3,4,5], eps=0.5))
  print(":bestRanks", {k: v.n for k, v in bestRanks(
    {"good":[1,2,3], "bad":[100,200,300]}).items()})
  out = confused({"a":{"a":80,"b":20}, "b":{"a":10,"b":90}})
  for s in out: print(f"  :{s.label.strip()} acc={s.acc}")

# ============================================================
# Tests (assertions over real data files)
# ============================================================

def eg_test_core(*_):
  """Core primitives: Num, Sym, Data, distance, format."""
  assert o(3.14159).startswith("3.14")
  assert thing("3.14") == 3.14
  t = S(); nest(t, "a.b.c", 42); assert t.a.b.c == 42
  c = adds([10, 20, 30, 40, 50], Num())
  assert c.mu == 30 and 15.8 < spread(c) < 15.9
  c = adds("aaabbc", Sym())
  assert mid(c) == "a" and 1.4 < spread(c) < 1.5
  cols = Cols(["name", "Age", "Weight-"])
  assert not cols.ys[0].heaven and len(cols.xs) == 2 and len(cols.ys) == 1
  f = need(EGOPT1)
  if not f: return
  d = Data(csv(f)); assert len(d.rows) > 0
  assert distx(d, d.rows[0], d.rows[0]) == 0
  ds = [disty(d, r) for r in d.rows]
  assert min(ds) >= 0 and max(ds) <= 1.0001
  print("ok eg_test_core")

def eg_test_tree(*_):
  """Tree: grow, leaf, plan."""
  f = need(EGOPT1)
  if not f: return
  _, d_train, _ = ready(f)
  t = treeGrow(d_train, d_train.rows)
  treeShow(t)
  assert t.left is not None and t.right is not None
  d, d_train, _ = ready(f)
  t = treeGrow(d_train, d_train.rows)
  here = treeLeaf(t, max(d.rows, key=lambda r: disty(d, r)))
  plans = sorted(treePlan(t, here))
  assert plans, "treePlan produced no counterfactuals"
  print("ok eg_test_tree")

def eg_test_cluster(*_):
  """kmeans, kpp, rhalf benchmarks."""
  f = need(EGOPT1)
  if not f: return
  d = Data(csv(f))
  cents = kpp(d, k=10)
  assert len(cents) == 10
  ds = kmeans(d, k=10, cents=cents)
  assert len(ds) >= 1
  ds2 = rhalf(d, k=10)
  assert len(ds2) >= 1
  print("ok eg_test_cluster")

def eg_test_search(*_):
  """sa, ls, de — energy decreases over budget."""
  f = need(EGOPT1)
  if not f: return
  d0 = Data(csv(f))
  shuffle(d0.rows)
  known = clone(d0, d0.rows[:50])
  srch  = clone(d0, d0.rows[50:])
  oracle = lambda r: oracleNearest(known, r)
  for name, fn in [("sa", lambda: sa(srch, oracle, budget=500)),
                   ("ls", lambda: ls(srch, oracle, budget=500)),
                   ("de", lambda: de(srch, oracle, budget=2000))]:
    es = [e for _, e, _ in fn()]
    assert es and es[-1] <= es[0], f"{name} regressed: e0={es[0]} eN={es[-1]}"
    print(f"  {name}: {len(es)} improvements, e0={o(es[0])} eN={o(es[-1])}")
  print("ok eg_test_search")

def eg_test_acquire(*_):
  """Active learning beats random baseline."""
  f = need(EGOPT1)
  if not f: return
  d0 = Data(csv(f))
  w1, w_rand = Num(), Num()
  win = wins(d0)
  for _ in range(20):
    d, d_train, test_rows = ready(d0)
    lab = acquire(d_train)
    add(w1, win(min(lab.rows[:the.learn.check], key=lambda r: disty(d_train, r))))
    add(w_rand, win(min(sample(test_rows, the.learn.check),
                        key=lambda r: disty(d_train, r))))
  print(f":acquire {int(mid(w1))} :rand {int(mid(w_rand))}")
  assert mid(w1) > mid(w_rand), f"acquire {mid(w1):.1f} <= rand {mid(w_rand):.1f}"
  print("ok eg_test_acquire")

def eg_test_classify(*_):
  """NB and Tree beat ZeroR (90/10 split, reps)."""
  f = need(EGCLASS2)
  if not f: return
  d = Data(csv(f)); k = d.cols.klass.at
  rows = list(csv(f)); header, body = rows[0], rows[1:]
  def zeroR(train, test):
    cs = {}; [cs.setdefault(r[k], 0) for r in train]
    for r in train: cs[r[k]] = cs.get(r[k], 0) + 1
    maj = max(cs, key=cs.get)
    return sum(1 for r in test if r[k] == maj) / (len(test) or 1e-32)
  def nbBatch(train, test):
    h, all = {}, Data([header])
    for r in train:
      w = r[k]; h.setdefault(w, clone(all)); add(all, add(h[w], r))
    ok = 0
    for r in test:
      got = max(h, key=lambda kl: likes(h[kl], r, len(all.rows), len(h)))
      ok += int(got == r[k])
    return ok / (len(test) or 1e-32)
  nb_a, zr_a = [], []
  for i in range(20):
    random.seed(the.seed + i)
    sh = body[:]; random.shuffle(sh)
    sp = int(0.9 * len(sh))
    tr, te = sh[:sp], sh[sp:]
    nb_a.append(nbBatch(tr, te))
    zr_a.append(zeroR(tr, te))
  nb, zr = sum(nb_a)/len(nb_a), sum(zr_a)/len(zr_a)
  print(f":NB {nb:.3f} :ZeroR {zr:.3f}")
  assert nb > zr, f"NB ({nb:.3f}) <= ZeroR ({zr:.3f})"
  print("ok eg_test_classify")

def eg_test_stats(*_):
  """same, bestRanks, confused."""
  assert same([10,20,30,40,50], [11,19,31,39,51], eps=0.5)
  assert not same([1,2,3,4,5], [100,200,300,400,500], eps=0.5)
  best = bestRanks({"good":[1,2,3], "bad":[100,200,300]})
  assert "good" in best and "bad" not in best
  out = confused({"a":{"a":80,"b":20}, "b":{"a":10,"b":90}})
  for s in out: assert 0 <= s.acc <= 100
  print("ok eg_test_stats")

def eg_test_textmine(*_):
  """CNB on processed text + tokenize on raw text."""
  f = need(EGCNB)
  if f:
    data = Data(csv(f))
    ws = cnb(data); assert len(ws) >= 2
    tmRandom(f)
  f = need(EGTXT)
  if f:
    p = tmPrepare(f); assert len(p.top) >= 20
  print("ok eg_test_textmine")

def eg_test_all(*_):
  """Run every eg_test_* function."""
  fails = 0
  for name in sorted(globals()):
    if name.startswith("eg_test_") and name != "eg_test_all":
      print(f"--- {name} ---")
      try: globals()[name]()
      except Exception as e:
        fails += 1; traceback.print_exc()
  print(f"\nDone. fails={fails}")
  if fails: sys.exit(1)

# ============================================================
# Dispatcher
# ============================================================

def parse_flags(argv):
  """Strip --key=val flags, set the.key=val, return remaining args."""
  rest = []
  for a in argv:
    if a.startswith("--") and "=" in a:
      k, v = a[2:].split("=", 1)
      nest(the, k, thing(v))
    elif a in ("-h", "--help"):
      print(__doc__); list_cmds(); sys.exit(0)
    elif a == "--list":
      list_cmds(); sys.exit(0)
    else:
      rest.append(a)
  return rest

def list_cmds():
  """Print all eg_* commands."""
  print("\nCommands (eg_* funcs):")
  for name in sorted(globals()):
    if name.startswith("eg_"):
      doc = (globals()[name].__doc__ or "").splitlines()[0]
      print(f"  {name[3:]:<18} {doc}")

def main():
  argv = sys.argv[1:]
  if not argv:
    print(__doc__); list_cmds(); return
  argv = parse_flags(argv)
  if not argv:
    print(__doc__); list_cmds(); return
  cmd, *rest = argv
  fn = globals().get(f"eg_{cmd}")
  if not fn:
    print(f"unknown: {cmd}"); list_cmds(); sys.exit(1)
  random.seed(the.seed)
  fn(*rest)

if __name__ == "__main__":
  main()
