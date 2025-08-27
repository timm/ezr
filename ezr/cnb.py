#!/usr/bin/env python3 -B
from ezr.data import *
from ezr.stats import *
from ezr.lib import *
import math
import random
# import pandas as pd
from collections import defaultdict
from typing import Any, Dict, List
from sklearn.naive_bayes import ComplementNB
import numpy as np

#--------------------------------------------------------------------
def cnbStats(data: Data, rows=None) -> o:
    """Calculate Complement Naive Bayes statistics from data.
    Returns an object with feature counts, class counts, and metadata."""
    rows = rows or data.rows
    stats = o(
        f=defaultdict(lambda: defaultdict(int)),  # feature counts per class
        t=defaultdict(int),                       # total feature counts
        c=defaultdict(int),                       # class counts
        n=len(data.cols.x),                       # number of features
        k=set()                                   # unique classes
    )
    
    key = data.cols.klass.at
    for row in rows:
        klass = row[key]
        stats.k.add(klass)
        stats.c[klass] += 1
        
        for col in data.cols.x:
            v = row[col.at]
            if v != "?":
                try:
                    n = float(v)
                    stats.f[klass][col.at] += n
                    stats.t[col.at] += n
                except ValueError:
                    pass
    return stats

def cnbWeights(stats: o, alpha: float = 1.0, norm: bool = False) -> Dict[str, Dict[str, float]]:
    """Calculate feature weights using Complement Naive Bayes formula.
    Returns weights for each class and feature combination."""
    t_term = sum(stats.t.values())
    n_feat = stats.n
    
    # Calculate log probabilities using complement formula
    logs = {}
    for k in stats.k:
        logs[k] = {}
        for c in stats.t:
            # Complement NB formula: log(P(not_c|not_k) / P(not_c))
            numerator = (stats.t[c] + alpha - stats.f[k].get(c, 0)) + 1e-32
            denominator = (t_term + n_feat * alpha - sum(stats.f[k].values())) + 1e-32
            logs[k][c] = math.log(numerator / denominator)
    
    if not norm:
        # Return negative log probabilities (for minimization)
        return {k: {c: -lp for c, lp in lps.items()} for k, lps in logs.items()}
    else:
        # Return normalized weights
        return {k: {c: lp / ((sum(lps.values()) or 1e-32)) for c, lp in lps.items()}
                for k, lps in logs.items()}

def cnbLike(row: Row, x_cols: List, weights_for_class: Dict[str, float]) -> float:
    """Calculate the score for a single class given a row.
    Higher scores indicate higher likelihood of belonging to the class."""
    score = 0
    for col in x_cols:
        val = row[col.at]
        if val != "?":
            try:
                score += float(val) * weights_for_class.get(col.at, 0)
            except ValueError:
                pass
    return score

def cnbBest(weights: Dict[str, Dict[str, float]], row: Row, data: Data) -> Any:
    """Determine the best class for a row using pre-calculated weights."""
    scores = {k: cnbLike(row, data.cols.x, w) for k, w in weights.items()}
    return max(scores, key=scores.get) if scores else None

#--------------------------------------------------------------------
def cnbCompare(file: str, n_repeats: int = 5, norm: bool = False, n_pos: int = 20) -> bool:
    """Compare EZR's CNB implementation with sklearn's ComplementNB.
    Returns True if implementations agree within tolerance."""
    data = Data(csv(file))
    df = pd.read_csv(file)
    X = df[df.columns[1:]]
    y = df[df.columns[0]]
    
    key = data.cols.klass.at
    positive_indices = [i for i, row in enumerate(data.rows) if row[key] == "yes"]
    negative_indices = [i for i, row in enumerate(data.rows) if row[key] == "no"]
    
    print(f"Dataset: {len(data.rows)} total rows")
    print(f"Running comparison with norm={norm} for {n_repeats} repeats...")

    ezr_recalls, ezr_false_alarms = [], []
    sk_recalls, sk_false_alarms = [], []
    compliance_count = 0

    for i in range(n_repeats):
        print(f"  Run {i+1}/{n_repeats}...")
        
        # Sample training data
        train_positive_indices = random.sample(positive_indices, n_pos)
        train_negative_indices = random.sample(negative_indices, n_pos)
        train_indices = train_positive_indices + train_negative_indices
        train_rows = [data.rows[i] for i in train_indices]
        
        # Train both models
        ezr_stats = cnbStats(data, train_rows)
        ezr_weights = cnbWeights(ezr_stats, norm=norm)
        
        X_train = X.iloc[train_indices]
        y_train = y.iloc[train_indices]
        cnb = ComplementNB(norm=norm)
        cnb.fit(X_train, y_train)

        # Test models
        ezr_tp, ezr_fn, ezr_fp, ezr_tn = 0, 0, 0, 0
        sk_tp, sk_fn, sk_fp, sk_tn = 0, 0, 0, 0
        
        for idx, row in enumerate(data.rows):
            actual = row[key]
            ezr_pred = cnbBest(ezr_weights, row, data)
            sk_pred = cnb.predict(X.iloc[idx:idx+1])[0]

            # Tally EZR results
            if actual == "yes":
                if ezr_pred == "yes": ezr_tp += 1 
                else: ezr_fn += 1
            else:
                if ezr_pred == "yes": ezr_fp += 1
                else: ezr_tn += 1
            
            # Tally sklearn results
            if actual == "yes":
                if sk_pred == "yes": sk_tp += 1
                else: sk_fn += 1
            else:
                if sk_pred == "yes": sk_fp += 1
                else: sk_tn += 1
        
        # Calculate metrics
        ezr_recall = (ezr_tp / (ezr_tp + ezr_fn) * 100) if (ezr_tp + ezr_fn) > 0 else 0
        ezr_false_alarm = (ezr_fp / (ezr_fp + ezr_tn) * 100) if (ezr_fp + ezr_tn) > 0 else 0
        sk_recall = (sk_tp / (sk_tp + sk_fn) * 100) if (sk_tp + sk_fn) > 0 else 0
        sk_false_alarm = (sk_fp / (sk_fp + sk_tn) * 100) if (sk_fp + sk_tn) > 0 else 0
        
        ezr_recalls.append(ezr_recall)
        ezr_false_alarms.append(ezr_false_alarm)
        sk_recalls.append(sk_recall)
        sk_false_alarms.append(sk_false_alarm)

        if abs(ezr_recall - sk_recall) < 1.0 and abs(ezr_false_alarm - sk_false_alarm) < 1.0:
            compliance_count += 1

    # Report results
    print(f"\n{'='*55}")
    print(f"STATISTICAL RESULTS OVER {n_repeats} RUNS")
    print(f"{'='*55}")
    print(f"{'Metric':<15} {'Model':<10} {'Median':>10} {'IQR':>10}")
    print("-" * 55)

    # Recall
    ezr_r_med = np.median(ezr_recalls)
    ezr_r_iqr = np.percentile(ezr_recalls, 75) - np.percentile(ezr_recalls, 25)
    sk_r_med = np.median(sk_recalls)
    sk_r_iqr = np.percentile(sk_recalls, 75) - np.percentile(sk_recalls, 25)
    print(f"{'Recall (%)':<15} {'EZR':<10} {ezr_r_med:10.1f} {ezr_r_iqr:10.1f}")
    print(f"{'':<15} {'sklearn':<10} {sk_r_med:10.1f} {sk_r_iqr:10.1f}")
    
    # False Alarm
    ezr_fa_med = np.median(ezr_false_alarms)
    ezr_fa_iqr = np.percentile(ezr_false_alarms, 75) - np.percentile(ezr_false_alarms, 25)
    sk_fa_med = np.median(sk_false_alarms)
    sk_fa_iqr = np.percentile(sk_false_alarms, 75) - np.percentile(sk_false_alarms, 25)
    print(f"{'False Alarm (%)':<15} {'EZR':<10} {ezr_fa_med:10.1f} {ezr_fa_iqr:10.1f}")
    print(f"{'':<15} {'sklearn':<10} {sk_fa_med:10.1f} {sk_fa_iqr:10.1f}")

    print("-" * 55)
    print(f"Median Recall Difference: {abs(ezr_r_med - sk_r_med):.1f}%")
    print(f"Median False Alarm Difference: {abs(ezr_fa_med - sk_fa_med):.1f}%")
    print(f"Perfect Compliance Rate: {compliance_count}/{n_repeats} ({compliance_count/n_repeats*100:.0f}%)")
    print(f"{'='*55}")

    return compliance_count == n_repeats

def text_mining(file: str, n_repeats: int = 5, norm: bool = False, n_pos: int = 20, n_neg: int = 80) -> bool:
    """Test EZR's CNB implementation on text mining datasets using EZR's confuse pattern."""
    data = Data(csv(file))
    
    key = data.cols.klass.at
    positive_indices = [i for i, row in enumerate(data.rows) if row[key] == "yes"]

    all_results = []

    for i in range(n_repeats):
        
        # Sample positive examples from known positive indices
        train_positive_indices = random.sample(positive_indices, n_pos)
        
        # Sample negative examples randomly from entire dataset
        all_indices = list(range(len(data.rows)))
        # Remove positive indices to avoid overlap
        available_indices = [i for i in all_indices if i not in train_positive_indices]
        train_negative_indices = random.sample(available_indices, n_neg)
        
        train_indices = train_positive_indices + train_negative_indices
        train_rows = [data.rows[i] for i in train_indices]
        
        # Train EZR CNB model
        stats = cnbStats(data, train_rows)
        weights = cnbWeights(stats, norm=norm)

        # Manually calculate confusion matrix
        tp, tn, fp, fn = 0, 0, 0, 0
        
        for row in data.rows:
            want = row[key]
            got = cnbBest(weights, row, data)
            
            if want == "yes" and got == "yes":
                tp += 1
            elif want == "yes" and got == "no":
                fn += 1
            elif want == "no" and got == "yes":
                fp += 1
            elif want == "no" and got == "no":
                tn += 1
        
        # Calculate metrics
        pd = (tp / (tp + fn) * 100) if (tp + fn) > 0 else 0  # recall
        prec = (tp / (tp + fp) * 100) if (tp + fp) > 0 else 0  # precision
        pf = (fp / (fp + tn) * 100) if (fp + tn) > 0 else 0   # false alarm
        acc = ((tp + tn) / (tp + tn + fp + fn) * 100) if (tp + tn + fp + fn) > 0 else 0  # accuracy
        
        results = {"tp": tp, "tn": tn, "fp": fp, "fn": fn, "pd": pd, "prec": prec, "pf": pf, "acc": acc}
        all_results.append(results)

    # Report results using EZR's confusion matrix format
    print(f"\n{'='*55}")
    print(f"EZR CNB RESULTS | {n_repeats} REPEATS | {n_pos} POS | {n_neg} NEG | {norm} NORM")
    print(f"{'='*55}")

    # Calculate per-run metrics collections
    pds   = [r["pd"]   for r in all_results]
    precs = [r["prec"] for r in all_results]
    pfs   = [r["pf"]   for r in all_results]
    accs  = [r["acc"]  for r in all_results]

    # Median and IQR helpers
    def _med(vals): return float(np.median(vals)) if vals else 0.0
    def _iqr(vals):
      if not vals: return 0.0
      q75 = float(np.percentile(vals, 75))
      q25 = float(np.percentile(vals, 25))
      return q75 - q25

    pd_med,   pd_iqr   = _med(pds),   _iqr(pds)
    prec_med, prec_iqr = _med(precs), _iqr(precs)
    pf_med,   pf_iqr   = _med(pfs),   _iqr(pfs)
    acc_med,  acc_iqr  = _med(accs),  _iqr(accs)

    print(f"\nMedian (IQR) across {n_repeats} runs:")
    print(f"Recall (pd): {pd_med:.1f} ({pd_iqr:.1f})%")
    print(f"Precision: {prec_med:.1f} ({prec_iqr:.1f})%")
    print(f"False Alarm (pf): {pf_med:.1f} ({pf_iqr:.1f})%")
    print(f"Accuracy: {acc_med:.1f} ({acc_iqr:.1f})%")
    print(f"{'='*55}")

    return True

#--------------------------------------------------------------------
# UNCHANGED BENCHMARKING EXAMPLE FUNCTIONS
#--------------------------------------------------------------------

# def eg__perfect_compliance_norm():
#   "Run the perfect compliance check with weight normalization enabled."
#   print("--- Running NORMALIZED Complement Naive Bayes Test ---")
#   return cnbCompare("../moot/text_mining/reading/processed/Hall.csv", norm=True)

# def eg__perfect_compliance_Hall():
#   "Run perfect compliance check on Hall dataset."
#   return cnbCompare("../moot/text_mining/reading/processed/Hall.csv")

# def eg__perfect_compliance_kitchenham():
#   "Run perfect compliance check on Kitchenham dataset."
#   return cnbCompare("../moot/text_mining/reading/processed/Kitchenham.csv")

# def eg__perfect_compliance_wahono():
#   "Run perfect compliance check on Wahono dataset."
#   return cnbCompare("../moot/text_mining/reading/processed/Wahono.csv")

# def eg__perfect_compliance_radjenovic():
#   "Run perfect compliance check on Radjenovic dataset."
#   return cnbCompare("../moot/text_mining/reading/processed/Radjenovic.csv")

def eg__cnbh():
  "Run Complement Naive Bayes on Hall dataset."
  text_mining("../moot/text_mining/reading/raw/Hall_minimally_processed.csv", n_pos=12, n_neg=12) # 96, 25
  text_mining("../moot/text_mining/reading/raw/Hall_minimally_processed.csv", n_pos=16, n_neg=16) # 96, 20
  return

def eg__cnbk():
  "Run Complement Naive Bayes on Kitchenham dataset."
  return text_mining("../moot/text_mining/reading/processed/Kitchenham.csv", n_pos=32, n_neg=32, norm=True) # 96, 49

def eg__cnbr():
  "Run Complement Naive Bayes on Radjenovic dataset."
  return text_mining("../moot/text_mining/reading/processed/Radjenovic.csv", n_pos=16, n_neg=16, norm=True) # 95, 49

def eg__cnbw():
  "Run Complement Naive Bayes on Wahono dataset."
  return text_mining("../moot/text_mining/reading/processed/Wahono.csv", n_pos=20, n_neg=20) # 95, 29