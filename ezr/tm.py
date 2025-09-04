#!/usr/bin/env python3 -B
from ezr.tree import *
from ezr.stats import *
from ezr.likely import *
from ezr.prep import *
from ezr.data import *
from ezr.lib import *
from ezr.cnb import *
import random

EARLY_STOPPING={
  "hall": 290,
  "kitchenham": 510,
  "radjenovic": 630,
  "wahono": 515
}

# EARLY_STOPPING={
#   "hall": 100,
#   "kitchenham": 100,
#   "radjenovic": 100,
#   "wahono": 100
# }
#------------------------------------------------------------------------------------------------
def load_dataset(dataset_file, text_col="Abstract", class_col="label"):
  prep = Prep(); rows = list(csv(dataset_file))
  if rows:
    ti, ki = rows[0].index(text_col), rows[0].index(class_col)
    [addDoc(prep, str(r[ti]), str(r[ki])) for r in rows[1:]
      if len(r) > ti and len(r) > ki and r[ti] != "?" and r[ki] != "?"]
    compute(prep)
  return prep

def evaluate_model(train_data, test_data, positive_class="yes", norm=False):
  cf = Confuse(); k = train_data.cols.klass.at
  stats = cnbStats(train_data, train_data.rows)
  weights = cnbWeights(stats, norm=norm)
  for r in test_data.rows:
    want = r[k]
    got = cnbBest(weights, r, train_data)
    confuse(cf, want, got)
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

def active_learning_loop(prep, n_pos=8, repeats=5, batch_size=1000, acq_stop=None, n_neg=None, norm=False):
  n_neg = n_neg or n_pos * 4
  pos, neg = [], []
  [(pos if d.klass == "yes" else neg).append(d) for d in prep.docs]
  if len(pos) < n_pos or len(neg) < n_neg: return []
  full = features(prep); R = []
  for _ in range(repeats):
    L = random.sample(pos, n_pos) + random.sample(neg, n_neg)
    P = [d for d in prep.docs if d not in L]
    S = []; T = create_training_subset(full, L, prep.docs)
    S.append(evaluate_model(T, full, norm=norm))
    acq = n_pos + n_neg
    while P:
      b = min(batch_size, len(P)); A = random.sample(P, b)
      P = [d for d in P if d not in A]; L.extend(A)
      T = create_training_subset(full, L, prep.docs); acq += b
      S.append(evaluate_model(T, full, norm=norm) if acq % batch_size == 0 else (0,0,0,0))
      if acq_stop is not None and acq >= acq_stop:
        break
    S.append(evaluate_model(T, full, norm=norm)); R.append(S)
  return R

def active_learning_text_mining(dataset_file, text_col="Abstract", class_col="label", n_pos=8, repeats=10, batch_size=1000, acq_stop=None, n_neg=None, norm=False):
  def _quantile(xs, q):
    xs = sorted(xs)
    n = len(xs)
    if n == 0: return 0
    if n == 1: return xs[0]
    pos = (n - 1) * q
    lo = int(pos)
    hi = min(lo + 1, n - 1)
    frac = pos - lo
    return xs[lo] * (1 - frac) + xs[hi] * frac
  def _iqr(xs):
    if not xs: return 0
    return _quantile(xs, 0.75) - _quantile(xs, 0.25)
  pout(f"Loading dataset: {dataset_file}")
  prep = load_dataset(dataset_file, text_col, class_col)
  if prep is None: return
  pout(f"Loaded {len(prep.docs)} documents")
  pout("Starting active learning loop...")
  results = active_learning_loop(prep, n_pos=n_pos, repeats=repeats, batch_size=batch_size, acq_stop=acq_stop, n_neg=n_neg, norm=norm)
  if results:
    steps = sorted({i for rr in results for i in range(len(rr))})
    n_neg_display = n_neg or n_pos * 4
    pout(f"\nResults@step (avg±IQR of {len(results)}) for {dataset_file} with {n_pos} pos & {n_neg_display} neg:")
    pout("-" * 70)
    pout(f"{'Step':<12} {'Precision':<18} {'Recall':<16} {'False_Alarm':<20} {'Accuracy':<16} {'Samples':<8}")
    pout("-" * 70)
    init = n_pos + (n_neg or n_pos * 4)
    for i in steps:
      sr = [rr[i] for rr in results if rr and i < len(rr)]
      if sr and any(any(x) for x in sr):
        cols = [[x[j] for x in sr] for j in range(4)]
        a = [sum(col)/len(col) for col in cols]
        iq = [_iqr(col) for col in cols]
        if i == 0: lab, s = "Initial", init
        elif i == len(steps) - 1: lab, s = "Final", len(prep.docs)
        else: acq = i * batch_size; lab, s = f"Step {acq}", init + acq
        # Show avg±IQR for each metric; False Alarm shown as percent
        pout(f"{lab:<12} {a[0]:.4f}±{iq[0]:.4f}   {a[1]:.4f}±{iq[1]:.4f}   {a[2]*100:.2f}%±{iq[2]*100:.2f}%   {a[3]:.4f}±{iq[3]:.4f}   {s:<8}")
  return results

#------------------------------------------------------------------------------------------------
def save_active_learning_results(results, path, initial_samples=None, batch_size=None, final_samples=None):
  """Save averaged Step, Samples, Recall (pd), and False Alarm (pf) per step to CSV.
  - Step is the step index (0 for initial, 1, 2, ...)
  - Samples uses initial_samples + Step * batch_size when provided; otherwise falls back to Step.
    If final_samples is provided, it is used for the last step.
  """
  import csv, os
  if not results: return
  steps = sorted({i for rr in results for i in range(len(rr))})
  rows = []
  for i in steps:
    sr = [rr[i] for rr in results if rr and i < len(rr)]
    if sr and any(any(x) for x in sr):
      cols = [[x[j] for x in sr] for j in range(4)]
      a = [sum(col)/len(col) for col in cols]
      # IQRs
      def _quantile(xs, q):
        xs = sorted(xs)
        n = len(xs)
        if n == 0: return 0
        if n == 1: return xs[0]
        pos = (n - 1) * q
        lo = int(pos)
        hi = min(lo + 1, n - 1)
        frac = pos - lo
        return xs[lo] * (1 - frac) + xs[hi] * frac
      def _iqr(xs):
        if not xs: return 0
        return _quantile(xs, 0.75) - _quantile(xs, 0.25)
      iq = [_iqr(col) for col in cols]
      if initial_samples is not None and batch_size is not None:
        samples = (final_samples if (final_samples is not None and i == len(steps)-1)
                   else initial_samples + i * batch_size)
      else:
        samples = i
      rows.append({"Step": i, "Samples": samples, "Recall": a[1], "Recall_IQR": iq[1], "False_Alarm": a[2], "False_Alarm_IQR": iq[2]})
  d = os.path.dirname(path)
  if d:
    os.makedirs(d, exist_ok=True)
  with open(path, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["Step","Samples","Recall","Recall_IQR","False_Alarm","False_Alarm_IQR"])
    w.writeheader()
    for r in rows:
      w.writerow(r)

def eg__al_uncertainty_hall():
  "SLOW: run uncertainty-based active learning on Hall dataset"
  results = active_learning_text_mining("../moot/text_mining/reading/raw/Hall.csv", n_pos=16, repeats=10, batch_size=1, acq_stop=EARLY_STOPPING["hall"], n_neg=16)
  save_active_learning_results(results, "results/hall_al.csv")

def eg__al_uncertainty_kit():
  "SLOW: run uncertainty-based active learning on Kitchenham dataset"
  active_learning_text_mining("../moot/text_mining/reading/raw/Kitchenham.csv", n_pos=8, repeats=10, batch_size=1, acq_stop=EARLY_STOPPING["kitchenham"], n_neg=16, norm=True)

def eg__al_uncertainty_rad():
  "SLOW: run uncertainty-based active learning on Radjenovic dataset"
  active_learning_text_mining("../moot/text_mining/reading/raw/Radjenovic.csv", n_pos=8, repeats=10, batch_size=1, acq_stop=EARLY_STOPPING["radjenovic"], n_neg=16, norm=True)

def eg__al_uncertainty_wah():
  "SLOW: run uncertainty-based active learning on Wahono dataset"
  active_learning_text_mining("../moot/text_mining/reading/raw/Wahono.csv", n_pos=8, repeats=10, batch_size=1, acq_stop=EARLY_STOPPING["wahono"], n_neg=16)

#------------------------------------------------------------------------------------------------

def eg__al_uncertainty_hall_1():
  "SLOW: run uncertainty-based active learning on Hall dataset"
  results = active_learning_text_mining("../moot/text_mining/reading/raw/Hall.csv", n_pos=16, repeats=10, batch_size=1, acq_stop=EARLY_STOPPING["hall"], n_neg=16)
  save_active_learning_results(results, "results/hall_16_16.csv")
  results2 = active_learning_text_mining("../moot/text_mining/reading/raw/Hall.csv", n_pos=16, repeats=10, batch_size=1, acq_stop=EARLY_STOPPING["hall"], n_neg=16, norm=True)
  save_active_learning_results(results2, "results/hall_16_16_norm.csv")
  return results

def eg__al_uncertainty_hall_2():
  "SLOW: run uncertainty-based active learning on Hall dataset"
  results = active_learning_text_mining("../moot/text_mining/reading/raw/Hall.csv", n_pos=20, repeats=10, batch_size=1, acq_stop=EARLY_STOPPING["hall"], n_neg=20)
  save_active_learning_results(results, "results/hall_20_20.csv")
  results2 = active_learning_text_mining("../moot/text_mining/reading/raw/Hall.csv", n_pos=20, repeats=10, batch_size=1, acq_stop=EARLY_STOPPING["hall"], n_neg=20, norm=True)
  save_active_learning_results(results2, "results/hall_20_20_norm.csv")
  return results

def eg__al_uncertainty_hall_3():
  "SLOW: run uncertainty-based active learning on Hall dataset"
  results = active_learning_text_mining("../moot/text_mining/reading/raw/Hall.csv", n_pos=24, repeats=10, batch_size=1, acq_stop=EARLY_STOPPING["hall"], n_neg=24)
  save_active_learning_results(results, "results/hall_24_24.csv")
  results2 = active_learning_text_mining("../moot/text_mining/reading/raw/Hall.csv", n_pos=24, repeats=10, batch_size=1, acq_stop=EARLY_STOPPING["hall"], n_neg=24, norm=True)
  save_active_learning_results(results2, "results/hall_24_24_norm.csv")
  return results

def eg__al_uncertainty_hall_4():
  "SLOW: run uncertainty-based active learning on Hall dataset"
  results = active_learning_text_mining("../moot/text_mining/reading/raw/Hall.csv", n_pos=32, repeats=10, batch_size=1, acq_stop=EARLY_STOPPING["hall"], n_neg=32)
  save_active_learning_results(results, "results/hall_32_32.csv")
  results2 = active_learning_text_mining("../moot/text_mining/reading/raw/Hall.csv", n_pos=32, repeats=10, batch_size=1, acq_stop=EARLY_STOPPING["hall"], n_neg=32, norm=True)
  save_active_learning_results(results2, "results/hall_32_32_norm.csv")
  return results

def eg__al_uncertainty_kit_1():
  "SLOW: run uncertainty-based active learning on Kitchenham dataset"
  results = active_learning_text_mining("../moot/text_mining/reading/raw/Kitchenham.csv", n_pos=16, repeats=10, batch_size=1, acq_stop=EARLY_STOPPING["kitchenham"], n_neg=16)
  save_active_learning_results(results, "results/kit_16_16.csv")
  results2 = active_learning_text_mining("../moot/text_mining/reading/raw/Kitchenham.csv", n_pos=16, repeats=10, batch_size=1, acq_stop=EARLY_STOPPING["kitchenham"], n_neg=16, norm=True)
  save_active_learning_results(results2, "results/kit_16_16_norm.csv")
  return results

def eg__al_uncertainty_kit_2():
  "SLOW: run uncertainty-based active learning on Kitchenham dataset"
  results = active_learning_text_mining("../moot/text_mining/reading/raw/Kitchenham.csv", n_pos=20, repeats=10, batch_size=1, acq_stop=EARLY_STOPPING["kitchenham"], n_neg=20)
  save_active_learning_results(results, "results/kit_20_20.csv")
  results2 = active_learning_text_mining("../moot/text_mining/reading/raw/Kitchenham.csv", n_pos=20, repeats=10, batch_size=1, acq_stop=EARLY_STOPPING["kitchenham"], n_neg=20, norm=True)
  save_active_learning_results(results2, "results/kit_20_20_norm.csv")
  return results

def eg__al_uncertainty_kit_3():
  "SLOW: run uncertainty-based active learning on Kitchenham dataset"
  results = active_learning_text_mining("../moot/text_mining/reading/raw/Kitchenham.csv", n_pos=24, repeats=10, batch_size=1, acq_stop=EARLY_STOPPING["kitchenham"], n_neg=24)
  save_active_learning_results(results, "results/kit_24_24.csv")
  results2 = active_learning_text_mining("../moot/text_mining/reading/raw/Kitchenham.csv", n_pos=24, repeats=10, batch_size=1, acq_stop=EARLY_STOPPING["kitchenham"], n_neg=24, norm=True)
  save_active_learning_results(results2, "results/kit_24_24_norm.csv")
  return results

def eg__al_uncertainty_kit_4():
  "SLOW: run uncertainty-based active learning on Kitchenham dataset"
  results = active_learning_text_mining("../moot/text_mining/reading/raw/Kitchenham.csv", n_pos=32, repeats=10, batch_size=1, acq_stop=EARLY_STOPPING["kitchenham"], n_neg=32)
  save_active_learning_results(results, "results/kit_32_32.csv")
  results2 = active_learning_text_mining("../moot/text_mining/reading/raw/Kitchenham.csv", n_pos=32, repeats=10, batch_size=1, acq_stop=EARLY_STOPPING["kitchenham"], n_neg=32, norm=True)
  save_active_learning_results(results2, "results/kit_32_32_norm.csv")
  return results

def eg__al_uncertainty_rad_1():
  "SLOW: run uncertainty-based active learning on Radjenovic dataset"
  results = active_learning_text_mining("../moot/text_mining/reading/raw/Radjenovic.csv", n_pos=16, repeats=10, batch_size=1, acq_stop=EARLY_STOPPING["radjenovic"], n_neg=16)
  save_active_learning_results(results, "results/rad_16_16.csv")
  results2 = active_learning_text_mining("../moot/text_mining/reading/raw/Radjenovic.csv", n_pos=16, repeats=10, batch_size=1, acq_stop=EARLY_STOPPING["radjenovic"], n_neg=16, norm=True)
  save_active_learning_results(results2, "results/rad_16_16_norm.csv")
  return results

def eg__al_uncertainty_rad_2():
  "SLOW: run uncertainty-based active learning on Radjenovic dataset"
  results = active_learning_text_mining("../moot/text_mining/reading/raw/Radjenovic.csv", n_pos=20, repeats=10, batch_size=1, acq_stop=EARLY_STOPPING["radjenovic"], n_neg=20)
  save_active_learning_results(results, "results/rad_20_20.csv")
  results2 = active_learning_text_mining("../moot/text_mining/reading/raw/Radjenovic.csv", n_pos=20, repeats=10, batch_size=1, acq_stop=EARLY_STOPPING["radjenovic"], n_neg=20, norm=True)
  save_active_learning_results(results2, "results/rad_20_20_norm.csv")
  return results

def eg__al_uncertainty_rad_3():
  "SLOW: run uncertainty-based active learning on Radjenovic dataset"
  results = active_learning_text_mining("../moot/text_mining/reading/raw/Radjenovic.csv", n_pos=24, repeats=10, batch_size=1, acq_stop=EARLY_STOPPING["radjenovic"], n_neg=24)
  save_active_learning_results(results, "results/rad_24_24.csv")
  results2 = active_learning_text_mining("../moot/text_mining/reading/raw/Radjenovic.csv", n_pos=24, repeats=10, batch_size=1, acq_stop=EARLY_STOPPING["radjenovic"], n_neg=24, norm=True)
  save_active_learning_results(results2, "results/rad_24_24_norm.csv")
  return results

def eg__al_uncertainty_rad_4():
  "SLOW: run uncertainty-based active learning on Radjenovic dataset"
  results = active_learning_text_mining("../moot/text_mining/reading/raw/Radjenovic.csv", n_pos=32, repeats=10, batch_size=1, acq_stop=EARLY_STOPPING["radjenovic"], n_neg=32)
  save_active_learning_results(results, "results/rad_32_32.csv")
  results2 = active_learning_text_mining("../moot/text_mining/reading/raw/Radjenovic.csv", n_pos=32, repeats=10, batch_size=1, acq_stop=EARLY_STOPPING["radjenovic"], n_neg=32, norm=True)
  save_active_learning_results(results2, "results/rad_32_32_norm.csv")
  return results

def eg__al_uncertainty_wah_1():
  "SLOW: run uncertainty-based active learning on Wahono dataset"
  results = active_learning_text_mining("../moot/text_mining/reading/raw/Wahono.csv", n_pos=16, repeats=10, batch_size=1, acq_stop=EARLY_STOPPING["wahono"], n_neg=16)
  save_active_learning_results(results, "results/wah_16_16.csv")
  results2 = active_learning_text_mining("../moot/text_mining/reading/raw/Wahono.csv", n_pos=16, repeats=10, batch_size=1, acq_stop=EARLY_STOPPING["wahono"], n_neg=16, norm=True)
  save_active_learning_results(results2, "results/wah_16_16_norm.csv")
  return results

def eg__al_uncertainty_wah_2():
  "SLOW: run uncertainty-based active learning on Wahono dataset"
  results = active_learning_text_mining("../moot/text_mining/reading/raw/Wahono.csv", n_pos=20, repeats=10, batch_size=1, acq_stop=EARLY_STOPPING["wahono"], n_neg=20)
  save_active_learning_results(results, "results/wah_20_20.csv")
  results2 = active_learning_text_mining("../moot/text_mining/reading/raw/Wahono.csv", n_pos=20, repeats=10, batch_size=1, acq_stop=EARLY_STOPPING["wahono"], n_neg=20, norm=True)
  save_active_learning_results(results2, "results/wah_20_20_norm.csv")
  return results

def eg__al_uncertainty_wah_3():
  "SLOW: run uncertainty-based active learning on Wahono dataset"
  results = active_learning_text_mining("../moot/text_mining/reading/raw/Wahono.csv", n_pos=24, repeats=10, batch_size=1, acq_stop=EARLY_STOPPING["wahono"], n_neg=24)
  save_active_learning_results(results, "results/wah_24_24.csv")
  results2 = active_learning_text_mining("../moot/text_mining/reading/raw/Wahono.csv", n_pos=24, repeats=10, batch_size=1, acq_stop=EARLY_STOPPING["wahono"], n_neg=24, norm=True)
  save_active_learning_results(results2, "results/wah_24_24_norm.csv")
  return results

def eg__al_uncertainty_wah_4():
  "SLOW: run uncertainty-based active learning on Wahono dataset"
  results = active_learning_text_mining("../moot/text_mining/reading/raw/Wahono.csv", n_pos=32, repeats=10, batch_size=1, acq_stop=EARLY_STOPPING["wahono"], n_neg=32)
  save_active_learning_results(results, "results/wah_32_32.csv")
  results2 = active_learning_text_mining("../moot/text_mining/reading/raw/Wahono.csv", n_pos=32, repeats=10, batch_size=1, acq_stop=EARLY_STOPPING["wahono"], n_neg=32, norm=True)
  save_active_learning_results(results2, "results/wah_32_32_norm.csv")
  return results

#------------------------------------------------------------------------------------------------
def eg__benchmark_all_datasets():
  """Benchmark EZR preprocessing vs NLTK on all four datasets (Hall, Kitchenham, Wahono, Radjenovic)."""
  import time
  import nltk
  from nltk.stem import PorterStemmer
  from nltk.corpus import stopwords
  from sklearn.feature_extraction.text import TfidfVectorizer
  import csv
  import re
  
  # Download required NLTK data if not already present
  try:
    nltk.data.find('tokenizers/punkt')
  except LookupError:
    nltk.download('punkt')
  
  try:
    nltk.data.find('corpora/stopwords')
  except LookupError:
    nltk.download('stopwords')
  
  def load_dataset_abstracts(filename):
    """Load abstracts from a dataset file."""
    texts = []
    try:
      with open(f"../moot/text_mining/reading/raw/{filename}", 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
          text = row.get('Abstract', '').strip()
          if text and len(text) > 10:  # Only include non-empty abstracts with reasonable length
            texts.append(text)
    except FileNotFoundError:
      pout(f"Warning: {filename} not found")
      return []
    return texts
  
  def preprocess_nltk_with_tfidf(texts):
    """Preprocess texts using NLTK and calculate TF-IDF scores using scikit-learn."""
    # Initialize NLTK components (like EZR's prep does)
    porter = PorterStemmer()
    stop_words = set(stopwords.words('english'))
    
    # Step 1: Tokenize, stem, and remove stop words for all documents
    processed_texts = []
    for text in texts:
      tokens = nltk.word_tokenize(text.lower())
      processed = [porter.stem(token) for token in tokens 
                  if token.isalnum() and len(token) > 2 and token not in stop_words]
      processed_texts.append(' '.join(processed))
    
    # Step 2: Use scikit-learn's TfidfVectorizer for TF-IDF calculation
    tfidf_vectorizer = TfidfVectorizer(
        min_df=1,         # Include terms that appear in at least 1 document
        max_df=1.0,       # Include terms that appear in at most 100% of documents
        norm=None         # No normalization (like EZR)
    )
    
    # Fit and transform the documents
    tfidf_matrix = tfidf_vectorizer.fit_transform(processed_texts)
    
    # Get feature names and their TF-IDF scores
    feature_names = tfidf_vectorizer.get_feature_names_out()
    
    # Calculate average TF-IDF scores across all documents for each term
    avg_tfidf_scores = {}
    for i, term in enumerate(feature_names):
        avg_tfidf_scores[term] = tfidf_matrix[:, i].mean()
    
    # Get top 50 terms by average TF-IDF score (like EZR)
    top_terms = sorted(avg_tfidf_scores.items(), key=lambda x: x[1], reverse=True)[:100]
    
    return {
      'processed_texts': processed_texts,
      'tfidf_matrix': tfidf_matrix,
      'feature_names': feature_names,
      'tfidf_scores': avg_tfidf_scores,
      'top_terms': top_terms,
      'vectorizer': tfidf_vectorizer
    }
 
  def preprocess_ezr_with_tfidf(texts):
    """Preprocess texts using EZR's prep functionality with TF-IDF."""
    prep = Prep()
    for text in texts:
      addDoc(prep, text, "dummy_label")
    compute(prep)
    return prep
  
  # Dataset names
  datasets = ['Hall.csv', 'Kitchenham.csv', 'Wahono.csv', 'Radjenovic.csv']
  
  # Benchmark parameters
  iterations = 10
  warmup_iterations = 2
  
  pout("=" * 80)
  pout("BENCHMARKING ALL DATASETS")
  pout("=" * 80)
  pout(f"Running {iterations} iterations on each dataset")
  pout("-" * 80)
  
  results = {}
  
  for dataset in datasets:
    pout(f"\nProcessing {dataset}...")
    
    # Load dataset
    texts = load_dataset_abstracts(dataset)
    if not texts:
      pout(f"Skipping {dataset} - no data loaded")
      continue
    
    pout(f"Loaded {len(texts)} abstracts")
    pout(f"Text length range: {min(len(text) for text in texts)}-{max(len(text) for text in texts)} characters")
    
    # Warmup runs
    pout("Running warmup iterations...")
    for _ in range(warmup_iterations):
      _ = preprocess_nltk_with_tfidf(texts)
      _ = preprocess_ezr_with_tfidf(texts)
    
    # Benchmark NLTK
    pout("Benchmarking NLTK with TF-IDF calculation...")
    nltk_times = []
    
    for i in range(iterations):
      start_time = time.time()
      result = preprocess_nltk_with_tfidf(texts)
      end_time = time.time()
      nltk_times.append(end_time - start_time)
      
      if (i + 1) % 5 == 0:
        pout(f"NLTK iteration {i + 1}/{iterations}")
    
    # Benchmark EZR
    pout("Benchmarking EZR with TF-IDF calculation...")
    ezr_times = []
    
    for i in range(iterations):
      start_time = time.time()
      result = preprocess_ezr_with_tfidf(texts)
      end_time = time.time()
      ezr_times.append(end_time - start_time)
      
      if (i + 1) % 5 == 0:
        pout(f"EZR iteration {i + 1}/{iterations}")
    
    # Calculate statistics
    nltk_avg = sum(nltk_times) / len(nltk_times)
    nltk_min = min(nltk_times)
    nltk_max = max(nltk_times)
    nltk_std = (sum((t - nltk_avg) ** 2 for t in nltk_times) / len(nltk_times)) ** 0.5
    
    ezr_avg = sum(ezr_times) / len(ezr_times)
    ezr_min = min(ezr_times)
    ezr_max = max(ezr_times)
    ezr_std = (sum((t - ezr_avg) ** 2 for t in ezr_times) / len(ezr_times)) ** 0.5
    
    # Store results
    results[dataset] = {
      'nltk_avg': nltk_avg,
      'nltk_min': nltk_min,
      'nltk_max': nltk_max,
      'nltk_std': nltk_std,
      'ezr_avg': ezr_avg,
      'ezr_min': ezr_min,
      'ezr_max': ezr_max,
      'ezr_std': ezr_std,
      'speedup': nltk_avg / ezr_avg if ezr_avg > 0 else 0,
      'num_texts': len(texts)
    }
    
    # Individual dataset results
    pout(f"\n{dataset} Results:")
    pout(f"  NLTK avg: {nltk_avg:.4f}s, EZR avg: {ezr_avg:.4f}s")
    pout(f"  EZR is {results[dataset]['speedup']:.2f}x faster than NLTK")
  
  # Summary results
  pout("\n" + "=" * 80)
  pout("SUMMARY RESULTS")
  pout("=" * 80)
  pout(f"{'Dataset':<15} {'Texts':<8} {'NLTK(s)':<10} {'EZR(s)':<10} {'Speedup':<10}")
  pout("-" * 80)
  
  for dataset, result in results.items():
    dataset_name = dataset.replace('.csv', '')
    pout(f"{dataset_name:<15} {result['num_texts']:<8} {result['nltk_avg']:<10.4f} {result['ezr_avg']:<10.4f} {result['speedup']:<10.2f}x")
  
  # Overall statistics
  if results:
    avg_speedup = sum(r['speedup'] for r in results.values()) / len(results)
    pout("-" * 80)
    pout(f"Average speedup across all datasets: {avg_speedup:.2f}x")
  
  pout("\n" + "=" * 80)
  pout("All datasets benchmark completed!")

def eg__simple_preprocess(dataset_file:str="../moot/text_mining/reading/raw/Hall.csv"):
  "Simple example: preprocess a dataset and save it"
  # Example dataset path - replace with your actual dataset
  text_col = "Abstract"
  class_col = "label"
  
  try:
    pout(f"Loading dataset: {dataset_file}")
    
    # Create preprocessor and load dataset
    prep = Prep()
    rows = list(csv(dataset_file))
    
    if rows:
      # Find column indices
      ti, ki = rows[0].index(text_col), rows[0].index(class_col)
      
      # Add documents to preprocessor
      [addDoc(prep, str(r[ti]), str(r[ki])) for r in rows[1:]
        if len(r) > ti and len(r) > ki and r[ti] != "?" and r[ki] != "?"]
      
      # Compute features
      compute(prep)
      
      # Generate output filename
      import os
      base_name = os.path.splitext(dataset_file)[0]
      output_file = f"{base_name}_minimally_processed.csv"
      
      # Save preprocessed dataset
      save(prep, output_file)
      
      pout(f"Successfully preprocessed dataset!")
      pout(f"Input: {dataset_file}")
      pout(f"Output: {output_file}")
      pout(f"Processed {len(prep.docs)} documents with {len(prep.top)} features")
      
    else:
      pout(f"No data found in {dataset_file}")
      
  except FileNotFoundError:
    pout(f"Dataset file not found: {dataset_file}")
    pout("Please provide a valid dataset path")
  except Exception as e:
    pout(f"Error preprocessing dataset: {e}")

def eg__simple_preprocess_hall():
  "Simple example: preprocess Hall dataset"
  return eg__simple_preprocess("../moot/text_mining/reading/raw/Hall.csv")

def eg__simple_preprocess_radjenovic():
  "Simple example: preprocess Radjenovic dataset"
  return eg__simple_preprocess("../moot/text_mining/reading/raw/Radjenovic.csv")

def eg__simple_preprocess_kitchenham():
  "Simple example: preprocess Kitchenham dataset"
  return eg__simple_preprocess("../moot/text_mining/reading/raw/Kitchenham.csv")

def eg__simple_preprocess_wahono():
  "Simple example: preprocess Wahono dataset"
  return eg__simple_preprocess("../moot/text_mining/reading/raw/Wahono.csv")  