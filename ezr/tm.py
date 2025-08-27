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
  pout(f"Loading dataset: {dataset_file}")
  prep = load_dataset(dataset_file, text_col, class_col)
  if prep is None: return
  pout(f"Loaded {len(prep.docs)} documents")
  pout("Starting active learning loop...")
  results = active_learning_loop(prep, n_pos=n_pos, repeats=repeats, batch_size=batch_size, acq_stop=acq_stop, n_neg=n_neg, norm=norm)
  if results:
    steps = sorted({i for rr in results for i in range(len(rr))})
    n_neg_display = n_neg or n_pos * 4
    pout(f"\nResults@step (avg of {len(results)}) for {dataset_file} with {n_pos} pos & {n_neg_display} neg:")
    pout("-" * 70)
    pout(f"{'Step':<12} {'Precision':<10} {'Recall':<8} {'False_Alarm':<12} {'Accuracy':<10} {'Samples':<8}")
    pout("-" * 70)
    init = n_pos + (n_neg or n_pos * 4)
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
      a = [sum(x[j] for x in sr)/len(sr) for j in range(4)]
      if initial_samples is not None and batch_size is not None:
        samples = (final_samples if (final_samples is not None and i == len(steps)-1)
                   else initial_samples + i * batch_size)
      else:
        samples = i
      rows.append({"Step": i, "Samples": samples, "Recall": a[1], "False_Alarm": a[2]})
  d = os.path.dirname(path)
  if d:
    os.makedirs(d, exist_ok=True)
  with open(path, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["Step","Samples","Recall","False_Alarm"])
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

def eg__benchmark_preprocessing():
  """Benchmark EZR preprocessing vs NLTK with TF-IDF calculations over multiple iterations."""
  import time
  import nltk
  from nltk.stem import PorterStemmer
  from nltk.corpus import stopwords
  from sklearn.feature_extraction.text import TfidfVectorizer
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
  
  # Load real dataset for benchmarking
  def load_hall_dataset():
    """Load abstracts from the Hall dataset."""
    import csv
    texts = []
    try:
      with open("../moot/text_mining/reading/raw/Hall.csv", 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
          # Use only the Abstract column
          text = row.get('Abstract', '').strip()
          if text and len(text) > 10:  # Only include non-empty abstracts with reasonable length
            texts.append(text)
    except FileNotFoundError:
      pout("Warning: Hall.csv not found, using sample texts instead")
      texts = [
        "The quick brown fox jumps over the lazy dog. This is a sample text for preprocessing.",
        "Machine learning algorithms are being applied to various domains including natural language processing.",
        "The researchers conducted experiments using different preprocessing techniques and evaluated their performance.",
        "Text mining involves extracting useful information from unstructured text data using computational methods.",
        "Information retrieval systems help users find relevant documents from large collections of text.",
        "Classification algorithms can automatically categorize documents into predefined classes.",
        "Feature extraction is an important step in text preprocessing for machine learning applications.",
        "Stemming reduces words to their root form, helping to improve text analysis performance.",
        "Stop words are commonly occurring words that are typically filtered out during preprocessing.",
        "TF-IDF weighting assigns higher importance to terms that are rare across documents but frequent within specific documents."
      ]
    return texts
  
  sample_texts = load_hall_dataset()  # Use all abstracts from Hall dataset
  
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
        max_features=50,  # Get top 50 features
        min_df=1,         # Include terms that appear in at least 1 document
        max_df=1.0,       # Include terms that appear in at most 100% of documents
        norm='l2'         # L2 normalization
    )
    
    # Fit and transform the documents
    tfidf_matrix = tfidf_vectorizer.fit_transform(processed_texts)
    
    # Get feature names and their TF-IDF scores
    feature_names = tfidf_vectorizer.get_feature_names_out()
    
    # Calculate average TF-IDF scores across all documents for each term
    avg_tfidf_scores = {}
    for i, term in enumerate(feature_names):
        avg_tfidf_scores[term] = tfidf_matrix[:, i].mean()
    
    # Get top terms by average TF-IDF score
    top_terms = sorted(avg_tfidf_scores.items(), key=lambda x: x[1], reverse=True)
    
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
  
  # Benchmark parameters
  iterations = 10  # Run for 10 iterations as requested
  warmup_iterations = 2
  
  pout(f"Benchmarking preprocessing with TF-IDF over {iterations} iterations...")
  pout(f"Sample texts: {len(sample_texts)}")
  pout(f"Text length range: {min(len(text) for text in sample_texts)}-{max(len(text) for text in sample_texts)} characters")
  pout("-" * 60)
  
  # Warmup runs
  pout("Running warmup iterations...")
  for _ in range(warmup_iterations):
    _ = preprocess_nltk_with_tfidf(sample_texts)
    _ = preprocess_ezr_with_tfidf(sample_texts)
  
  # Benchmark NLTK
  pout("Benchmarking NLTK with TF-IDF calculation...")
  nltk_times = []
  nltk_results = []
  
  for i in range(iterations):
    start_time = time.time()
    result = preprocess_nltk_with_tfidf(sample_texts)
    end_time = time.time()
    nltk_times.append(end_time - start_time)
    nltk_results.append(result)
    
    if (i + 1) % 10 == 0:
      pout(f"NLTK iteration {i + 1}/{iterations}")
  
  # Benchmark EZR
  pout("Benchmarking EZR with TF-IDF calculation...")
  ezr_times = []
  ezr_results = []
  
  for i in range(iterations):
    start_time = time.time()
    result = preprocess_ezr_with_tfidf(sample_texts)
    end_time = time.time()
    ezr_times.append(end_time - start_time)
    ezr_results.append(result)
    
    if (i + 1) % 10 == 0:
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
  
  # Results
  pout("\n" + "=" * 60)
  pout("BENCHMARK RESULTS")
  pout("=" * 60)
  pout(f"Total iterations: {iterations}")
  pout(f"Texts per iteration: {len(sample_texts)}")
  pout(f"Total texts processed: {iterations * len(sample_texts)}")
  pout("-" * 60)
  
  pout("NLTK with TF-IDF:")
  pout(f"  Average time: {nltk_avg:.4f} seconds")
  pout(f"  Min time: {nltk_min:.4f} seconds")
  pout(f"  Max time: {nltk_max:.4f} seconds")
  pout(f"  Std dev: {nltk_std:.4f} seconds")
  pout(f"  Avg time per text: {nltk_avg/len(sample_texts):.6f} seconds")
  
  pout("\nEZR with TF-IDF:")
  pout(f"  Average time: {ezr_avg:.4f} seconds")
  pout(f"  Min time: {ezr_min:.4f} seconds")
  pout(f"  Max time: {ezr_max:.4f} seconds")
  pout(f"  Std dev: {ezr_std:.4f} seconds")
  pout(f"  Avg time per text: {ezr_avg/len(sample_texts):.6f} seconds")
  
  pout("\n" + "-" * 60)
  if ezr_avg < nltk_avg:
    speedup = nltk_avg / ezr_avg
    pout(f"EZR is {speedup:.2f}x FASTER than NLTK")
  else:
    speedup = ezr_avg / nltk_avg
    pout(f"NLTK is {speedup:.2f}x FASTER than EZR")
  
  # Sample output comparison
  pout("\n" + "=" * 60)
  pout("SAMPLE OUTPUT COMPARISON")
  pout("=" * 60)
  
  # Compare TF-IDF results
  nltk_result = preprocess_nltk_with_tfidf(sample_texts)
  ezr_result = preprocess_ezr_with_tfidf(sample_texts)
  
  pout(f"Number of unique terms (NLTK): {len(nltk_result['tfidf_scores'])}")
  pout(f"Number of unique terms (EZR): {len(ezr_result.tfidf)}")
  
  pout("\nTop 10 terms by TF-IDF score:")
  pout("NLTK (scikit-learn):")
  for i, (term, score) in enumerate(nltk_result['top_terms'][:10]):
    pout(f"  {i+1:2d}. {term:<15} {score:.4f}")
  
  pout("\nEZR:")
  for i, (term, score) in enumerate(ezr_result.top[:10]):
    pout(f"  {i+1:2d}. {term:<15} {score:.4f}")
  
  # Compare processing results
  pout(f"\nNLTK processed {len(nltk_result['processed_texts'])} documents")
  pout(f"EZR processed {len(ezr_result.docs)} documents")
  
  if nltk_result['processed_texts'] and ezr_result.docs:
    pout(f"\nSample processed text (NLTK): {nltk_result['processed_texts'][0][:100]}...")
    pout(f"Sample processed tokens (EZR): {list(ezr_result.tf[0].keys())[:10]}")
  
  pout("\n" + "=" * 60)
  pout("Benchmark completed!")

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
        max_features=50,  # Get top 50 features
        min_df=1,         # Include terms that appear in at least 1 document
        max_df=1.0,       # Include terms that appear in at most 100% of documents
        norm='l2'         # L2 normalization
    )
    
    # Fit and transform the documents
    tfidf_matrix = tfidf_vectorizer.fit_transform(processed_texts)
    
    # Get feature names and their TF-IDF scores
    feature_names = tfidf_vectorizer.get_feature_names_out()
    
    # Calculate average TF-IDF scores across all documents for each term
    avg_tfidf_scores = {}
    for i, term in enumerate(feature_names):
        avg_tfidf_scores[term] = tfidf_matrix[:, i].mean()
    
    # Get top terms by average TF-IDF score
    top_terms = sorted(avg_tfidf_scores.items(), key=lambda x: x[1], reverse=True)
    
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

def eg__benchmark_basic_preprocessing():
  """Benchmark EZR vs NLTK on basic preprocessing only (tokenization, stemming, stop words)."""
  import time
  import nltk
  from nltk.stem import PorterStemmer
  from nltk.corpus import stopwords
  import csv
  
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
  
  def preprocess_nltk_basic(texts):
    """Basic preprocessing using NLTK (tokenization, stemming, stop words)."""
    # Initialize NLTK components
    porter = PorterStemmer()
    stop_words = set(stopwords.words('english'))
    
    processed_texts = []
    for text in texts:
      tokens = nltk.word_tokenize(text.lower())
      processed = [porter.stem(token) for token in tokens 
                  if token.isalnum() and len(token) > 2 and token not in stop_words]
      processed_texts.append(' '.join(processed))
    return processed_texts
  
  def preprocess_ezr_basic(texts):
    """Basic preprocessing using EZR (tokenization, stemming, stop words)."""
    prep = Prep()
    processed_texts = []
    for text in texts:
      tokens = tokenize(text, prep.stops, prep.sufs)
      processed_texts.append(' '.join(tokens))
    return processed_texts
  
  # Dataset names
  datasets = ['Hall.csv', 'Kitchenham.csv', 'Wahono.csv', 'Radjenovic.csv']
  
  # Benchmark parameters
  iterations = 10
  warmup_iterations = 2
  
  pout("=" * 80)
  pout("BASIC PREPROCESSING BENCHMARK")
  pout("=" * 80)
  pout("Comparing tokenization, stemming, and stop word removal only")
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
      _ = preprocess_nltk_basic(texts)
      _ = preprocess_ezr_basic(texts)
    
    # Benchmark NLTK
    pout("Benchmarking NLTK basic preprocessing...")
    nltk_times = []
    
    for i in range(iterations):
      start_time = time.time()
      result = preprocess_nltk_basic(texts)
      end_time = time.time()
      nltk_times.append(end_time - start_time)
      
      if (i + 1) % 5 == 0:
        pout(f"NLTK iteration {i + 1}/{iterations}")
    
    # Benchmark EZR
    pout("Benchmarking EZR basic preprocessing...")
    ezr_times = []
    
    for i in range(iterations):
      start_time = time.time()
      result = preprocess_ezr_basic(texts)
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
  pout("BASIC PREPROCESSING SUMMARY")
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
  pout("Basic preprocessing benchmark completed!")

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