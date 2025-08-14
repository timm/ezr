#!/usr/bin/env python3 -B
from ezr.tree import *
from ezr.stats import *
from ezr.likely import *
from ezr.prep import *
from ezr.data import *
from ezr.lib import *
import random

#------------------------------------------------------------------------------------------------
def load_dataset(dataset_file, text_col="Abstract", class_col="label"):
  prep = Prep(); rows = list(csv(dataset_file))
  if rows:
    ti, ki = rows[0].index(text_col), rows[0].index(class_col)
    [addDoc(prep, str(r[ti]), str(r[ki])) for r in rows[1:]
      if len(r) > ti and len(r) > ki and r[ti] != "?" and r[ki] != "?"]
    compute(prep)
  return prep

def evaluate_model(train_data, test_data, positive_class="yes"):
  cf = Confuse(); d = {}; k = train_data.cols.klass.at
  for r in train_data.rows:
    w = r[k]; d[w] = d.get(w) or clone(train_data); add(d[w], r)
  n = len(train_data.rows)
  [confuse(cf, r[k], likeBest(d, r, n)) for r in test_data.rows]
  for r in confused(cf):
    if r.label == positive_class:
      return (r.prec/100, r.pd/100, r.pf/100, r.acc/100)
  return (0,0,0,0)

def create_training_subset(full_data, labeled_docs, all_docs):
  S = {(d.txt, d.klass) for d in labeled_docs}
  t = clone(full_data)
  [add(t, full_data.rows[i]) for i,d in enumerate(all_docs)
    if (d.txt, d.klass) in S and i < len(full_data.rows)]
  return t

def active_learning_loop(prep, n_pos=8, repeats=5, batch_size=1000):
  pos, neg = [], []
  [(pos if d.klass == "yes" else neg).append(d) for d in prep.docs]
  if len(pos) < n_pos or len(neg) < n_pos * 4: return []
  full = features(prep); R = []
  for _ in range(repeats):
    L = random.sample(pos, n_pos) + random.sample(neg, n_pos * 4)
    P = [d for d in prep.docs if d not in L]
    S = []; T = create_training_subset(full, L, prep.docs)
    S.append(evaluate_model(T, full))
    acq = 0
    while P:
      b = min(batch_size, len(P)); A = random.sample(P, b)
      P = [d for d in P if d not in A]; L.extend(A)
      T = create_training_subset(full, L, prep.docs); acq += b
      S.append(evaluate_model(T, full) if acq % batch_size == 0 else (0,0,0,0))
    S.append(evaluate_model(T, full)); R.append(S)
  return R

def active_learning_text_mining(dataset_file, text_col="Abstract", class_col="label", n_pos=8, repeats=10, batch_size=1000):
  pout(f"Loading dataset: {dataset_file}")
  prep = load_dataset(dataset_file, text_col, class_col)
  if prep is None: return
  pout(f"Loaded {len(prep.docs)} documents")
  pout("Starting active learning loop...")
  results = active_learning_loop(prep, n_pos=n_pos, repeats=repeats, batch_size=batch_size)
  if results:
    steps = sorted({i for rr in results for i in range(len(rr))})
    pout(f"\nResults@step (avg of {len(results)}) for {dataset_file} with {n_pos} pos & {n_pos * 4} neg:")
    pout("-" * 70)
    pout(f"{'Step':<12} {'Precision':<10} {'Recall':<8} {'False_Alarm':<12} {'Accuracy':<10} {'Samples':<8}")
    pout("-" * 70)
    init = n_pos + n_pos * 4
    for i in steps:
      sr = [rr[i] for rr in results if rr and i < len(rr)]
      if sr and any(any(x) for x in sr):
        a = [sum(x[j] for x in sr)/len(sr) for j in range(4)]
        if i == 0: lab, s = "Initial", init
        elif i == len(steps) - 1: lab, s = "Final", len(prep.docs)
        else: acq = i * batch_size; lab, s = f"Step {acq}", init + acq
        pout(f"{lab:<12} {a[0]:<10.4f} {a[1]:<8.4f} {a[2]:<12.2f}% {a[3]:<10.4f} {s:<8}")
  return results

#------------------------------------------------------------------------------------------------
def eg__al_uncertainty_hall():
  "SLOW: run uncertainty-based active learning on Hall dataset"
  active_learning_text_mining("../moot/text_mining/reading/raw/Hall.csv", n_pos=8, repeats=10, batch_size=1000)

def eg__al_uncertainty_kit():
  "SLOW: run uncertainty-based active learning on Kitchenham dataset"
  active_learning_text_mining("../moot/text_mining/reading/raw/Kitchenham.csv", n_pos=8, repeats=10, batch_size=100)

def eg__al_uncertainty_rad():
  "SLOW: run uncertainty-based active learning on Radjenovic dataset"
  active_learning_text_mining("../moot/text_mining/reading/raw/Radjenovic.csv", n_pos=8, repeats=10, batch_size=1000)

def eg__al_uncertainty_wah():
  "SLOW: run uncertainty-based active learning on Wahono dataset"
  active_learning_text_mining("../moot/text_mining/reading/raw/Wahono.csv", n_pos=8, repeats=10, batch_size=1000)