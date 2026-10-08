#!/usr/bin/env python3 -B
# vim: set et sw=2 ts=2 sts=2 cc=75 :
"""
ezr1.py: ezr0.py with binned rows.  Each Row keeps its `raw` cells
plus `bins`: every x value as a 0..1 bin (width 1/Bins) or, for a
symbol, the symbol as a string.  Bins are set once, from the whole
table, so nothing past `discretize` needs to know NUM from SYM: a
float is a bin, anything else is a symbol.  Ys stay raw.

Explain and plan score (column, bin) ranges by b^2/(b+r), where b, r
are the shares of best and rest rows in that bin.  Plans jump a row,
one bin width at a time, toward each column's top range.

Options:
   -Bins=5      bins per numeric column
   -Cut=10      plan: skip ranges under this % of the top score
   -Push=1      1 = take the jump when no single bin step helps
   -Kmax=0      most columns a plan may change; 0 = no cap
   -Earn=0      keep the shortest prefix within Earn% of the best gain
   -Enough=10   stop once the y gap left is under this % of the start
   -Stop=50     rows we may label, all up
   -Check=5     of that budget, saved for the unseen rows
   -Judge=64    rig: rows held out for the judge, per seed
   -Test=100    rig: holdout rows planned, per seed
   -Repeats=20  rig: seeds
   -Seed=1      random number seed
   -File=~/gits/moot/optimize/misc/auto93.csv

Usage: ./ezr1.py [--explain] [-Option value]...
"""
import os, random, re, sys
from math import exp, log, sqrt

class o(dict): # dicts with dot. Easier to use than SimpleNamespace.
  __getattr__, __setattr__ = dict.__getitem__, dict.__setitem__

def atom(s): # '22' -> 22. '3.1' -> 3.1. 'True' -> True. 'x' -> 'x'.
  for fn in (int, float):
    try: return fn(s)
    except ValueError: pass
  s = s.strip()
  return {"True": True, "False": False}.get(s, s)

def csv(file): # rows of FILE, one at a time; -sig drops any BOM
  with open(os.path.expanduser(file), encoding="utf-8-sig") as f:
    for ln in f:
      if ln.strip(): yield [atom(s) for s in ln.split(",")]

the = o(**{k: atom(v) for k, v in re.findall(r"-(\w+)=(\S+)", __doc__)})

#-- columns, rows ----------------------------------------------
def Col(txt=" ", at=0): # uppercase name = NUM, else SYM
  return Num(txt, at) if txt[0].isupper() else Sym(txt, at)

class Num: # +- marks a goal; 0 = minimise, 1 = maximise
  __slots__ = ("at", "txt", "n", "mu", "m2", "sd", "goal")
  def __init__(i, txt=" ", at=0):
    i.at,i.txt,i.n,i.mu,i.m2,i.sd = at,txt,0,0,0,0; i.goal = txt[-1]!="-"

class Sym: # the class is what tells a SYM from a NUM
  __slots__ = ("at", "txt", "n", "has")
  def __init__(i, txt=" ", at=0): i.at,i.txt,i.n,i.has = at,txt,0,{}

class Row: # raw cells, and (after `discretize`) their bins
  __slots__ = ("raw", "bins")
  def __init__(i, raw): i.raw, i.bins = raw, None

def add(col, v): # show V to COL
  if v != "?":
    col.n += 1
    if type(col) is Sym: col.has[v] = col.has.get(v, 0) + 1
    else:
      d = v - col.mu                          # Welford
      col.mu += d / col.n
      col.m2 += d * (v - col.mu)
      col.sd  = 0 if col.n < 2 else (col.m2 / (col.n - 1))**.5

def norm(col, v): # to 0..1, by the logistic curve
  z = max(-3, min(3, (v - col.mu) / (1e-32 + col.sd)))
  return 1 / (1 + exp(-1.7 * z))

def bin1(col, v): # the one place that asks NUM or SYM
  if col is None or v == "?": return v      # skipped column, unknown
  if type(col) is Sym: return str(v)
  return min(the.Bins - 1, int(the.Bins * norm(col, v))) / the.Bins

#-- tables -----------------------------------------------------
def Tbl(src): # header names the columns: X skip, +-! goal
  src = iter(src)
  tbl = Cols(o(rows=[], cols={}, x=[], y=[], names=next(src)))
  for raw in src: addRow(tbl, Row(raw))
  return discretize(tbl)

def Cols(tbl): # create column roles
  for at, s in enumerate(tbl.names):
    if s[-1] == "X": continue             # skip me entirely
    (tbl.y if s[-1] in "+-!" else tbl.x).append(
      tbl.cols.setdefault(at, Col(s, at)))
  return tbl

def addRow(tbl, row): # keep ROW, and show its raw cells to my columns
  tbl.rows += [row]
  for at, col in tbl.cols.items(): add(col, row.raw[at])
  return row

def discretize(tbl): # bins, from this table's stats, once
  for r in tbl.rows:
    r.bins = [bin1(tbl.cols.get(at), v) for at, v in enumerate(r.raw)]
  return tbl

def clone(tbl, rows=None): # an empty copy of TBL, plus ROWS (bins kept)
  out = Cols(o(rows=[], cols={}, x=[], y=[], names=tbl.names))
  for r in rows or []: addRow(out, r)
  return out

#-- distance ---------------------------------------------------
def dist(vs, n): return sqrt(sum(v*v for v in vs) / n)

def ydist(tbl, row): # how far ROW's goals are from the best they could be
  return dist((abs(norm(c, row.raw[c.at]) - c.goal) for c in tbl.y),
              len(tbl.y))

def gap(a, b): # two bins: floats are numbers, the rest symbols
  if a == "?" or b == "?": return 1
  return abs(a - b) if type(a) is float is type(b) else a != b

def xdist(tbl, b1, b2): # how far apart two bin lists are
  return dist((gap(b1[c.at], b2[c.at]) for c in tbl.x), len(tbl.x))

def wins(tbl): # grader: 100 at the pool's best row, 0 at an average one
  ys = sorted(ydist(tbl, r) for r in tbl.rows)
  lo, avg = ys[0], sum(ys) / len(ys)
  return lambda row: max(-100, min(100,
                     100 * (1 - (ydist(tbl,row)-lo) / (avg-lo+1e-32))))

#-- model: best, rest, and their ranges ------------------------
def ranges(tbl, best, rest): # (column, bin) ranges, by b^2/(b+r)
  out = []
  for c in tbl.x:
    nb, nr = {}, {}
    for rows, n in ((best, nb), (rest, nr)):
      for r in rows:
        if (v := r.bins[c.at]) != "?": n[v] = n.get(v, 0) + 1
    for v in sorted(nb, key=str):      # bins best never visits score 0
      b, r = nb[v] / len(best), nr.get(v, 0) / len(rest)
      out += [o(score=b*b/(b+r), at=c.at, v=v)]
  return sorted(out, key=lambda z: -z.score)

def tops(rs): # each column's top range, strongest first, minus weak
  seen, out = set(), []
  for z in rs:
    if z.at not in seen: seen.add(z.at); out += [z]
  return [z for z in out if z.score >= the.Cut/100 * out[0].score]

def model(tbl, rows): # label a budget at random, split best from rest
  lab = clone(tbl, rows[:the.Stop - the.Check])
  lab.rows.sort(key=lambda r: ydist(lab, r))
  k   = int(sqrt(len(lab.rows)))           # sqrt best, rest rest
  rs  = ranges(tbl, lab.rows[:k], lab.rows[k:])
  return o(lab=lab, best=lab.rows[:k], rest=lab.rows[k:],
           ranges=rs, tops=tops(rs))

#-- explain ----------------------------------------------------
def say(v): # a bin, two wide: -- - . + ++ (Bins=5), else its index
  if type(v) is not float: return str(v)
  i = round(v * the.Bins)
  return ("--", "-", ".", "+", "++")[i] if the.Bins == 5 else str(i)

def explain(tbl, m): # per column, b^2/(b+r) of each bin; top first
  bins = [i / the.Bins for i in range(the.Bins)]
  print(" ".join(f"{say(b):>2}" for b in bins), " top  attribute")
  for z in m.tops:
    c, s = tbl.cols[z.at], {r.v: r.score for r in m.ranges
                            if r.at == z.at}
    if type(z.v) is float:
      strip = " ".join(f"{min(99, int(100*s.get(b, 0))) or '':>2}"
                       for b in bins)
    else:
      strip = " ".join(f"{'':>2}" for _ in bins)
    print(strip, f"{say(z.v):>4}  {c.txt}"
          + ("" if type(z.v) is float else f"  ({100*z.score:.0f})"))

#-- plan -------------------------------------------------------
def near(tbl, m, bins): # nearest labelled row (exact g2 sums: ties go first)
  return min(m.lab.rows,
             key=lambda z: sum(g2(bins[c.at], z.bins[c.at]) for c in tbl.x))

def g2(a, b): # squared gap, in bin widths: exact ints, so sums can update
  if a == "?" or b == "?": return the.Bins ** 2
  if type(a) is float is type(b): return round((a - b) * the.Bins) ** 2
  return the.Bins ** 2 * (a != b)

def steps(a, v): # bins from A to V, one bin width at a time
  if type(a) is not float or type(v) is not float: return [v]
  n = round((v - a) * the.Bins); s = 1 if n > 0 else -1
  return [round(a * the.Bins + s*k) / the.Bins for k in range(1, abs(n)+1)]

def plan1(tbl, m, r0): # least change to labelled R0, most y per x
  y   = lambda r: ydist(m.lab, r)
  ylo = y(m.lab.rows[0])
  L   = m.lab.rows                  # ss[j]: now to L[j], summed g2s;
  now = r0.bins[:]                  # a one-column move updates it in
  ss  = [sum(g2(now[c.at], z.bins[c.at]) for c in tbl.x) for z in L]
  best = lambda s2: L[min(range(len(L)), key=s2.__getitem__)]
  def peek(at, b): # ss, and nearest label, if now[at] became B
    s2 = [s - g2(now[at], z.bins[at]) + g2(b, z.bins[at])
          for s, z in zip(ss, L)]
    return s2, best(s2)
  w = best(ss); y0 = y(w)
  out, seen = [], [(0, now[:], w)]
  for z in m.tops:
    if the.Kmax and len(out) >= the.Kmax: break        # change budget
    if now[z.at] == z.v: continue
    top = None
    for b in steps(now[z.at], z.v):      # smallest jump wins ties: dx
      new = now[:]; new[z.at] = b
      s2, w2 = peek(z.at, b)
      dy, dx = y(w) - y(w2), xdist(tbl, now, new)
      if dy > 0 and (top is None or dy/dx > top[0]):
        top = (dy/dx, new, w2, s2)
    if top is None:                       # no single step helps
      if not the.Push: continue
      new = now[:]; new[z.at] = z.v; top = (0, new, *peek(z.at, z.v)[::-1])
    _, now, w, ss = top                                     # lock it
    out += [o(at=z.at, was=r0.bins[z.at], to=now[z.at])]
    seen += [(y0 - y(w), now, w)]
    if y(w) - ylo <= the.Enough/100 * (y0 - ylo): break   # near enough
  hi = max(dy for dy, *_ in seen)           # shortest prefix that earns
  i  = next(j for j, (dy, *_) in enumerate(seen)       # near the most
            if dy >= (1 - the.Earn/100) * hi) if hi > 0 else 0
  return o(changes=out[:i], bins=seen[i][1], witness=seen[i][2])

def apply(bins, changes): # bins move by deltas; symbols get set
  new, top = bins[:], (the.Bins - 1) / the.Bins
  for c in changes:
    a = new[c.at]
    if all(type(v) is float for v in (a, c.was, c.to)):
      new[c.at] = max(0, min(top, round((a + c.to - c.was)*the.Bins)
                                  / the.Bins))
    else: new[c.at] = c.to
  return new

#-- rig: same protocol, same judge as ezr0_cmp.py ---------------
def unbin(col, b): # a bin's centre, back in raw units
  p = (round(b * the.Bins) + .5) / the.Bins
  z = max(-3, min(3, log(p / (1 - p)) / 1.7))
  return col.mu + z * col.sd

def rebin(col, b): # a changed bin, back to a raw cell
  if type(col) is Num: return unbin(col, b)
  return next(k for k in col.has if str(k) == b)

def rawdist(t, a, b): # ezr0's xdist, on raw cells: the judge's ruler
  def g(c, u, v):
    if u == "?" or v == "?": return 1
    return abs(norm(c,u) - norm(c,v)) if type(c) is Num else u != v
  return dist((g(c, a[c.at], b[c.at]) for c in t.x), len(t.x))

def one(t, w, seed): # judge rows out first, then 50:50; plan Test rows
  random.seed(seed)
  rows = random.sample(t.rows, len(t.rows))
  pool, rows = rows[:the.Judge], rows[the.Judge:]
  n     = len(rows) // 2
  m     = model(t, rows[:n])
  judge = lambda raw: w(min(pool, key=lambda z: rawdist(t, raw, z.raw)))
  cache = {id(r): plan1(t, m, r) for r in m.lab.rows}
  out   = []
  for r in rows[n:][:the.Test]:
    nu  = apply(r.bins, cache[id(near(t, m, r.bins))].changes)
    raw = [v if nu[at] == r.bins[at] else rebin(t.cols[at], nu[at])
           for at, v in enumerate(r.raw)]
    out += [o(win0=judge(r.raw), win1=judge(raw), dx=rawdist(t, r.raw, raw),
              k=sum(r.bins[c.at] != nu[c.at] for c in t.x))]
  return out

def report(ss):
  med = lambda xs: sorted(xs)[len(xs)//2]
  f   = lambda a: f"{sum(a)/len(a):7.1f}{med(a):6.1f}"
  g   = lambda a: f"{sum(a)/len(a):7.3f}{med(a):6.3f}"
  print(f"{'':6}{'win0':>13}{'win1':>13}{'gain':>13}{'dx':>13}"
        f"{'k':>6}{'gain/k':>8}{'cover':>7}   (mean, median)")
  print(f"{'bins':6}{f([s.win0 for s in ss])}{f([s.win1 for s in ss])}"
        f"{f([s.win1 - s.win0 for s in ss])}{g([s.dx for s in ss])}"
        f"{sum(s.k for s in ss)/len(ss):6.2f}"
        f"{sum(s.win1-s.win0 for s in ss)/(sum(s.k for s in ss)+1e-32):8.1f}"
        f"{sum(s.k > 0 for s in ss)/len(ss):7.0%}")

if __name__ == "__main__":
  if "-h" in sys.argv: print(__doc__); sys.exit()
  for _k, _v in zip(sys.argv[1:], sys.argv[2:]):
    if _k[1:] in the: the[_k[1:]] = atom(_v)
  _t = Tbl(csv(the.File))
  if "--explain" in sys.argv:
    random.seed(the.Seed)
    explain(_t, model(_t, random.sample(_t.rows, len(_t.rows))))
  else:
    _w, _ss = wins(_t), []
    for _s in range(1, the.Repeats + 1): _ss += one(_t, _w, _s)
    print(f"{the.File}  seeds={the.Repeats}  rows={len(_ss)}")
    report(_ss)
