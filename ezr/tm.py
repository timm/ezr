#!/usr/bin/env python3 -B
from ezr.tree import *
from ezr.stats import *
from ezr.likely import *
from ezr.prep import *
from ezr.data import *
from ezr.lib import *
import csv as csv_module
import random

#------------------------------------------------------------------------------------------------
def load_dataset(dataset_file, text_col="Abstract", class_col="label"):
  """Load and preprocess dataset from CSV file."""
  prep = Prep()
  
  # Try different encodings
  for encoding in ['utf-8', 'latin1', 'cp1252', 'iso-8859-1']:
    try:
      with open(dataset_file, 'r', encoding=encoding) as f:
        rows = list(csv_module.reader(f))
      break
    except UnicodeDecodeError:
      continue
  else:
    pout("ERROR: Could not read file with any encoding")
    return None
  
  header = rows[0]
  text_idx, label_idx = header.index(text_col), header.index(class_col)
  
  # Add documents
  for row in rows[1:]:
    if len(row) > max(text_idx, label_idx):
      text, label = str(row[text_idx]), str(row[label_idx])
      if text and label and text != "?" and label != "?":
        addDoc(prep, text, label)
  
  compute(prep)
  return prep

#------------------------------------------------------------------------------------------------
def get_metrics(results):
  """Extract metrics from evaluation results."""
  try:
    if "_OVERALL" in results:
      overall = results["_OVERALL"]
      return (overall['precision']/100, overall['recall']/100, 
              overall['false_alarm'], overall['accuracy']/100)
  except:
    pass
  return (0, 0, 0, 0)

def evaluate_model(train_data, test_data, wait=5):
  """Evaluate a model trained on train_data against test_data."""
  cf = Confuse()
  d, key = {}, train_data.cols.klass.at
  
  # Build class models from training data
  for row in train_data.rows:
    want = row[key]
    d[want] = d.get(want) or clone(train_data)
    add(d[want], row)
  
  # Make predictions on test data
  for n, row in enumerate(test_data.rows):
    if n > wait: 
      confuse(cf, row[key], likeBest(d, row, len(train_data.rows)))
  
  # Get results and calculate overall metrics
  results = confused(cf)
  metrics = {}
  
  for result in results:
    if result.label != "_OVERALL":
      metrics[result.label] = {
        'recall': result.pd, 'false_alarm': result.pf, 'precision': result.prec,
        'accuracy': result.acc, 'tp': result.tp, 'fp': result.fp, 'tn': result.tn, 'fn': result.fn
      }
  
  # Calculate overall metrics for binary classification
  if "yes" in metrics:
    m = metrics["yes"]
    tp, fp, tn, fn = m['tp'], m['fp'], m['tn'], m['fn']
    total = tp + fp + fn + tn
    metrics['_OVERALL'] = {
      'precision': (tp / (tp + fp) * 100) if (tp + fp) > 0 else 0,
      'recall': (tp / (tp + fn) * 100) if (tp + fn) > 0 else 0,
      'false_alarm': (fp / (fp + tn) * 100) if (fp + tn) > 0 else 0,
      'accuracy': (tp + tn) / total * 100 if total > 0 else 0,
      'tp': tp, 'fp': fp, 'tn': tn, 'fn': fn
    }
  else:
    overall = next((r for r in results if r.label == "_OVERALL"), None)
    if overall:
      metrics['_OVERALL'] = {
        'precision': overall.prec, 'recall': overall.pd, 'false_alarm': overall.pf,
        'accuracy': overall.acc, 'tp': overall.tp, 'fp': overall.fp, 'tn': overall.tn, 'fn': overall.fn
      }
  
  return metrics

def create_training_subset(full_data, labeled_docs, all_docs):
  """Create training data subset by selecting rows from the full preprocessed data."""
  labeled_set = {(doc.txt, doc.klass) for doc in labeled_docs}
  train_data = clone(full_data)
  
  for idx, doc in enumerate(all_docs):
    if (doc.txt, doc.klass) in labeled_set and idx < len(full_data.rows):
      add(train_data, full_data.rows[idx])
  
  return train_data

def active_learning_loop(prep, n_pos=8, repeats=5, batch_size=1000):
  """Uncertainty-based active learning using EZR's Prep infrastructure."""
  pos_docs = [doc for doc in prep.docs if doc.klass == "yes"]
  neg_docs = [doc for doc in prep.docs if doc.klass == "no"]
  
  if len(pos_docs) < n_pos or len(neg_docs) < n_pos * 4:
    return []
  
  full_data = features(prep)
  results = []
  
  for _ in range(repeats):
    # Randomly select initial samples
    labeled_docs = random.sample(pos_docs, n_pos) + random.sample(neg_docs, n_pos * 4)
    pool_docs = [doc for doc in prep.docs if doc not in labeled_docs]
    
    step_metrics = []
    train_data = create_training_subset(full_data, labeled_docs, prep.docs)
    
    # Initial evaluation
    step_metrics.append(get_metrics(evaluate_model(train_data, full_data)))
    
    # Active learning loop
    acq = 0
    while pool_docs:
      batch_to_acquire = min(batch_size, len(pool_docs))
      acquired_docs = random.sample(pool_docs, batch_to_acquire)
      pool_docs = [doc for doc in pool_docs if doc not in acquired_docs]
      
      labeled_docs.extend(acquired_docs)
      train_data = create_training_subset(full_data, labeled_docs, prep.docs)
      acq += batch_to_acquire
      
      # Evaluate after each batch
      if acq % batch_size == 0 and acq > 0:
        step_metrics.append(get_metrics(evaluate_model(train_data, full_data)))
      elif acq > 0:
        step_metrics.append((0, 0, 0, 0))
    
    # Final evaluation
    step_metrics.append(get_metrics(evaluate_model(train_data, full_data)))
    results.append(step_metrics)
  
  return results

def active_learning_text_mining(dataset_file, text_col="Abstract", class_col="label", n_pos=8, repeats=10, batch_size=1000):
  """Run uncertainty-based active learning on a dataset."""
  prep = load_dataset(dataset_file, text_col, class_col)
  if prep is None:
    return
  
  results = active_learning_loop(prep, n_pos=n_pos, repeats=repeats, batch_size=batch_size)
  
  if results:
    all_steps = set()
    for repeat_results in results:
      if repeat_results:
        all_steps.update(range(len(repeat_results)))
    
    sorted_steps = sorted(all_steps)
    pout(f"\nResults per step (avg over {len(results)} repeats) for {dataset_file} with {n_pos} pos & {n_pos * 4} neg:")
    pout("-" * 70)
    pout(f"{'Step':<12} {'Precision':<10} {'Recall':<8} {'False_Alarm':<12} {'Accuracy':<10} {'Samples':<8}")
    pout("-" * 70)
    
    initial_samples = n_pos + n_pos * 4
    for step_idx in sorted_steps:
      step_results = [repeat_results[step_idx] for repeat_results in results 
                     if repeat_results and step_idx < len(repeat_results)]
      
      if step_results and any(any(result) for result in step_results):
        avg_metrics = [sum(result[i] for result in step_results) / len(step_results) for i in range(4)]
        
        if step_idx == 0:
          step_label, sample_count = "Initial", initial_samples
        elif step_idx == len(sorted_steps) - 1:
          step_label, sample_count = "Final", len(prep.docs)
        else:
          acquired_samples = step_idx * batch_size
          step_label, sample_count = f"Step {acquired_samples}", initial_samples + acquired_samples
        
        pout(f"{step_label:<12} {avg_metrics[0]:<10.4f} {avg_metrics[1]:<8.4f} "
             f"{avg_metrics[2]:<12.2f}% {avg_metrics[3]:<10.4f} {sample_count:<8}")
  
  return results

#------------------------------------------------------------------------------------------------
def eg__al_uncertainty_hall():
  "run uncertainty-based active learning on Hall dataset"
  active_learning_text_mining("../moot/text_mining/reading/raw/Hall.csv", n_pos=8, repeats=10, batch_size=1000)

def eg__al_uncertainty_kit():
  "run uncertainty-based active learning on Kitchenham dataset"
  active_learning_text_mining("../moot/text_mining/reading/raw/Kitchenham.csv", n_pos=8, repeats=10, batch_size=1000)

def eg__al_uncertainty_rad():
  "run uncertainty-based active learning on Radjenovic dataset"
  active_learning_text_mining("../moot/text_mining/reading/raw/Radjenovic.csv", n_pos=8, repeats=10, batch_size=1000)

def eg__al_uncertainty_wah():
  "run uncertainty-based active learning on Wahono dataset"
  active_learning_text_mining("../moot/text_mining/reading/raw/Wahono.csv", n_pos=8, repeats=10, batch_size=1000)