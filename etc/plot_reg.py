#!/usr/bin/env python3 -B
"""plot_reg.py: a regressor against LightGBM, one column per dataset.

The regression twin of `plot_pdpf.py`.  Error is MAE over
(mean - min) of the test y, so datasets of different scale sit on
one axis -- and that axis is log, because the suite spans three
orders of magnitude, from `mv` at .003 to `meta` at 3.7.

Sorted by the gap, so it reads left to right as "where the arm is
behind" into "where it is ahead".  A column is shaded where
`ezr.same` cannot separate the two over the 20 seeds.  LOWER IS
BETTER throughout.

  ./etc/plot_reg.py OUT.png tree=raw.txt
"""
import os, sys, statistics as S
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
import ezr as E
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

ARM, LGB, GREY, D = "#1f6fb4", "#d1702f", "#9aa0a6", .35

def read(f):
  rs = []
  for l in open(f):
    p = l.split()
    if p[0] != "#raw": continue
    a = [float(z) for z in p[5].split(",")]
    b = [float(z) for z in p[6].split(",")]
    rs += [(p[1], int(p[2]), a, b, E.same(a, b, D))]
  return sorted(rs, key=lambda z: S.median(z[3]) - S.median(z[2]))

def main(out, spec):
  nm, f = spec.split("=", 1)
  rs = read(f)
  xs = list(range(len(rs)))
  fig, ax = plt.subplots(figsize=(15, 6.4))
  for i, z in enumerate(rs):
    if z[4]: ax.axvspan(i-.5, i+.5, color="#ececec", lw=0, zorder=0)
  for j, (c, lab) in ((2, (ARM, nm)), (3, (LGB, "LightGBM"))):
    ys = [S.median(z[j]) for z in rs]
    ax.plot(xs, ys, color=c, lw=1.5, zorder=2, label=lab)
    ax.scatter(xs, ys, s=24, zorder=3, linewidth=.8, edgecolor="white",
               color=[(GREY if z[4] else c) for z in rs])
  ax.set_yscale("log")
  ax.set_xticks(xs)
  ax.set_xticklabels([f"{z[0]}  ({z[1]})" for z in rs], rotation=60,
                     ha="right", fontsize=7.5)
  ax.set_xlim(-.8, len(rs)-.2)
  ax.set_ylabel("error: MAE / (mean - min) of the test y\n"
                "(log; LOWER is better)", fontsize=10)
  w  = sum(1 for z in rs if not z[4] and S.median(z[2]) < S.median(z[3]))
  nt = sum(1 for z in rs if z[4])
  ax.set_title(f"{nm} on 256 random labels vs LightGBM on every "
               f"training row\n{len(rs)} moot/regression sets, 20 seeds; "
               f"sorted by the gap.  {nm} wins {w}, ties {nt}, "
               f"loses {len(rs)-w-nt}.  x labels carry the row count.",
               fontsize=12, pad=12)
  ax.grid(axis="y", color="#e8e8e8", lw=.8); ax.set_axisbelow(True)
  for s in ("top", "right"): ax.spines[s].set_visible(False)
  ax.legend(handles=[
    Line2D([], [], color=ARM, lw=2, marker="o", ms=6, label=nm),
    Line2D([], [], color=LGB, lw=2, marker="o", ms=6,
           label="LightGBM, every training row"),
    Patch(facecolor="#ececec",
          label=f"grey = same(cliffs, ks, cohen d={D}): {nt} of "
                f"{len(rs)} cannot be told apart")],
    loc="upper left", frameon=False, fontsize=9.5)
  fig.tight_layout(); fig.savefig(out, dpi=200)
  print(f"-> {out}")

if __name__ == "__main__": main(sys.argv[1], sys.argv[2])
