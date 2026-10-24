#!/usr/bin/env python3 -B
"""compare.py: several arms at once, against LightGBM and each other.

Each argument is `name=file`, where the file holds the `#raw`
lines an arm printed.  LightGBM comes from `etc/lgbm60.tsv`.
Prints one row per dataset, then w/t/l and median for every arm
against LightGBM, then the arms against each other.

  python3 etc/compare.py nb=a.txt tan=b.txt dtan=c.txt
"""
import os, sys, statistics as S
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
import ezr as E

D   = .35
CSV = int(os.environ.get("CSV", 0))       # 1 = machine readable

def load(spec):
  "name=file -> dataset -> accuracies"
  name, f = spec.split("=", 1)
  out = {}
  for l in open(f):
    p = l.split()
    if p[0] == "#raw": out[p[1]] = [float(z) for z in p[-1].split(",")]
  return name, out

def lgbms():
  out = {}
  for l in open(os.path.join(HERE, "etc", "lgbm60.tsv")):
    dn, k, x, a = l.split("\t")
    out[dn] = (int(k), int(x), [float(z) for z in a.split(",")])
  return out

def times():
  """Seconds per seed, to train and test, from `etc/times60.txt` --
  the one timing run made serially, so the numbers are not each
  other's noise.  An arm with no timed twin prints blank."""
  out = {}
  for l in open(os.path.join(HERE, "etc", "times60.txt")):
    if "|" not in l: continue
    p = l.split("|")[-1].split("wide")[0].split()
    if len(p) != 3: continue
    try: t = dict(zip(("nb", "aode", "lgbm"), [float(z) for z in p]))
    except ValueError: continue
    if not t["aode"]: t["aode"] = t["nb"]   # too wide: it WAS naive bayes
    out[l.split()[0]] = t
  return out

def wtl(A, B, ds):
  "How often A beats B over the datasets DS, and by how much."
  w = t = l = 0; gaps = []
  for d in ds:
    a, b = A[d], B[d]
    g = S.median(a) - S.median(b); gaps += [g]
    if E.same(a, b, D) or g == 0: t += 1
    elif g > 0: w += 1
    else: l += 1
  return f"{w}/{t}/{l}", S.median(gaps)

def main(specs):
  L = lgbms()
  arms = dict(load(s) for s in specs)
  ds = sorted(set.intersection(*[set(v) for v in arms.values()]) & set(L))
  lg = {d: L[d][2] for d in ds}
  ns = list(arms)
  if not CSV:
    print(f"{len(ds)} datasets, 20 seeds, vs LightGBM "
          f"(+/-/= by same, cohen d={D})\n")
  T   = times()
  tn  = [n for n in ns if any(n in v for v in T.values())] + ["lgbm"]
  key = lambda d: S.median(arms[ns[-1]][d]) - S.median(lg[d])
  if CSV:
    print(",".join(["data", "k", "x"] + ns + ["lgbm"]
                   + [f"{n}-lgbm" for n in ns] + [f"{n}sig" for n in ns]
                   + [f"s/{n}" for n in tn]))
    for d in sorted(ds, key=key):
      a = [S.median(arms[n][d]) for n in ns]; l = S.median(lg[d])
      g = [z - l for z in a]
      sg = ["=" if E.same(arms[n][d], lg[d], D) or z == 0 else
            ("+" if z > 0 else "-") for n, z in zip(ns, g)]
      print(",".join([d, str(L[d][0]), str(L[d][1])]
                     + [f"{z:.1f}" for z in a + [l] + g] + sg
                     + [f"{T.get(d, {}).get(n, 0):.2f}" for n in tn]))
    return
  print(f"{'data':<18}{'k':>3}{'x':>5} |" + "".join(f"{n:>7}" for n in ns)
        + f"{'lgbm':>7} |" + "".join(f"{n[:5]+'-L':>8}" for n in ns)
        + " |" + "".join(f"{'s/'+n:>8}" for n in tn))
  for d in sorted(ds, key=key):
    row = f"{d:<18}{L[d][0]:>3}{L[d][1]:>5} |"
    row += "".join(f"{S.median(arms[n][d]):>7.0f}" for n in ns)
    row += f"{S.median(lg[d]):>7.0f} |"
    for n in ns:
      g = S.median(arms[n][d]) - S.median(lg[d])
      s = "=" if E.same(arms[n][d], lg[d], D) or g == 0 else (
          "+" if g > 0 else "-")
      row += f"{g:>+7.0f}{s}"
    row += " |" + "".join(f"{T.get(d, {}).get(n, 0):>8.2f}" for n in tn)
    print(row)
  print("\nagainst LightGBM")
  for n in ns:
    s, m = wtl(arms[n], lg, ds)
    t = sum(T.get(d, {}).get(n, 0) for d in ds)
    tl = sum(T.get(d, {}).get("lgbm", 0) for d in ds)
    print(f"  {n:<22}{s:>10}  median {m:+5.1f}"
          + (f"   {t:7.1f}s = lgbm/{tl/t:.1f}" if t else ""))
  print(f"  {'lgbm':<22}{'':>10}         "
        f"   {sum(T.get(d, {}).get('lgbm', 0) for d in ds):7.1f}s")
  print("\nagainst each other (row beats column)")
  print(" " * 24 + "".join(f"{n:>18}" for n in ns[1:]))
  for i, a in enumerate(ns[:-1]):
    line = f"  {a:<22}" + " " * (18*i)
    for b in ns[i+1:]:
      s, m = wtl(arms[a], arms[b], ds)
      line += f"{s + f' ({m:+.1f})':>18}"
    print(line)

if __name__ == "__main__": main(sys.argv[1:])
