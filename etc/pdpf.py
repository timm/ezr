#!/usr/bin/env python3 -B
"""pdpf.py: the standard report, read in recall and false alarm.

Takes what `d2h.py RAW=1` writes -- three lines per dataset, `#pd`,
`#pf` and `#d2h`, each holding per-seed scores -- and prints a row
per dataset, then win/tie/loss and a median gap for every arm
against LightGBM, under each of the three.

Each argument is `name=file`.  The arm taken from a file is its
naive bayes column, so one file per setting; LightGBM is read from
whichever file has it (it is deterministic, so running it twice
would buy nothing).

  python3 etc/pdpf.py nb17=a.txt nb7=b.txt nb3=c.txt
"""
import os, sys, statistics as S
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "etc"))
import ezr as E
from compare import times              # pylint: disable=C0413

D, MS = .35, ("pd", "pf", "d2h")

def read(f):
  """measure -> dataset -> (k, maj, arm, arm, lgbm, secs).  SECS is
  what this arm spent per seed, and is missing from files written
  before it was recorded."""
  out = {}
  for l in open(f):
    if not l.startswith("#"): continue
    p = l.split()
    if p[0][1:] not in MS: continue
    out.setdefault(p[0][1:], {})[p[1]] = (
      int(p[2]), int(p[3]),
      *[None if c == "-" else [float(z) for z in c.split(",")]
        for c in p[4:7]],
      float(p[7]) if len(p) > 7 else None)
  return out

def sec(x):
  "Seconds, 2dp, no leading zero -- blank if nobody timed it."
  return "" if x is None else (f"{x:.2f}".lstrip("0") or "0")

def mark(a, b, less: bool):
  "A against B, with LESS saying whether small numbers win."
  d = S.median(a) - S.median(b)
  if E.same(a, b, D) or d == 0: return d, "="
  return d, ("+" if (d < 0) == less else "-")

def main(specs):
  arms, L, who, T = {}, {}, {}, {}
  for spec in specs:
    nm, f = spec.split("=", 1)
    got = read(f)
    arms[nm] = {m: {d: v[2] for d, v in got[m].items()} for m in MS}
    T[nm] = {d: v[5] for d, v in got["d2h"].items()}
    for d, v in got["d2h"].items():
      who[d] = (v[0], v[1])
      if v[4]: L.setdefault("d2h", {})[d] = v[4]
    for m in MS:
      for d, v in got[m].items():
        if v[4]: L.setdefault(m, {})[d] = v[4]
  ns = list(arms)
  ds = sorted(set.intersection(*[set(a["d2h"]) for a in arms.values()])
              & set(L["d2h"]),
              key=lambda d: mark(arms[ns[-1]]["d2h"][d],
                                 L["d2h"][d], True)[0])
  dot = lambda x: f"{x:.2f}".lstrip("0") or "0"
  LT, w = times(), 6                     # lightgbm's own seconds
  head = ns + ["lgbm"]
  print(f"{len(ds)} datasets, 20 seeds.  pd = recall, macro over the "
        f"classes.  pf = false alarm, ditto.\nd2h = how far from "
        f"(pd=1, pf=0).  pd higher is better; pf and d2h lower.  "
        f"s = seconds per seed.\n")
  print(f"{'':<22}" + "".join(f"{h:>{2+w*len(head)}}" for h in
        ("pd (higher)", "pf (lower)", "d2h (lower)", "secs")))
  print(f"{'data':<14}{'k':>3}{'maj%':>5}"
        + "".join(" |" + "".join(f"{n:>{w}}" for n in head)
                  for _ in range(4)))
  for d in ds:
    line = f"{d[:14]:<14}{who[d][0]:>3}{who[d][1]:>5}"
    for m in MS:
      line += " |" + "".join(f"{dot(S.median(arms[n][m][d])):>{w}}"
                             for n in ns)
      line += f"{dot(S.median(L[m][d])):>{w}}"
    line += " |" + "".join(f"{sec(T[n][d]):>{w}}" for n in ns)
    line += f"{sec(LT.get(d, {}).get('lgbm')):>{w}}"
    print(line)
  tot = [sum(T[n][d] or 0 for d in ds) for n in ns] + \
        [sum(LT.get(d, {}).get("lgbm") or 0 for d in ds)]
  print(f"{'TOTAL':<14}{'':>8}" + "".join(" |" + " "*(w*len(head))
        for _ in MS) + " |" + "".join(f"{t:>{w}.1f}" for t in tot))
  print(f"\n{'arm':<8}" + "".join(f"{h:>24}" for h in
        ("pd (higher better)", "pf (lower better)", "d2h (lower better)")))
  for n in ns:
    out = ""
    for m, less in (("pd", False), ("pf", True), ("d2h", True)):
      w = t = l = 0; gs = []
      for d in ds:
        g, s = mark(arms[n][m][d], L[m][d], less); gs += [g]
        w, t, l = w+(s == "+"), t+(s == "="), l+(s == "-")
      out += f"{f'{w}/{t}/{l} ({S.median(gs):+.2f})':>24}"
    print(f"{n:<8}{out}")
  print("\n(+/-/= by same(cliffs, ks, cohen d=.35), against LightGBM)")
  if int(os.environ.get("CSV", 0)):    # the same table, for a spreadsheet
    f = os.path.expanduser(os.environ.get("B", "~/tmp/b.csv"))
    with open(f, "w") as fp:
      print("data,k,maj," + ",".join(f"{m}_{n}" for m in MS
            for n in head) + "," + ",".join(f"s_{n}" for n in head),
            file=fp)
      for d in ds:
        print(f"{d},{who[d][0]},{who[d][1]},"
          + ",".join(f"{S.median((arms[n][m] if n in arms else L[m])[d]):.4f}"
                     for m in MS for n in head) + ","
          + ",".join(str(T[n][d] if n in T else
                         LT.get(d, {}).get("lgbm")) for n in head), file=fp)
    print(f"(also written to {f})")

if __name__ == "__main__": main(sys.argv[1:])
