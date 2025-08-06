#!/usr/bin/env python3 -B
from ezr.data import *
import math

#--------------------------------------------------------------------
def load(f:str) -> set:
  "load words from file"
  try:
    with open(f) as f: return set(w.strip().lower() for w in f if w.strip())
  except: return set()

def stem(w:str, sufs:list) -> str:
  "stem word by removing longest suffix"
  for s in sufs:
    if w.endswith(s) and len(w) > len(s) + 2: return w[:-len(s)]
  return w

def tokenize(txt:str, stops:set, sufs:list) -> list:
  "tokenize and stem text"
  return [stem(w, sufs) for w in txt.lower().split() 
          if w.isalpha() and len(w) > 2 and w not in stops]

#--------------------------------------------------------------------
def Prep(stops="etc/stop_words.txt", sufs="etc/suffixes.txt") -> o:
  "create text preprocessor"
  return o(it=Prep, stops=load(stops), sufs=sorted(load(sufs), key=len, reverse=True),
           docs=[], tf=[], df={}, tfidf={}, top=[])

def addDoc(prep:o, txt:str, klass:str):
  "add document to preprocessor"
  prep.docs.append(o(txt=txt, klass=klass))

def loadData(prep:o, data:o, txt_col="text", klass_col="klass"):
  "load documents from EZR data"
  txt_idx = data.cols.names.index(txt_col)
  klass_idx = data.cols.names.index(klass_col)
  for row in data.rows:
    addDoc(prep, str(row[txt_idx]), str(row[klass_idx]))

def compute(prep:o):
  "compute term frequencies and TF-IDF"
  # Count terms per doc and doc frequency
  for doc in prep.docs:
    tokens = tokenize(doc.txt, prep.stops, prep.sufs)
    counts = {}
    for t in tokens:
      counts[t] = counts.get(t, 0) + 1
    # Increment DF only once per document per word
    for t in counts:
      prep.df[t] = prep.df.get(t, 0) + 1
    prep.tf.append(counts)
  
  # Compute TF-IDF
  N = len(prep.docs)
  for word in prep.df:
    prep.tfidf[word] = sum(c.get(word, 0) * math.log(N / prep.df[word]) 
                          for c in prep.tf if word in c)
  
  # Get top 50 words
  prep.top = sorted(prep.tfidf.items(), key=lambda x: x[1], reverse=True)[:50]

def features(prep:o) -> o:
  "create EZR Data object with features"
  header = ['klass!'] + [w.capitalize() for w, _ in prep.top]
  rows = []
  for doc, doc_tf in zip(prep.docs, prep.tf):
    row = [doc.klass]
    for word, _ in prep.top:
      row.append(doc_tf.get(word, 0))
    rows.append(row)
  return Data([header] + rows)

def save(prep:o, f="preprocessed.csv"):
  "save results to CSV"
  with open(f, 'w') as f:
    # Use 'klass!' to mark it as the class column for EZR
    header = ['klass!'] + [w.capitalize() for w, _ in prep.top]
    f.write(','.join(header) + '\n')
    for doc, doc_tf in zip(prep.docs, prep.tf):
      row = [doc.klass]
      for word, _ in prep.top:
        row.append(str(doc_tf.get(word, 0)))
      f.write(','.join(row) + '\n')