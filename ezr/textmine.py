#!/usr/bin/env python3 -B
"""textmine.py: complement naive bayes"""
import random, statistics
from math import log
from collections import defaultdict
from ez    import Data, O, csv, main, align, the
from stats import Confuse, confuse, confused
from prep  import dataFromPrep

def cnbStats(data, rows=None):
  rows=rows or data.rows
  st=O(f=defaultdict(lambda:defaultdict(int))
       ,t=defaultdict(int), c=defaultdict(int)
       ,n=len(data.cols.x), k=set())
  key=data.cols.klass.at
  for r in rows:
    k=r[key]; st.k.add(k); st.c[k]+=1
    for col in data.cols.x:
      v,a=r[col.at],col.at
      try:
        n=float(v) if v!="?" else 0
        st.f[k][a]+=n; st.t[a]+=n
      except ValueError: pass
  return st

def cnbWeights(st, alpha=1.0, norm=False):
  T=sum(st.t.values()); ws={}
  for k in st.k:
    den=T+st.n*alpha-sum(st.f[k].values())+1e-32
    ws[k]={c:log((st.t[c]+alpha-st.f[k].get(c,0)
      +1e-32)/den) for c in st.t}
  if norm:
    return {k:{c:v/(sum(w.values()) or 1e-32)
               for c,v in w.items()}
            for k,w in ws.items()}
  return {k:{c:-v for c,v in w.items()}
          for k,w in ws.items()}

def cnbClassify(ws, row, data):
  def v(c,w):
    try: return float(row[c.at])*w.get(c.at,0) if row[c.at]!="?" else 0
    except ValueError: return 0
  return max(ws, key=lambda k:sum(v(c,ws[k]) for c in data.cols.x))

def _run1(data, key, n, pos, idx):
  ti=random.sample(pos,min(n,len(pos)))
  rest=list(idx-set(ti))
  tr=[data.rows[i] for i in ti+random.sample(rest,min(n,len(rest)))]
  ws=cnbWeights(cnbStats(data,tr),norm=the.Norm)
  cf=Confuse()
  [confuse(cf,str(r[key]),str(cnbClassify(ws,r,data))) for r in data.rows]
  c=next(c for c in confused(cf) if c.label=="yes")
  return dict(pd=c.pd,prec=c.prec,pf=c.pf,acc=c.acc)

def _report(out, n, reps):
  print(f"\n{'='*40}\nCNB {reps}x {n}+/{n}- norm={the.Norm}\n{'='*40}")
  rows=[["metric","median","iqr"]]
  for k in "pd prec pf acc".split():
    vs=[r[k] for r in out]
    qs=statistics.quantiles(vs,n=4)
    rows.append([k,statistics.median(vs),qs[2]-qs[0]])
  align(rows)

def text_mining(src, reps=5):
  n=the.Budget
  data=(Data(csv(src)) if isinstance(src,str)
        else dataFromPrep(src))
  key=data.cols.klass.at
  pos=[i for i,r in enumerate(data.rows) if r[key]=="yes"]
  idx=set(range(len(data.rows)))
  out=[_run1(data,key,n,pos,idx) for _ in range(reps)]
  _report(out,n,reps); return True

def eg__cnb(file:str):
  "CNB text mining"
  return text_mining(file)

if __name__=="__main__": main(globals())