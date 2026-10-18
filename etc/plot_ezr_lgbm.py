#!/usr/bin/env python3 -B
"""plot_ezr_lgbm.py: ezr tree@256 against LightGBM-on-everything.

Two profiles across 48 datasets, sorted by the gap between them, so
the crossover is the place to look.  Where ezr.same cannot separate
the pair, both lines go grey and the column is shaded: those are
the datasets this experiment has nothing to say about.  `meta` is
clipped; LightGBM scores 3.67 there and would flatten the rest.

  ./etc/plot_ezr_lgbm.py etc/big50.tsv docs/ezr_vs_lgbm.png
"""
import sys, statistics as S
sys.path.insert(0, "/Users/timm/gits/timm/ezr")
import ezr as E
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

EZR, LGB, GREY = "#1f6fb4", "#d1702f", "#9aa0a6"
D, TOP = 0.35, 4.0         # cohen's d; and the top of the axis

def read(f):
  d, meta = {}, {}
  for l in open(f):
    n, r, te, x, y, k, *v = l.split("\t")
    d[(n,k)] = [float(z) for z in v]; meta[n] = int(r)
  m = S.median
  return sorted(((n, m(d[(n,"ezr")]), m(d[(n,"lgbm")]),
                  m(d[(n,"n")]) >= int(.8*meta[n]),
                  E.same(d[(n,"ezr")], d[(n,"lgbm")], d=D))
                 for n in meta), key=lambda z: z[2] - z[1])

def main(src, out):
  rs  = read(src)
  xs  = list(range(len(rs)))
  a   = [z[1] for z in rs]        # linear, and tall enough for meta,
  b   = [z[2] for z in rs]        # so nothing is clipped
  fig, ax = plt.subplots(figsize=(15, 6.4))
  for i, z in enumerate(rs):                  # shade the dead zone
    if z[4]: ax.axvspan(i-.5, i+.5, color="#ececec", lw=0, zorder=0)
  ax.plot(xs, a, color=EZR, lw=1.8, zorder=2)
  ax.plot(xs, b, color=LGB, lw=1.8, zorder=2)
  for ys, c in ((a, EZR), (b, LGB)):          # grey the tied points
    ax.scatter(xs, ys, s=26, zorder=3, linewidth=.8, edgecolor="white",
               color=[GREY if z[4] else c for z in rs])
  ax.set_xticks(xs)
  ax.set_xticklabels([z[0] for z in rs], rotation=60, ha="right",
                     fontsize=8)
  for t, z in zip(ax.get_xticklabels(), rs):
    if z[3]: t.set_color("#1a7f37")     # 256 WAS all its training data
  ax.set_ylim(0, TOP); ax.set_xlim(-.8, len(rs)-.2)
  ax.set_yticks([0,1,2,3,4])
  ax.set_ylabel("error:  MAE / (mean - min) of the test y\n(lower is"
                " better)", fontsize=10)
  ax.set_title("ezr regression tree on 256 random labels vs LightGBM "
               "on the whole training half\n48 datasets from "
               "moot/regression, 20 seeds each, median; sorted by the"
               " gap between them", fontsize=12, pad=14)
  ax.grid(axis="y", color="#e3e3e3", lw=.8); ax.set_axisbelow(True)
  for s in ("top","right"): ax.spines[s].set_visible(False)
  nt = sum(1 for z in rs if z[4])
  ax.legend(handles=[
    Line2D([],[], color=EZR, lw=2, marker="o", ms=6,
           label="ezr tree, 256 random labels"),
    Line2D([],[], color=LGB, lw=2, marker="o", ms=6,
           label="LightGBM, every training label"),
    Patch(facecolor="#ececec",
          label=f"grey = same(cliffs, ks, cohen d={D}): {nt} of"
                f" {len(rs)} cannot be told apart"),
    Line2D([],[], ls="", marker="s", color="#1a7f37", ms=7,
           label="green name = 256 WAS all of its training data"),
    Line2D([],[], ls="", marker="", label="y is linear, 0 to 4:"
           " every value shown, nothing clipped")],
    loc="upper left", frameon=False, fontsize=9)
  fig.tight_layout(); fig.savefig(out, dpi=220)
  print(f"-> {out}  ({nt} tied of {len(rs)})")

if __name__ == "__main__":
  main(*(sys.argv[1:] or ["etc/big50.tsv", "docs/ezr_vs_lgbm.png"]))
