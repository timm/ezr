#!/usr/bin/env python3 -B
# vim: set et sw=2 ts=2 sts=2 cc=75 :
"""
ezr1.py: label a few rows, learn rules of ranges, plan by them.

Rows keep their `raw` cells and their `bins`: each x value as a 0..1
bin (width 1/Bins), or a symbol as a string.  Bins are set once, from
the whole table, so past `bin1` nothing asks NUM or SYM: a float is a
bin, anything else a symbol.  Ys stay raw.

Ranges: each (column, bin), scored b^2/(b+r), where b and r are the
shares of best and rest rows in it.  Rules: bins per column (OR in a
column, AND across).  WHICH: start from one-range rules, sorted; Which
times, merge two (picked at random, favouring the top) and sort the
new rule back in (Stack = 0 keeps all; picks fall off as Geo^i).

Plan: move each column a row breaks, in the top rule, to the rule's
nearest bin.  Predict y: per column, the labels' mean y in the row's
bin, mixed by that column's best range score.  Rank: score a row by the top Rank rules it meets;
ties go to rows nearest the best rows' modal bins.  The
rig that grades all this is ezr1_eg.py.

Options:
   -Bins=5      bins per numeric column
   -Which=100   merges
   -Stack=0     rules kept (0 = keep all)
   -Geo=0.9     pick: 0 = r^2 over the stack; else P(i) ~ Geo^i
   -Rank=10     top rules used to rank a row
   -Cut=10      explain: skip ranges under this % of the top score
   -Stop=50     rows we may label, all up
   -Check=5     of that budget, saved for the unseen rows
   -Seed=1      random number seed
   -File=~/gits/moot/optimize/misc/auto93.csv

Usage: ./ezr1.py [-Option value]...      (prints explain)
"""
import os, random, re, sys
from math import exp, log, sqrt

#-- lib --------------------------------------------------------
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

def struct(name, **d): # a __slots__ class; type defaults fresh per object
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

#-- structs ----------------------------------------------------
# Camel = a plain struct. UPPER = a struct built by a Camel def.
the   = struct("The", **opts(__doc__))()
Num   = struct("Num",   at=0, txt=" ", n=0, mu=0, m2=0, sd=0, goal=1)
Sym   = struct("Sym",   at=0, txt=" ", n=0, has=dict)
Row   = struct("Row",   raw=list, bins=None)
COLS  = struct("COLS",  names=list, all=dict, x=list, y=list)
TBL   = struct("TBL",   rows=list, cols=None)
Model = struct("Model", lab=None, ranges=list, stack=list)

#-- columns ----------------------------------------------------
def Col(txt=" ", at=0): # uppercase = NUM, else SYM; "-" ends a minimise
  return (Num(at=at, txt=txt, goal=txt[-1] != "-") if txt[0].isupper()
          else Sym(at=at, txt=txt))

def add(col, v): # show V to COL
  if v == "?": return
  col.n += 1
  if type(col) is Sym: col.has[v] = col.has.get(v, 0) + 1; return
  d = v - col.mu                            # Welford
  col.mu += d / col.n
  col.m2 += d * (v - col.mu)
  col.sd  = 0 if col.n < 2 else (col.m2 / (col.n - 1)) ** .5

def norm(col, v): # to 0..1, by the logistic curve
  z = max(-3, min(3, (v - col.mu) / (1e-32 + col.sd)))
  return 1 / (1 + exp(-1.7 * z))

def bin1(col, v): # the one place that asks NUM or SYM
  if col is None or v == "?": return v      # skipped column, unknown
  if type(col) is Sym: return str(v)
  return min(the.Bins - 1, int(the.Bins * norm(col, v))) / the.Bins

#-- tables -----------------------------------------------------
def Cols(names): # COLS from a header: X skip, +-! goal
  cs = COLS(names=names)
  for at, s in enumerate(names):
    if s[-1] != "X":
      col = cs.all[at] = Col(s, at)
      (cs.y if s[-1] in "+-!" else cs.x).append(col)
  return cs

def Tbl(names): # an empty TBL
  return TBL(cols=Cols(names))

def addRow(tbl, row): # keep ROW; show its raw cells to my columns
  tbl.rows += [row]
  for at, col in tbl.cols.all.items(): add(col, row.raw[at])

def clone(tbl, rows=()): # an empty copy of TBL, plus ROWS (bins kept)
  out = Tbl(tbl.cols.names)
  for r in rows: addRow(out, r)
  return out

def load(src): # header, then rows; then bin them all, once
  src = iter(src)
  tbl = Tbl(next(src))
  for raw in src: addRow(tbl, Row(raw=raw))
  for r in tbl.rows:
    r.bins = [bin1(tbl.cols.all.get(at), v) for at, v in enumerate(r.raw)]
  return tbl

#-- distance ---------------------------------------------------
def dist(vs, n): return sqrt(sum(v*v for v in vs) / n)

def ydist(tbl, row): # how far ROW's goals are from the best they could be
  ys = tbl.cols.y
  return dist((abs(norm(c, row.raw[c.at]) - c.goal) for c in ys), len(ys))

def g2(a, b): # squared gap, in bin widths
  if a == "?" or b == "?": return the.Bins ** 2
  if type(a) is float is type(b): return round((a - b) * the.Bins) ** 2
  return the.Bins ** 2 * (a != b)

#-- rules ------------------------------------------------------
def selects(rule, row): # rule = {at: {bins}}; "?" never matches
  return all(row.bins[at] in vs for at, vs in rule.items())

def score(rule, best, rest): # b^2/(b+r)
  b = sum(selects(rule, z) for z in best) / len(best)
  r = sum(selects(rule, z) for z in rest) / len(rest)
  return b * b / (b + r + 1e-32)

def ranges(tbl, best, rest): # (score, at, bin), best first
  return sorted(((score({c.at: {v}}, best, rest), c.at, v)
                 for c in tbl.cols.x
                 for v in sorted({z.bins[c.at] for z in best} - {"?"},
                                 key=str)),
                key=lambda z: -z[0])

def merge(a, b): # same column: more bins (wider); new column: narrower
  return {at: a.get(at, set()) | b.get(at, set()) for at in a | b}

def which(best, rest, rs): # good rules rise, useless ones sink
  key  = lambda z: (-z[0], len(z[1]))       # ties: fewer columns first
  cut  = lambda xs: xs[:the.Stack] if the.Stack else xs
  todo = cut(sorted(((s, {at: {v}}) for s, at, v in rs), key=key))
  def pick():
    if not the.Geo: return todo[int(len(todo) * random.random() ** 2)][1]
    i = int(log(1 - random.random()) / log(the.Geo))   # geometric
    return todo[min(i, len(todo) - 1)][1]
  for _ in range(the.Which):
    new = merge(pick(), pick())
    if all(new != r for _, r in todo):
      todo = cut(sorted(todo + [(score(new, best, rest), new)], key=key))
  return todo

def model(tbl, rows): # label a budget; sqrt best, rest rest; rules
  lab = clone(tbl, rows[:the.Stop - the.Check])
  lab.rows.sort(key=lambda r: ydist(lab, r))
  k   = int(sqrt(len(lab.rows)))
  best, rest = lab.rows[:k], lab.rows[k:]
  rs  = ranges(tbl, best, rest)
  return Model(lab=lab, ranges=rs, stack=which(best, rest, rs))

#-- plan, rank -------------------------------------------------
def mend(rule, bins): # each column BINS breaks, to the rule's nearest bin
  new = bins[:]
  for at, vs in rule.items():
    if new[at] not in vs:
      new[at] = min(sorted(vs, key=str), key=lambda v: g2(new[at], v))
  return new

def plan(m, row): # ROW's bins, mended to meet the top rule
  return mend(m.stack[0][1], row.bins)

def rank(m): # sort key: most (and best) top rules met; ties: nearest
  k    = int(sqrt(len(m.lab.rows)))        # the best rows' modal bins
  mode = [max(c, key=c.count) if (c := [r.bins[at] for r in
          m.lab.rows[:k] if r.bins[at] != "?"]) else "?"
          for at in range(len(m.lab.rows[0].bins))]
  return lambda row: (-sum(s for s, rule in m.stack[:the.Rank]
                           if selects(rule, row)),
                      sum(g2(a, b) for a, b in zip(row.bins, mode)))

#-- predict ----------------------------------------------------
def predict(m): # y guess: per column, the labels' mean y in ROW's bin
  L  = m.lab.rows                  # (shrunk to the overall mean), mixed
  ys = [ydist(m.lab, z) for z in L]          # by each column's power
  mu, pw = sum(ys) / len(ys), {}
  for s, at, _ in m.ranges: pw[at] = max(pw.get(at, 0), s)
  def guess(row):
    num = den = 0
    for at, w in pw.items():
      v = [y for z, y in zip(L, ys)
           if row.bins[at] != "?" and z.bins[at] == row.bins[at]]
      num += w * (sum(v) + 2 * mu) / (len(v) + 2); den += w
    return num / den if den else mu
  return guess

#-- explain ----------------------------------------------------
def say(v): # a bin, two wide: -- - . + ++ (Bins=5), else its index
  if type(v) is not float: return str(v)
  i = round(v * the.Bins)
  return ("--", "-", ".", "+", "++")[i] if the.Bins == 5 else str(i)

def show(tbl, rule): # e.g. Volume in {-- -} and origin in {2}
  bins = lambda vs: " ".join(map(say, sorted(vs, key=str)))
  return " and ".join(f"{tbl.cols.all[at].txt} in {{{bins(vs)}}}"
                      for at, vs in rule.items())

def explain(tbl, m): # per column: top score, each bin's; then top rules
  bins = [i / the.Bins for i in range(the.Bins)]
  print("score", " ".join(f"{say(b):>2}" for b in bins), " attribute")
  for at in dict.fromkeys(at for _, at, _ in m.ranges):   # best first
    s   = {v: sc for sc, at1, v in m.ranges if at1 == at}
    top = max(s.values())
    if top < the.Cut / 100 * m.ranges[0][0]: break
    if all(type(v) is float for v in s):
      cells, syms = [f"{min(99, round(100*s[b])) if b in s else '':>2}"
                     for b in bins], ""
    else:
      cells = ["  "] * the.Bins
      syms  = "  " + " ".join(f"{v}:{100*sc:.0f}" for v, sc in
                              sorted(s.items(), key=lambda z: -z[1]))
    print(f"{100*top:5.0f}", " ".join(cells), "",
          tbl.cols.all[at].txt + syms)
  print("\nscore  rule")
  for s, rule in m.stack[:5]: print(f"{100*s:5.0f}  {show(tbl, rule)}")

if __name__ == "__main__":
  if "-h" in sys.argv: print(__doc__); sys.exit()
  cli(the, sys.argv[1:])
  _t = load(csv(the.File))
  random.seed(the.Seed)
  explain(_t, model(_t, random.sample(_t.rows, len(_t.rows))))
