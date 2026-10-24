#!/usr/bin/env python3 -B
"""plot_arms.py: any arms against LightGBM, one column per dataset.

Reads the `#raw` files that RAW=1 writes, one per arm, and draws
each as a line over the 60 datasets, sorted by the LAST arm's gap
to LightGBM -- so the crossover is the place to look.  Where
`ezr.same` cannot separate that arm from LightGBM the column is
shaded grey: those sets say nothing.  Higher is better.

  ./etc/plot_arms.py docs/out.png "nb=a.txt" "aode=b.txt" ...
"""
import os, sys, statistics as S
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
import ezr as E
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

LGB, GREY, D = "#d1702f", "#9aa0a6", .35
INK = ["#7fb3d9", "#1f6fb4", "#14543f", "#6a3d9a"]

def load(spec):
  name, f = spec.split("=", 1)
  out = {}
  for l in open(f):
    p = l.split()
    if p[0] == "#raw": out[p[1]] = [float(z) for z in p[-1].split(",")]
  return name, out

def lgbms():
  out = {}
  for l in open(os.path.join(HERE, "etc", "lgbm60.tsv")):
    dn, k, _, a = l.split("\t")
    out[dn] = (int(k), [float(z) for z in a.split(",")])
  return out

def main(out, specs):
  L, arms = lgbms(), dict(load(s) for s in specs)
  ns = list(arms)
  ds = sorted(set.intersection(*[set(v) for v in arms.values()]) & set(L))
  ds.sort(key=lambda d: S.median(arms[ns[-1]][d]) - S.median(L[d][1]))
  xs = list(range(len(ds)))
  tie = [E.same(arms[ns[-1]][d], L[d][1], D) for d in ds]
  fig, ax = plt.subplots(figsize=(16, 6.6))
  for i, z in enumerate(tie):
    if z: ax.axvspan(i-.5, i+.5, color="#ececec", lw=0, zorder=0)
  for j, n in enumerate(ns):
    ys = [S.median(arms[n][d]) for d in ds]
    last = j == len(ns)-1
    ax.plot(xs, ys, color=INK[j % len(INK)], lw=1.8 if last else 1.2,
            ls="-" if last else "--", zorder=2)
    ax.scatter(xs, ys, s=26 if last else 12, zorder=3, linewidth=.8,
               edgecolor="white" if last else "none",
               color=[(GREY if (t and last) else INK[j % len(INK)])
                      for t in tie])
  ys = [S.median(L[d][1]) for d in ds]
  ax.plot(xs, ys, color=LGB, lw=1.8, zorder=2)
  ax.scatter(xs, ys, s=26, zorder=3, linewidth=.8, edgecolor="white",
             color=[(GREY if t else LGB) for t in tie])
  ax.set_xticks(xs)
  ax.set_xticklabels([f"{d}  ({L[d][0]})" for d in ds], rotation=60,
                     ha="right", fontsize=7.5)
  ax.set_ylim(0, 102); ax.set_xlim(-.8, len(ds)-.2)
  ax.set_ylabel("accuracy %, median of 20 seeds\n(higher is better)",
                fontsize=10)
  nt = sum(tie)
  w  = sum(1 for i, d in enumerate(ds) if not tie[i] and
           S.median(arms[ns[-1]][d]) > S.median(L[d][1]))
  ax.set_title(f"{' vs '.join(ns)} vs LightGBM, all on the whole "
               f"training set\n{len(ds)} datasets of moot/classify, "
               f"20 seeds; sorted by the {ns[-1]}-LightGBM gap.  "
               "x labels carry the class count.", fontsize=12, pad=14)
  ax.grid(axis="y", color="#e3e3e3", lw=.8); ax.set_axisbelow(True)
  for s in ("top", "right"): ax.spines[s].set_visible(False)
  keys = [Line2D([], [], color=INK[j % len(INK)], marker="o",
                 lw=1.8 if j == len(ns)-1 else 1.2,
                 ls="-" if j == len(ns)-1 else "--",
                 ms=6 if j == len(ns)-1 else 4, label=n)
          for j, n in enumerate(ns)]
  ax.legend(handles=keys + [
    Line2D([], [], color=LGB, lw=2, marker="o", ms=6,
           label="LightGBM, 100 estimators"),
    Patch(facecolor="#ececec",
          label=f"grey = same(cliffs, ks, cohen d={D}): {nt} of"
                f" {len(ds)} cannot be told apart")],
    loc="lower right", frameon=False, fontsize=9.5)
  fig.tight_layout(); fig.savefig(out, dpi=220)
  print(f"-> {out}  ({len(ds)} sets, {nt} tied, {w} clear wins)")

if __name__ == "__main__": main(sys.argv[1], sys.argv[2:])
