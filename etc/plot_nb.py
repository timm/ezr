#!/usr/bin/env python3 -B
"""plot_nb.py: naive bayes against LightGBM, 60 sets.

One column per dataset, sorted by the gap, so the crossover is the
place to look.  Where ezr.same cannot separate the pair, both dots
go grey and the column is shaded: those are the sets this says
nothing about.  Higher is better here -- it is accuracy, not error.

  ./etc/plot_nb.py etc/nb60b7.tsv docs/nb_vs_lgbm.png
"""
import os, sys
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

NB, LGB, GREY, D = "#1f6fb4", "#d1702f", "#9aa0a6", 0.35
BINS = 7

def read(f):
  "data, nb, lgbm, class count, and whether `same` called it a tie."
  rs = []
  for l in open(f):
    p = l.split("|")
    if len(p) < 3: continue
    d, a = p[0].split(), p[1].split()
    rs += [(d[0], float(a[0]), float(a[1]), int(d[1]), a[3] == "=")]
  return sorted(rs, key=lambda z: z[1] - z[2])

def main(src, out):
  rs = read(src)
  xs = list(range(len(rs)))
  fig, ax = plt.subplots(figsize=(16, 6.4))
  for i, z in enumerate(rs):
    if z[4]: ax.axvspan(i-.5, i+.5, color="#ececec", lw=0, zorder=0)
  ax.plot(xs, [z[1] for z in rs], color=NB, lw=1.8, zorder=2)
  ax.plot(xs, [z[2] for z in rs], color=LGB, lw=1.8, zorder=2)
  for j, c in ((1, NB), (2, LGB)):
    ax.scatter(xs, [z[j] for z in rs], s=26, zorder=3, linewidth=.8,
               edgecolor="white",
               color=[GREY if z[4] else c for z in rs])
  ax.set_xticks(xs)
  ax.set_xticklabels([f"{z[0]}  ({z[3]})" for z in rs], rotation=60,
                     ha="right", fontsize=7.5)
  ax.set_ylim(0, 102); ax.set_xlim(-.8, len(rs)-.2)
  ax.set_ylabel("accuracy %, median of 20 seeds\n(higher is better)",
                fontsize=10)
  nt = sum(1 for z in rs if z[4])
  w  = sum(1 for z in rs if z[1] > z[2] and not z[4])
  ax.set_title(f"naive bayes ({BINS} bins) vs LightGBM, both on the "
               "whole training set\n60 datasets of moot/classify, 20 "
               "seeds each; sorted by the gap.  "
               "x labels carry the class count.", fontsize=12, pad=14)
  ax.grid(axis="y", color="#e3e3e3", lw=.8); ax.set_axisbelow(True)
  for s in ("top", "right"): ax.spines[s].set_visible(False)
  ax.legend(handles=[
    Line2D([], [], color=NB, lw=2, marker="o", ms=6,
           label=f"naive bayes: {BINS} bins on the logistic norm,"
                 " m=2, k=1"),
    Line2D([], [], color=LGB, lw=2, marker="o", ms=6,
           label="LightGBM, 100 estimators, symbols as categories"),
    Patch(facecolor="#ececec",
          label=f"grey = same(cliffs, ks, cohen d={D}): {nt} of"
                f" {len(rs)} cannot be told apart")],
    loc="lower right", frameon=False, fontsize=10)
  fig.tight_layout(); fig.savefig(out, dpi=220)
  print(f"-> {out}  ({len(rs)} sets, {nt} tied, {w} clear nb wins)")

if __name__ == "__main__":
  main(*(sys.argv[1:] or [os.path.join(HERE, "etc", "nb60b7.tsv"),
                          os.path.join(HERE, "docs", "nb_vs_lgbm.png")]))
