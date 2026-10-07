#!/usr/bin/env python3 -B
# vim: set et sw=2 ts=2 sts=2 cc=75 :
"""
ezr0_eg.py: rigs that grade ezr0.py.  Try ./ezr0_eg.py --h
(c) 2026 Tim Menzies <timm@ieee.org> MIT license.

Nothing here is part of the method.  Everything here calls
`wins`, which reads every label in the table -- a luxury the
learner never gets.

Options:
   -Repeats=20  how many seeds per rig
   -Worst=0     plan rig: rows to advise; 0 = the whole holdout
"""
# pylint: disable=bad-indentation,multiple-statements
# pylint: disable=invalid-name,wildcard-import,unused-wildcard-import
import random, statistics as st, sys
import ezr0
from ezr0 import *

the.Repeats, the.Worst = 20, 0

def _split(seed):
  "One seeded train/test split, and the model built from it."
  t = Tbl(csv(the.File))
  random.seed(seed); the.Seed = seed
  rows = random.sample(t.rows, len(t.rows))
  n    = len(rows)//2
  return t, rows[n:], model(t, rows[:n])

def _walk(t, m, r0, w):
  "Mutate R0 toward best, one column at a time.  Grade each step."
  now, out, w0 = r0[:], [], w(r0)
  for k, (_, at, v) in enumerate(gaps(t, m), 1):
    now[at] = v
    wit = min(m.lab.rows, key=lambda z: xdist(t, now, z))
    out += [o(k=k, win=w(wit), gain=w(wit)-w0,
              snapDx=xdist(t, now, wit),      # mutant -> its witness
              moveDx=xdist(t, r0, now),       # row0   -> mutant
              realDx=xdist(t, r0, wit))]      # row0   -> witness
  return out

def eg_h() -> None:
  "Show the options and the rigs."
  print(ezr0.__doc__, __doc__, "Rigs:",
        *[f"  --{k[3:]:<9} {f.__doc__}"
          for k,f in globals().items() if k[:3]=="eg_"], sep="\n")

def eg_holdout() -> None:
  "REPEATS holdouts, as wins.  100 = pool best, 0 = average row."
  ws = []
  for s in range(1, the.Repeats+1):
    t, _, _ = _split(s)
    ws += [wins(t)(holdout(t))]
  print("  ", sorted(round(v) for v in ws))
  print(f"   median {st.median(ws):.0f}  mean {sum(ws)/len(ws):.0f}")

def eg_plan() -> None:
  "One row advised: the gaps, then the walk, in wins."
  t, pool, m = _split(the.Seed)
  w  = wins(t)
  explain(t, m)
  r0 = max(pool, key=m.key)
  print(f"\nplan for a rest-side row (win {w(r0):.0f}):")
  print(f"{'win':>5}{'dx':>7}  plan (changes so far)")
  for s in plan(t, m, r0):
    print(f"{w(s.witness):5.0f}{s.dx:7.2f}  {' and '.join(s.steps)}")

def eg_stop() -> None:
  """Six ways to stop the walk, against two baselines.
  The trivial baseline is the whole point: it spends no new
  labels, it just names the best row already bought."""
  R = {k: ([],[]) for k in
       ("k=all", "gain/snapDx", "gain/moveDx", "gain/realDx",
        "best k (oracle)", "trivial: best label")}
  for s in range(1, the.Repeats+1):
    t, pool, m = _split(s)
    w, best = wins(t), m.lab.rows[0]
    for r0 in (pool if not the.Worst else
               sorted(pool, key=lambda z: -m.key(z))[:the.Worst]):
      ss = _walk(t, m, r0, w)
      pick = lambda f: max(ss, key=f)
      for name, f in (("k=all",           lambda s: s.k),
                      ("gain/snapDx",     lambda s: s.gain/(s.snapDx+1e-32)),
                      ("gain/moveDx",     lambda s: s.gain/(s.moveDx+1e-32)),
                      ("gain/realDx",     lambda s: s.gain/(s.realDx+1e-32)),
                      ("best k (oracle)", lambda s: s.win)):
        b = pick(f); R[name][0].append(b.k); R[name][1].append(b.win)
      R["trivial: best label"][0].append(
          sum(1 for c in t.x if r0[c.at] != best[c.at]))
      R["trivial: best label"][1].append(w(best))
  print(f"  {len(t.x)} x columns, {len(R['k=all'][0])} plans")
  print(f"  {'rule':<22}{'mean k':>8}{'mean win':>10}{'median win':>12}")
  for k,(ks,ws) in R.items():
    print(f"  {k:<22}{sum(ks)/len(ks):8.1f}{sum(ws)/len(ws):10.0f}"
          f"{st.median(ws):12.0f}")

def eg_cut() -> None:
  "How many columns survive -Cut, and does the cut cost wins?"
  for cut in (0, 10, 20, 40):
    the.Cut, ks, ws = cut, [], []
    for s in range(1, the.Repeats+1):
      t, pool, m = _split(s)
      w = wins(t); keep = worth(t, m); ks += [len(keep)]
      for r0 in sorted(pool, key=lambda z: -m.key(z))[:10]:
        now = r0[:]; hi = w(r0)
        for _, at, v in keep:
          now[at] = v
          hi = max(hi, w(min(m.lab.rows, key=lambda z: xdist(t,now,z))))
        ws += [hi]
    print(f"  Cut={cut:>2}%  columns kept {sum(ks)/len(ks):4.1f}"
          f"  best-k win {sum(ws)/len(ws):4.0f}")
  the.Cut = the._Cut

def eg_all() -> None:
  "Run every rig; exit code counts the crashes."
  bad = 0
  for k, f in list(globals().items()):
    if k[:3] == "eg_" and f is not eg_all:
      print(f"\n# {k[3:]}")
      try: f()
      except Exception as e: bad += 1; print("CRASH", e)
  sys.exit(bad)

if __name__ == "__main__":
  the._Cut = the.Cut
  _av = sys.argv[1:] or ["--h"]
  while _av:
    _s = _av.pop(0)
    if   _s[:2] == "--":
      random.seed(the.Seed); globals().get("eg_"+_s[2:], eg_h)()
    elif _s[1:] in the: the[_s[1:]] = atom(_av.pop(0))
    else: print(f"unknown arg: {_s}")
