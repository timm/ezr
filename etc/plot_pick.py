#!/usr/bin/env python3 -B
"""plot_pick.py: how good is the best row on a model's shortlist?

Rank the TEST rows by what a model predicts, walk down that order,
and after x rows report the true percentile of the best row found
so far -- 0 means you are holding the genuinely best row.  x counts
rows, so the curves of a 100-row and an 8000-row test set average.

Only test halves of at least 100 rows are averaged, so every curve
is over the same 23 datasets at every x.

  ./etc/plot_pick.py etc/pick.tsv docs/ezr_pick.png
"""
import sys, statistics as S
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

X = [3, 6, 12, 24, 48, 100]      # ticks, and where the dots go

C = {"lgbm": ("#d1702f", "LightGBM, every training label"),
     "256":  ("#1f6fb4", "ezr tree, 256 random labels"),
     "50":   ("#7b53b5", "ezr tree, 50 random labels"),
     "rand": ("#9aa0a6", "no model: look in random order")}

def read(f, floor=100):
  d, keep = {}, set()
  for l in open(f):
    n, te, arm, secs, *v = l.split("\t")
    if int(te) >= floor:
      keep.add(n); d[(n,arm)] = [float(x) for x in v]
      d[(n,arm,"s")] = float(secs)
  return d, sorted(keep)

def main(src, out):
  d, ns = read(src)
  fig, ax = plt.subplots(figsize=(9, 5.8))
  for arm in ("rand", "50", "256", "lgbm"):
    col, lab = C[arm]
    ys = [S.mean(d[(n,arm)][x] for n in ns) for x in range(100)]
    ax.plot(range(1, 101), ys, color=col, lw=2.2, label=lab)
    ax.scatter(X, [ys[x-1] for x in X],
               s=26, color=col, zorder=3, edgecolor="white", lw=.8)
  ax.set_xscale("log")           # log x, so one panel does the work
  ax.set_xticks(X)                        # two panels used to do
  ax.set_xticklabels([str(x) for x in X])
  ax.set_yscale("log")           # log y too: nothing here is zero,
  T = [.05,.1,.2,.5,1,2,5,10,20,50]        # so nothing is clipped
  ax.set_yticks(T)
  ax.set_yticklabels([str(v).lstrip("0") if v < 1 else str(int(v))
                      for v in T])
  ax.minorticks_off()
  ax.set_xlim(1, 100); ax.set_ylim(.03, 60)
  ax.set_xlabel("rows examined, off the top of the ranking  (log)")
  ax.set_ylabel("true percentile of the BEST row found so far\n"
                "(log; 0 = you hold the genuinely best row)")
  ax.grid(color="#e9e9e9", lw=.8); ax.set_axisbelow(True)
  for sp in ("top","right"): ax.spines[sp].set_visible(False)
  ax.legend(frameon=False, fontsize=10)
  ax.set_title("If you used the model to pick, how good would your"
               " pick be?\n23 datasets of moot/regression with 100+"
               " test rows, 20 seeds each, mean", fontsize=12, pad=12)
  fig.tight_layout(); fig.savefig(out, dpi=220)
  print(f"-> {out}   ({len(ns)} datasets)")
  w = max(len(l) for _, l in C.values())
  print(f"\n{'':<{w}}" + "".join(f"{('x='+str(x)):>8}"
                                 for x in (1,2,3,5,10,20,50,100)))
  for arm in ("rand", "50", "256", "lgbm"):
    ys = [S.mean(d[(n,arm)][x-1] for n in ns)
          for x in (1,2,3,5,10,20,50,100)]
    print(f"{C[arm][1]:<{w}}" + "".join(f"{v:8.1f}" for v in ys))
  print(f"\n{'median fit seconds':<{w}}" + "".join(
    f"{S.median([d[(n,a,'s')] for n in ns]):8.3f}" for a in
    ("rand","50","256","lgbm")) + "   (rand/50/256/lgbm)")

if __name__ == "__main__":
  main(*(sys.argv[1:] or ["etc/pick.tsv", "docs/ezr_pick.png"]))
