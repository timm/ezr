#!/usr/bin/env python3 -B
"""cmp_fft_lgbm.py: frugal trees against LightGBM, same 80:20 split.

Both arms see the same rows, the same target (ydist when a file has
several goals, else the lone y column) and the same scaler -- the
TRAIN table's columns -- so nothing about the test half leaks into
either one.  Error is MAE over (mean - min) of the test y, which
makes files of wildly different units printable in one column.

  ./etc/cmp_fft_lgbm.py FILE...        # one line per file
"""
import os, re, sys, time, random, statistics as S
sys.path.insert(0, os.path.dirname(os.path.dirname(
                   os.path.abspath(__file__))))
import ezr as E
import attic as A

SEEDS = int(os.environ.get("SEEDS", 5))
DEPTH  = 5
BUDGET = int(os.environ.get("BUDGET", 64))
PRUNE  = os.environ.get("PRUNE", "")   # acq | any | "" = every row

def split(f, seed):
  "The one split both arms are judged on."
  random.seed(seed)
  t  = E.Tbl(E.csv(f))
  t  = E.clone(t, [r for r in t.rows         # a row with no target
                   if all(r[c.at] != "?" for c in t.cols.y)])
  rs = random.sample(t.rows, len(t.rows))    # cannot score anyone
  n  = int(.8 * len(rs))
  return t, E.clone(t, rs[:n]), E.clone(t, rs[n:])

def scale(tr, rows):
  "Test y, and what to divide its errors by.  Train's columns."
  _, Y = E.target(tr)
  vs = [Y(r) for r in rows]
  return Y, sum(vs)/len(vs) - min(vs) + 1E-32

def fft(tr, te):
  """Frugal, then the plain tree as a reference.  Both see all of
  TR's labels; frugal just spends a quarter of them picking its
  spine instead of growing with them."""
  t0        = time.time()
  best, _   = A.frugal(tr, tr.rows)
  secs      = time.time() - t0
  root      = E.fit(E.tree(tr, tr.rows, DEPTH), *E.target(tr))
  Y, d      = scale(tr, te.rows)
  err = sum(abs(Y(r) - A.fleaf(best,r)) for r in te.rows)
  big = sum(abs(Y(r) - E.leaf(root,r).pred) for r in te.rows)
  return err/len(te.rows)/d, big/len(te.rows)/d, secs, len(best)

def lgbm(tr, te):
  """Same rows, same target, LightGBM's defaults.  Symbols get a
  code learned on TRAIN (so a symbol only test has seen is just
  missing) and are declared categorical, which is the nearest
  thing lgbm has to ezr treating two symbols as simply unequal."""
  import numpy as np, lightgbm as lgb
  xs   = [c.at for c in tr.cols.x]
  cats = {at: {v: i for i, v in enumerate(sorted(
                 {r[at] for r in tr.rows if type(r[at]) is str
                  and r[at] != "?"}))}
          for at in xs if type(tr.cols.all[at]) is E.Sym}
  def X(rows):
    return np.array(
      [[cats[at].get(r[at], np.nan) if at in cats else
        (np.nan if r[at] == "?" else r[at]) for at in xs]
       for r in rows], dtype=float)
  _, Ytr = E.target(tr)
  Yte, d = scale(tr, te.rows)
  t0 = time.time()
  m  = lgb.LGBMRegressor(verbose=-1, n_estimators=100)
  m.fit(X(tr.rows), [Ytr(r) for r in tr.rows],
        categorical_feature=[i for i,at in enumerate(xs) if at in cats])
  secs = time.time() - t0
  p = m.predict(X(te.rows))
  err = sum(abs(Yte(r) - v) for r,v in zip(te.rows, p))
  return err/len(te.rows)/d, secs

def prune(tr, how):
  """BUDGET rows out of train.  `acquire` sees the whole half, not
  the.Few: with a pool of 128 and a budget of 64 it would be
  picking half of a random sample, which is barely a choice."""
  E.the.Few = len(tr.rows)
  t0  = time.time()
  got = (E.acquire if how == "acq" else E.grabs)(tr, BUDGET)
  return E.clone(tr, got), time.time() - t0

def n2(v, sign=False):
  "0.237 -> .24 ; -0.103 -> -.10 ; 1.498 -> 1.50"
  return re.sub(r"(?<![\d.])0\.", ".", f"{v:{'+' if sign else ''}.2f}")

def main(files):
  "One TSV line per file: name, rows, budget, then the medians."
  acq = PRUNE == "acq"
  for f in files:
    ks = ("fft tree0 lgbm rnd sf sl" if acq else
          "fft tree0 lgbm sf sl").split()
    a  = {k: [] for k in ks}
    for seed in range(SEEDS):
      t, full, te = split(f, seed)
      tr, sp = full, 0
      if PRUNE:
        tr, sp = prune(full, PRUNE)       # the rows both arms see
        if acq:                           # ...and a random control
          rnd, _ = prune(full, "any"); a["rnd"] += [fft(rnd, te)[0]]
      e1, e0, s1, _ = fft(tr, te); e2, s2 = lgbm(tr, te)
      for k, v in zip("fft tree0 lgbm sf sl".split(),
                      (e1, e0, e2, s1+sp, s2)): a[k] += [v]
    pre = [os.path.basename(f)[:-4], str(len(t.rows)),
           str(BUDGET if PRUNE else 0)]
    if os.environ.get("RAW"):     # every seed, for --stats to test
      for k in ks:
        print("\t".join(pre + [k] + [f"{v:.5f}" for v in a[k]]),
              flush=True)
    else:
      print("\t".join(pre + [f"{S.median(a[k]):.4f}" for k in ks]),
            flush=True)

def rows(lines):
  "name, rows, budget, values"
  return [(n, int(r), int(b), [float(x) for x in v])
          for n, r, b, *v in (l.split("\t") for l in lines if l.strip())]

def fmt(lines):
  "One budget, sorted by delta.  8 values = a rnd column."
  rs  = rows(lines)
  acq = len(rs[0][3]) == 6
  rs  = sorted(rs, key=lambda z: z[3][2] - z[3][0])   # lgbm - fft
  b   = rs[0][2]
  print(f"{SEEDS} seeds, 80:20, Depth={DEPTH} (<= 3^5 = 243 trees),"
        + (f" train = {'acquire' if acq else 'random'}({b}) of the"
           " train half" if b else " train = the whole train half")
        + "." + ("\nrnd = the same budget taken at random." if acq
                else "")
        + "\nmedian over seeds.  error = MAE / (mean - min) of the"
          " test y; lower\nwins.  delta = lgbm - fft, so NEGATIVE ="
          " LightGBM won.\n")
  rnd  = f"{'rnd':>6}" if acq else ""
  head = (f"{'data':<13}{'ezr s':>7}{'lgbm s':>7} |{'rows':>6} |"
          f"{'fft':>6}{'tree0':>6}{'lgbm':>6}{rnd} |{'delta':>7}")
  print(head); print("-" * len(head))
  for n, r, _, v in rs:
    print(f"{n[:13]:<13}{v[-2]:7.2f}{v[-1]:7.2f} |{r:6} |"
          f"{n2(v[0]):>6}{n2(v[1]):>6}{n2(v[2]):>6}"
          + (f"{n2(v[3]):>6}" if acq else "")
          + f" |{n2(v[2]-v[0], 1):>7}")
  print("-" * len(head))
  c = [sum(x)/len(x) for x in zip(*[z[3] for z in rs])]
  print(f"{'mean':<13}{c[-2]:7.2f}{c[-1]:7.2f} |{'':6} |"
        f"{n2(c[0]):>6}{n2(c[1]):>6}{n2(c[2]):>6}"
        + (f"{n2(c[3]):>6}" if acq else "")
        + f" |{n2(c[2]-c[0], 1):>7}")

def sweep(lines):
  "Error against label budget, one block per arm."
  rs = rows(lines)
  bs = sorted({z[2] for z in rs})          # 0 sorts first = all
  bs = [b for b in bs if b] + ([0] if 0 in bs else [])
  ns = sorted({z[0] for z in rs},
              key=lambda n: -max(z[1] for z in rs if z[0]==n))
  at = {(z[0], z[2]): z[3] for z in rs}
  sz = {z[0]: z[1] for z in rs}
  print(f"{SEEDS} seeds, 80:20, Depth={DEPTH}, grabs(budget) of the"
        " train half.\nerror = MAE / (mean - min) of the test y;"
        " lower wins.  `all` = every\ntrain row (80%).  A budget at"
        " or over that is the same run as `all`.\n")
  for arm, i in (("fft", 0), ("lgbm", 2), ("delta", -1)):
    head = (f"{arm:<13}" + "".join(f"{(b or 'all'):>6}" for b in bs)
            + f" |{'train':>7}")
    print(head); print("-" * len(head))
    cell = ((lambda v: n2(v[2]-v[0], 1)) if i < 0 else
            (lambda v: n2(v[i])))
    for n in ns:
      print(f"{n[:13]:<13}" + "".join(
        cell(at[(n,b)]).rjust(6) if (n,b) in at else "     ."
        for b in bs) + f" |{int(.8*sz[n]):7}")
    print("-" * len(head))
    print(f"{'mean':<13}" + "".join(
      cell([sum(at[(n,b)][j] for n in ns if (n,b) in at) /
            sum(1 for n in ns if (n,b) in at) for j in range(3)]
           ).rjust(6) for b in bs) + "\n")
    if i < 0: print("  delta = lgbm - fft.  NEGATIVE = LightGBM won,"
                    " positive = frugal won.")

def stats(lines):
  """Medians over every seed, and a `!` on each arm that ezr.same
  (cliffs + ks) cannot separate from the best one in its row."""
  d, sz = {}, {}
  for l in lines:
    if not l.strip(): continue
    n, r, b, k, *v = l.split("\t")
    d[(n,k)] = [float(x) for x in v]; sz[n] = (int(r), int(b))
  arms = [k for (_,k) in d if k in ("fft","tree0","lgbm")]
  arms = sorted(set(arms), key="fft tree0 lgbm".split().index)
  ns   = sorted(sz, key=lambda n: -sz[n][0])
  N    = len(next(iter(d.values())))
  b    = next(iter(sz.values()))[1]
  print(f"{N} seeds, 80:20, Depth={DEPTH}, grabs({b}) of the train"
        " half.\nerror = MAE / (mean - min) of the test y; lower"
        " wins.  `!` = cannot be\nseparated from the best cell in"
        " that row (cliffs d=.197 and ks 95%).\n")
  head = (f"{'data':<13}|" + "".join(f"{a:>8}" for a in arms)
          + f" |{'rows':>7}")
  print(head); print("-" * len(head))
  won = {a: 0 for a in arms}
  for n in ns:
    best = min(arms, key=lambda a: S.median(d[(n,a)]))
    out  = ""
    for a in arms:
      ok = a == best or E.same(d[(n,a)], d[(n,best)])
      won[a] += ok
      out += f"{n2(S.median(d[(n,a)])):>7}" + ("!" if ok else " ")
    print(f"{n[:13]:<13}|{out} |{sz[n][0]:7}")
  print("-" * len(head))
  print(f"{'median':<13}|" + "".join(
    f"{n2(S.median([S.median(d[(n,a)]) for n in ns])):>8}"
    for a in arms) + f" |{'':7}")
  print(f"{'# of ! rows':<13}|" + "".join(f"{won[a]:>8}" for a in arms)
        + f" |{len(ns):7}")

if __name__ == "__main__":
  if   sys.argv[1:2] == ["--fmt"]:   fmt(sys.stdin.readlines())
  elif sys.argv[1:2] == ["--sweep"]: sweep(sys.stdin.readlines())
  elif sys.argv[1:2] == ["--stats"]: stats(sys.stdin.readlines())
  else: main(sys.argv[1:] or [E.the.File])
