#!/usr/bin/env python3 -B
# vim: set et sw=2 ts=2 sts=2 cc=75 :
"""
cmp_bayes_lgbm.py: min.py's naive bayes vs LightGBM, on moot/classify.

Per data set: SHUFFLES shuffles; each trains both models on the same
first 75% and scores them on the same last 25%.  Accuracy as mean (sd),
* = statistically the same as the best (cliff's delta and Kolmogorov-
Smirnov, thresholds from gawk4ai/slides/clas.py), sorted by the gap.
Writes a bar chart beside this file.  Nothing here belongs in min.py.

Usage: ./cmp_bayes_lgbm.py [-a] [-c] [-n SHUFFLES] [-f FILES]
   -a   all of moot/classify, not the mid-range sample
   -c   redraw from the cached json, run nothing
   -n   shuffles per data set (default 20)
   -f   how many data sets (default 50)
"""
import os, sys, json, time, random, shutil, subprocess, warnings
from bisect import bisect_right
from statistics import mean, stdev

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
warnings.filterwarnings("ignore")
import min as m                             # Tbl, csv, clone, bins, nb
import numpy as np
from lightgbm import LGBMClassifier

MOOT  = os.path.expanduser("~/gits/moot/classify")
CACHE = f"{HERE}/cmp_bayes_lgbm.json"
SVG   = f"{HERE}/cmp_bayes_lgbm.svg"
TRAIN = .75
# bayes runs in its own interpreter: pypy if we have it, since
# LightGBM is a C extension that will not load there.
PYPY  = shutil.which("pypy3") or sys.executable
MID   = (200, 1500)        # "a few mid range data sets" unless -a

#-- stats, verbatim from gawk4ai/slides/clas.py ------------------
CLIFFS = .197

def cliffs(xs, ys):          # true if the effect size is small
  gt = sum(x > y for x in xs for y in ys)
  lt = sum(x < y for x in xs for y in ys)
  return abs(gt - lt) / (len(xs) * len(ys)) <= CLIFFS

def ks(xs, ys):              # kolmogorov-smirnov: "same" at 95%?
  xs, ys = sorted(xs), sorted(ys)
  n, k = len(xs), len(ys)
  cdf = lambda a, v: bisect_right(a, v) / len(a)
  d = max(abs(cdf(xs, v) - cdf(ys, v)) for v in xs + ys)
  return d <= 1.36 * ((n + k) / (n * k)) ** 0.5

def same(xs, ys): return cliffs(xs, ys) and ks(xs, ys)

#-- the two learners ---------------------------------------------
def bayes(file, n):                   # _bayes.py, under PYPY, all n
  out = subprocess.run([PYPY, f"{HERE}/_bayes.py", file, str(n),
                        str(TRAIN)], capture_output=True, text=True)
  if out.returncode: return None
  j = json.loads(out.stdout)          # it times only its own work,
  return j["acc"], j["secs"]          # so pypy start-up is not counted

def lgbm(t, tr, te, klass):           # same split, ordinal-coded x
  seen = [{} for _ in t.cols.all]     # one code book per column
  def code(row):
    out = []
    for c in t.cols.x:
      v = row.raw[c.at]
      if v == "?": out += [np.nan]
      elif type(v) is str:
        out += [seen[c.at].setdefault(v, len(seen[c.at]))]
      else: out += [v]
    return out
  X, y = [code(r) for r in tr], [klass(r) for r in tr]
  Xt, yt = [code(r) for r in te], [klass(r) for r in te]
  f = LGBMClassifier(verbose=-1, n_jobs=1).fit(np.array(X, float), y)
  return 100 * sum(a == b for a, b in
                   zip(f.predict(np.array(Xt, float)), yt)) / len(yt)

#-- one data set -------------------------------------------------
def runs(file, n):
  t = m.Tbl(m.csv(file))
  if type(t.cols.klass) is not m.SYM: return None   # a NUM !-column
  ks = {r.raw[t.cols.klass.at] for r in t.rows}      # is a regression
  if not 2 <= len(ks) or len(t.rows) < 20: return None
  klass = lambda row: str(row.raw[t.cols.klass.at])   # lgbm wants
  got = bayes(file, n)
  if not got: return None
  a, b, secs = got[0], [], [got[1], 0.0]
  for seed in range(n):
    rows = t.rows[:]
    random.Random(seed).shuffle(rows)     # the order _bayes.py used
    k = int(TRAIN * len(rows))
    tr, te = rows[:k], rows[k:]
    c = time.time(); b += [lgbm(t, tr, te, klass)]; secs[1] += time.time()-c
  return len(t.rows), a, b, secs

#-- figure, ported from gawk4ai/slides/small.py ------------------
INK, PICK, GRID = "#1559b3", "#cc7000", "#e6e8e9"
AXIS, MUTED, DARK = "#9aa0a6", "#5f6368", "#202124"
W, RH, BAR = 900, 12, 7        # width, row height, bar thickness
NX, GX, LX, AX = 252, 338, 432, 478    # rows, bayes, lgbm, axis columns

def bar(x, y, w, h, fill):            # 3px rounded on the data end only
  r = min(3, abs(w))
  d = (f"M{x},{y} h{w-r} a{r},{r} 0 0 1 {r},{r} v{h-2*r} "
       f"a{r},{r} 0 0 1 {-r},{r} h{-(w-r)} z") if w >= 0 else (
      f"M{x},{y} h{w+r} a{r},{r} 0 0 0 {-r},{r} v{h-2*r} "
      f"a{r},{r} 0 0 0 {r},{r} h{-(w+r)} z")
  return f'<path d="{d}" fill="{fill}"/>'

def txt(x, y, s, anchor="start", size=12, fill=DARK):
  return (f'<text x="{x:.0f}" y="{y:.0f}" text-anchor="{anchor}" '
          f'font-size="{size}" fill="{fill}">{s}</text>')

def thin(out, n=50):                  # the ends in full, middle sampled
  if len(out) <= n: return out
  mid, k = out[10:-10], n - 20
  step = (len(mid) - 1) / (k - 1)
  keep = sorted({round(i * step) for i in range(k)})
  return out[:10] + [mid[i] for i in keep] + out[-10:]

def chart(out, d, secs):
  """One diverging bar per file: bayes minus lgbm, sorted.  Blue =
  bayes ahead, orange = lgbm ahead.  Every row prints both means with
  sd and dots the winner, so identity is never colour alone."""
  all_n, out = len(out), thin(out)
  lo = min(min(r["gap"] for r in out), 0) - 1
  hi = max(max(r["gap"] for r in out), 0) + 1
  span, h = W - AX - 70, RH * (len(out) + 1) + 54
  sx = lambda v: AX + 30 + (v - lo) / (hi - lo) * span
  o = [f'<svg viewBox="0 0 {W} {h}" width="{W}" height="{h}" '
       f'xmlns="http://www.w3.org/2000/svg" role="img" '
       f'aria-label="accuracy of naive bayes versus LightGBM">',
       f'<rect width="{W}" height="{h}" fill="#ffffff"/>',   # or it is
       # transparent, which renders black in a dark-mode viewer
       txt(20, 16, "data", size=11, fill=MUTED),
       txt(NX, 16, "rows", "end", 11, MUTED),
       txt(GX, 16, "bayes", "end", 11, MUTED),
       txt(LX, 16, "lgbm", "end", 11, MUTED),
       txt(sx(0), 16, "delta", "middle", 11, MUTED)]
  for i, r in enumerate(out):
    y, win, sd = 26 + i * RH, r["win"], r["sd"]
    o += [txt(20, y + 8, r["name"][:26], size=11),
          txt(NX, y + 8, f'{r["rows"]}', "end", 11, MUTED),
          txt(GX, y + 8, f'{r["a"]:.0f} ({sd[0]:.0f})', "end", 11,
              INK if win[0] else MUTED),
          txt(LX, y + 8, f'{r["b"]:.0f} ({sd[1]:.0f})', "end", 11,
              PICK if win[1] else MUTED)]
    for on, x, hue in ((win[0], GX + 7, INK), (win[1], LX + 7, PICK)):
      if on: o += [f'<circle cx="{x}" cy="{y+4}" r="2.5" fill="{hue}"/>']
    g = r["gap"]
    o += [bar(sx(0), y, sx(g) - sx(0), BAR, INK if g > 0 else PICK),
          txt(sx(g) + (6 if g > 0 else -6), y + 8, f"{g:+.0f}",
              "start" if g > 0 else "end", 11, MUTED)]
  y = 26 + len(out) * RH
  o += [f'<line x1="{sx(0)}" y1="22" x2="{sx(0)}" y2="{y-3}" '
        f'stroke="{AXIS}" stroke-width="1"/>',
        f'<line x1="20" y1="{y}" x2="{W-20}" y2="{y}" stroke="{GRID}" '
        f'stroke-width="1"/>',
        txt(20, y + 15, f"mean, all {all_n}", size=11, fill=MUTED),
        txt(GX, y + 15, f"{d[0]:.0f}", "end", 11, MUTED),
        txt(LX, y + 15, f"{d[1]:.0f}", "end", 11, MUTED),
        txt(sx(0) + 6, y + 15, f"{d[0]-d[1]:+.0f}", size=11, fill=MUTED),
        txt(20, y + 30, "seconds", size=11, fill=MUTED),
        txt(GX, y + 30, f"{secs[0]:.0f}", "end", 11,
            INK if secs[0] <= secs[1] else MUTED),
        txt(LX, y + 30, f"{secs[1]:.0f}", "end", 11,
            PICK if secs[1] < secs[0] else MUTED),
        txt(sx(0) + 6, y + 30,
            f"{max(secs)/max(1e-9,min(secs)):.0f}x faster", size=11,
            fill=MUTED),
        "</svg>"]
  open(SVG, "w").write("\n".join(o) + "\n")
  png()

def png():                            # the chart uses six colours, so
  """a 16-colour palette is lossless to the eye and 5x smaller than
  rgb: 63k not 342k.  Needs rsvg-convert; Pillow is optional."""
  if not shutil.which("rsvg-convert"): return
  out = SVG[:-4] + ".png"
  subprocess.run(["rsvg-convert", "-w", "1800", SVG, "-o", out])
  try:
    from PIL import Image
    Image.open(out).convert("RGB").quantize(colors=16).save(
      out, optimize=True)
  except ImportError: pass

#-- main ---------------------------------------------------------
def ok(file):                         # a file we can actually classify
  t = m.Tbl(m.csv(file))              # (a NUM !-column is a regression)
  return (type(t.cols.klass) is m.SYM and len(t.rows) >= 20
          and len({r.raw[t.cols.klass.at] for r in t.rows}) >= 2)

def report(out, secs):
  out = sorted(out, key=lambda r: -r["gap"])
  print(f"{'data':<18}{'rows':>6}{'bayes':>12}{'lgbm':>12}{'delta':>8}")
  for r in out:
    f = lambda v, s, w: f"{v:.0f} ({s:.0f}){'*' if w else ' '}"
    print(f'{r["name"]:<18}{r["rows"]:>6}'
          f'{f(r["a"],r["sd"][0],r["win"][0]):>12}'
          f'{f(r["b"],r["sd"][1],r["win"][1]):>12}{r["gap"]:>+8.0f}')
  d = [mean([r["a"] for r in out]), mean([r["b"] for r in out])]
  print(f"{'mean, all '+str(len(out)):<18}{'':>6}{d[0]:>12.0f}"
        f"{d[1]:>12.0f}{d[0]-d[1]:>+8.0f}")
  print(f"{'seconds':<18}{'':>6}{secs[0]:>12.0f}{secs[1]:>12.0f}")
  chart(out, d, secs)
  print("->", SVG)

def main(files, n):
  out, secs = [], [0.0, 0.0]
  for i, f in enumerate(files):
    got = runs(f, n)
    if not got: continue
    rows, a, b, s = got
    best = a if mean(a) >= mean(b) else b
    out += [dict(name=os.path.basename(f)[:-4], rows=rows,
                 a=mean(a), b=mean(b), sd=[stdev(a), stdev(b)],
                 gap=mean(a) - mean(b),
                 win=[same(a, best), same(b, best)])]
    secs[0] += s[0]; secs[1] += s[1]
    print(f"{i+1:3}/{len(files)} {out[-1]['name']:<20}"
          f"{out[-1]['gap']:+5.0f}  {secs[0]:6.0f}s {secs[1]:6.0f}s",
          flush=True)
  json.dump(dict(out=out, secs=secs), open(CACHE, "w"))
  report(out, secs)

if __name__ == "__main__":
  arg = lambda f, d: (int(sys.argv[sys.argv.index(f) + 1])
                      if f in sys.argv else d)
  if "-c" in sys.argv:
    j = json.load(open(CACHE)); report(j["out"], j["secs"]); sys.exit()
  fs = sorted(f"{MOOT}/{f}" for f in os.listdir(MOOT) if f.endswith(".csv"))
  if "-a" not in sys.argv:
    fs = [f for f in fs if MID[0] <= sum(1 for _ in open(f)) <= MID[1]]
  k = arg("-f", 50)
  fs = [f for f in fs if ok(f)]         # drop them BEFORE we sample,
  fs = sorted(fs, key=lambda f: sum(1 for _ in open(f)))  # else -f lies
  if len(fs) > k:                       # k of them, evenly by size, so
    step = (len(fs) - 1) / (k - 1)      # the big sets are in the sample
    fs = [fs[round(i * step)] for i in range(k)]
  main(fs, arg("-n", 20))
