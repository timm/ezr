#!/usr/bin/env python3 -B
"""textmine.py: complement naive bayes + active learning"""
import random, statistics
from math import log
from collections import defaultdict
from ez_class import (Data, Row, csv, main, align,
                      the, say, filename, eg_B, eg_s)
from prep     import dataFromPrep

#---- CNB core --------------------------------------------------------
def cnb(data:Data, rows:list=None,
        alpha:float=1.0) -> dict:
  rows, key = rows or data.rows, data.cols.klass
  freq = defaultdict(lambda:defaultdict(float))
  total, klasses = defaultdict(float), set()
  for r in rows:
    k=r[key]; klasses.add(k)
    for at in data.cols.x:
      try: v=float(r[at]) if r[at]!="?" else 0
      except ValueError: v=0
      freq[k][at]+=v; total[at]+=v
  T,n,ws = sum(total.values()), len(data.cols.x), {}
  for k in klasses:
    den=T+n*alpha-sum(freq[k].values())+1e-32
    ws[k]={a:-log((total[a]+alpha
      -freq[k].get(a,0)+1e-32)/den) for a in total}
  if the.Norm:
    ws={k:{a:v/(sum(abs(x) for x in w.values())
           or 1e-32) for a,v in w.items()}
        for k,w in ws.items()}
  return ws

def cnbLike(ws:dict, at:int, row:Row,
            k:str) -> float:
  try: v=float(row[at]) if row[at]!="?" else 0
  except ValueError: return 0
  return v * ws[k].get(at, 0)

def cnbLikes(ws:dict, data:Data, row:Row,
             k:str) -> float:
  return sum(cnbLike(ws,at,row,k) for at in data.cols.x)

#---- helpers ---------------------------------------------------------
def _setup(src:str) -> tuple:
  data=(Data(csv(src)) if isinstance(src,str)
        else dataFromPrep(src))
  key=data.cols.klass
  pos=[i for i,r in enumerate(data.rows)
       if r[key]=="yes"]
  return data, key, pos, set(range(len(data.rows)))

def _best(ws:dict, data:Data, r:Row) -> str:
  return max(ws, key=lambda k:cnbLikes(ws,data,r,k))

def _recall(ws:dict, data:Data, key:int) -> int:
  ps=[r for r in data.rows if r[key]=="yes"]
  if not ps: return 0
  return int(100*sum(
    _best(ws,data,r)=="yes" for r in ps)/len(ps))

def _iqr(vs:list) -> float:
  qs=statistics.quantiles(vs,n=4); return qs[2]-qs[0]

def _warm(pos:list, idx:set) -> set:
  ti=random.sample(pos,min(the.yes,len(pos)))
  rest=list(idx-set(ti))
  return set(ti+random.sample(rest,min(the.no,len(rest))))

#---- random baseline -------------------------------------------------
def text_mining(src:str) -> bool:
  data,key,pos,idx=_setup(src)
  out=[_recall(cnb(data,[data.rows[i] for i in
       _warm(pos,idx)]),data,key)
       for _ in range(the.valid)]
  md=statistics.median(out)
  print(f"Random {the.yes}+/{the.no}-: "
        f"pd={md} iqr={_iqr(out) if len(out)>1 else 0}")
  return True

#---- active learning -------------------------------------------------
def active(src:str) -> bool:
  data,key,pos,idx=_setup(src)
  trails=[]
  for _ in range(the.valid):
    lab=_warm(pos,idx); pool=idx-lab; trail=[]
    while True:
      ws=cnb(data,[data.rows[i] for i in lab])
      trail.append(_recall(ws,data,key))
      if len(lab)>=the.Budget or not pool: break
      pick=max(pool, key=lambda i:
        cnbLikes(ws,data,data.rows[i],"yes"))
      lab.add(pick); pool.discard(pick)
    trails.append(trail)
  n=min(len(t) for t in trails)
  w0=the.yes+the.no
  print(f"\n{'='*40}\nActive CNB {the.valid}x "
        f"warm={w0} B={the.Budget}\n{'='*40}")
  rows=[["labeled","pd","iqr"]]
  for s in range(n):
    vs=[t[s] for t in trails]; md=statistics.median(vs)
    rows.append([w0+s,md,_iqr(vs) if len(vs)>1 else 0])
  align(rows); return True

#---- setters ---------------------------------------------------------
def eg_N(n:int): the.Norm=n
def eg_y(n:int): the.yes=n
def eg_Y(n:int): the.no=n
def eg_v(n:int): the.valid=n

#---- demos -----------------------------------------------------------
def eg__like(file:filename):
  "show CNB scores for first 5 rows"
  data=Data(csv(file)); ws=cnb(data)
  rows=[["want","got","score"]]
  for r in data.rows[:5]:
    got=_best(ws,data,r)
    sc=max(cnbLikes(ws,data,r,k) for k in ws)
    rows.append([r[data.cols.klass],got,round(sc,2)])
  align(rows)

def eg__sweep(file:filename):
  "vary sample size: 10, 20, 40"
  for y in [10, 20, 40]:
    the.yes=the.no=y; text_mining(file)

def eg__file(file:filename):
  "random baseline evaluation"
  return text_mining(file)

def eg__active(file:filename):
  "active learning: warm start then acquire to budget"
  return active(file)

if __name__=="__main__": main(globals())