#!/usr/bin/env python3 -B
from ezr.data import *
import math
import re
import os
import heapq

#--------------------------------------------------------------------
def load(f:str) -> set:
  try:
    with open(f) as f: return set(w.strip().lower() for w in f if w.strip())
  except: return set()

def stem(w:str, sufs:list, cache:dict={}, max_iter:int=1) -> str:
  "recursive stemmer with caching and iteration limit"
  if w in cache: return cache[w]
  if max_iter <= 0: return cache.setdefault(w, w)
  
  original = w
  for s in sufs:
    if w.endswith(s) and len(w) > len(s) + 2:
      candidate = w[:-len(s)]
      # Prevent over-stemming: ensure reasonable stem length
      if len(candidate) >= 2 and len(candidate) >= len(w) * 0.5:
        # Recursively stem the candidate
        result = stem(candidate, sufs, cache, max_iter - 1)
        return cache.setdefault(original, result)
  return cache.setdefault(original, w)

def tokenize(txt:str, stops:set, sufs:list, cache:dict={}) -> list:
  "tokenize and stem text with shared cache"
  words = re.findall(r'\b[a-zA-Z]+\b', txt.lower())
  return [stem(w, sufs, cache) for w in words 
          if len(w) > 2 and w not in stops]

#--------------------------------------------------------------------
def Prep(stops="sh/stop_words.txt", sufs="sh/suffixes.txt") -> o:
  "create text preprocessor"
  # Load and deduplicate suffixes, sort by length (longest first)
  raw_suffixes = load(sufs)
  suffixes = sorted(list(set(raw_suffixes)), key=len, reverse=True)
  return o(it=Prep, stops=load(stops), sufs=suffixes,
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

def compute(prep:o, top_k:int=100):
  "compute term frequencies and TF-IDF with optimized top-k selection"
  # Shared cache across all documents for better performance
  stem_cache = {}
  
  # Count terms per doc and doc frequency
  for doc in prep.docs:
    tokens = tokenize(doc.txt, prep.stops, prep.sufs, stem_cache)
    counts = {}
    for t in tokens:
      counts[t] = counts.get(t, 0) + 1
    # Increment DF only once per document per word
    for t in counts:
      prep.df[t] = prep.df.get(t, 0) + 1
    prep.tf.append(counts)
  
  # Simple TF-IDF computation (like NLTK approach)
  N = len(prep.docs)
  prep.tfidf = {}
  
  # Calculate all TF-IDF scores first
  word_scores = []
  for word, df in prep.df.items():
    # Compute TF-IDF score for this word
    score = sum(c.get(word, 0) * math.log(N / df) for c in prep.tf if word in c)
    word_scores.append((word, score))
  
  # Sort and take top k (like NLTK does)
  word_scores.sort(key=lambda x: x[1], reverse=True)
  prep.top = word_scores[:top_k]
  
  # Store only top k TF-IDF values
  prep.tfidf = {word: score for word, score in prep.top}

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

#--------------------------------------------------------------------
def eg__prep(file:str="../moot/text_mining/reading/processed/Hall.csv"):
  "test text preprocessor"
  prep = Prep()
  loadData(prep, Data(csv(file)))
  compute(prep)
  save(prep)
  return prep

def eg__prep_hall():
  "test text preprocessor with Hall dataset"
  return eg__prep("../moot/text_mining/reading/raw/Hall.csv")

def eg__prep_radjenovic():
  "test text preprocessor with Radjenovic dataset"
  return eg__prep("../moot/text_mining/reading/raw/Radjenovic.csv")

def eg__prep_kitchenham():
  "test text preprocessor with Kitchenham dataset"
  return eg__prep("../moot/text_mining/reading/raw/Kitchenham.csv")

def eg__prep_wahono():
  "test text preprocessor with Wahono dataset"
  return eg__prep("../moot/text_mining/reading/raw/Wahono.csv")


# ================================================================================
# SUMMARY RESULTS
# ================================================================================
# Dataset         Texts    NLTK(s)    EZR(s)     Speedup   
# --------------------------------------------------------------------------------
# Hall            8911     13.8037    4.6827     2.95      x
# Kitchenham      1700     2.2862     0.5279     4.33      x
# Wahono          7002     12.0579    3.7675     3.20      x
# Radjenovic      6000     9.1057     2.7897     3.26      x
# --------------------------------------------------------------------------------
# Average speedup across all datasets: 3.44x

# ================================================================================