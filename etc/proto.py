"""Per class, find two extremes, project everyone onto that line,
then take C rows spaced evenly along it.  1-NN against just those.
Controls: the same number of rows at random, and all 512."""
# pylint: disable=no-member   # `type()` structs confuse pylint
import os, sys, time, random, statistics as S
sys.path.insert(0, os.path.dirname(os.path.dirname(
                   os.path.abspath(__file__))))
import ezr as E
SEEDS = int(os.environ.get("SEEDS", 10))
CS    = (2, 4, 8, 16)

def spaced(tbl, rows, c):
  "C rows of ROWS, spread along its two most distant points."
  if len(rows) <= c: return rows
  a = max(rows, key=lambda r: E.xdist(tbl, r, rows[0]))
  b = max(rows, key=lambda r: E.xdist(tbl, r, a))
  d = E.xdist(tbl, a, b) + 1e-32
  ps = sorted(rows, key=lambda r: (E.xdist(tbl,r,a)**2 + d*d
                                   - E.xdist(tbl,r,b)**2)/(2*d))
  step = len(ps)/c
  return [ps[min(len(ps)-1, int(i*step))] for i in range(c)]

def protos(tbl, rows, k, c):
  "Group by class, then space C out of each group."
  by = {}
  for r in rows: by.setdefault(r[k], []).append(r)
  return [r for g in by.values() for r in spaced(tbl, g, c)]

print(f"{'data':<12}{'cls':>4}{'c':>4}{'N':>5} |{'spaced':>8}"
      f"{'random':>8}{'delta':>7}{'':>2}|{'full':>7}{'s/sp':>7}{'s/full':>8}{'x':>6}")
for dn in sys.argv[1:]:
  f  = os.path.expanduser(f"~/gits/moot/classify/{dn}.csv")
  sp = {c: [] for c in CS}; rd = {c: [] for c in CS}
  ns = {c: [] for c in CS}; ts = {c: 0.0 for c in CS}
  fu, nf, tf = [], 0, 0.0
  for s in range(SEEDS):
    random.seed(s)
    t  = E.Tbl(E.csv(f))
    t  = E.clone(t, [r for r in t.rows if r[t.cols.klass.at] != "?"])
    rs = random.sample(t.rows, len(t.rows)); m = int(.75*len(rs))
    full, te = E.clone(t, rs[:m]), E.clone(t, rs[m:])
    k  = t.cols.klass.at
    def sc(ref):
      t0 = time.time()
      a  = 100*sum(str(min(ref, key=lambda o: E.xdist(full,o,r))[k])
                   == str(r[k]) for r in te.rows)/len(te.rows)
      return a, time.time()-t0
    nf = min(512, len(full.rows))
    a, dt = sc(random.sample(full.rows, nf))
    fu += [a]; tf += dt
    for c in CS:
      t0 = time.time()
      P  = protos(full, full.rows, k, c)
      tsel  = time.time()-t0
      a, dt = sc(P); sp[c] += [a]; ns[c] += [len(P)]
      ts[c] += tsel + dt
      a, _  = sc(random.sample(full.rows, min(len(P), len(full.rows))))
      rd[c] += [a]
  nk = len({r[k] for r in t.rows})
  for c in CS:
    d  = S.median(sp[c]) - S.median(rd[c])
    sig= (" =" if E.same(sp[c],rd[c],.35) or abs(d)<1e-9
          else (" +" if d>0 else " -"))
    print(f"{dn:<12}{nk:>4}{c:>4}{S.median(ns[c]):>5.0f} |"
          f"{S.median(sp[c]):>8.1f}{S.median(rd[c]):>8.1f}{d:>7.1f}{sig}|"
          f"{S.median(fu):>7.1f}{ts[c]/SEEDS:>7.3f}"
          f"{tf/SEEDS:>8.3f}{tf/(ts[c]+1e-9):>6.1f}", flush=True)
