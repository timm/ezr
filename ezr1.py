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

Plan: move each column a row breaks, in the top rule, to that rule's
nearest bin.  Rank: score a row by the summed scores of the top Rank
rules it meets.  The rig that grades all this is in ezr1_eg.py.

Options:
   -Bins=5      bins per numeric column
   -Cut=10      explain: skip ranges under this % of the top score
   -Which=100   which: merges
   -Stack=32    which: rules kept
   -Rank=10     rank: top rules used to score a row
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

#-- structs -----------------------------------------------------
def struct(name, **d): # a __slots__ class; type defaults (dict, list) fresh per object
  def init(i, **kw):
    for k, v in d.items():
      setattr(i, k, kw[k] if k in kw else v() if type(v) is type else v)
  return type(name, (), dict(__slots__=tuple(d), __init__=init))

def opts(doc): # -key=value pairs in DOC, as a dict
  return {k: atom(v) for k, v in re.findall(r"-(\w+)=(\S+)", doc)}

def cli(s, args): # -key value pairs, for keys S already has
  for k, v in zip(args, args[1:]):
    if k[:1] == "-" and k[1:] in s.__slots__: setattr(s, k[1:], atom(v))
  return s

Num   = struct("Num",   at=0, txt=" ", n=0, mu=0, m2=0, sd=0, goal=1)
Sym   = struct("Sym",   at=0, txt=" ", n=0, has=dict)  # type tells SYM/NUM
Row   = struct("Row",   raw=list, bins=None)  # raw cells; later, bins
Cols  = struct("Cols",  names=list, all=dict, x=list, y=list)
Tbl   = struct("Tbl",   rows=list, cols=None)
Model = struct("Model", lab=None, ranges=list, stack=list)

def Col(txt=" ", at=0): # uppercase name = NUM, else SYM; +- marks a goal
  return (Num(at=at, txt=txt, goal=txt[-1] != "-") if txt[0].isupper()
          else Sym(at=at, txt=txt))

def table(names): # an empty Tbl; header names its columns: X skip, +-! goal
  cs = Cols(names=names)
  for at, s in enumerate(names):
    if s[-1] == "X": continue               # skip me entirely
    col = cs.all[at] = Col(s, at)
    (cs.y if s[-1] in "+-!" else cs.x).append(col)
  return Tbl(cols=cs)

the = struct("The", **opts(__doc__))()

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
  tbl = table(next(src))
  for raw in src: addRow(tbl, Row(raw=raw))
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
  out = table(tbl.cols.names)
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
  rs  = ranges(tbl, best, rest)
  return Model(lab=lab, ranges=rs, stack=which(best, rest, rs))

#-- plan -------------------------------------------------------
def mend(rule, bins): # each column BINS breaks, to the rule's nearest bin
  new = bins[:]
  for at, vs in rule.items():
    if new[at] not in vs:
      new[at] = min(sorted(vs, key=str), key=lambda v: g2(new[at], v))
  return new

def plan(m, row): # ROW's bins, mended to meet the top rule
  return mend(m.stack[0][1], row.bins)

def rank(m): # sort key: rows meeting more (and better) top rules first
  return lambda row: -sum(s for s, rule in m.stack[:the.Rank]
                          if selects(rule, row))

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
  print("\nscore  rule")
  for s, rule in m.stack[:5]: print(f"{100*s:5.0f}  {show(tbl, rule)}")

if __name__ == "__main__":
  if "-h" in sys.argv: print(__doc__); sys.exit()
  cli(the, sys.argv[1:])
  _t = load(csv(the.File))
  random.seed(the.Seed)
  explain(_t, model(_t, random.sample(_t.rows, len(_t.rows))))
