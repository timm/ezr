#!/usr/bin/env python3 -B
"""plot_aode.py: AODE against naive bayes and LightGBM, 60 sets.

One column per dataset, sorted by the AODE-LightGBM gap, so the
crossover is the place to look.  Where ezr.same cannot separate
that pair, both dots go grey and the column is shaded: those are
the sets this says nothing about.  Naive bayes is drawn underneath
so the lift AODE buys is the distance between the two blue lines.
A hollow blue dot is a table too wide (x>40) for AODE, where it
fell back to naive bayes.  Higher is better -- accuracy, not error.

  ./etc/plot_aode.py            # etc/aode60.tsv -> docs/aode_vs_lgbm.png
"""
import os, sys, statistics as S
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
import ezr as E
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

AOD, NB, LGB, GREY, D = "#1f6fb4", "#7fb3d9", "#d1702f", "#9aa0a6", .35
SRC = os.path.join(HERE, "etc", "aode60.tsv")
OUT = os.path.join(HERE, "docs", "aode_vs_lgbm.png")

def read(src):
  "data, k, nb, aode, lgbm, tie?, too-wide?"
  rs = []
  for l in open(src):
    p = l.split()
    if p[0] != "#raw": continue
    a = [[float(z) for z in c.split(",")] for c in p[5:8]]
    m = [S.median(v) for v in a]
    rs += [(p[1], int(p[2]), m[0], m[1], m[2],
            E.same(a[1], a[2], D), int(p[4]))]
  return sorted(rs, key=lambda z: z[3] - z[4])

def main(src, out):
  rs = read(src)
  xs = list(range(len(rs)))
  fig, ax = plt.subplots(figsize=(16, 6.6))
  for i, z in enumerate(rs):
    if z[5]: ax.axvspan(i-.5, i+.5, color="#ececec", lw=0, zorder=0)
  ax.plot(xs, [z[2] for z in rs], color=NB,  lw=1.2, zorder=1, ls="--")
  ax.plot(xs, [z[3] for z in rs], color=AOD, lw=1.8, zorder=2)
  ax.plot(xs, [z[4] for z in rs], color=LGB, lw=1.8, zorder=2)
  ax.scatter(xs, [z[2] for z in rs], s=12, zorder=2, color=NB)
  for j, c in ((3, AOD), (4, LGB)):
    ax.scatter(xs, [z[j] for z in rs], s=26, zorder=3, linewidth=.8,
               edgecolor=["#777" if z[6] and j == 3 else "white"
                          for z in rs],
               color=[("white" if z[6] and j == 3 else
                       (GREY if z[5] else c)) for z in rs])
  ax.set_xticks(xs)
  ax.set_xticklabels([f"{z[0]}  ({z[1]})" for z in rs], rotation=60,
                     ha="right", fontsize=7.5)
  ax.set_ylim(0, 102); ax.set_xlim(-.8, len(rs)-.2)
  ax.set_ylabel("accuracy %, median of 20 seeds\n(higher is better)",
                fontsize=10)
  nt = sum(1 for z in rs if z[5])
  w  = sum(1 for z in rs if z[3] > z[4] and not z[5])
  ax.set_title("AODE vs LightGBM, both on the whole training set\n"
               "60 datasets of moot/classify, 20 seeds, BINS=17; "
               "sorted by the AODE-LightGBM gap.  "
               "x labels carry the class count.", fontsize=12, pad=14)
  ax.grid(axis="y", color="#e3e3e3", lw=.8); ax.set_axisbelow(True)
  for s in ("top", "right"): ax.spines[s].set_visible(False)
  ax.legend(handles=[
    Line2D([], [], color=AOD, lw=2, marker="o", ms=6,
           label="AODE: every column once as superparent, averaged"),
    Line2D([], [], color=NB, lw=1.2, ls="--", marker="o", ms=4,
           label="plain naive bayes (the same counts, independent)"),
    Line2D([], [], color=LGB, lw=2, marker="o", ms=6,
           label="LightGBM, 100 estimators"),
    Line2D([], [], color="none", marker="o", ms=6, mec="#777",
           mfc="white", label=f"hollow = x>40, AODE skipped "
                              f"({sum(z[6] for z in rs)})"),
    Patch(facecolor="#ececec",
          label=f"grey = same(cliffs, ks, cohen d={D}): {nt} of"
                f" {len(rs)} cannot be told apart")],
    loc="lower right", frameon=False, fontsize=9.5)
  fig.tight_layout(); fig.savefig(out, dpi=220)
  print(f"-> {out}  ({len(rs)} sets, {nt} tied, {w} clear AODE wins)")

if __name__ == "__main__": main(SRC, OUT)
