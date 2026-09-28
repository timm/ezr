#!/usr/bin/env python3 -B
"""
how.py: one function per application of how.md, built on ezr.py

Options:

      -Eras=4          trends: number of time slices
      -Draws=20        spread, simulation: samples drawn
      -Stop=20         optimize: labelling budget

Demos: --all, or --<name> for any test_<name> below.
"""
# pylint: disable=invalid-name,missing-function-docstring
import sys, random
import ezr
from ezr import (the, csv, Tbl, clone, Sym, adds, mid, sd, size, xdist,
                 ydist, ymu, acquire, same, say, wins, cli, run)

_dist = ezr._dist
the.Eras, the.Draws = 4, 20
the._defaults.update(Eras=4, Draws=20)

#-- missing primitives ------------------------------------
# Section 6 of how.md: the cost. Here it is, paid.

def middles(tbl, ats=None):        # ezr.mids is x-only; this is not
  return {at: mid(c) for at, c in tbl.cols.items()
          if ats is None or at in ats}

def sample(col):                   # generate
  if type(col) is Sym:
    return random.choices(list(col), weights=col.values())[0]
  return random.gauss(col[1], sd(col))

def delta(a, b):                   # extrapolate; a earlier, b later
  if type(a) is Sym:
    u  = {**a, **b}
    pa = {v: a.get(v,0)/max(1,size(a)) for v in u}
    pb = {v: b.get(v,0)/max(1,size(b)) for v in u}
    p  = {v: max(0, 2*pb[v] - pa[v]) for v in u}
    n  = sum(p.values()) or 1
    return {v: c/n for v, c in p.items() if c > 0}
  n  = max(2, round(2*b[0] - a[0]))
  s  = max(0, 2*sd(b) - sd(a))
  return (n, 2*b[1] - a[1], s*s*(n-1))

def project(tbl, a, b):            # cosine rule; t=0 at a, t=1 at b
  c = xdist(tbl, a, b) + 1e-32
  return lambda r: (xdist(tbl,a,r)**2 + c*c - xdist(tbl,b,r)**2)/(2*c)

#-- one operator ------------------------------------------

def halve(tbl, rows=None, stop=None):   # cluster: poles, no y values
  stop = stop or the.Leaf
  def go(rows):
    if len(rows) <= stop: return [clone(tbl, rows)]
    a = max(rows, key=lambda r: xdist(tbl, r, rows[0]))
    b = max(rows, key=lambda r: xdist(tbl, r, a))
    rows = sorted(rows, key=project(tbl, a, b))
    n = len(rows) // 2
    return go(rows[:n]) + go(rows[n:])
  return go(list(tbl.rows if rows is None else rows))

#-- three ways to point a primitive at a cluster ----------

def relevant(tbl, row, cs):
  return min(cs, key=lambda c: xdist(tbl, row, middles(c, tbl.x)))

def DISTINGUISH(tbl, a, b, ats=None):   # (at, b's value there)
  ats = ats or tbl.x
  at  = max(ats, key=lambda at: _dist(tbl.cols[at],
                                      mid(a.cols[at]), mid(b.cols[at])))
  return at, mid(b.cols[at])

def impute(tbl, row, c, ats):
  return tuple(sample(c.cols[at]) if at in ats else v
               for at, v in enumerate(row))

def targets(tbl):
  return [tbl.klass] if tbl.klass is not None else list(tbl.y)

def blank(tbl): return tuple("?" for _ in tbl.names)

def eras(tbl, at, n=None):         # the order on rows section 6 wants
  n    = n or the.Eras
  rows = sorted((r for r in tbl.rows if r[at] != "?"), key=lambda r: r[at])
  k    = max(1, len(rows) // n)
  return [clone(tbl, rows[i*k:(i+1)*k]) for i in range(n)]

#-- the applications --------------------------------------

def SUMMARIZATION(tbl, c=None):
  return middles(c or tbl)

def CLASSIFICATION(tbl, row, cs):
  return mid(relevant(tbl, row, cs).cols[tbl.klass])

def REGRESSION(tbl, row, cs):
  return middles(relevant(tbl, row, cs), list(tbl.y))

def ANOMALY(tbl, row, cs):
  return xdist(tbl, row, middles(relevant(tbl, row, cs), tbl.x))

def RETRIEVAL(tbl, row, cs):
  return relevant(tbl, row, cs).rows

def SPREAD(tbl, row, cs, n=None):  # the unnamed row of the table
  c = relevant(tbl, row, cs)
  return {at: sorted(sample(c.cols[at]) for _ in range(n or the.Draws))
          for at in targets(tbl)}

def SYNTHESIS(tbl, c):
  return impute(tbl, blank(tbl), c, set(c.cols))

def REPAIR(tbl, row, cs):
  c = relevant(tbl, row, cs)
  return impute(tbl, row, c, {at for at in c.cols if row[at] == "?"})

def PLANNING(tbl, row, cs, can=None):     # minimal: one attribute
  here   = relevant(tbl, row, cs)
  better = min(cs, key=lambda c: ymu(tbl, c.rows))
  if better is here: return None
  at, v = DISTINGUISH(tbl, here, better, can)
  return (tbl.names[at], row[at], v)

def PLANNING_TOTAL(tbl, row, cs, can=None):   # total: every cell
  better = min(cs, key=lambda c: ymu(tbl, c.rows))
  return impute(tbl, row, better, set(can or tbl.x))

def MONITORING(tbl, row, cs, can=None):
  here  = relevant(tbl, row, cs)
  worse = max(cs, key=lambda c: ymu(tbl, c.rows))
  at, v = DISTINGUISH(tbl, here, worse, can)
  return (tbl.names[at], row[at], v)

def EXPLANATION(tbl, a, b):
  at, v = DISTINGUISH(tbl, a, b)
  return f"{tbl.names[at]} = {say(v)}"

def TRENDS(tbl, ers, row, stop=None):
  return [relevant(tbl, row, halve(e, stop=stop)) for e in ers]

def FORECAST(tbl, ers, row, stop=None):
  cs = TRENDS(tbl, ers, row, stop)
  return {at: delta(cs[-2].cols[at], cs[-1].cols[at]) for at in cs[-1].cols}

def ALERTS(tbl, ers, row, stop=None):
  cs    = TRENDS(tbl, ers, row, stop)
  steps = [xdist(tbl, middles(a, tbl.x), middles(b, tbl.x))
           for a, b in zip(cs, cs[1:])]
  if len(steps) < 3: return steps, False
  h = adds(steps[:-1])
  return steps, steps[-1] > h[1] + 2*sd(h)

def SIMULATION(tbl, cs, n=None):   # rows that never happened, scored
  out = []
  for _ in range(n or the.Draws):
    r = impute(tbl, blank(tbl), random.choice(cs), set(tbl.x))
    out += [(r, REGRESSION(tbl, r, cs))]
  return out

def OPTIMIZATION(tbl, budget=None):
  return acquire(tbl, budget or the.Stop)

def DISTINGUISHABILITY(xs, ys):
  return same(xs, ys)

def SETTLED(b4, now):              # the stopping rule
  return same(b4, now)

#-- demos -------------------------------------------------
# Every application, run once, on real data.

def _cars():
  t = Tbl(csv(the.File)); return t, halve(t, stop=16)

def test_summarize():
  "SUMMARIZATION: the usual values in a cluster"
  t, cs = _cars()
  c = min(cs, key=lambda c: ymu(t, c.rows))
  print("best cluster n=%d " % len(c.rows),
        {t.names[at]: say(v) for at, v in SUMMARIZATION(t, c).items()})

def test_predict():
  "CLASSIFICATION and REGRESSION: one act, two column types"
  t, cs = _cars()
  r = t.rows[0]
  print("regress ", {t.names[at]: say(v)
                     for at, v in REGRESSION(t, r, cs).items()})
  print("actual  ", {t.names[at]: r[at] for at in t.y})
  d = Tbl(csv(the.Klass)); dcs = halve(d, stop=16)
  print("classify", CLASSIFICATION(d, d.rows[0], dcs),
        "actual", d.rows[0][d.klass])

def test_anomaly():
  "ANOMALY DETECTION: prediction's discarded byproduct"
  t, cs = _cars()
  ds = sorted((ANOMALY(t, r, cs), i) for i, r in enumerate(t.rows))
  print(f"typical {say(ds[0][0])}  odd {say(ds[-1][0])}"
        f"  oddest row {t.rows[ds[-1][1]]}")

def test_retrieve():
  "RETRIEVAL: the rows, not the summary"
  t, cs = _cars()
  print("like", t.rows[0], "->")
  for r in RETRIEVAL(t, t.rows[0], cs)[:3]: print("   ", r)

def test_spread():
  "SPREAD: the hole in the table -- a distribution, not a point"
  t, cs = _cars()
  s = SPREAD(t, t.rows[0], cs, 40)
  for at, ys in s.items():
    print(f"{t.names[at]:>7} point {say(mid(relevant(t,t.rows[0],cs).cols[at]))}"
          f"  10th-90th {say(ys[4])} .. {say(ys[-5])}")

def test_synth():
  "SYNTHESIS and REPAIR: impute, aimed two ways"
  t, cs = _cars()
  c = min(cs, key=lambda c: ymu(t, c.rows))
  print("synth ", tuple(say(v) for v in SYNTHESIS(t, c)))
  holed = tuple("?" if at in (0, 1) else v
                for at, v in enumerate(t.rows[0]))
  print("holed ", holed)
  print("repair", tuple(say(v) for v in REPAIR(t, holed, cs)))

def test_advise():
  "EXPLANATION, PLANNING, MONITORING: one DISTINGUISH, three pairs"
  t, cs = _cars()
  best = min(cs, key=lambda c: ymu(t, c.rows))
  rest = max(cs, key=lambda c: ymu(t, c.rows))
  can  = [0, 1, 3]                      # Clndrs, Volume, Model
  print("explain", EXPLANATION(t, rest, best))
  print("plan   ", PLANNING(t, rest.rows[0], cs, can))
  print("monitor", MONITORING(t, best.rows[0], cs, can))
  print("total  ", tuple(say(v) for v in
                         PLANNING_TOTAL(t, rest.rows[0], cs, can)))

def test_trends():
  "TRENDS, FORECAST, ALERTS: one trajectory, three readings"
  t  = Tbl(csv(the.File))
  ers = eras(t, 3)                      # Model year is the order
  r   = t.rows[0]
  cs  = TRENDS(t, ers, r, stop=16)
  print("era mpg ", [say(mid(c.cols[7])) for c in cs])
  print("era lbs ", [say(mid(c.cols[5])) for c in cs])
  f = FORECAST(t, ers, r, stop=16)
  print("next mpg", say(mid(f[7])), " next lbs", say(mid(f[5])))
  print("next origin", say(f[4]))
  steps, odd = ALERTS(t, ers, r, stop=16)
  print("steps   ", [say(s) for s in steps], "alert:", odd)

def test_optimize():
  "OPTIMIZATION: a few lookups beat the whole table"
  t = Tbl(csv(the.File)); w = wins(t)
  the.Stop = 20
  got = OPTIMIZATION(t)
  print(f"{the.Stop} lookups of {len(t.rows)} rows -> win {round(w(got[0]))}")

def test_simulate():
  "SIMULATION: rows that never happened, scored without lookups"
  t, cs = _cars()
  for r, y in SIMULATION(t, cs, 3)[:3]:
    print(tuple(say(v) for v in r[:5]), "->",
          {t.names[at]: say(v) for at, v in y.items()})

def test_settled():
  "DISTINGUISHABILITY: the gate on every claim above"
  a = [random.gauss(10, 1) for _ in range(40)]
  b = [random.gauss(10, 1) for _ in range(40)]
  c = [random.gauss(11, 1) for _ in range(40)]
  print("same(a,b)", SETTLED(a, b), " same(a,c)", SETTLED(a, c))

def test_all():
  "Run every demo"
  bad = 0
  for k, f in list(globals().items()):
    if k[:5] == "test_" and f is not test_all:
      print(f"\n# {k[5:]}: {f.__doc__}")
      bad += run(f)
  sys.exit(bad)

def main(): cli(the, globals(), sys.argv[1:] or ["--all"])

if __name__ == "__main__": main()
