#!/usr/bin/env python3 -B
"""prep.py: text preprocessing for text mining"""
import re, math, csv as CSV
from pathlib import Path
from ez import Data, O, main

_DIR=Path(__file__).parent

def load(path=None, pkg=""):
  try: s=open(path).read() if path else (_DIR/pkg).read_text()
  except Exception: s=""
  return {w.strip().lower() for w in s.splitlines() if w.strip()}

def stem(w, sufs, cache, n=1):
  if w in cache or n<=0: return cache.setdefault(w,w)
  for s in sufs:
    if w.endswith(s) and len(w)>len(s)+2:
      c=w[:-len(s)]
      if len(c)>=2 and len(c)>=len(w)*.5:
        return cache.setdefault(w,stem(c,sufs,cache,n-1))
  return cache.setdefault(w,w)

def tokenize(txt, stops, sufs, cache):
  return [stem(w,sufs,cache)
          for w in re.findall(r'\b[a-zA-Z]+\b',txt.lower())
          if len(w)>2 and w not in stops]

def Prep(stops=None, sufs=None):
  ws=load(stops,"resources/text/stop_words.txt")
  sx=sorted(load(sufs,"resources/text/suffixes.txt"),
            key=len, reverse=True)
  return O(it=Prep, stops=ws, sufs=sx,
           docs=[], tf=[], df={}, tfidf={}, top=[])

def loadRaw(p, f, txt_col="abstract",
            klass_col="label"):
  with open(f, encoding="utf-8") as fh:
    rows=CSV.reader(fh); hdr=next(rows)
    assert txt_col in hdr, (
      f"need '{txt_col}' col (raw CSV?)")
    t,k=hdr.index(txt_col),hdr.index(klass_col)
    for r in rows: p.docs.append(O(txt=r[t],klass=r[k]))

def compute(p, top_k=100):
  cache={}
  for d in p.docs:
    c={}
    for t in tokenize(d.txt,p.stops,p.sufs,cache):
      c[t]=c.get(t,0)+1
    for t in c: p.df[t]=p.df.get(t,0)+1
    p.tf.append(c)
  N=len(p.docs) or 1
  ws=sorted([(w,sum(c.get(w,0)*math.log(N/df)
              for c in p.tf if w in c))
             for w,df in p.df.items()],
            key=lambda x:x[1], reverse=True)[:top_k]
  p.top, p.tfidf = ws, {w:s for w,s in ws}

def dataFromPrep(p):
  ws=list(p.tfidf) or sorted(
    {w for c in p.tf for w in c})[:100]
  return Data(
    [[w.capitalize() for w in ws]+["klass!"]]
   +[[tf.get(w,0) for w in ws]+[d.klass]
     for tf,d in zip(p.tf, p.docs)])

def prepare(f, txt="abstract", klass="label"):
  p=Prep(); loadRaw(p,f,txt,klass)
  compute(p); return p

def eg__prep(file:str):
  "preprocess file"
  return prepare(file)

if __name__=="__main__": main(globals())