#!/usr/bin/env python3 -B
# vim: set et sw=2 ts=2 sts=2 cc=75 :
"""
ezr1.py: ezr0.py with binned rows.  Each Row keeps its `raw` cells
plus `bins`: every x value as a 0..1 bin (width 1/Bins) or, for a
symbol, the symbol as a string.  Bins are set once, from the whole
table, so nothing past `discretize` needs to know NUM from SYM: a
float is a bin, anything else is a symbol.  Ys stay raw.

Explain shows (column, bin) ranges, scored by b^2/(b+r), where b, r
are the shares of best and rest rows in that bin.

WHICH: start from those ranges as one-range rules, sorted by score.
Merge two (picked at random, favouring the top) and sort the new
rule back in, keeping the top Stack; Which times.  A rule holds bins
per column (OR within a column, AND across), so merging on a column
widens it.

Plan, per row: from the stack, pick the rule with the most benefit
per cost.  Cost = columns the row breaks; benefit = the row's
expected y (its nearest label's) less the mean y of the labels the
rule selects.  Skip rules the row already meets, or that do not
help.  Move just the broken columns, each to the rule's nearest bin.
The rig that grades all this is in ezr1_eg.py.

Options:
   -Bins=5      bins per numeric column
   -Cut=10      explain: skip ranges under this % of the top score
   -Which=100   which: merges
   -Stack=32    which: rules kept
   -Pay=0       which: % off the score per column past the first
   -Stop=50     rows we may label, all up
   -Check=5     of that budget, saved for the unseen rows
   -Seed=1      random number seed
   -File=~/gits/moot/optimize/misc/auto93.csv

Usage: ./ezr1.py [-Option value]...      (prints explain)
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

class Model: # labels; (score, at, bin) ranges; (score, rule, mu) stack
  __slots__ = ("lab", "ranges", "stack")
  def __init__(i, lab, ranges, stack): i.lab,i.ranges,i.stack=lab,ranges,stack

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

#-- model: best, rest, their ranges, and rules of ranges --------
def ranges(tbl, best, rest): # (score, at, bin) ranges, by b^2/(b+r)
  out = []
  for c in tbl.cols.x:
    for v in sorted({z.bins[c.at] for z in best} - {"?"}, key=str):
      out += [(score({c.at: {v}}, best, rest), c.at, v)]
  return sorted(out, key=lambda z: -z[0])

def selects(rule, row): # rule = {at: {bins}}: OR within, AND across
  return all(row.bins[at] in vs for at, vs in rule.items())  # "?" fails

def score(rule, best, rest): # b^2/(b+r), less Pay% per extra column
  b = sum(selects(rule, z) for z in best) / len(best)
  r = sum(selects(rule, z) for z in rest) / len(rest)
  return b*b / (b + r + 1e-32) * (1 - the.Pay/100) ** (len(rule) - 1)

def merge(a, b): # same column: more bins (wider); new column: narrower
  return {at: a.get(at, set()) | b.get(at, set()) for at in a | b}

def which(best, rest, rs): # good rules rise, useless ones sink
  key  = lambda z: (-z[0], len(z[1]))     # ties: fewer columns first
  todo = sorted(((s, {at: {v}}) for s, at, v in rs), key=key)[:the.Stack]
  pick = lambda: todo[int(len(todo) * random.random() ** 2)][1]
  for _ in range(the.Which):
    new = merge(pick(), pick())
    if all(new != r for _, r in todo):
      todo = sorted(todo + [(score(new, best, rest), new)],
                    key=key)[:the.Stack]
  return todo

def model(tbl, rows): # label a budget, split best from rest, learn rules
  lab = clone(tbl, rows[:the.Stop - the.Check])
  lab.rows.sort(key=lambda r: ydist(lab, r))
  k   = int(sqrt(len(lab.rows)))           # sqrt best, rest rest
  best, rest = lab.rows[:k], lab.rows[k:]
  rs, stack = ranges(tbl, best, rest), []
  for s, rule in which(best, rest, rs):   # mu = mean y of rows selected
    if ys := [ydist(lab, z) for z in lab.rows if selects(rule, z)]:
      stack += [(s, rule, sum(ys) / len(ys))]
  return Model(lab, rs, stack)

#-- plan -------------------------------------------------------
def mend(rule, bins): # each column BINS breaks, to the rule's nearest bin
  new = bins[:]
  for at, vs in rule.items():
    if new[at] not in vs:
      new[at] = min(sorted(vs, key=str), key=lambda v: g2(new[at], v))
  return new

def plan(tbl, m, row): # the stack rule with most benefit per broken column
  y0, top = ydist(m.lab, near(tbl, m, row.bins)), None
  for _, rule, mu in m.stack:
    cost = sum(row.bins[at] not in vs for at, vs in rule.items())
    if cost and y0 > mu and (top is None or (y0 - mu)/cost > top[0]):
      top = ((y0 - mu) / cost, rule)
  return mend(top[1], row.bins) if top else row.bins[:]

#-- explain ----------------------------------------------------
def say(v): # a bin, two wide: -- - . + ++ (Bins=5), else its index
  if type(v) is not float: return str(v)
  i = round(v * the.Bins)
  return ("--", "-", ".", "+", "++")[i] if the.Bins == 5 else str(i)

def show(tbl, rule): # e.g. Volume in {-- -} and origin in {2}
  return " and ".join(f"{tbl.cols.all[at].txt} in "
                      f"{{{' '.join(say(v) for v in sorted(vs, key=str))}}}"
                      for at, vs in rule.items())

def explain(tbl, m): # per column: top score, each bin's score; rules
  bins, cut = [i / the.Bins for i in range(the.Bins)], m.ranges[0][0]
  print("score", " ".join(f"{say(b):>2}" for b in bins), " attribute")
  for at in dict.fromkeys(at for _, at, _ in m.ranges):   # best first
    s = {v: sc for sc, at1, v in m.ranges if at1 == at}
    if max(s.values()) < the.Cut/100 * cut: break
    num = all(type(v) is float for v in s)
    strip = " ".join(f"{min(99, round(100*s[b])) if b in s else '':>2}"
                     if num else "  " for b in bins)
    syms  = "" if num else "  " + " ".join(
              f"{v}:{100*sc:.0f}" for v, sc in sorted(s.items(),
                                                     key=lambda z: -z[1]))
    print(f"{100*max(s.values()):5.0f}", strip, "", tbl.cols.all[at].txt + syms)
  print("\nscore   mu  rule")
  for s, rule, mu in m.stack[:5]:
    print(f"{100*s:5.0f} {mu:4.2f}  {show(tbl, rule)}")

if __name__ == "__main__":
  if "-h" in sys.argv: print(__doc__); sys.exit()
  the.cli(sys.argv[1:])
  _t = load(csv(the.File))
  random.seed(the.Seed)
  explain(_t, model(_t, random.sample(_t.rows, len(_t.rows))))
