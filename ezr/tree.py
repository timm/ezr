#!/usr/bin/env python3 -B
import ez
from ez import (BIG,OBJ,DATA,NUM,SYM,the,
  add,adds,csv,clone,disty,main,o,sd,shuffle, filename)

def selects(rows, at, fn):
  lo, hi = [], []
  for r in rows:
    if (v := r[at]) != "?": (lo if fn(v) else hi).append(r)
  return ((lo,hi) if len(lo) >= the.leaf and len(hi) >= the.leaf
                  else (None,None))

def splits(col, rows):
  at = col.at
  if SYM is col.it:
    for v in set(r[at] for r in rows if r[at]!="?"):
      lo,hi = selects(rows,at,lambda x,v=v: x==v)
      if lo: yield v, lo, hi
  else:
    vals = sorted(r[at] for r in rows if r[at]!="?")
    if len(vals) >= 2:
      med = vals[len(vals)//2]
      lo,hi = selects(rows,at,lambda x: x<=med)
      if lo: yield med, lo, hi

def _w(data,rows): 
  return len(rows)*sd(adds(disty(data,r) for r in rows))

def tree(data, rows):
  if len(rows) >= 2*the.leaf:
    if b := min(
       (OBJ(col=c,cut=cut,lo=lo,hi=hi)
        for c in data.cols.x
        for cut,lo,hi in splits(c,rows)),
       key=lambda b: _w(data,b.lo)+_w(data,b.hi),
       default=None):
      return OBJ(col=b.col, cut=b.cut,
                 lo=tree(data,b.lo),
                 hi=tree(data,b.hi))
  return OBJ(y=adds(disty(data,r) for r in rows))
 
def treeLeaf(t, row):
  if c := t.get('col'):
    v = row[c.at]
    if v == "?": return treeLeaf(t.lo, row)
    if SYM is c.it: kid = t.lo if v==t.cut else t.hi
    else:           kid = t.lo if v<=t.cut else t.hi
    return treeLeaf(kid, row)
  return t

def treeShow(t, lvl=0, pre=""):
  s = f"{'|.. '*(lvl-1)}{pre}" if pre else ""
  if c := t.get('col'):
    if pre: print(s)
    op = '==' if SYM is c.it else '<='
    no = '!=' if SYM is c.it else '>'
    treeShow(t.lo,lvl+1,f"{c.txt} {op} {o(t.cut)}")
    treeShow(t.hi,lvl+1,f"{c.txt} {no} {o(t.cut)}")
  else:
    print(f"{s:{the.Show}} {o(t.y.mu):>6} ({t.y.n})")
   
#-------------------------------------------------
def eg__tree(f: filename):
  "treeing"
  data = DATA(csv(f))
  data1 = clone(data,
                shuffle(data.rows)[:the.Budget])
  treeShow(tree(data1, data1.rows))

def eg__test(f: filename):
  "testing"
  data = DATA(csv(f))
  half = len(data.rows)//2
  Y = lambda r: disty(data,r)
  b4 = sorted(Y(r) for r in data.rows)
  win = lambda r: int(
    100*(1-(Y(r)-b4[0])/(b4[half]-b4[0]+1E-6)))
  wins = NUM()
  for _ in range(60):
    rows = shuffle(data.rows)
    test = rows[half:]
    train = rows[:half][:the.Budget]
    t = tree(clone(data,train), train)
    test.sort(key=lambda r: treeLeaf(t,r).y.mu)
    add(wins, win(min(test[:the.Check], key=Y)))
  print(f"{round(wins.mu)}"
        f" ,sd {round(sd(wins))}"
        f" ,b4 {o(b4[half])}"
        f" ,lo {o(b4[0])}"
        f" ,B {the.Budget}",
    *[f"{s} {len(a)}" for s,a in
      dict(x=data.cols.x, y=data.cols.y,
           r=data.rows).items()],
    *f.split("/")[-2:], sep=" ,")

if __name__=="__main__": main(the,globals())
