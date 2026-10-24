#!/usr/bin/env python3 -B
"""nb.py: dull old naive bayes against LightGBM.

Two ways to read a numeric column.  BINS=0 keeps it numeric and
scores it with a Gaussian (mu, sd straight off ezr's Welford
column).  BINS=n chops it into n bins on the logistic norm, as
`ezr1.bin1` does, and then it is just another symbol.  Symbols
either way take an m-estimate, the prior a k-estimate.

Both arms read EVERY training row -- no budget, no active
learning -- so this asks what the method is worth, not what the
labels are.

  BINS=0 M=2 K=1 SEEDS=5 python3 etc/nb.py diabetes soybean ...

LGB=0 drops the LightGBM arm; RAW=1 dumps per-seed accuracies
instead of the table, for comparing runs against each other.
"""
# pylint: disable=no-member   # `type()` structs confuse pylint
import os, sys, time, random, statistics as S
from math import exp, pi, log
sys.path.insert(0, os.path.dirname(os.path.dirname(
                   os.path.abspath(__file__))))
import ezr as E

SEEDS = int(os.environ.get("SEEDS", 5))
BINS  = int(os.environ.get("BINS", 0))   # 0 = gaussian
M     = float(os.environ.get("M", 2))    # likelihood, for symbols
K     = float(os.environ.get("K", 1))    # prior
LGB   = int(os.environ.get("LGB", 1))    # 0 = skip LightGBM
RAW   = int(os.environ.get("RAW", 0))    # dump per-seed accuracies

def dot(x: float) -> str:
  "Two decimals, no leading zero: 0.029 -> .03"
  return f"{x:.2f}".lstrip("0") or "0"

def bin1(col, v):
  "V as a bin label, or as itself if BINS is off or COL is a symbol."
  if not BINS or type(col) is E.Sym: return v
  return min(BINS-1, int(BINS * E.norm(col, v)))

def fit(tbl: E.TBL, rows: list) -> tuple:
  """Per class: how many rows it has, and per x-column either a NUM
  (gaussian) or a count of bins.  Also, per column, what an unseen
  value falls back on -- a variance floor, or how many bins there
  are to spread M over."""
  at, by = tbl.cols.klass.at, {}
  for r in rows:
    k = by.setdefault(r[at], [0, {c.at: (E.Num() if not BINS and
                                         type(c) is E.Num else {})
                                 for c in tbl.cols.x}])
    k[0] += 1
    for c in tbl.cols.x:
      v = r[c.at]
      if v == "?": continue
      slot = k[1][c.at]
      if type(slot) is dict:
        b = bin1(c, v); slot[b] = slot.get(b, 0) + 1
      else: E.add(slot, v)
  sp = {c.at: (max(1e-12, .01*c.sd**2) if not BINS and type(c) is E.Num
               else (BINS if type(c) is E.Num else max(1, len(c.has))))
        for c in tbl.cols.x}
  return by, sp

def gauss(col, v, floor: float) -> float:
  """How likely V is, if COL were a bell.  A class holding one row
  has sd=0 and would otherwise score 1.0 on every column -- i.e.
  beat everyone -- so variance is floored by a share of what the
  whole training set shows in that column (sklearn's trick)."""
  var = max(col.sd**2, floor)
  return exp(-(v - col.mu)**2 / (2*var)) / (2*pi*var)**.5

def nb(tbl: E.TBL, by: dict, sp: dict, row) -> str:
  "The class whose prior times likelihoods is largest.  Logs, to add."
  n, nk = sum(v[0] for v in by.values()), len(by)
  best, most = None, -1e30
  for k, (cnt, cols) in by.items():
    s = log((cnt + K) / (n + K*nk))
    for c in tbl.cols.x:
      v = row[c.at]
      if v == "?": continue
      slot = cols[c.at]
      p = (gauss(slot, v, sp[c.at]) if type(slot) is not dict else
           (slot.get(bin1(c, v), 0) + M/sp[c.at]) / (cnt + M))
      s += log(max(p, 1e-300))
    if s > most: best, most = k, s
  return best

def lgbm(tbl: E.TBL, tr: E.TBL, te: E.TBL):
  """LightGBM's defaults, every training row, symbols as categories.
  A Sym column may hold numbers (ezr reads a column's type from its
  name, not its values), so the codes are keyed on the value itself
  -- key on `str` only and such a column maps to nothing but nan.
  Returns its guesses, as strings, and the seconds it took."""
  import numpy as np, lightgbm as lgb       # pylint: disable=C0415
  xs   = [c.at for c in tbl.cols.x]
  cats = {at: {v: i for i, v in enumerate(sorted(
                 {r[at] for r in tr.rows if r[at] != "?"}, key=str))}
          for at in xs if type(tbl.cols.all[at]) is E.Sym}
  X = lambda rows: np.array(
    [[cats[at].get(r[at], np.nan) if at in cats else
      (np.nan if r[at] == "?" else r[at]) for at in xs]
     for r in rows], dtype=float)
  at = tbl.cols.klass.at
  ks = sorted({str(r[at]) for r in tr.rows})
  ix = {k: i for i, k in enumerate(ks)}
  t0 = time.time()
  mdl = lgb.LGBMClassifier(verbose=-1, n_estimators=100)
  mdl.fit(X(tr.rows), [ix[str(r[at])] for r in tr.rows],
          categorical_feature=[i for i, a in enumerate(xs) if a in cats])
  p = mdl.predict(X(te.rows))
  return [ks[int(v)] for v in p], time.time()-t0

def tt(tr: str, te: str, lg: str = None):
  """One frozen split, from `etc/cache.py`: fit on -t, score -T, and
  say how it did beside whatever LightGBM already said about the
  same two files.  No shuffling, no seeds -- the split IS the file,
  so two arms compared this way saw exactly the same rows."""
  import d2h as H                         # pylint: disable=C0415
  t = E.Tbl(E.csv(tr)); b = E.Tbl(E.csv(te))
  at = t.cols.klass.at                    # ezr types a column by its
  t0 = time.time(); by, sp = fit(t, t.rows)   # NAME, so the training
  g  = [nb(t, by, sp, r) for r in b.rows]     # table alone is enough
                                              # -- and the test rows
                                              # must not touch the bins
  dt = time.time()-t0
  want = [r[at] for r in b.rows]
  acc  = 100*sum(str(x) == str(w) for x, w in zip(g, want))/len(want)
  out  = [("nb", acc, *H.pdpf(want, g), dt)]
  if lg and os.path.exists(lg):
    x = [l.strip() for l in open(lg)]
    out += [("lgbm", 100*sum(a == str(w) for a, w in zip(x, want))
                     / len(want), *H.pdpf(want, x), 0)]
  for nm, a1, p1, p2, h, dt in out:
    print(f"{nm:<6}{a1:>6.0f}{p1:>7.2f}{p2:>7.2f}{h:>7.2f}{dt:>8.3f}")

def main(names):
  if "-t" in names:                       # one frozen split, not a sweep
    print(f"{'arm':<6}{'acc':>6}{'pd':>7}{'pf':>7}{'d2h':>7}{'secs':>8}")
    return tt(names[names.index("-t")+1], names[names.index("-T")+1],
              names[names.index("-L")+1] if "-L" in names else None)
  print(f"BINS={BINS or 'gauss'} M={M:g} K={K:g} SEEDS={SEEDS}\n"
        f"{'data':<12}{'k':>3}{'maj%':>6}{'train':>7}{'test':>6} |"
        f"{'nb':>7}{'lgbm':>7}{'d':>7}{'':>2} |{'s/nb':>7}"
        f"{'s/lgbm':>8}{'x':>6}")
  for dn in names:
    f = os.path.expanduser(f"~/gits/moot/classify/{dn}.csv")
    nbs, lgs, tn, tl = [], [], 0.0, 0.0
    t = E.Tbl(E.csv(f))                 # parse once, shuffle often
    t = E.clone(t, [r for r in t.rows if r[t.cols.klass.at] != "?"])
    for s in range(SEEDS):
      random.seed(s)
      rs = random.sample(t.rows, len(t.rows)); m = int(.75*len(rs))
      tr, te = E.clone(t, rs[:m]), E.clone(t, rs[m:])
      at = t.cols.klass.at
      t0 = time.time(); by, sp = fit(tr, tr.rows)
      nbs += [100*sum(str(nb(tr, by, sp, r)) == str(r[at])
                      for r in te.rows)/len(te.rows)]
      tn  += time.time()-t0
      if LGB:
        g, dt = lgbm(t, tr, te); tl += dt
        lgs += [100*sum(x == str(r[at]) for x, r in
                        zip(g, te.rows))/len(te.rows)]
      else: lgs += [0]
    cnt = {}
    for r in t.rows: cnt[r[at]] = cnt.get(r[at], 0) + 1
    d   = S.median(nbs) - S.median(lgs)
    sig = ("  " if SEEDS < 2 else                # cohen needs n>1
           " =" if E.same(nbs, lgs, .35) or d == 0 else
           " +" if d > 0 else " -")
    if RAW:
      print(f"#raw {dn} {BINS} {len(cnt)} "
            f"{100*max(cnt.values())/len(t.rows):.0f} "
            + ",".join(f"{x:g}" for x in nbs), flush=True)
      continue
    print(f"{dn:<12}{len(cnt):>3}{100*max(cnt.values())/len(t.rows):>6.0f}"
          f"{len(tr.rows):>7}{len(te.rows):>6} |{S.median(nbs):>7.0f}"
          f"{S.median(lgs):>7.0f}{d:>+7.0f}{sig} |{dot(tn/SEEDS):>7}"
          f"{dot(tl/SEEDS):>8}{tl/(tn+1e-9):>6.0f}", flush=True)

if __name__ == "__main__": main(sys.argv[1:])
