#!/usr/bin/env python3
"""
ezr_eg.py: demos for ezr.py.  Try  ./ezr_eg.py --h
(c) 2026 Tim Menzies <timm@ieee.org> MIT license
"""

# pylint: disable=bad-indentation,multiple-statements
# pylint: disable=invalid-name,broad-exception-caught
# pylint: disable=wildcard-import,unused-wildcard-import
# pylint: disable=too-many-locals,missing-function-docstring
# pylint: disable=protected-access

import os, sys, random # pylint: disable=C0410
import ezr
from ezr import *
sys.dontWriteBytecode = True

the.Eras, the.Draws, the.Restart = 4, 20, 30
the.Klass = "~/gits/moot/classify/diabetes.csv"
the._defaults.update(Eras=4, Draws=20, Restart=30,
                     Klass=the.Klass)

def eg_h() -> None:
  "Show the options and the demos."
  print(ezr.__doc__, "Demos:", *[f"  --{k[3:]:<9} {f.__doc__}"
        for k,f in globals().items() if k[:3]=="eg_"], sep="\n")

def eg_num() -> None:
  "Welford matches the textbook mean and sd."
  c = adds([2,4,4,4,5,5,7,9])
  assert c.n==8 and mid(c)==5 and abs(div(c)-2.138) < .01
  print(say(c))                      # also checks __repr__

def eg_sym() -> None:
  "Syms count; mid is the mode, div is entropy."
  c = adds("aabbbc", Sym())
  assert c.has["b"]==3 and mid(c)=="b" and abs(div(c)-1.459)<.01
  print(f"mode {mid(c)} ent {say(div(c))}")

def eg_tbl() -> None:
  "The header routes each column."
  t = Tbl([["Age","job!","SkipX","Weight-"],[2,"a",3,80]])
  assert [c.at for c in t.x]==[0] and [c.at for c in t.y]==[1,3]
  print(f"x {[c.at for c in t.x]} y {[c.at for c in t.y]}")

def eg_dist() -> None:
  "A row is nearest itself, and ydist orders the data."
  t  = Tbl(csv(the.File))
  r  = t.rows[0]
  assert xdist(t,r,r) == 0
  ys = sorted(ydist(t,r) for r in t.rows)
  print(f"ydist best {say(ys[0])} mid {say(ys[len(ys)//2])}"
        f" worst {say(ys[-1])}")

def eg_tree() -> None:
  "Acquire, then grow and show a tree."
  t   = Tbl(csv(the.File))
  lab = clone(t, acquire(t))
  show(lab, tree(lab, lab.rows))

def eg_same() -> None:
  "The stats tell noise from signal."
  x = [random.gauss(10,1) for _ in range(40)]
  y = [random.gauss(10,1) for _ in range(40)]
  z = [random.gauss(11,1) for _ in range(40)]
  assert same(x,y) and not same(x,z) and same(x,x)
  print(f"same {same(x,y)} differ {not same(x,z)}")

def eg_holdout() -> None:
  "Mean win over REPEATS holdouts."
  t = Tbl(csv(the.File)); w = wins(t)
  ws = sorted(round(w(holdout(t))) for _ in range(the.Repeats))
  print(
    f"{round(sum(ws)/len(ws)):>4} {os.path.basename(the.File)}")

def eg_vs() -> None:
  "Acquire versus random, same budget.  0 if the same."
  t = Tbl(csv(the.File)); w = wins(t)
  a = [w(holdout(t, acquire)) for _ in range(the.Repeats)]
  b = [w(holdout(t, grabs))   for _ in range(the.Repeats)]
  d = 0 if same(a,b) else round(sum(a)/len(a) - sum(b)/len(b))
  print(f"{round(sum(a)/len(a)):>4} {round(sum(b)/len(b)):>4}"
        f" {d:>4} {os.path.basename(the.File)}")

#-- optimize ------------------------------------------------
# de is differential evolution (storn+price 1997): build a
# candidate by interpolating between three population members
# (per x column, a + f*(b-c), applied with probability cr);
# keep the candidate if it beats the member it challenges.

def interpolate(col: COL, a: ATOM, b: ATOM, c: ATOM,
                f: float = 0.5) -> ATOM:
  "DE crossover term.  Syms, or unknowns, just pick one."
  if "has" in col or "?" in (a, b, c):
    return random.choice([a, b, c])
  return a + f*(b - c)

def de(tbl: TBL, score: Callable[[ROW], float],
       np: int = 20, cr: float = 0.9) -> ROW:
  "Differential evolution.  Lower SCOREs are better."
  pop = [r[:] for r in random.sample(tbl.rows, np)]
  es  = [score(r) for r in pop]
  h   = np
  while h < the.Stop:
    for i, s in enumerate(pop):
      if h >= the.Stop: break
      a, b, c = random.sample(pop, 3)
      sn   = s[:]
      keep = random.choice(tbl.x).at   # sn keeps >= 1 of s
      for col in tbl.x:
        if col.at != keep and random.random() < cr:
          sn[col.at] = interpolate(col, a[col.at],
                                   b[col.at], c[col.at])
      en = score(sn); h += 1
      if en < es[i]: pop[i], es[i] = sn, en
  return pop[es.index(min(es))]

def pick(col: COL, v: ATOM = None) -> ATOM:
  "Sample a plausible value, near V if V is known."
  if "has" in col:
    return random.choices(list(col.has),
                          weights=col.has.values())[0]
  mu = col.mu if v is None or v == "?" else v
  lo, hi = col.mu - 3*col.sd, col.mu + 3*col.sd
  new = mu + col.sd*2*(random.random() + random.random()
                       + random.random() - 1.5)
  return lo + (new - lo) % (hi - lo + 1e-32)

def oneplus1(tbl: TBL, mutate, accept, score,
             restart: int = 0) -> ROW:
  "1+1 evolution: mutate, maybe accept, remember the best."
  s, e, best, be = random.choice(tbl.rows), 1e32, None, 1e32
  h = imp = 0
  while h < the.Stop:
    for sn in mutate(s):
      h += 1
      en = score(sn)
      if accept(en, e, h, the.Stop): s, e = sn, en
      if en < be: best, be, imp = sn, en, h
      if restart and h - imp > restart:
        s, e = random.choice(tbl.rows), 1e32
      if h >= the.Stop: break
  return best

def ls(tbl: TBL, score, tries: int = 20) -> ROW:
  "Local search: nudge one column; keep only improvements."
  def mutate(s):
    col = random.choice(tbl.x)
    for _ in range(tries):
      s2 = s[:]; s2[col.at] = pick(col, s[col.at])
      yield s2
  return oneplus1(tbl, mutate,
                  lambda en, e, *_: en < e, score,
                  the.Restart)

def sa(tbl: TBL, score, m: float = 0.5) -> ROW:
  "Simulated annealing: accept worse, less as time runs out."
  def accept(en, e, h, b):
    return en < e or random.random() < exp(
      (e - en) / (1 - h/b + 1e-32))
  def mutate(s):
    s2 = s[:]
    for col in tbl.x:
      if random.random() < m:
        s2[col.at] = pick(col, s2[col.at])
    yield s2
  return oneplus1(tbl, mutate, accept, score)

def seek(t: TBL, searcher, picker: PICKER = grabs) -> ROW:
  """Train : validate : test, in thirds. SEARCHER breeds
  candidates from TRAIN; it scores them on the nearest row
  of VALIDATE's few labelled rows (PICKER spends Stop there,
  and nothing else is ever labelled); the winner is read off
  the untouched TEST.  (Standard ezr -- acquire, holdout --
  mashes train+validate into one pool: the rows it labels
  are the rows it searches.)"""
  rows  = random.sample(t.rows, len(t.rows))
  n     = len(rows) // 3
  train = rows[:n][:the.Few]
  valid = rows[n:2*n]
  test  = rows[2*n:]
  lab   = picker(clone(t, valid), the.Stop)
  def near(r: ROW, pool: ROWS) -> ROW:
    return min(pool, key=lambda z: xdist(t, r, z))
  best = searcher(clone(t, train),
                  lambda r: ydist(t, near(r, lab)))
  return near(best, test)

def eg_seek() -> None:
  "DE, SA, LS; scorer labelled by grabs or acquire."
  t = Tbl(csv(the.File)); w = wins(t)
  for searcher in [de, sa, ls]:
    for picker in [grabs, acquire]:
      ws = [w(seek(t, searcher, picker))
            for _ in range(the.Repeats)]
      print(f"{searcher.__name__:<3} {picker.__name__:<7}"
            f" win {round(sum(ws)/len(ws)):>4}")

#-- how: missing primitives ---------------------------------
# Section 6 of how.md: the cost. Here it is, paid.

def middles(tbl: TBL, ats=None) -> MIDS:
  "Mids of all columns (or just ATS), keyed by position."
  return {at: mid(c) for at, c in tbl.cols.items()
          if ats is None or at in ats}

def sample(col: COL) -> ATOM:
  "Generate: one plausible value from COL."
  if "has" in col:
    return random.choices(list(col.has),
                          weights=col.has.values())[0]
  return random.gauss(col.mu, col.sd)

def delta(a: COL, b: COL):
  "Extrapolate: A earlier, B later; guess the next era."
  if "has" in a:
    u  = {**a.has, **b.has}
    pa = {v: a.has.get(v,0)/max(1,a.n) for v in u}
    pb = {v: b.has.get(v,0)/max(1,b.n) for v in u}
    p  = {v: max(0, 2*pb[v] - pa[v]) for v in u}
    n  = sum(p.values()) or 1
    return {v: c/n for v, c in p.items() if c > 0}
  n = max(2, round(2*b.n - a.n))
  s = max(0, 2*b.sd - a.sd)
  return o(at=b.at, txt=b.txt, n=n, mu=2*b.mu - a.mu,
           m2=s*s*(n-1), sd=s)

def project(tbl: TBL, a: ROW, b: ROW):
  "Place rows on the line from pole A to pole B."
  c = xdist(tbl, a, b) + 1e-32
  return lambda r: (xdist(tbl,a,r)**2 + c*c
                    - xdist(tbl,b,r)**2) / (2*c)

def halve(tbl: TBL, rows=None, stop=None) -> list:
  "Cluster: recursive halving between poles; no y values."
  stop = stop or the.Leaf
  def go(rows):
    if len(rows) <= stop: return [clone(tbl, rows)]
    a = max(rows, key=lambda r: xdist(tbl, r, rows[0]))
    b = max(rows, key=lambda r: xdist(tbl, r, a))
    rows = sorted(rows, key=project(tbl, a, b))
    n = len(rows) // 2
    return go(rows[:n]) + go(rows[n:])
  return go(list(tbl.rows if rows is None else rows))

def xats(tbl: TBL) -> list:
  "Positions of the x columns."
  return [c.at for c in tbl.x]

def klass(tbl: TBL):
  "Position of the `!` column, or None."
  return next((c.at for c in tbl.y if c.txt[-1]=="!"), None)

def targets(tbl: TBL) -> list:
  "The columns predictions should talk about."
  k = klass(tbl)
  return [k] if k is not None else [c.at for c in tbl.y]

def ymu(tbl: TBL, rows: ROWS) -> float:
  "Mean ydist of ROWS."
  return sum(ydist(tbl, r) for r in rows) / len(rows)

def blank(tbl: TBL) -> ROW:
  return ["?" for _ in tbl.names]

def eras(tbl: TBL, at: int, n=None) -> list:
  "Split rows, ordered by column AT, into N equal slices."
  n    = n or the.Eras
  rows = sorted((r for r in tbl.rows if r[at] != "?"),
                key=lambda r: r[at])
  k    = max(1, len(rows) // n)
  return [clone(tbl, rows[i*k:(i+1)*k]) for i in range(n)]

#-- how: three ways to aim a primitive at a cluster ---------

def relevant(tbl: TBL, row: ROW, cs: list) -> TBL:
  "The cluster whose x-centroid is nearest ROW."
  return min(cs, key=lambda c: xdist(tbl, row, middles(c)))

def DISTINGUISH(tbl: TBL, a: TBL, b: TBL, ats=None):
  "The x column that best tells cluster A from B."
  ats = ats or xats(tbl)
  at  = max(ats, key=lambda at: gap(tbl.cols[at],
                                    mid(a.cols[at]),
                                    mid(b.cols[at])))
  return at, mid(b.cols[at])

def impute(row: ROW, c: TBL, ats) -> ROW:
  "Write cluster C's expectations into ROW at ATS."
  return [sample(c.cols[at]) if at in ats else v
          for at, v in enumerate(row)]

#-- how: the applications -----------------------------------

def SUMMARIZATION(tbl, c=None):
  return middles(c or tbl)

def CLASSIFICATION(tbl, row, cs):
  return mid(relevant(tbl, row, cs).cols[klass(tbl)])

def REGRESSION(tbl, row, cs):
  return middles(relevant(tbl, row, cs),
                 [c.at for c in tbl.y])

def ANOMALY(tbl, row, cs):
  return xdist(tbl, row, middles(relevant(tbl, row, cs)))

def RETRIEVAL(tbl, row, cs):
  return relevant(tbl, row, cs).rows

def SPREAD(tbl, row, cs, n=None): # table's unnamed row
  c = relevant(tbl, row, cs)
  return {at: sorted(sample(c.cols[at])
                     for _ in range(n or the.Draws))
          for at in targets(tbl)}

def SYNTHESIS(tbl, c):
  return impute(blank(tbl), c, set(c.cols))

def REPAIR(tbl, row, cs):
  c = relevant(tbl, row, cs)
  return impute(row, c,
                {at for at in c.cols if row[at] == "?"})

def PLANNING(tbl, row, cs, can=None):  # minimal: one column
  here   = relevant(tbl, row, cs)
  better = min(cs, key=lambda c: ymu(tbl, c.rows))
  if better is here: return None
  at, v = DISTINGUISH(tbl, here, better, can)
  return (tbl.names[at], row[at], v)

def PLANNING_TOTAL(tbl, row, cs, can=None): # total: all cells
  better = min(cs, key=lambda c: ymu(tbl, c.rows))
  return impute(row, better, set(can or xats(tbl)))

def MONITORING(tbl, row, cs, can=None):
  here  = relevant(tbl, row, cs)
  worse = max(cs, key=lambda c: ymu(tbl, c.rows))
  at, v = DISTINGUISH(tbl, here, worse, can)
  return (tbl.names[at], row[at], v)

def EXPLANATION(tbl, a, b):
  at, v = DISTINGUISH(tbl, a, b)
  return f"{tbl.names[at]} = {say(v)}"

def TRENDS(tbl, ers, row, stop=None):
  return [relevant(tbl, row, halve(e, stop=stop))
          for e in ers]

def FORECAST(tbl, ers, row, stop=None):
  cs = TRENDS(tbl, ers, row, stop)
  return {at: delta(cs[-2].cols[at], cs[-1].cols[at])
          for at in cs[-1].cols}

def ALERTS(tbl, ers, row, stop=None):
  cs    = TRENDS(tbl, ers, row, stop)
  steps = [xdist(tbl, middles(a), middles(b))
           for a, b in zip(cs, cs[1:])]
  if len(steps) < 3: return steps, False
  h = adds(steps[:-1])
  return steps, steps[-1] > h.mu + 2*h.sd

def SIMULATION(tbl, cs, n=None):   # unseen rows, scored
  out = []
  for _ in range(n or the.Draws):
    r = impute(blank(tbl), random.choice(cs),
               set(xats(tbl)))
    out += [(r, REGRESSION(tbl, r, cs))]
  return out

def OPTIMIZATION(tbl, budget=None):     # demoed by eg_vs
  return acquire(tbl, budget or the.Stop)

def DISTINGUISHABILITY(xs, ys):         # demoed by eg_same
  return same(xs, ys)

#-- how: demos ----------------------------------------------

def _cars():
  t = Tbl(csv(the.File)); return t, halve(t, stop=16)

def eg_summarize() -> None:
  "SUMMARIZATION: the usual values in a cluster."
  t, cs = _cars()
  c = min(cs, key=lambda c: ymu(t, c.rows))
  print(f"best cluster n={len(c.rows)}",
        {t.names[at]: say(v)
         for at, v in SUMMARIZATION(t, c).items()})

def eg_predict() -> None:
  "CLASSIFICATION and REGRESSION: one act, two col types."
  t, cs = _cars()
  r = t.rows[0]
  print("regress ", {t.names[at]: say(v) for at, v in
                     REGRESSION(t, r, cs).items()})
  print("actual  ", {t.names[c.at]: r[c.at] for c in t.y})
  d   = Tbl(csv(the.Klass))
  dcs = halve(d, stop=16)
  print("classify", CLASSIFICATION(d, d.rows[0], dcs),
        "actual", d.rows[0][klass(d)])

def eg_anomaly() -> None:
  "ANOMALY DETECTION: prediction's discarded byproduct."
  t, cs = _cars()
  ds = sorted((ANOMALY(t, r, cs), i)
              for i, r in enumerate(t.rows))
  print(f"typical {say(ds[0][0])}  odd {say(ds[-1][0])}"
        f"  oddest {t.rows[ds[-1][1]]}")

def eg_retrieve() -> None:
  "RETRIEVAL: the rows, not the summary."
  t, cs = _cars()
  print("like", t.rows[0], "->")
  for r in RETRIEVAL(t, t.rows[0], cs)[:3]:
    print("   ", r)

def eg_spread() -> None:
  "SPREAD: a distribution, not a point."
  t, cs = _cars()
  r = t.rows[0]
  c = relevant(t, r, cs)
  for at, ys in SPREAD(t, r, cs, 40).items():
    print(f"{t.names[at]:>7} point {say(mid(c.cols[at]))}"
          f"  10th-90th {say(ys[4])} .. {say(ys[-5])}")

def eg_synth() -> None:
  "SYNTHESIS and REPAIR: impute, aimed two ways."
  t, cs = _cars()
  c = min(cs, key=lambda c: ymu(t, c.rows))
  print("synth ", [say(v) for v in SYNTHESIS(t, c)])
  holed = ["?" if at in (0, 1) else v
           for at, v in enumerate(t.rows[0])]
  print("holed ", holed)
  print("repair", [say(v) for v in REPAIR(t, holed, cs)])

def eg_advise() -> None:
  "EXPLANATION, PLANNING, MONITORING: one DISTINGUISH."
  t, cs = _cars()
  best = min(cs, key=lambda c: ymu(t, c.rows))
  rest = max(cs, key=lambda c: ymu(t, c.rows))
  can  = [0, 1, 3]              # Clndrs, Volume, Model
  print("explain", EXPLANATION(t, rest, best))
  print("plan   ", PLANNING(t, rest.rows[0], cs, can))
  print("monitor", MONITORING(t, best.rows[0], cs, can))
  print("total  ", [say(v) for v in
                    PLANNING_TOTAL(t, rest.rows[0], cs, can)])

def eg_trends() -> None:
  "TRENDS, FORECAST, ALERTS: one trajectory, three reads."
  t   = Tbl(csv(the.File))
  ers = eras(t, 3)              # Model year is the order
  r   = t.rows[0]
  cs  = TRENDS(t, ers, r, stop=16)
  print("era mpg ", [say(mid(c.cols[7])) for c in cs])
  print("era lbs ", [say(mid(c.cols[5])) for c in cs])
  f = FORECAST(t, ers, r, stop=16)
  print("next mpg", say(mid(f[7])),
        " next lbs", say(mid(f[5])))
  print("next origin", say(f[4]))
  steps, odd = ALERTS(t, ers, r, stop=16)
  print("steps   ", [say(s) for s in steps], "alert:", odd)

def eg_simulate() -> None:
  "SIMULATION: rows that never happened, scored."
  t, cs = _cars()
  for r, y in SIMULATION(t, cs, 3):
    print([say(v) for v in r[:5]], "->",
          {t.names[at]: say(v) for at, v in y.items()})

def eg_all() -> None:
  "Run every demo; exit code counts the crashes."
  sys.exit(sum(print(f"\n# {k[3:]}") or run(f)
                for k,f in list(globals().items())
                if k[:3]=="eg_" and f is not eg_all))

if __name__ == "__main__":
  main(sys.argv[1:] or ["--h"], globals())
