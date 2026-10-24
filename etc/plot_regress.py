#!/usr/bin/env python3 -B
"""plot_regress.py: the two regression figures of rq.md's RQ4.

Fig A, the bake-off: six predictors over 59 moot/regression sets,
each drawn as its own sorted profile -- dataset i on one curve is
not dataset i on another, which is the point.  A curve that sits
above another is better everywhere, not just on average.

Fig B, ezr against LightGBM: 48 sets, error against error, so the
diagonal is the tie line.  Grey where `ezr.same` cannot separate
the pair.  The inset is where the cost went.

  ./etc/plot_regress.py            # writes both into docs/
"""
# pylint: disable=no-member   # `type()` structs confuse pylint
import os, sys, statistics as S
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
import ezr as E
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

EZR, LGB, GREY = "#1f6fb4", "#d1702f", "#9aa0a6"
D = .35
ARMS = dict(rmeans="#1f6fb4", wknn5="#d1702f", tree="#1a7f37",
            knn5="#8a5fc0", knn1="#c03a5b", proto=GREY)

def bakeoff(src):
  "Per arm: every dataset's rho, and how often it was best-or-tied."
  rho = {a: [] for a in ARMS}; win = {a: 0 for a in ARMS}
  for l in open(src):
    if l.startswith(("#", "ERR")): continue
    for cell in l.split()[:-1]:
      a, v = cell.split("=")
      win[a] += v.endswith("!")
      rho[a].append(float(v.rstrip("!")))
  return rho, win

def figA(src, out):
  rho, win = bakeoff(src)
  n = len(next(iter(rho.values())))
  fig, (ax, bx) = plt.subplots(1, 2, figsize=(13, 5.2),
                               gridspec_kw=dict(width_ratios=[2.1, 1]))
  for a, c in ARMS.items():
    ax.plot(range(1, n+1), sorted(rho[a], reverse=True), color=c,
            lw=2 if a in ("rmeans", "wknn5") else 1.3,
            label=f"{a}  (mean {S.mean(rho[a]):.2f})")
  ax.set_xlabel("datasets, each curve sorted on its own", fontsize=10)
  ax.set_ylabel("Spearman(guess, truth) on 100 held-out rows\n"
                "(higher is better)", fontsize=10)
  ax.set_xlim(1, n); ax.set_ylim(-.1, 1)
  ax.axhline(0, color="#cccccc", lw=.8)
  ax.legend(loc="lower left", frameon=False, fontsize=9)
  ax.grid(color="#e3e3e3", lw=.8); ax.set_axisbelow(True)

  o = sorted(ARMS, key=lambda a: win[a])
  bx.barh(range(len(o)), [win[a] for a in o],
          color=[ARMS[a] for a in o], height=.62)
  for i, a in enumerate(o):
    bx.text(win[a]+.8, i, str(win[a]), va="center", fontsize=9)
  bx.set_yticks(range(len(o))); bx.set_yticklabels(o, fontsize=10)
  bx.set_xlim(0, max(win.values())*1.18)
  bx.set_xlabel(f"datasets where this arm was best or tied, of {n}",
                fontsize=10)
  bx.grid(axis="x", color="#e3e3e3", lw=.8); bx.set_axisbelow(True)
  for s in ("top", "right"):
    ax.spines[s].set_visible(False); bx.spines[s].set_visible(False)
  fig.suptitle("Six predictors on 59 moot/regression sets: 256 random"
               " training labels, 100 test rows, 20 seeds\n"
               "best-or-tied by ezr.same (cliffs + ks) over the seeds",
               fontsize=12)
  fig.tight_layout(rect=(0, 0, 1, .93)); fig.savefig(out, dpi=220)
  print(f"-> {out}")

def arms(src):
  "Per dataset: ezr and lgbm error, their seconds, and the tie flag."
  d = {}
  for l in open(src):
    f = l.rstrip("\n").split("\t")
    d.setdefault(f[0], {}).setdefault(f[5], {})[f[6]] = \
      [float(x) for x in f[7:]]
  m = S.median
  return [(k, m(v["ezr-cpy"]["err"]), m(v["lgbm"]["err"]),
           E.same(v["ezr-cpy"]["err"], v["lgbm"]["err"], d=D),
           m(v["ezr-cpy"]["secs"]), m(v["ezr-pypy"]["secs"]),
           m(v["lgbm"]["secs"])) for k, v in sorted(d.items())]

def figB(src, out):
  rs = arms(src)
  fig, (ax, bx) = plt.subplots(1, 2, figsize=(12.5, 5.4),
                               gridspec_kw=dict(width_ratios=[1.5, 1]))
  lo = min(min(z[1] for z in rs), min(z[2] for z in rs)) * .8
  hi = max(max(z[1] for z in rs), max(z[2] for z in rs)) * 1.25
  ax.plot([lo, hi], [lo, hi], color="#bbbbbb", lw=1, zorder=1)
  hue = lambda z: GREY if z[3] else (EZR if z[1] < z[2] else LGB)
  ax.scatter([z[2] for z in rs], [z[1] for z in rs], s=38, zorder=3,
             linewidth=.8, edgecolor="white",
             color=[hue(z) for z in rs])
  ax.set_xscale("log"); ax.set_yscale("log")
  ax.set_xlim(lo, hi); ax.set_ylim(lo, hi)
  ax.set_xlabel("LightGBM, all 80% of the training rows", fontsize=10)
  ax.set_ylabel("ezr tree, 256 random labels", fontsize=10)
  ax.set_title("error:  MAE / (mean - min) of the test y,  lower is"
               " better", fontsize=10)
  nt = sum(z[3] for z in rs)
  nw = sum(1 for z in rs if not z[3] and z[1] < z[2])
  ax.text(.04, .95, "above the line: LightGBM wins", transform=ax.transAxes,
          fontsize=9, color="#555555", va="top")
  ax.legend(handles=[
    Line2D([], [], ls="", marker="o", color=EZR, ms=7,
           label=f"ezr wins: {nw}"),
    Line2D([], [], ls="", marker="o", color=LGB, ms=7,
           label=f"LightGBM wins: {len(rs)-nt-nw}"),
    Line2D([], [], ls="", marker="o", color=GREY, ms=7,
           label=f"same(cliffs, ks, cohen d={D}): {nt} of {len(rs)}")],
    loc="lower right", frameon=False, fontsize=9)
  ax.grid(which="both", color="#eeeeee", lw=.7); ax.set_axisbelow(True)

  lab = ("LightGBM\nCPython", "ezr\nCPython", "ezr\npypy3")
  val = [S.median([z[6] for z in rs]), S.median([z[4] for z in rs]),
         S.median([z[5] for z in rs])]
  bx.barh(range(3), val, color=[LGB, EZR, "#1a7f37"], height=.55)
  for i, v in enumerate(val):
    bx.text(v*1.12, i, f"{v:.3f}s", va="center", fontsize=10)
  bx.set_yticks(range(3)); bx.set_yticklabels(lab, fontsize=10)
  bx.set_xscale("log"); bx.set_xlim(val[1]*.5, val[0]*4)
  bx.set_xlabel("median seconds to train, one seed  (log)", fontsize=10)
  bx.set_title("LightGBM will not import on pypy at all", fontsize=10)
  bx.grid(axis="x", which="both", color="#eeeeee", lw=.7)
  bx.set_axisbelow(True)
  for s in ("top", "right"):
    ax.spines[s].set_visible(False); bx.spines[s].set_visible(False)
  fig.suptitle("ezr regression tree on 256 random labels vs LightGBM on"
               " all of an 80% training split\n48 moot/regression sets,"
               " 20 seeds, median", fontsize=12)
  fig.tight_layout(rect=(0, 0, 1, .9)); fig.savefig(out, dpi=220)
  print(f"-> {out}")

if __name__ == "__main__":
  figA(f"{HERE}/etc/learn_regress.txt", f"{HERE}/docs/rq_regress.png")
  figB(f"{HERE}/etc/arms.tsv", f"{HERE}/docs/rq_regress_lgbm.png")
