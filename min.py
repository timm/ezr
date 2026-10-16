#!/usr/bin/env python3 -B
# vim: set et sw=2 ts=2 sts=2 cc=75 :
"""  
min.py: label a few rows, learn rules of ranges, plan by them.
(c) 2026, Tim Menzies (timm@ieee.org) MIT License

Usage: ./min.py [-Option value]...      (prints explain)

Options:
   -Bins=5      bins per numeric column
   -Which=100   merges
   -Stack=0     rules kept (0 = keep all)
   -Geo=0.9     pick: 0 = r^2 over the stack; else P(i) ~ Geo^i
   -Rank=10     top rules used to rank a row
   -Cut=10      explain: skip ranges under this % of the top score
   -Train=.75   fraction of the rows we train on
   -Any=2048    test rows we score (0 = all of them)
   -Rand=0      >0: skip the model, label this many at random
   -Stop=50     rows we may label, all up
   -Check=5     of that budget, saved for the unseen rows
   -Seed=1      random number seed
   -File=~/gits/moot/optimize/misc/auto93.csv

"""
import os, random, re, sys, traceback
from math import exp, log, sqrt

#-- lib --------------------------------------------------------
def atom(s): # '22' -> 22. '3.1' -> 3.1. 'True' -> True. 'x' -> 'x'.
  for fn in (int, float):
    try: return fn(s)
    except ValueError: pass
  return s=="True" or (s!="False" and s) # or False

def csv(file): # rows of FILE, one at a time; -sig drops any BOM
  with open(os.path.expanduser(file), encoding="utf-8-sig") as f:
    for ln in f:
      if ln.strip(): 
        lst = [atom(s.strip()) for s in ln.split(",")]
        yield Row(raw=lst,bins=lst[:])

def some(file, n): # n rows at random, parsing only the ones we keep
  """csv() pays atom() on every cell of every line.  At 167k rows that
  is 2.1s, against 0.08s to actually rank 2048 of them.  So reservoir
  the raw lines first; a line is cheap until you parse it."""
  src = iter(open(os.path.expanduser(file), encoding="utf-8-sig"))
  out, i = [next(src)], 0                # the header is never dropped
  for ln in src:
    if not ln.strip(): continue
    if i < n: out += [ln]
    elif (j := int(random.random() * (i + 1))) < n: out[j + 1] = ln
    i += 1
  return [Row(raw=[atom(c.strip()) for c in ln.split(",")]) for ln in out]

def say(x): print(saw(x)); return x
def saw(x):
  if type(x) is float: x = round(x,2)
  if type(x) is dict : x = {k:saw(v) for k,v in x.items()}
  if type(x) in (list,tuple): x = type(x)(saw(v) for v in x)
  return str(x)

def box(s, **d): # a __slots__ class; type defaults fresh per object
  def init(i, **kw):
    for k, v in d.items():
      setattr(i, k, kw[k] if k in kw else v() if type(v) is type else v)
  def show(i): return s + saw({k:getattr(i,k) for k in d})
  return type(s,(),dict(__slots__=tuple(d),__init__=init,__repr__=show))

#-- structs ----------------------------------------------------
#TYPE=Constructor = Slots
TBL =         box("TBL", rows=list, cols=None)
NUM = Num   = box("NUM", at=0, txt=" ", n=0, mu=0, m2=0, sd=0, goal=1)
SYM = Sym   = box("SYM", at=0, txt=" ", n=0, has=dict)
ROW = Row   = box("ROW", raw=list, bins=None)
COLS = Cols = box("COLS",names=list, all=list, x=list, y=list,klass=None)
THE = The  = box("The",**{k: atom(v) 
                       for k, v in re.findall(r"-(\w+)=(\S+)", __doc__)})

the = THE()
#-- columns ----------------------------------------------------
def Col(txt=" ", at=0): # uppercase = NUM, else SYM; "-" ends a minimise
  return (Num(at=at, txt=txt, goal=txt[-1] != "-") if txt[0].isupper()
          else Sym(at=at, txt=txt))

def add(col, v): # show V to COL
  if v == "?": return
  col.n += 1
  if type(col) is SYM: col.has[v] = col.has.get(v, 0) + 1; return
  d = v - col.mu 
  col.mu += d / col.n
  col.m2 += d * (v - col.mu)
  col.sd  = 0 if col.n < 2 else (col.m2 / (col.n - 1)) ** .5

def norm(col, v): # to 0..1, by the logistic curve
  z = (v - col.mu) / (1e-32 + col.sd)
  return 1 / (1 + exp(-1.7 * max(-3, min(3, z))))

def bin(col, v): # the one place that asks NUM or SYM
  if v == "?": return v      # skipped column, unknown
  if type(col) is SYM: return str(v)
  return min(the.Bins - 1, int(the.Bins * norm(col, v))) / the.Bins

#-- tables -----------------------------------------------------
def Cols(names): # COLS from a header: X skip, +-! goal
  klass,x,y,all = None,[],[],[]
  for at, s in enumerate(names):
    if s[-1] != "X":
      col = Col(s, at); all += [col]
      if s[-1]=="!": klass = col
      (y if s[-1] in "+-!" else x).append(col)
  return COLS(names=names, x=x, y=y, all=all, klass=klass)

def Tbl(src): # an empty TBL
  src = iter(src)
  tbl = TBL(cols = Cols(next(src).raw))
  for row in src: addRow(tbl,row)
  return tbl

def addRow(tbl, row): # keep ROW; show its raw cells to my columns
  tbl.rows += [row]
  for col in tbl.cols.all: add(col, row.raw[col.at])

def clone(tbl, rows=None): # an empty copy of TBL, plus ROWS (bins kept)
  return Tbl([Row(raw=tbl.cols.names)] + (rows or []))

def binRow(tbl, row): # discretize ROW by TBL's cols (train's, at test)
  row.bins = {col.at: bin(col, row.raw[col.at]) for col in tbl.cols.all}
  return row

def bins(tbl):
  for row in tbl.rows: binRow(tbl, row)

def split(tbl, p=.5): # shuffle, then the first p as train, rest as test
  rows = tbl.rows[:]
  random.shuffle(rows)
  m = int(p * len(rows))
  return clone(tbl, rows[:m]), clone(tbl, rows[m:])

#-- distance ---------------------------------------------------
def dist(vs, n): return sqrt(sum(v*v for v in vs) / n)

def ydist(tbl, row): # how far ROW's goals are from the best they could be
  return dist((abs(norm(col, row.raw[col.at]) - col.goal)
               for col in tbl.cols.y), len(tbl.cols.y))

def xdist(tbl,row1,row2):
  return dist((_xdist(col, row1.raw[col.at], row2.raw[col.at])
              for col in tbl.cols.x), len(tbl.cols.x))

def _xdist(col,a, b): # squared gap, in bin widths
  if a == "?" or b == "?": return 1
  if type(col) is SYM: return a != b
  a, b = norm(col,a), norm(col,b)
  return a - b

#-- classify ---------------------------------------------------
def nb(tbl, rows, klass): # naive bayes on bins: class = KLASS(row)
  n, f = {}, {}                             # n[class], f[class,at,bin]
  for r in rows:
    k = klass(r); n[k] = n.get(k, 0) + 1
    for c in tbl.cols.x:
      if (b := r.bins[c.at]) != "?": f[k,c.at,b] = f.get((k,c.at,b), 0) + 1
  def guess(row): # most likely class; m-estimate (m=2) per bin
    def like(k):
      return log(n[k] / len(rows)) + sum(
        log((f.get((k,c.at,row.bins[c.at]), 0) + 2/the.Bins) / (n[k] + 2))
        for c in tbl.cols.x if row.bins[c.at] != "?")
    return max(n, key=like)
  return guess

#-- report -----------------------------------------------------
def abcd(pairs): # (guess,actual) pairs -> a row per class, best pd first
  n, got, want, hit = 0, {}, {}, {}
  for g,a in pairs:
    n += 1
    got[g]  = got.get(g,0)  + 1
    want[a] = want.get(a,0) + 1
    hit[g]  = hit.get(g,0)  + (g==a)
  print("   n,  tn,  fn,  fp,  tp, acc, pre,  pf,  pd, class")
  out = []
  for x in want:
    tp = hit.get(x,0)
    fp = got.get(x,0) - tp
    fn = want[x] - tp
    tn = n - fn - fp - tp
    out += [(want[x], tn, fn, fp, tp, pc(tn+tp,n), pc(tp,fp+tp),
             pc(fp,tn+fp), pc(tp,fn+tp), x)]
  for r in sorted(out, key=lambda r: -r[8]):
    print(("%4d,"*9 + " %s") % r)

def pc(x,y): return 100*x/y if y else 0

#-- main ----------------------------------------------------
def eg_h(): print(__doc__)         # --h : the usage text above

def near(tbl, row):   # the labelled row that looks most like this one
  return min(tbl.rows, key=lambda r: xdist(tbl, r, row))

def eg_rank(): # --rank : label Stop, shortlist Check, report the truth
  t = Tbl(some(the.File, the.Any) if the.Any else csv(the.File))
  rows = t.rows[:]
  random.shuffle(rows)
  k = the.Stop - the.Check               # team A pays for this many
  todo, train = rows[k:], clone(t, rows[:k])
  look = (random.sample(todo, the.Rand) if the.Rand else      # no model
          sorted(todo, key=lambda r: ydist(train, near(train, r)))
          [:the.Check])
  pick = min(look, key=lambda r: ydist(t, r))        # what team B pays
  ys = sorted(ydist(t, r) for r in todo) # what we could not have known
  print(f"{the.File.split('/')[-1]}: {k}+{the.Check} labels,"
        f" rank {int(100 * ys.index(ydist(t, pick)) / len(ys))}%"
        f" of {len(todo)}")

def eg_nb(): # --nb : train on half, guess the rest, score it
  t = Tbl(csv(the.File))
  train, test = split(t, the.Train)
  bins(train)                            # train's bins, from train
  klass = lambda row: row.raw[t.cols.klass.at]
  guess = nb(train, train.rows, klass)
  pairs = [(guess(binRow(train, row)), klass(row)) for row in test.rows]
  ok = sum(g == a for g, a in pairs)
  print(f"$ {the.File.split('/')[-1]}: {len(train.cols.klass.has)} classes,"
        f" {len(train.rows)} train, {len(pairs)} guesses,"
        f" {100*ok//len(pairs)}% right")
  abcd(pairs)

def run(fun): # FUN sees the options main parsed; undo its edits after
  b4 = {k: getattr(the, k) for k in the.__slots__}
  random.seed(the.Seed)
  try: fun()
  except Exception as e: traceback.print_exception(e); return 1
  finally: [setattr(the, k, v) for k, v in b4.items()]
  return 0

def main(args):
  funs = {k:f for k,f in globals().items() if k[:3] == "eg_"}
  out = 0
  while args:
    s = args.pop(0)
    if   "eg_" + s.lstrip("-") in funs:  # -nb or --nb runs eg_nb
      out += run(funs["eg_" + s.lstrip("-")])
    elif hasattr(the, s[1:]): setattr(the, s[1:], atom(args.pop(0)))
    else: print(f"unknown arg: {s}")
  sys.exit(out)

if __name__=="__main__": main(sys.argv[1:] or ["-h"])
