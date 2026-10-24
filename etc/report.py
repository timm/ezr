#!/usr/bin/env python3 -B
"""report.py: the standard report for any arm, against LightGBM.

Reads `#raw <data> <k> <x> <flag> <accs>...` lines on stdin (what
`RAW=1` prints) and joins them against `etc/lgbm60.tsv`, which
holds LightGBM's per-seed accuracies.  LightGBM is deterministic
given a seed, so it is run once and reused -- which is what makes
trying many arms cheap.

  RAW=1 LGB=0 ... | python3 etc/report.py "name of the arm"
"""
import os, sys, statistics as S
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
import ezr as E

D = .35

def lgbms():
  "dataset -> (k, x, LightGBM's accuracies)"
  out = {}
  for l in open(os.path.join(HERE, "etc", "lgbm60.tsv")):
    dn, k, x, a = l.split("\t")
    out[dn] = (int(k), int(x), [float(z) for z in a.split(",")])
  return out

def mark(a, b):
  "a - b, and whether `same` can tell them apart."
  d = S.median(a) - S.median(b)
  return d, ("=" if E.same(a, b, D) or d == 0 else ("+" if d > 0 else "-"))

def main(name, lines):
  L, got = lgbms(), {}
  for l in lines:
    p = l.split()
    if p[0] != "#raw": continue
    got[p[1]] = [float(z) for z in p[-1].split(",")]
  rs = []
  for dn, a in got.items():
    k, x, lg = L[dn]
    d, s = mark(a, lg)
    rs += [(dn, k, x, S.median(a), S.median(lg), d, s)]
  rs.sort(key=lambda r: r[5])
  print(f"\n== {name}  ({len(rs)} datasets, 20 seeds, vs LightGBM)")
  print(f"{'data':<18}{'k':>3}{'x':>5} |{'arm':>6}{'lgbm':>6}{'d':>7}")
  for r in rs:
    print(f"{r[0]:<18}{r[1]:>3}{r[2]:>5} |{r[3]:>6.0f}{r[4]:>6.0f}"
          f"{r[5]:>+6.0f} {r[6]}")
  w = sum(1 for r in rs if r[6] == "+"); t = sum(1 for r in rs if r[6] == "=")
  print(f"\n{name}: w/t/l {w}/{t}/{len(rs)-w-t}   "
        f"median {S.median(r[5] for r in rs):+.1f}")

if __name__ == "__main__":
  main(sys.argv[1] if len(sys.argv) > 1 else "arm", sys.stdin)
