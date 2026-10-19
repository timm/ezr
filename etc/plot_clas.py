#!/usr/bin/env python3 -B
"""plot_clas.py: an ezr forest against LightGBM, 51 sets.

One column per dataset, sorted by the gap, so the crossover is the
place to look.  Where ezr.same cannot separate the pair, both dots
go grey and the column is shaded: those are the sets this says
nothing about.  Higher is better here -- it is accuracy, not error.

  ./etc/plot_clas.py etc/clas51.tsv docs/ezr_clas.png
"""
import sys, statistics as S
sys.path.insert(0, "/Users/timm/gits/timm/ezr")
import ezr as E
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

EZR, LGB, GREY, D = "#1f6fb4", "#d1702f", "#9aa0a6", 0.35
ARM = "rf"                 # 20 trees, sqrt(#x) per split

def read(f, metric="acc"):
  d, ks, lab = {}, {}, {}
  for l in open(f):
    n, te, x, k, arm, secs, n512, mm, *v = l.rstrip().split("\t")
    if mm == metric: d[(n,arm)] = [float(z) for z in v]
    ks[n] = int(k)
    if arm == ARM: lab[n] = int(n512)
  m = S.median
  return sorted(((n, m(d[(n,ARM)]), m(d[(n,"lgbm")]), ks[n],
                  lab[n], E.same(d[(n,ARM)], d[(n,"lgbm")], d=D))
                 for n in ks), key=lambda z: z[1] - z[2])

def main(src, out, metric="acc"):
  rs = read(src, metric)
  xs = list(range(len(rs)))
  fig, ax = plt.subplots(figsize=(16, 6.4))
  for i, z in enumerate(rs):
    if z[5]: ax.axvspan(i-.5, i+.5, color="#ececec", lw=0, zorder=0)
  ax.plot(xs, [z[1] for z in rs], color=EZR, lw=1.8, zorder=2)
  ax.plot(xs, [z[2] for z in rs], color=LGB, lw=1.8, zorder=2)
  for j, c in ((1, EZR), (2, LGB)):
    ax.scatter(xs, [z[j] for z in rs], s=26, zorder=3, linewidth=.8,
               edgecolor="white",
               color=[GREY if z[5] else c for z in rs])
  ax.set_xticks(xs)
  ax.set_xticklabels([f"{z[0]}  ({z[3]})" for z in rs], rotation=60,
                     ha="right", fontsize=7.5)
  ax.set_ylim(0, 102); ax.set_xlim(-.8, len(rs)-.2)
  ax.set_ylabel("accuracy %, median of 20 seeds\n(higher is better)",
                fontsize=10)
  nt = sum(1 for z in rs if z[5])
  w  = sum(1 for z in rs if z[1] > z[2] and not z[5])
  ax.set_title("an ezr forest on 512 random labels vs "
               "LightGBM on the whole training half\n51 datasets of "
               "moot/classify, 20 seeds each; sorted by the gap.  "
               f"x labels carry the class count.", fontsize=12, pad=14)
  ax.grid(axis="y", color="#e3e3e3", lw=.8); ax.set_axisbelow(True)
  for s in ("top","right"): ax.spines[s].set_visible(False)
  ax.legend(handles=[
    Line2D([],[], color=EZR, lw=2, marker="o", ms=6,
           label="ezr forest: 20 trees, min(#train,512) labels,"
                 " sqrt(#x) columns per split"),
    Line2D([],[], color=LGB, lw=2, marker="o", ms=6,
           label="LightGBM, every training label"),
    Patch(facecolor="#ececec",
          label=f"grey = same(cliffs, ks, cohen d={D}): {nt} of"
                f" {len(rs)} cannot be told apart")],
    loc="lower right", frameon=False, fontsize=10)
  fig.tight_layout(); fig.savefig(out, dpi=220)
  print(f"-> {out}  ({len(rs)} sets, {nt} tied, {w} clear ezr wins)")

if __name__ == "__main__":
  main(*(sys.argv[1:] or ["etc/clas51.tsv", "docs/ezr_clas.png"]))
