#!/usr/bin/env python3 -B
"""d2h.py: naive bayes, AODE and LightGBM by distance to heaven.

Accuracy counts every row the same, so on a skewed table it says
"95%" about a model that only ever guesses the majority class.
Distance to heaven asks the other question: per class, how much of
it did you find (recall), and how often did you cry wolf (false
alarm)?

  d2h(class) = sqrt((1 - recall)^2 + falsealarm^2) / sqrt(2)

which is 0 for a perfect class and 1 for the exact opposite.  The
classes are averaged unweighted (sklearn calls this `macro`), so a
class holding 2% of the rows counts as loudly as one holding 60%.
The other averages are no use here: `micro` in a single-label
problem is just accuracy again, and `weighted` puts back the very
class-size bias this metric exists to remove.  LOWER IS BETTER.

  SEEDS=20 BINS=17 ABINS=5 python3 etc/d2h.py diabetes vowel ...
"""
# pylint: disable=no-member   # `type()` structs confuse pylint
import os, sys, time, random, statistics as S
from math import sqrt
sys.path.insert(0, os.path.dirname(os.path.dirname(
                   os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ezr as E
import nb as NB, aode as A                # pylint: disable=C0413

SEEDS = int(os.environ.get("SEEDS", 20))
BINS  = int(os.environ.get("BINS", 17))   # bins naive bayes reads at
ABINS = int(os.environ.get("ABINS", 5))   # bins AODE reads at
LGB   = int(os.environ.get("LGB", 1))     # 0 = reuse a cached run
RAW   = int(os.environ.get("RAW", 0))

def pdpf(want: list, got: list) -> tuple:
  """One class at a time against all the others, then the macro
  mean of each: pd (recall, how much of the class you found), pf
  (false alarm, how often you called it wrongly), and the distance
  from the (pd=1, pf=0) corner that both of them live in."""
  pds, pfs, hs = [], [], []
  for c in sorted({str(w) for w in want}):
    tp = fp = fn = tn = 0
    for w, g in zip(want, got):
      w, g = str(w) == c, str(g) == c
      tp, fp, fn, tn = tp+(w and g), fp+(g and not w), \
                       fn+(w and not g), tn+(not w and not g)
    r  = tp/(tp+fn) if tp+fn else 0
    fa = fp/(fp+tn) if fp+tn else 0
    pds += [r]; pfs += [fa]
    hs  += [sqrt((1-r)**2 + fa**2) / sqrt(2)]
  return S.mean(pds), S.mean(pfs), S.mean(hs)

def d2h(want: list, got: list) -> float:
  "Just the distance, for callers that want the one number."
  return pdpf(want, got)[2]

def main(names):
  if not RAW:
    print(f"BINS={BINS} ABINS={ABINS} SEEDS={SEEDS}   "
          f"d2h: 0 is heaven, LOWER IS BETTER\n"
          f"{'data':<16}{'k':>3}{'maj%':>6} |{'nb':>6}{'aode':>6}"
          f"{'lgbm':>6} |{'nb-L':>7}{'':>2}{'aod-L':>7}{'':>2}")
  for dn in names:
    f = os.path.expanduser(f"~/gits/moot/classify/{dn}.csv")
    h1, h2, h3 = [], [], []           # (pd, pf, d2h) per seed
    t = E.Tbl(E.csv(f))                 # parse once, shuffle often
    t = E.clone(t, [r for r in t.rows if r[t.cols.klass.at] != "?"])
    for s in range(SEEDS):
      random.seed(s)
      rs = random.sample(t.rows, len(t.rows)); m = int(.75*len(rs))
      tr, te = E.clone(t, rs[:m]), E.clone(t, rs[m:])
      at   = t.cols.klass.at
      want = [r[at] for r in te.rows]
      NB.BINS = BINS
      by, sp  = NB.fit(tr, tr.rows)
      nbs = [NB.nb(tr, by, sp, r) for r in te.rows]
      h1 += [pdpf(want, nbs)]
      NB.BINS = ABINS
      if len(t.cols.x) > A.AMAX: h2 += [h1[-1]]
      else:
        mod = A.fit(tr, tr.rows)
        h2 += [pdpf(want, [A.aode(tr, mod, r) or g
                           for g, r in zip(nbs, te.rows)])]
      NB.BINS = BINS
      h3 += [pdpf(want, NB.lgbm(t, tr, te)[0]) if LGB else None]
    cnt = {}
    for r in t.rows: cnt[r[at]] = cnt.get(r[at], 0) + 1
    if RAW:
      for nm, h in (("pd", 0), ("pf", 1), ("d2h", 2)):
        print(f"#{nm} {dn} {len(cnt)} "
              f"{100*max(cnt.values())/len(t.rows):.0f} "
              + " ".join("-" if a[0] is None else      # arm not run
                         ",".join(f"{x[h]:.4f}" for x in a)
                         for a in (h1, h2, h3)), flush=True)
      continue
    def mark(x, y):                       # lower is better, so flip
      d = S.median(x) - S.median(y)
      return (d, " =" if E.same(x, y, .35) or d == 0 else
              (" +" if d < 0 else " -"))
    h1, h2, h3 = ([x[2] if x else 0 for x in h] for h in (h1, h2, h3))
    d1, s1 = mark(h1, h3); d2, s2 = mark(h2, h3)
    print(f"{dn:<16}{len(cnt):>3}"
          f"{100*max(cnt.values())/len(t.rows):>6.0f} |"
          f"{S.median(h1):>6.2f}{S.median(h2):>6.2f}{S.median(h3):>6.2f} |"
          f"{d1:>+7.2f}{s1}{d2:>+7.2f}{s2}", flush=True)

if __name__ == "__main__": main(sys.argv[1:])
