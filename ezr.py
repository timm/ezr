#!/usr/bin/env python3 -B
"""
ezr.py: multi-objective XAI using minimal labels.   
Faster, simpler AI. Better maps, not bigger boots.    
(c) 2026 Tim Menzies <timm@ieee.org> MIT license.    

Options:    
      -Start=4         acquire: initial random labels   
      -Stop=50         acquire: total labelling budget   
      -Few=128         holdout: max training rows   
      -Cuts=8          tree: splits to try, per num   
      -Leaf=4          tree: min rows in any leaf  
      -Check=5         holdout: top picks to label  
      -Frugal=2        frugal: most collapses per node (1 or 2)  
      -Depth=4         frugal: longest spine (so <= 3^Depth trees)  
      -Repeats=20      holdout: how many train/test splits  
      -Seed=1234567891 random number seed  
      -File=~/gits/moot/optimize/misc/auto93.csv   

One file, five layers.  Each calls the layers above it and
knows nothing of the ones below.  Cut on the banners to get
five files back:    

      core     columns, tables, distance.  Calls nothing.    
      acquire  spend a label budget.    
      tree     recursive splits, and a way to read them.    
      frugal   collapse subtrees; keep the best of the bunch.    
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
from math import exp, log2, sqrt
from collections.abc import Callable, Iterable, Iterator

#-- types --------------------------------------------------
type QTY    = int | float             # any number
type ATOM   = QTY | str               # one cell; "?" = unknown
type ROW    = list[ATOM]
type MIDS   = dict[int, ATOM]         # a centroid
type ROWS   = list[ROW]
type NUMS   = list[QTY]
type COL    = NUM | SYM               # summary of a column
type GO     = Callable[[ROW], bool]   # which way does a row go?
type ORACLE = Callable[[ROW], ROW]    # labels one row
type PICKER = Callable[[TBL, int, ORACLE], ROWS]
type RANKER = Callable[[TBL], Callable[[ROW], float]]
                                      # ranks unlabelled rows

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
             mu=0, pred=0, err=0)      # pred, err: set by `fit`

# Constructors are the TYPE itself, unless named here.
Num,Sym,Node = NUM,SYM,NODE          # Tbl and Cols are defined below
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
  "Every column's middle, cached until the next addCols."
  tbl.mids = tbl.mids or {at: mid(c) for at,c in tbl.cols.all.items()}
  return tbl.mids

def div(col: COL) -> float:
  "Spread: entropy, or standard deviation."
  return (-sum(v/col.n*log2(v/col.n) for v in col.has.values())
          if type(col) is Sym else col.sd)  # sd kept by `add`

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

def addRow(tbl: TBL, row: ROW) -> ROW:
  "Keep ROW, and show it to my columns."
  tbl.rows += [row]
  return addCols(tbl, row)

def addCols(tbl: TBL, row: ROW, inc: int = 1) -> ROW:
  "Show ROW to my columns, without keeping it."
  tbl.mids = None                 # a new row moves the middles
  for at, col in tbl.cols.all.items(): add(col, row[at], inc)
  return row

def clone(tbl: TBL, rows: ROWS = None) -> TBL:
  "An empty copy of TBL, plus ROWS."
  return Tbl([tbl.cols.names] + (rows or []))

#-- distance -----------------------------------------------
def dist(vs: Iterable[QTY], n: int) -> float:
  "Root mean square of N gaps."
  return sqrt(sum(v*v for v in vs) / n)

def ydist(tbl: TBL, row: ROW) -> float:
  "How far ROW's goals are from the best they could be."
  return dist((abs(norm(c, row[c.at]) - c.goal)
                    for c in tbl.cols.y), len(tbl.cols.y))

def gap(col: COL, a: ATOM, b: ATOM) -> QTY:
  "Distance between two values of one column."
  if a == "?" or b == "?": return 1    # unknown = far
  return a!=b if type(col) is Sym else abs(norm(col,a)-norm(col,b))

def xdist(tbl: TBL, r1: ROW, r2: ROW | MIDS) -> float:
  "How far apart two rows are, over the x columns."
  return dist((gap(c, r1[c.at], r2[c.at])
                    for c in tbl.cols.x), len(tbl.cols.x))

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
      addRow(rest, addCols(best, best.rows.pop(), -1))
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
  ys = [ydist(tbl, r) for r in rows]
  out, least = None, 1e30
  for col in tbl.cols.x:
    for v, go in candidates(col, rows):
      a, b = Num(), Num()   # one pass, so one `go` per row
      for r,y in zip(rows,ys): add(a if go(r) else b, y)
      if a.n >= the.Leaf and b.n >= the.Leaf:
        score = (div(a)*a.n + div(b)*b.n) / (a.n + b.n)
        if score < least: out, least = (col.at, v, go), score
  return out

def candidates(col: COL, rows: ROWS) -> Iterator[tuple[ATOM,GO]]:
  "What splits to try: one per symbol, or CUTS per num."
  at = col.at
  if type(col) is Sym:
    for v in sorted({r[at] for r in rows if r[at] != "?"}):
      yield v, lambda r,v=v,at=at: r[at] == v
  else:                # by rank, not value: THESE rows are dense
    xs = sorted(r[at] for r in rows if r[at] != "?")
    k  = max(1, len(xs)//the.Cuts)     # cuts, spaced by rank
    for v in xs[k-1:-1:k]:
      yield v, (lambda r,v=v,at=at: r[at] != "?" and r[at] <= v)

def tree(tbl: TBL, rows: ROWS) -> NODE:
  "Split while a split keeps both sides big enough."
  node = NODE(rows=rows,
              mu=sum(ydist(tbl,r) for r in rows)/len(rows))
  if len(rows) > the.Leaf and (found := cut(tbl, rows)):
    at, v, go = found
    yes, no = [], []
    for r in rows: (yes if go(r) else no).append(r)
    node.at, node.v, node.go = at, v, go # cut kepts sides big
    node.kids = [tree(tbl, yes), tree(tbl, no)]
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



#-- frugal -------------------------------------------------
# Calls tree.  A fast and frugal tree exits on ONE side of every
# test, so it is a spine, not a bush.  Which side, at each depth,
# is a different inductive bias -- so one tree0 hides up to 3^d
# of them, and we can go shopping.
def ys(tbl: TBL, rows: ROWS) -> dict:
  "The thing to regress: the lone y column, else ydist."
  c = tbl.cols.y
  f = (lambda r: r[c[0].at]) if len(c)==1 else lambda r: ydist(tbl,r)
  return {id(r): f(r) for r in rows}

def fit(node: NODE, Y: dict) -> NODE:
  """What this node would predict, and what that costs.  Pay it
  once here, and a variant costs O(depth), not O(rows)."""
  vs = [Y[id(r)] for r in node.rows]
  node.pred = sum(vs) / len(vs)
  node.err  = sum(abs(v - node.pred) for v in vs)
  for kid in node.kids: fit(kid, Y)
  return node

def frugals(node: NODE, n: int = 2, d: int = 4,
            path: list | None = None) -> Iterator[list]:
  """Every frugal variant, as a list of (node, side) steps: side
  0 or 1 collapses that kid and walks on into the other, 2
  collapses both and stops, None is a leaf of tree0.  PATH is one
  reused list -- copy it if you mean to keep it."""
  path = [] if path is None else path
  if not node.kids or d < 1:
    path += [(node, None)]; yield path; path.pop(); return
  for side in (0, 1):
    path += [(node, side)]
    yield from frugals(node.kids[1-side], n, d-1, path)
    path.pop()
  if n > 1:
    path += [(node, 2)]; yield path; path.pop()

def exits(path: list) -> Iterator[NODE]:
  "A frugal tree\'s leaves: whatever it collapsed.  No overlaps."
  for z, s in path:
    if   s is None: yield z
    elif s == 2:    yield from z.kids
    else:           yield z.kids[s]

def frugal(tbl: TBL, rows: ROWS = None) -> list:
  "Of up to 3^Depth frugal trees, the one training likes best."
  rows = rows or tbl.rows
  root = fit(tree(tbl, rows), ys(tbl, rows))
  best, least = None, 1e30                # only ever two paths in
  for path in frugals(root, the.Frugal, the.Depth):   # hand: this
    err = sum(x.err for x in exits(path))             # one, and
    if err < least: best, least = path[:], err        # the best
  return best

def fleaf(path: list, row: ROW) -> QTY:
  "Walk ROW along the spine; the first exit it meets answers."
  for z, s in path:                  # the last step always exits,
    if s is None: return z.pred      # so this cannot fall through
    k = 0 if z.go(row) else 1
    if s in (2, k): return z.kids[k].pred

def fmae(path: list, tbl: TBL, rows: ROWS) -> float:
  "MAE, over how far the mean y sits above the best y."
  Y  = ys(tbl, rows)
  vs = list(Y.values())
  return (sum(abs(Y[id(r)] - fleaf(path,r)) for r in rows) / len(rows)
          / (sum(vs)/len(vs) - min(vs) + 1E-32))

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
def adds(vs: Iterable[ATOM], col: COL | None = None) -> COL:
  "Every item of VS into COL."
  col = Num() if col is None else col
  for v in vs: add(col, v)
  return col

def cohen(xs: NUMS, ys: NUMS, d: float = 0.35,
          eps: float = 0) -> bool:
  "Are the means within D pooled standard deviations?"
  a, b = adds(xs), adds(ys)
  pool = ((a.n-1)*div(a)**2 + (b.n-1)*div(b)**2)/(a.n+b.n-2)
  return abs(a.mu - b.mu) <= max(eps, d * sqrt(pool))

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

def same(xs: NUMS, ys: NUMS, eps: float = 0) -> bool:
  """Indistinguishable.  Always cliffs and ks; EPS adds cohen, and
  doubles as its effect size (eps=0 skips that third test)."""
  xs, ys = sorted(xs), sorted(ys)
  return (cliffs(xs,ys) and ks(xs,ys)
          and (not eps or cohen(xs,ys,d=eps)))

#-- start --------------------------------------------------
DEFAULTS = opts(__doc__ or "")   # an extension adds its own, then
Settings = struct("Settings", **DEFAULTS)   # rebuilds this struct
the      = Settings()

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
