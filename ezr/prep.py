#!/usr/bin/env python3 -B
"""prep.py: text preprocessing for text mining"""
import re, math
from pathlib import Path
from types import SimpleNamespace as o
from typing import Iterable
from ez import (Data, Val, cast, main, align,
                      the, filename)

_DIR = Path(__file__).parent

def prepare(f:str) -> o:
  return tfidf(stem(nostop(tokenize(f))))

#---- resources -------------------------------------------------------
def _load(pkg:str) -> set:
  try: s = (_DIR / pkg).read_text()
  except Exception: s = ""
  return {w.strip().lower() for w in s.splitlines() if w.strip()}

def _stem1(w:str, sufs:list, cache:dict, n:int=1) -> str:
  if w in cache or n <= 0: return cache.setdefault(w, w)
  for s in sufs:
    if w.endswith(s) and len(w) > len(s) + 2:
      c = w[:-len(s)]
      if len(c) >= 2 and len(c) >= len(w) * .5:
        return cache.setdefault(w, _stem1(c, sufs, cache, n-1))
  return cache.setdefault(w, w)

#---- csv with quote-aware parsing ------------------------------------
def _cells(s:str) -> list[str]:
  r,c,q=[],[],0
  for ch in s:
    if   ch=='"' and (not c or q): q^=1
    elif q<1 and ch==',': r+=[''.join(c)]; c=[]
    else:                  c+=[ch]
  return r+[''.join(c)]

def _csv(f:str) -> Iterable[list[Val]]:
  with open(f, encoding="utf-8") as fh:
    for s in fh:
      r = _cells(s)
      if any(x.strip() for x in r):
        yield [cast(x.strip()) for x in r]

#---- pipeline --------------------------------------------------------
def tokenize(f:str, txt:str="abstract",
             klass:str="label") -> o:
  p = o(docs=[], tf=[], df={}, tfidf={}, top=[])
  rows = _csv(f); hdr = next(rows)
  assert txt in hdr, f"need '{txt}' col (raw CSV?)"
  t, k = hdr.index(txt), hdr.index(klass)
  for r in rows:
    ws = [w for w in re.findall(r'\b[a-zA-Z]+\b',
          str(r[t]).lower()) if len(w) > 2]
    p.docs.append(o(words=ws, klass=str(r[k])))
  return p

def nostop(p:o) -> o:
  s = _load("resources/text/stop_words.txt")
  for d in p.docs: d.words=[w for w in d.words if w not in s]
  return p

def stem(p:o) -> o:
  sufs = sorted(_load("resources/text/suffixes.txt"),
                key=len, reverse=True)
  cache = {}
  for d in p.docs: d.words=[_stem1(w,sufs,cache) for w in d.words]
  return p

def tfidf(p:o) -> o:
  for d in p.docs:
    c = {}
    for t in d.words: c[t] = c.get(t, 0) + 1
    for t in c: p.df[t] = p.df.get(t, 0) + 1
    p.tf.append(c)
  N = len(p.docs) or 1
  ws = sorted([(w, sum(c.get(w, 0) * math.log(N / df)
                for c in p.tf if w in c))
               for w, df in p.df.items()],
              key=lambda x: x[1], reverse=True)[:the.Top]
  p.top, p.tfidf = ws, {w: s for w, s in ws}
  return p

def dataFromPrep(p:o) -> Data:
  ws = list(p.tfidf) or sorted(
    {w for c in p.tf for w in c})[:the.Top]
  return Data(
    [[w.capitalize() for w in ws] + ["klass!"]]
    + [[tf.get(w, 0) for w in ws] + [d.klass]
       for tf, d in zip(p.tf, p.docs)])

#---- demos -----------------------------------------------------------
def eg__tokenize(file:filename):
  assert (p:=tokenize(file)), "crash in eg__tokenize"
  print(f"{len(p.docs)} docs")
  for d in p.docs[:3]: print(d.words[:8])

def eg__nostop(file:filename):
  p=tokenize(file); b=p.docs[0].words[:12][:]
  assert nostop(p), "crash in eg__nostop"
  gone=[w for w in b if w not in p.docs[0].words]
  print(f"removed: {gone}")
  print(f"before:  {b}")
  print(f"after:   {p.docs[0].words[:12]}")

def eg__stem(file:filename):
  p=nostop(tokenize(file)); b=p.docs[0].words[:8][:]
  assert stem(p), "crash in eg__stem"
  for a,b in zip(b, p.docs[0].words[:8]):
    print(f"{a} -> {b}")

def eg__tfidf(file:filename):
  assert (p:=prepare(file)), "crash in eg__tfidf"
  align([[w, round(s, 2)] for w, s in p.top[:20]])

def eg_T(n:int): the.Top=n

if __name__ == "__main__": main(globals())