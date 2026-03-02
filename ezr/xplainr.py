#!/usr/bin/env python3 -B
"""xplainr.py: rule generation from top signals
(c) 2026 Tim Menzies timm@ieee.org, MIT license

Options:
  -B Bpc=2         best bins per column
  -M Maxr=5        max rule size
  -S Support=10    min rows matching a rule
  -T Top=8         top columns by signal"""
import re
from types     import SimpleNamespace as o
from ez     import Data,Num,Sym,Row,csv,adds,the,cast,main,shuffle,filename
from xplain import xplanTrain, signal, rowBin

cfg = o(**{k: cast(v) for k,v in re.findall(r"(\S+)=(\S+)", __doc__)})

def ruleMatch(d:Data, rule:dict, row:Row) -> bool:
  return all(row[at] != "?" and rowBin(d.cols.x[at], row[at]) == b
             for at,b in rule.items())

def ruleScore(d:Data, rule:dict, rows:list) -> "Num|None":
  ys = adds(d.disty(r) for r in rows if ruleMatch(d, rule, r))
  return ys if ys.seen >= cfg.Support else None

def ruleStr(d:Data, rule:dict) -> str:
  def part(at, b):
    col = d.cols.x[at]; name = d.cols.names[at]; s = col.bins[b]
    lo,hi = round(s.lo,the.decs), round(s.hi,the.decs)
    return (f"{name}={b}"    if isinstance(col,Sym) else
            f"{name}={lo}"   if lo==hi              else
            f"{name}={lo}..{hi}")
  return " and ".join(part(at,b) for at,b in sorted(rule.items()))

def rules(d:Data, train:list):
  def scored(rule):
    k = tuple(sorted(rule.items()))
    if k not in seen:
      seen.add(k)
      if ys := ruleScore(d, rule, train): return ys.mid()
  def bestBins(x, at):
    byScore = lambda b: x.bins[b].y.mid()
    return [(scored({at:b}), at, b)
            for b in sorted(x.bins, key=byScore)[:cfg.Bpc]]
  def grow(rule, spans):
    return [(s, len(seen), {**rule, at:b})
            for s0,at,b in spans if at not in rule
            if (s:=scored({**rule, at:b})) is not None]
  def top(triples):
    return sorted((t for t in triples if t[0] is not None))[:cfg.Top]

  seen = set()
  bySignal  = sorted(d.cols.x.items(), key=lambda kv: signal(kv[1]), reverse=True)
  spans     = top(t for at,x in bySignal[:cfg.Top] for t in bestBins(x,at))
  beam      = [(s, i, {at:b}) for i,(s,at,b) in enumerate(spans)]
  for s,_,rule in beam: yield s, rule
  for _ in range(2, cfg.Maxr+1):
    beam = top(t for _,_,rule in beam for t in grow(rule, spans))
    if not beam: break
    for s,_,rule in beam: yield s, rule

def report(d:Data):
  rows       = shuffle(d.rows[:])
  train,test = rows[:len(rows)//2], rows[len(rows)//2:]
  d_train    = Data([d.cols.names] + train)
  xplanTrain(d_train)
  print(f"{'train':>6}  {'test':>6}  {'n':>4}  rule")
  all_rules  = sorted((s,i,r) for i,(s,r) in enumerate(rules(d_train,train)))
  for s,_,rule in all_rules[:cfg.Top]:
    if t := ruleScore(d_train, rule, test):
      print(f"{s:>6.2f}  {t.mid():>6.2f}  {t.seen:>4}  {ruleStr(d_train,rule)}")

def eg__data(f:filename): "generate rules"; report(Data(csv(f)))
def eg_B(n:int): cfg.Bpc     = n
def eg_M(n:int): cfg.Maxr    = n
def eg_S(n:int): cfg.Support = n
def eg_T(n:int): cfg.Top     = n

if __name__ == "__main__": main(globals())
