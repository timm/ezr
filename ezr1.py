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
one bin width at a time, toward each column's top range.  The rig
that grades this lives next door, in ezr1_eg.py.

Options:
   -Bins=5      bins per numeric column
   -Cut=10      plan: skip ranges under this % of the top score
   -Enough=10   stop once the y gap left is under this % of the start
   -Stop=50     rows we may label, all up
   -Check=5     of that budget, saved for the unseen rows
   -Seed=1      random number seed
   -File=~/gits/moot/optimize/misc/auto93.csv

Usage: ./ezr1.py [-Option value]...      (prints the explain table)
"""
import os, random, re, sys
from math import exp, sqrt

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

#-- classes ----------------------------------------------------
class Settings: # one attribute per -key=value in a docstring
  def __init__(i, doc):
    i.__dict__.update({k: atom(v)
                       for k, v in re.findall(r"-(\w+)=(\S+)", doc)})
  def __repr__(i): return f"Settings{i.__dict__}"
  def cli(i, args): # -key value pairs, for keys I already have
    for k, v in zip(args, args[1:]):
      if k[:1] == "-" and k[1:] in vars(i): setattr(i, k[1:], atom(v))
    return i

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

class Cols: # column roles, from the header: X skip, +-! goal
  __slots__ = ("names", "all", "x", "y")
  def __init__(i, names):
    i.names, i.all, i.x, i.y = names, {}, [], []
    for at, s in enumerate(names):
      if s[-1] == "X": continue             # skip me entirely
      col = i.all[at] = Col(s, at)
      (i.y if s[-1] in "+-!" else i.x).append(col)

class Tbl: # rows, and the columns that summarise them
  __slots__ = ("rows", "cols")
  def __init__(i, names): i.rows, i.cols = [], Cols(names)

class Model: # the labels; their (score, at, bin) ranges; each column's top
  __slots__ = ("lab", "ranges", "tops")
  def __init__(i, lab, ranges, tops): i.lab,i.ranges,i.tops = lab,ranges,tops

def Col(txt=" ", at=0): # uppercase name = NUM, else SYM
  return Num(txt, at) if txt[0].isupper() else Sym(txt, at)

the = Settings(__doc__)

#-- columns: add, norm, bin ------------------------------------
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
def load(src): # header names the columns; then rows, then bins
  src = iter(src)
  tbl = Tbl(next(src))
  for raw in src: addRow(tbl, Row(raw))
  return discretize(tbl)

def addRow(tbl, row): # keep ROW, and show its raw cells to my columns
  tbl.rows += [row]
  for at, col in tbl.cols.all.items(): add(col, row.raw[at])
  return row

def discretize(tbl): # bins, from this table's stats, once
  for r in tbl.rows:
    r.bins = [bin1(tbl.cols.all.get(at), v) for at, v in enumerate(r.raw)]
  return tbl

def clone(tbl, rows=None): # an empty copy of TBL, plus ROWS (bins kept)
  out = Tbl(tbl.cols.names)
  for r in rows or []: addRow(out, r)
  return out

#-- distance ---------------------------------------------------
def dist(vs, n): return sqrt(sum(v*v for v in vs) / n)

def ydist(tbl, row): # how far ROW's goals are from the best they could be
  return dist((abs(norm(c, row.raw[c.at]) - c.goal) for c in tbl.cols.y),
              len(tbl.cols.y))

def g2(a, b): # squared gap, in bin widths: exact ints, so sums can update
  if a == "?" or b == "?": return the.Bins ** 2
  if type(a) is float is type(b): return round((a - b) * the.Bins) ** 2
  return the.Bins ** 2 * (a != b)

def near(tbl, m, bins): # nearest label: least summed g2 (ties go first)
  return min(m.lab.rows,
             key=lambda z: sum(g2(bins[c.at], z.bins[c.at])
                               for c in tbl.cols.x))

#-- model: best, rest, and their ranges ------------------------
def ranges(tbl, best, rest): # (score, at, bin) ranges, by b^2/(b+r)
  out = []
  for c in tbl.cols.x:
    nb, nr = {}, {}
    for rows, n in ((best, nb), (rest, nr)):
      for r in rows:
        if (v := r.bins[c.at]) != "?": n[v] = n.get(v, 0) + 1
    for v in sorted(nb, key=str):      # bins best never visits score 0
      b, r = nb[v] / len(best), nr.get(v, 0) / len(rest)
      out += [(b*b/(b+r), c.at, v)]
  return sorted(out, key=lambda z: -z[0])

def tops(rs): # each column's top range, strongest first, minus weak
  seen, out = set(), []
  for z in rs:
    if z[1] not in seen: seen.add(z[1]); out += [z]
  return [z for z in out if z[0] >= the.Cut/100 * out[0][0]]

def model(tbl, rows): # label a budget, split best from rest
  lab = clone(tbl, rows[:the.Stop - the.Check])
  lab.rows.sort(key=lambda r: ydist(lab, r))
  k   = int(sqrt(len(lab.rows)))           # sqrt best, rest rest
  rs  = ranges(tbl, lab.rows[:k], lab.rows[k:])
  return Model(lab, rs, tops(rs))

#-- explain ----------------------------------------------------
def say(v): # a bin, two wide: -- - . + ++ (Bins=5), else its index
  if type(v) is not float: return str(v)
  i = round(v * the.Bins)
  return ("--", "-", ".", "+", "++")[i] if the.Bins == 5 else str(i)

def explain(tbl, m): # per column, b^2/(b+r) of each bin; top first
  bins = [i / the.Bins for i in range(the.Bins)]
  print(" ".join(f"{say(b):>2}" for b in bins), " top  attribute")
  for score, at, v in m.tops:
    s = {v1: s1 for s1, at1, v1 in m.ranges if at1 == at}
    strip = " ".join(f"{min(99, int(100*s.get(b, 0))) or '':>2}"
                     if type(v) is float else "  " for b in bins)
    print(strip, f"{say(v):>4}  {tbl.cols.all[at].txt}"
          + ("" if type(v) is float else f"  ({100*score:.0f})"))

#-- plan -------------------------------------------------------
def steps(a, v): # bins from A to V, one bin width at a time
  if type(a) is not float or type(v) is not float: return [v]
  n = round((v - a) * the.Bins); s = 1 if n > 0 else -1
  return [round(a * the.Bins + s*k) / the.Bins for k in range(1, abs(n)+1)]

def plan1(tbl, m, r0): # least change to labelled R0, most y per x
  """Per column, top range first: take the bin step with most dy/dx
  (dx = bins moved), or, if none helps, jump to the top bin anyway.
  Return the shortest prefix of those changes with the most dy."""
  y   = lambda r: ydist(m.lab, r)
  ylo = y(m.lab.rows[0])
  L   = m.lab.rows                  # ss[j]: now to L[j], summed g2s;
  now = r0.bins[:]                  # a one-column move updates it in
  ss  = [sum(g2(now[c.at], z.bins[c.at]) for c in tbl.cols.x) for z in L]
  best = lambda s2: L[min(range(len(L)), key=s2.__getitem__)]
  def peek(at, b): # ss, and nearest label, if now[at] became B
    s2 = [s - g2(now[at], z.bins[at]) + g2(b, z.bins[at])
          for s, z in zip(ss, L)]
    return s2, best(s2)
  w = best(ss); y0 = y(w)
  out, seen = [], [(0, w)]
  for _, at, v in m.tops:
    if now[at] == v: continue
    top = None
    for b in steps(now[at], v):          # smallest jump wins ties: dx
      s2, w2 = peek(at, b)
      dy = y(w) - y(w2)
      dx = abs(b - now[at]) if type(b) is float is type(now[at]) else 1
      if dy > 0 and (top is None or dy/dx > top[0]): top = (dy/dx, b, w2, s2)
    if top is None: top = (0, v, *peek(at, v)[::-1])   # jump anyway
    _, now[at], w, ss = top                                 # lock it
    out += [(at, r0.bins[at], now[at])]          # (at, was, to)
    seen += [(y0 - y(w), w)]
    if y(w) - ylo <= the.Enough/100 * (y0 - ylo): break   # near enough
  i = max(range(len(seen)), key=lambda j: (seen[j][0], -j))   # most dy,
  return out[:i] if seen[i][0] > 0 else []                # fewest steps

def apply(bins, changes): # bins move by deltas; symbols get set
  new, top = bins[:], (the.Bins - 1) / the.Bins
  for at, was, to in changes:
    a = new[at]
    if all(type(v) is float for v in (a, was, to)):
      new[at] = max(0, min(top, round((a + to - was) * the.Bins) / the.Bins))
    else: new[at] = to
  return new

if __name__ == "__main__":
  if "-h" in sys.argv: print(__doc__); sys.exit()
  the.cli(sys.argv[1:])
  _t = load(csv(the.File))
  random.seed(the.Seed)
  explain(_t, model(_t, random.sample(_t.rows, len(_t.rows))))
