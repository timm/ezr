#!/usr/bin/env python3
"""Reproduce Table 5 of arXiv:2606.03640 (Can AI be Easy?).
Four treatments (ls/sa, restart on/off) x 20 MOOT benchmarks,
20 repeats each, budget=1000 oracle calls, scored by ezr's
wins() (Eq 1 of the paper) both with and without the 0.35*sd
clamp (reviewer M5). Protocol per section 5.2: shuffle rows,
50 rows -> surrogate oracle, search the rest. Emits plain and
LaTeX tables. Usage: python3 etc/table5.py  (needs $HOME/gits/moot)"""
import os, sys, random, statistics
from multiprocessing import Pool
sys.path.insert(0, os.path.dirname(os.path.dirname(
  os.path.abspath(__file__))))
from ezr import (Data, csv, clone, wins, disty, ls, sa,
                 oracleNearest, last, bestRanks)

MOOT  = os.path.expanduser("~/gits/moot/optimize/config")
FILES = ["SS-X", "SQL_AllMeasurements", "SS-U", "SS-M",
         "SS-N", "SS-P", "SS-G", "SS-F",
         "X264_AllMeasurements", "SS-S", "SS-D",
         "wc+wc-3d-c4-obj1", "SS-T", "Apache_AllMeasurements",
         "SS-H", "wc+sol-3d-c4-obj1", "SS-J",
         "wc+rs-3d-c4-obj1", "rs-6d-c3_obj1", "sol-6d-c2-obj1"]
TREATS = [("ls-r", ls, 0), ("ls+r", ls, 100),
          ("sa-r", sa, 0), ("sa+r", sa, 100)]

def wins_noclamp(data):
  "ezr.wins minus the 0.35*sd clamp (reviewer M5)"
  ys = sorted(disty(data, row) for row in data.rows)
  ten = len(ys)//10
  lo, med = ys[0], ys[5*ten]
  return lambda row: max(-100, min(100, int(
    100*(1 - (disty(data, row)-lo)/(med-lo + 1e-32)))))

def one(name):
  d0   = Data(csv(os.path.join(MOOT, name + ".csv")))
  win  = wins(d0)
  win0 = wins_noclamp(d0)
  out = {"file": name, "rows": len(d0.rows),
         "x": len(d0.cols.xs), "y": len(d0.cols.ys)}
  for t, fn, r in TREATS:
    scores, raw = [], []
    for rep in range(20):
      random.seed(rep + 1)
      rows = d0.rows[:]
      random.shuffle(rows)
      known = clone(d0, rows[:50])
      srch  = clone(d0, rows[50:])
      got = last(fn(srch, lambda row: oracleNearest(known, row),
                    restarts=r, budget=1000))
      scores.append(win(got[2]))
      raw.append(win0(got[2]))
    out[t] = (statistics.mean(scores), statistics.pstdev(scores))
    out[t + "0"] = (statistics.mean(raw), statistics.pstdev(raw))
    out[t + "_s"], out[t + "0_s"] = scores, raw
  for sfx in ("_s", "0_s"):
    out["wins" + sfx] = len(bestRanks(
      {t: out[t + sfx] for t, _, _ in TREATS}))
  print("done", name, flush=True)
  return out

if __name__ == "__main__":
  with Pool(8) as p:
    rs = p.map(one, FILES)
  rs.sort(key=lambda z: z["ls-r"][0])
  for tag, sfx in (("CLAMPED (as paper)", ""),
                   ("NO CLAMP (M5)", "0")):
    print("\n==", tag)
    hdr = "%-24s %9s %9s %9s %9s %6s %3s %2s"
    print(hdr % ("file", "ls-r", "ls+r", "sa-r", "sa+r",
                 "#rows", "#x", "#y"))
    for z in rs:
      print(hdr % ((z["file"],)
        + tuple("%3.0f (%2.0f)" % z[t + sfx]
                for t, _, _ in TREATS)
        + (z["rows"], z["x"], z["y"])))
    print(hdr % (("mean",) + tuple(
      "%3.0f" % statistics.mean(z[t + sfx][0] for z in rs)
      for t, _, _ in TREATS) + ("", "", "")))
  for tag, sfx in (("CLAMPED", ""), ("NO CLAMP", "0")):
    print("\n%% LATEX", tag)
    for z in rs:
      cells = " & ".join("%.0f (%.0f)" % z[t + sfx]
                         for t, _, _ in TREATS)
      print("%d & %s & %d & %d & %d & %s \\\\" % (
        z["wins" + sfx + "_s"], cells, z["rows"], z["x"],
        z["y"], z["file"].replace("_", r"\_")))
    print("  & " + " & ".join(
      "%.0f" % statistics.mean(z[t + sfx][0] for z in rs)
      for t, _, _ in TREATS) + r" & & & & mean \\")
