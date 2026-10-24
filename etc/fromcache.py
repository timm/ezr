#!/usr/bin/env python3 -B
"""fromcache.py: score one arm off the frozen splits.

Reads the `~/tmp/ezr/<data>/<seed>.{tr,te}.csv` pairs that
`cache.py` wrote, fits whatever BINS says, and scores it beside the
LightGBM guesses cached next to them -- so LightGBM is never run
again, and two settings compared this way are compared on exactly
the same rows.

Writes the `#pd`, `#pf`, `#d2h` lines `pdpf.py` reads.

  BINS=0 python3 etc/fromcache.py diabetes vowel ...   # gaussian
  BINS=7 python3 etc/fromcache.py diabetes vowel ...   # binned
  ARM=tree CAP=50 python3 etc/fromcache.py diabetes ... # ezr tree

ARM=tree reads CAP labels at random (`grabs`) and grows one tree
over just those, so it sees a fraction of what the other arms get.
"""
# pylint: disable=no-member   # `type()` structs confuse pylint
import os, sys, time, random
from math import sqrt
sys.path.insert(0, os.path.dirname(os.path.dirname(
                   os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ezr as E
import nb as NB, d2h as H                 # pylint: disable=C0413

SEEDS = int(os.environ.get("SEEDS", 20))
ARM   = os.environ.get("ARM", "nb")
CAP   = int(os.environ.get("CAP", 256))   # labels the tree may have
OUT   = os.path.expanduser(os.environ.get("OUT", "~/tmp/ezr"))

def bayes(tr, te):
  "Naive bayes over every training row, binned by BINS."
  by, sp = NB.fit(tr, tr.rows)
  return [NB.nb(tr, by, sp, r) for r in te.rows]

def oney(t):
  """One y column, please.  moot's spambase has a column named
  `CHAR_FREQ_!`, so ezr sees two goals and the tree asks for the
  ydist of a symbol.  Demote everything but the klass."""
  if len(t.cols.y) < 2: return t
  k  = t.cols.klass.at
  ns = [s if i == k else s.rstrip("!+-")
        for i, s in enumerate(t.cols.names)]
  return E.Tbl([ns] + t.rows)

def tree(tr, te):
  "ezr's tree on CAP random labels, about sqrt(n) leaves."
  tr = oney(tr)
  n = min(CAP, len(tr.rows))
  E.the.Leaf = max(2, int(sqrt(n)))
  lab  = E.clone(tr, E.grabs(tr, n))
  root = E.fit(E.tree(lab, lab.rows), *E.target(lab))
  return [E.leaf(root, r).pred for r in te.rows]

def main(names):
  for dn in names:
    a, b, k, maj, secs = [], [], 0, 0, 0.0
    for s in range(SEEDS):
      random.seed(s)
      d  = f"{OUT}/{dn}/{s}"
      tr = E.Tbl(E.csv(f"{d}.tr.csv")); te = E.Tbl(E.csv(f"{d}.te.csv"))
      at = tr.cols.klass.at                 # types come from the header,
      want = [r[at] for r in te.rows]       # so TR alone sets the bins:
      t0 = time.time()                      # test rows must not be seen
      g  = dict(nb=bayes, tree=tree)[ARM](tr, te)
      secs += time.time()-t0
      a += [H.pdpf(want, g)]
      b += [H.pdpf(want, [l.strip() for l in open(f"{d}.lgbm")])]
      if not k:
        cnt, all_ = {}, tr.rows + te.rows
        for r in all_: cnt[r[at]] = cnt.get(r[at], 0) + 1
        k, maj = len(cnt), 100*max(cnt.values())/len(all_)
    for nm, i in (("pd", 0), ("pf", 1), ("d2h", 2)):
      print(f"#{nm} {dn} {k} {maj:.0f} "
            + " ".join(",".join(f"{x[i]:.4f}" for x in h)
                       for h in (a, a, b))
            + f" {secs/SEEDS:.4f}", flush=True)

if __name__ == "__main__": main(sys.argv[1:])
