#!/usr/bin/env python3 -B
"""plot_pdpf.py: naive bayes and LightGBM, on recall and false alarm.

Three panels, one per measure, each drawing BOTH arms at their
real heights on a 0..1 axis -- so a gap is only as alarming as the
room it had to move in.  Each panel is still sorted by the gap, so
it reads left to right as "where this arm is behind" into "where
it is ahead".  A column is shaded where `ezr.same` cannot separate
the two over the 20 seeds.

pd is a recall, so higher is better; pf and d2h are costs, so for
them lower is better -- which is why each panel says which way is
up rather than relying on the reader to remember.

  ./etc/plot_pdpf.py OUT.png nb7=raw.txt lgbm=base.txt
"""
import os, sys, statistics as S
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "etc"))
import ezr as E
import pdpf as P                          # pylint: disable=C0413
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

UP, LGB, GREY, D = "#1f6fb4", "#d1702f", "#9aa0a6", .35

def main(out, arm, base):
  nm, f = arm.split("=", 1)
  A, L = P.read(f), P.read(base.split("=", 1)[1])
  fig, axs = plt.subplots(3, 1, figsize=(15, 12))
  for ax, (m, less, say) in zip(axs, (
      ("pd",  False, "pd: recall, macro over classes"),
      ("pf",  True,  "pf: false alarm, macro over classes"),
      ("d2h", True,  "d2h: distance from pd=1, pf=0"))):
    rs = []
    for d, v in A[m].items():
      if d not in L[m] or not L[m][d][4]: continue
      a, b = v[2], L[m][d][4]
      g = S.median(a) - S.median(b)
      rs += [(d, -g if less else g, E.same(a, b, D), v[0],
              S.median(a), S.median(b))]
    rs.sort(key=lambda z: z[1])
    xs = list(range(len(rs)))
    for i, z in enumerate(rs):
      if z[2]: ax.axvspan(i-.5, i+.5, color="#ececec", lw=0, zorder=0)
    for j, (c, lab) in ((4, (UP, nm)), (5, (LGB, "LightGBM"))):
      ys = [z[j] for z in rs]
      ax.plot(xs, ys, color=c, lw=1.4, zorder=2, label=lab)
      ax.scatter(xs, ys, s=22, zorder=3, linewidth=.8, edgecolor="white",
                 color=[(GREY if z[2] else c) for z in rs])
    ax.set_ylim(-.02, 1.02)
    ax.set_yticks([0, .25, .5, .75, 1])
    ax.legend(loc="upper left", frameon=False, fontsize=9)
    ax.set_xticks(xs)
    ax.set_xticklabels([f"{z[0]}  ({z[3]})" for z in rs], rotation=60,
                       ha="right", fontsize=6.5)
    ax.set_xlim(-.8, len(rs)-.2)
    ax.set_ylabel(f"{m}\n({'lower' if less else 'higher'} is better)",
                  fontsize=9)
    nt = sum(1 for z in rs if z[2])
    w  = sum(1 for z in rs if z[1] > 0 and not z[2])
    ax.set_title(f"{say}   --   {nm} beats LightGBM on {w}, "
                 f"ties {nt}, loses {len(rs)-w-nt} of {len(rs)}"
                 f"   (sorted by the gap)", fontsize=11, pad=8)
    ax.grid(axis="y", color="#e8e8e8", lw=.8); ax.set_axisbelow(True)
    for s in ("top", "right"): ax.spines[s].set_visible(False)
  fig.suptitle(f"{nm} against LightGBM, 60 moot/classify sets, 20 seeds."
               "  Grey column = same(cliffs, ks, cohen d=.35) cannot "
               "tell the two apart.\nx labels carry the class count.",
               fontsize=12)
  fig.tight_layout(rect=[0, 0, 1, .97]); fig.savefig(out, dpi=200)
  print(f"-> {out}")

if __name__ == "__main__": main(sys.argv[1], sys.argv[2], sys.argv[3])
