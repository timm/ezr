#!/usr/bin/env python3 -B
"""
tm.py: text mining CNB runner and CNB/preprocessing utilities.
"""
import random, math
from ezr import *

#--------------------------------------------------------------------
def load(f:str) -> set:
  try: return set(w.strip().lower() for w in open(f) if w.strip())
  except: return set()

def stem(w:str, sufs:list, cache:dict={}, max_iter:int=1) -> str:
  if w in cache or max_iter<=0: return cache.setdefault(w,w)
  for s in sufs:
    if w.endswith(s) and len(w)>len(s)+2:
      c=w[:-len(s)]
      if len(c)>=2 and len(c)>=len(w)*.5:
        return cache.setdefault(w, stem(c,sufs,cache,max_iter-1))
  return cache.setdefault(w,w)

def tokenize(txt:str, stops:set, sufs:list, cache:dict={}) -> list:
  return [stem(w,sufs,cache) for w in re.findall(r'\b[a-zA-Z]+\b', txt.lower()) if len(w)>2 and w not in stops]

def Prep(stops="etc/stop_words.txt", sufs="etc/suffixes.txt") -> o:
  sufs=sorted(list(load(sufs)), key=len, reverse=True)
  return o(it=Prep, stops=load(stops), sufs=sufs, docs=[], tf=[], df={}, tfidf={}, top=[])

def addDoc(prep:o, txt:str, klass:str): prep.docs.append(o(txt=txt, klass=klass))

def loadData(prep:o, data:o, txt_col="text", klass_col="klass"):
  t=data.cols.names.index(txt_col); k=data.cols.names.index(klass_col)
  for r in data.rows: addDoc(prep, str(r[t]), str(r[k]))

def compute(prep:o, top_k:int=100):
  cache={}
  for d in prep.docs:
    toks=tokenize(d.txt, prep.stops, prep.sufs, cache); c={}
    for t in toks: c[t]=c.get(t,0)+1
    for t in c: prep.df[t]=prep.df.get(t,0)+1
    prep.tf.append(c)
  N=len(prep.docs); ws=[(w, sum(c.get(w,0)*math.log(N/df) for c in prep.tf if w in c)) for w,df in prep.df.items()]
  ws.sort(key=lambda x:x[1], reverse=True); prep.top=ws[:top_k]; prep.tfidf={w:s for w,s in prep.top}

#--------------------------------------------------------------------
def cnbStats(data: Data, rows=None) -> o:
  rows=rows or data.rows; st=o(f=defaultdict(lambda: defaultdict(int)), t=defaultdict(int), c=defaultdict(int), n=len(data.cols.x), k=set()); key=data.cols.klass.at
  for r in rows:
    k=r[key]; st.k.add(k); st.c[k]+=1
    for col in data.cols.x:
      v=r[col.at]
      if v!="?":
        try: n=float(v); st.f[k][col.at]+=n; st.t[col.at]+=n
        except ValueError: pass
  return st

def cnbWeights(st: o, alpha: float = 1.0, norm: bool = False):
  T=sum(st.t.values()); logs={}
  for k in st.k:
    logs[k]={}
    for c in st.t:
      num=(st.t[c]+alpha-st.f[k].get(c,0))+1e-32
      den=(T+st.n*alpha-sum(st.f[k].values()))+1e-32
      logs[k][c]=math.log(num/den)
  return ({k:{c:-lp for c,lp in lps.items()} for k,lps in logs.items()} if not norm
          else {k:{c:lp/((sum(lps.values()) or 1e-32)) for c,lp in lps.items()} for k,lps in logs.items()})

def cnbLike(row, x_cols, w):
  s=0
  for col in x_cols:
    v=row[col.at]
    if v!="?":
      try: s+=float(v)*w.get(col.at,0)
      except ValueError: pass
  return s

def cnbBest(ws, row, data):
  sc={k:cnbLike(row, data.cols.x, w) for k,w in ws.items()}
  return max(sc, key=sc.get) if sc else None

#--------------------------------------------------------------------
def text_mining(file: str, n_repeats: int = 5, norm: bool = False, n_pos: int = 20, n_neg: int = 80) -> bool:
  data=Data(csv(file)); key,idx=data.cols.klass.at, set(range(len(data.rows)))
  pos=[i for i,r in enumerate(data.rows) if r[key]=="yes"]; out=[]
  for _ in range(n_repeats):
    tp=fn=fp=tn=0; tpidx=random.sample(pos,n_pos)
    tr=[data.rows[i] for i in tpidx+random.sample(list(idx-set(tpidx)), n_neg)]
    ws=cnbWeights(cnbStats(data,tr), norm=norm)
    for r in data.rows:
      want=r[key]=="yes"; got=cnbBest(ws,r,data)=="yes"
      tp+=want and got; fn+=want and not got; fp+=(not want) and got; tn+=(not want) and not got
    safe=lambda a,b: a/b*100 if b>0 else 0
    out.append(dict(pd=safe(tp,tp+fn), prec=safe(tp,tp+fp), pf=safe(fp,fp+tn), acc=safe(tp+tn,tp+fn+fp+tn)))
  def P(v,p):
    if not v: return 0
    s,k=sorted(v),(len(v)-1)*p; f=int(math.floor(k)); c=int(math.ceil(k)); return s[f]+(s[c]-s[f])*(k-f)
  B='='*55; print(f"\n{B}\nEZR CNB RESULTS | {n_repeats} REPEATS | {n_pos} POS | {n_neg} NEG | {norm} NORM\n{B}\n\nMedian (IQR) across {n_repeats} runs:")
  for k,nm in dict(pd="Recall (pd)",prec="Precision",pf="False Alarm (pf)",acc="Accuracy").items():
    vals=[r[k] for r in out]; print(f"{nm}: {P(vals,.5):.1f} ({P(vals,.75)-P(vals,.25):.1f})%")
  print(B); return True