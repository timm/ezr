#!/usr/bin/env python3 -B
"""
ezr.py: multi-objective XAI using minimal labels.   
Faster, simpler AI. Better maps, not bigger boots.    
(c) 2026 Tim Menzies <timm@ieee.org> MIT license.    

Options:    
      -Start=4         acquire: initial random labels   
      -Stop=50         acquire: total labelling budget   
      -Few=128         holdout: max training rows   
      -Leaf=4          tree: min rows in any leaf  
      -Check=5         holdout: top picks to label  
      -Repeats=20      holdout: how many train/test splits  
      -Seed=1234567891 random number seed  
      -File=~/gits/moot/optimize/misc/auto93.csv   

One file, five layers.  Each calls the layers above it and
knows nothing of the ones below.  Cut on the banners to get
five files back:    

      core     columns, tables, distance.  Calls nothing.    
      acquire  spend a label budget.    
      tree     recursive splits, and a way to read them.    
      rig      wins, holdout.  Takes its ranker as an argument,    
               so the tree is its default, not its requirement.    
      stats    cliffs, ks, cohen.  A leaf: nothing calls it.    

"""
# pylint: disable=bad-indentation,multiple-statements  
# pylint: disable=invalid-name,ungrouped-imports   
# pylint: disable=attribute-defined-outside-init   
# pylint: disable=protected-access,broad-exception-caught  
# pylint: disable=no-member,assigning-non-slot  # `type()` structs
from typing import Any
import os, re, sys, random, traceback # pylint: disable=C0410
from copy import copy
from itertools import groupby
from math import exp, log2, sqrt
from collections.abc import Callable, Iterable, Iterator

#-- types --------------------------------------------------
# Plain aliases, not `type X = ...`: that is 3.12 syntax, and pypy
# is on 3.11.  So the ones naming a struct wait until it exists.
QTY    = int | float                  # any number
ATOM   = QTY | str                    # one cell; "?" = unknown
ROW    = list[ATOM]
MIDS   = dict[int, ATOM]              # a centroid
ROWS   = list[ROW]
NUMS   = list[QTY]
GO     = Callable[[ROW], bool]        # which way does a row go?
ORACLE = Callable[[ROW], ROW]         # labels one row

#-- misc ---------------------------------------------------
def say(x: Any, p: int = 2) -> str:
  "Floats get P decimals; dicts list their keys."
  if isinstance(x,float): x= f"{x:.{p}f}".rstrip("0").rstrip(".")
  if isinstance(x, dict):
    x= "{"+", ".join(f"{k}: {say(v,p)}" for k,v in x.items())+"}"
  return str(x)

def struct(s: str, **d: Any) -> type:
  """A __slots__ class, in one line.  A default that is a type is
  called, so every object gets its own list/dict (not a shared one)."""
  def init(i, **kw):
    for k, v in d.items():
      setattr(i, k, kw[k] if k in kw else v() if type(v) is type else v)
  return type(s, (), dict( __slots__ = tuple(d), __init__  = init,
                     __repr__=lambda i:say({k:getattr(i,k) for k in d})))

def opts(doc: str) -> dict:
  "The -key=value pairs in DOC."
  return {k: atom(v) for k,v in re.findall(r"-(\w+)=(\S+)", doc)}

def atom(s: str) -> ATOM:
  "'22' -> 22. '3.1' -> 3.1. 'True' -> True. 'x' -> 'x'."
  for fn in (int, float):
    try: return fn(s)
    except ValueError: pass
  return s=="True" or (s !="False" and s) # or (s=="False" and False)

def csv(file: str) -> Iterator[ROW]:
  "ROWS of FILE, each cell coerced."
  with open(os.path.expanduser(file),  # -sig drops any BOM
           encoding="utf-8-sig") as f:
    for line in f:
      if line.strip(): yield [atom(s.strip()) for s in line.split(",")]

#-- structs ------------------------------------------------
# UPPER is the struct.  A default that is a type gets called, so
# `cols=COLS` gives every TBL its own COLS.
NUM = struct("NUM", txt=" ", at=0, n=0, mu=0, m2=0, sd=0, goal=1)
SYM = struct("SYM", txt=" ", at=0, n=0, has=dict)
COLS= struct("COLS", names=list, all=dict, x=list, y=list, klass=None)
TBL = struct("TBL", rows=list, cols=COLS, mids=None)
NODE= struct("NODE", rows=list, at=None, v=None, go=None, kids=list,
             mu=0, pred=0, err=0, verr=0)   # pred,err,verr: `fit*`

# Constructors are the TYPE itself, unless named here.
Num,Sym,Node = NUM,SYM,NODE          # Tbl and Cols are defined below

COL    = NUM | SYM                    # the aliases that needed one
PICKER = Callable[[TBL, int, ORACLE], ROWS]
RANKER = Callable[[TBL], Callable[[ROW], float]]
                                      # ranks unlabelled rows
#-- columns ------------------------------------------------
def Col(txt: str = " ", at: int = 0) -> COL:
  "Factory that returns NUM or SYM.  A trailing `-` minimises."
  return (Num(at=at, txt=txt, goal=0 if txt[-1] == "-" else 1)
          if txt[0].isupper() else Sym(at=at, txt=txt))

def add(col: COL, v: ATOM, inc: int = 1) -> None:
  "Show V to COL.  INC=-1 takes it away.  `?` changes nothing."
  if v != "?":
    col.n += inc
    if type(col) is Sym:
      col.has[v] = col.has.get(v, 0) + inc
    else:
      d = v - col.mu                      # Welford, for `div`
      col.mu += inc * d / max(1, col.n)
      col.m2  = max(0, col.m2 + inc * d * (v - col.mu))
      col.sd  = 0 if col.n < 2 else (col.m2/(col.n-1))**.5

def mid(col: COL) -> ATOM:
  "Middle: the mean, or the most common symbol; ? if none."
  return (max(col.has, key=col.has.get) if col.has else "?"
          ) if type(col) is Sym else col.mu

def mids(tbl: TBL) -> MIDS:
  "Every column's middle, cached until the next addRow."
  tbl.mids = tbl.mids or {at: mid(c) for at,c in tbl.cols.all.items()}
  return tbl.mids

def div(col: COL) -> float:
  "Spread: entropy, or standard deviation."
  return (-sum(v/col.n*log2(v/col.n) for v in col.has.values())
          if type(col) is Sym else col.sd)  # sd kept by `add`

def adds(vs: Iterable[ATOM], col: COL | None = None) -> COL:
  "Every item of VS into COL."
  col = Num() if col is None else col
  for v in vs: add(col, v)
  return col

def norm(col: COL, v: ATOM) -> ATOM:
  "To 0..1, by the logistic curve.  Symbols do not scale."
  if type(col) is Sym: return v
  z = max(-3, min(3, (v - col.mu) / (1e-32 + div(col))))
  return 1 / (1 + exp(-1.7 * z))

#-- tables -------------------------------------------------
def Tbl(src: Iterable[ROW]) -> TBL:
  "Header names the columns: X skip, +- goal, ! klass."
  src = iter(src)
  tbl = TBL(cols=Cols(next(src)))
  for row in src: addRow(tbl, row)
  return tbl

def Cols(names: list[str]) -> COLS:
  "Column roles, from a header: X skip, +- goal, ! klass."
  cols = COLS(names=names)
  for at, s in enumerate(names):
    if s[-1] == "X": continue            # skip me entirely
    cols.all[at] = col = Col(s, at)      # keyed by at: X leaves gaps
    if s[-1] == "!": cols.klass = col
    (cols.y if s[-1] in "+-!" else cols.x).append(col)
  return cols

def addRow(tbl: TBL, row: ROW, inc: int = 1,
           keep: bool = True) -> ROW:
  """Show ROW to my columns.  KEEP also files it under tbl.rows;
  INC=-1 takes it back out of the columns, and wants keep=False."""
  if keep: tbl.rows += [row]
  tbl.mids = None                 # a new row moves the middles
  for at, col in tbl.cols.all.items(): add(col, row[at], inc)
  return row

def clone(tbl: TBL, rows: ROWS = None) -> TBL:
  "An empty copy of TBL, plus ROWS."
  return Tbl([tbl.cols.names] + (rows or []))

#-- distance -----------------------------------------------
def dist(vs: Iterable[QTY]) -> float:
  "Root mean square of the gaps.  VS is counted, not asked for n."
  vs = list(vs)
  return sqrt(sum(v*v for v in vs) / len(vs))

def ydist(tbl: TBL, row: ROW) -> float:
  "How far ROW's goals are from the best they could be."
  return dist(abs(norm(c, row[c.at]) - c.goal) for c in tbl.cols.y)

def gap(col: COL, a: ATOM, b: ATOM) -> QTY:
  "Distance between two values of one column."
  if a == "?" or b == "?": return 1    # unknown = far
  return a!=b if type(col) is Sym else abs(norm(col,a)-norm(col,b))

def xdist(tbl: TBL, r1: ROW, r2: ROW | MIDS) -> float:
  "How far apart two rows are, over the x columns."
  return dist(gap(c, r1[c.at], r2[c.at]) for c in tbl.cols.x)

#-- acquire ------------------------------------------------

def oracle(row: ROW) -> ROW:
  """Labeller. Rows here arrive with ys, so nothing to do.
  Real oracles fill in any missing y cells (and can close
  over a TBL to know which cells those are)."""
  return row

def acquire(tbl: TBL, cap: int | None = None,
            label: ORACLE = oracle) -> ROWS:
  "Label near the best rows, far from the rest."
  cap  = cap or the.Stop
  todo = random.sample(tbl.rows, len(tbl.rows))[:the.Few]
  both = clone(tbl, [label(todo.pop()) for _ in range(the.Start)])
  both.rows.sort(key=lambda r: ydist(both, r))
  n    = int(sqrt(the.Start))
  best,rest = clone(tbl,both.rows[:n]), clone(tbl,both.rows[n:])
  while todo and len(both.rows) < cap:
    todo.sort(key=lambda z: xdist(tbl, z, mids(rest)) -
                            xdist(tbl, z, mids(best)))
    addRow(best, addRow(both, label(todo.pop())))
    best.rows.sort(key=lambda z: ydist(both, z))  # no y leak
    if len(best.rows) > sqrt(len(both.rows)): # best stays small
      addRow(rest, addRow(best, best.rows.pop(), -1, keep=False))
  return both.rows

def grabs(tbl: TBL, cap: int | None = None,
          label: ORACLE = oracle) -> ROWS:
  "The straw man: same budget, taken at random."
  cap = cap or the.Stop
  return [label(r) for r in
          random.sample(tbl.rows, min(cap, len(tbl.rows)))]

#-- tree ---------------------------------------------------
# Calls core.  Nothing above this line calls down here.
def cut(tbl: TBL, rows: ROWS) -> tuple[int,ATOM,GO]|None:
  "The (at, v, go) whose two sides have the tightest ys."
  Y   = {id(r): ydist(tbl, r) for r in rows}   # ydist, ALWAYS: a
  tot = adds(Y.values())      # tree splits on how good a row is,
  out, least = None, 1e30     # not on what `ys` would regress
  for col in tbl.cols.x:
    at = col.at                 # this column as sorted (x,y) pairs:
    vs = sorted((r[at], Y[id(r)])         # a num cuts between them,
                for r in rows if r[at] != "?")   # a sym groups by
    for v, a, b in candidates(col, vs, copy(tot)):          # them
      if a.n >= the.Leaf and b.n >= the.Leaf:
        s = (div(a)*a.n + div(b)*b.n) / (a.n + b.n)
        if s < least: out, least = (col, v), s
  if out: return out[0].at, out[1], gate(*out)

def candidates(col: COL, vs: list, tot: NUM) -> Iterator:
  """Every split of COL as (v, left, right): the ys each side would
  hold.  VS is this column\'s (x,y) pairs, sorted; TOT is every y of
  every row, the "?" ones too, and is consumed here -- which is why
  the caller hands over a copy.  LEFT and RIGHT are reused between
  yields, so score them before asking for the next one."""
  if type(col) is Sym:
    for v, g in groupby(vs, lambda z: z[0]):   # one symbol, and
      a, b = Num(), copy(tot)                  # then all the rest
      for _, y in g: add(a, y); add(b, y, -1)
      yield v, a, b
  else:
    a = Num()
    for (v, y), (nxt, _) in zip(vs, vs[1:]):
      add(a, y); add(tot, y, -1)      # one row moves right to left
      if v != nxt: yield v, a, tot    # no cutting inside a tie

def gate(col: COL, v: ATOM) -> GO:
  "The test that sends a row to the left kid."
  return ((lambda r: r[col.at] == v) if type(col) is Sym else
          (lambda r: r[col.at] != "?" and r[col.at] <= v))

def tree(tbl: TBL, rows: ROWS, most: int = 1000) -> NODE:
  """Split while a split keeps both sides big enough.  MOST caps
  the depth, for a caller that will not read past it: building
  what nobody looks at is the whole cost on a wide file."""
  node = NODE(rows=rows,
              mu=sum(ydist(tbl,r) for r in rows)/len(rows))
  if most and len(rows) > the.Leaf and (found := cut(tbl, rows)):
    at, v, go = found
    yes, no = [], []
    for r in rows: (yes if go(r) else no).append(r)
    node.at, node.v, node.go = at, v, go # cut kepts sides big
    node.kids = [tree(tbl, yes, most-1), tree(tbl, no, most-1)]
  return node

def leaf(node: NODE, row: ROW) -> NODE:
  "Walk ROW down to its leaf."
  while node.kids: node = node.kids[0 if node.go(row) else 1]
  return node

def leafs(node: NODE) -> list[NODE]:
  "Return leaves of this tree."
  return [x for k in node.kids for x in leafs(k)] or [node]

def show(tbl: TBL, node: NODE, pre: str | None = None,
         edge: str = "") -> None:
  "Tree on the left; ydist and n on the right."
  ls = sorted(leafs(node), key=lambda z: z.mu)
  def walk(z: NODE, pre: str | None, edge: str) -> None:
    m = "+" if z is ls[0] else "-" if z is ls[-1] else " "
    print(f"{m} {round(100*z.mu):>4} {len(z.rows):>5}   "
          f"{(pre or '')+edge}".rstrip())
    op = "=" if type(tbl.cols.all[z.at or 0]) is Sym else "<="
    no = "!=" if op == "=" else ">"
    for kid, oper in zip(z.kids, [op, no]):
      walk(kid, "" if pre is None else pre + "|  ",
           f"{tbl.cols.names[z.at]} {oper} {say(z.v)}")
  print(" ydist     n")
  walk(node, pre, edge)



#-- regress ------------------------------------------------
# Calls tree.  A tree splits on ydist; these two let it predict a
# number instead, and say what that prediction costs.
def ys(tbl: TBL) -> Callable[[ROW], QTY]:
  """A row\'s y: its lone y column, or else its ydist.  Returns a
  FUNCTION, and one that remembers -- ydist is not cheap and a row
  is asked for its y once per level of a tree.  Not cached on the
  row itself: ydist reads TBL\'s columns, so the same row has a
  different y in another table."""
  c    = tbl.cols.y
  f    = (lambda r: r[c[0].at]) if len(c)==1 else lambda r: ydist(tbl,r)
  memo = {}
  def y(row):
    if id(row) not in memo: memo[id(row)] = f(row)
    return memo[id(row)]
  return y

def fit(node: NODE, Y: Callable[[ROW], QTY]) -> NODE:
  "What this node would predict (PRED), and what that costs (ERR)."
  vs = [Y(r) for r in node.rows]
  node.pred = sum(vs) / len(vs)
  node.err  = sum(abs(v - node.pred) for v in vs)
  for kid in node.kids: fit(kid, Y)
  return node

#-- rig ----------------------------------------------------
# Calls core, acquire, and one RANKER -- tree's, by default.
def ranker(lab: TBL) -> Callable[[ROW], float]:
  "Grow a tree on LAB; score any row by its leaf's mean ydist."
  node = tree(lab, lab.rows)
  return lambda r: leaf(node, r).mu

def wins(tbl: TBL) -> Callable[[ROW], float]:
  "100 at the best row, 0 at an average one."
  ys = sorted(ydist(tbl, r) for r in tbl.rows)
  lo, avg = ys[0], sum(ys)/len(ys)
  return lambda r: max(-100, min(100, 100*(1 - (ydist(tbl,r)-lo)
                                            / (avg-lo+1e-32))))

def holdout(tbl: TBL, pick: PICKER = acquire,
            rank: RANKER = ranker,
            label: ORACLE = oracle) -> ROW:
  "Train on half; of CHECK guesses on the rest, pick best."
  rows  = random.sample(tbl.rows, len(tbl.rows))
  n     = len(rows)//2
  tr    = clone(tbl, rows[:n][:the.Few])
  lab   = clone(tbl, pick(tr, the.Stop - the.Check, label))
  top   = sorted(rows[n:], key=rank(lab))
  return min(top[:the.Check], key=lambda r: ydist(lab, label(r)))


#-- stats --------------------------------------------------
# A leaf: it calls core, and nothing here calls it.
def cohen(xs: NUMS, ys: NUMS, d: float = 0.35) -> bool:
  "Are the means within D pooled standard deviations?"
  a, b = adds(xs), adds(ys)
  pool = ((a.n-1)*div(a)**2 + (b.n-1)*div(b)**2)/(a.n+b.n-2)
  return abs(a.mu - b.mu) <= d * sqrt(pool)

def cliffs(xs: NUMS, ys: NUMS, d: float = 0.197) -> bool:
  "Sorted in.  Is the rank imbalance small enough?"
  gt = lt = j = k = 0
  for x in xs:
    while j < len(ys) and ys[j] <  x: j += 1; k = j
    while k < len(ys) and ys[k] <= x: k += 1
    gt += j; lt += len(ys) - k
  return abs(gt - lt) / (len(xs) * len(ys)) <= d

def ks(xs: NUMS, ys: NUMS, a: float = 1.36) -> bool:
  "Sorted in.  95% Kolmogorov-Smirnov."
  n, m, i, j, d = len(xs), len(ys), 0, 0, 0
  while i < n and j < m:
    v = min(xs[i], ys[j])
    while i < n and xs[i] <= v: i += 1
    while j < m and ys[j] <= v: j += 1
    d = max(d, abs(i/n - j/m))
  return d <= a * sqrt((n + m) / (n * m))

def same(xs: NUMS, ys: NUMS, d: float = 0) -> bool:
  """Indistinguishable.  Always cliffs and ks; a non-zero D adds
  cohen, and is its effect size -- a multiple of the pooled sd,
  NOT an absolute floor.  d=0 skips that third test."""
  xs, ys = sorted(xs), sorted(ys)
  return cliffs(xs,ys) and ks(xs,ys) and (not d or cohen(xs,ys,d))

#-- start --------------------------------------------------
Settings = struct("Settings", **opts(__doc__))  # an extension adds
the      = Settings()       # its own, then rebuilds this from both

def run(f: Callable) -> int:
  "Run F. Demos may poke `the`, so always put it back."
  # Put it back IN PLACE, not by rebinding: an extension holds its
  # own name for this same object, and must not be left behind.
  b4 = {k: getattr(the,k) for k in the.__slots__}
  random.seed(the.Seed)
  try:                   f()
  except Exception as e: traceback.print_exception(e); return 1
  finally:               [setattr(the,k,v) for k,v in b4.items()]
  return 0

def main(args: list[str], funcs: dict) -> None:
  """Dispatch -x or --x to FUNCS' eg_x; -key val updates `the`.
  Dashes are stripped, so -h and --h are the same ask."""
  while args:
    s = args.pop(0); k = s.lstrip("-")
    if   "eg_" + k in funcs: run(funcs["eg_" + k])
    elif hasattr(the, k):    setattr(the, k, atom(args.pop(0)))
    else: print(f"unknown arg: {s}")
