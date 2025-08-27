import math
import random
import pandas as pd
from collections import defaultdict
from typing import Any, Dict, List

# Assuming the existence of your data utility classes and functions
from ezr.data import *
from ezr.stats import *
from sklearn.naive_bayes import ComplementNB
import numpy as np

def cnb_stats(train_rows: list, full_data: Data) -> dict:
    """Calculates all necessary counts from the training data."""
    stats = {"f": defaultdict(lambda: defaultdict(int)), "t": defaultdict(int),
             "c": defaultdict(int), "n": len(full_data.cols.x), "k": set()}
    key = full_data.cols.klass.at
    for row in train_rows:
        klass = row[key]
        stats["k"].add(klass)
        stats["c"][klass] += 1
        for col in full_data.cols.x:
            v = row[col.at]
            if v != "?":
                try:
                    n = float(v)
                    stats["f"][klass][col.at] += n
                    stats["t"][col.at] += n
                except ValueError:
                    pass
    return stats

def cnb_weights(stats: dict, alpha: float = 1.0, norm: bool = False) -> dict:
    """Calculates feature weights using the pre-computed stats."""
    t_term = sum(stats["t"].values())
    n_feat = stats["n"]
    logs = {k: {c: math.log(((stats["t"][c] + alpha - stats["f"][k].get(c, 0)) + 1e-32) /
                           ((t_term + n_feat*alpha - sum(stats["f"][k].values())) + 1e-32))
                for c in stats["t"]} for k in stats["k"]}

    if not norm:
        return {k: {c: -lp for c, lp in lps.items()} for k, lps in logs.items()}
    else:
        return {k: {c: lp / ((sum(lps.values()) or 1e-32)) for c, lp in lps.items()}
                for k, lps in logs.items()}

def cnb_like(row: Row, x_cols: list, weights_for_class: dict) -> float:
    """Calculates the score for a single class given a row."""
    score = 0
    for col in x_cols:
        val = row[col.at]
        if val != "?":
            try:
                score += float(val) * weights_for_class.get(col.at, 0)
            except ValueError:
                pass
    return score

# --- Helper functions to demonstrate usage ---

def cnb_best(weights: dict, row: Row, data: Data) -> any:
    """Determines the best class for a row using pre-calculated weights."""
    scores = {k: cnb_like(row, data.cols.x, w) for k, w in weights.items()}
    return max(scores, key=scores.get) if scores else None

def cnb_classifier(file: str, norm: bool = False) -> Confuse:
    """Orchestrates the CNB classification process."""
    cf = Confuse()
    data = Data(csv(file))
    # Using all rows for both training and testing in this example
    stats = cnb_stats(data.rows, data)
    weights = cnb_weights(stats, norm=norm)

    for row in data.rows:
        want = row[data.cols.klass.at]
        got = cnb_best(weights, row, data)
        confuse(cf, want, got)
    return confused(cf)

def perfect_compliance_check(dataset_path="../moot/text_mining/reading/processed/Hall.csv", n_repeats=10, norm: bool = False):
    """
    MODIFIED: Runs the comparison `n` times on different random samples.
    Reports the median and IQR for recall and false alarm rates for both models.
    """
    # --- 1. SETUP (Done once) ---
    data = Data(csv(dataset_path))
    df = pd.read_csv(dataset_path)
    X = df[df.columns[1:]]
    y = df[df.columns[0]]
    
    key = data.cols.klass.at
    positive_indices = [i for i, row in enumerate(data.rows) if row[key] == "yes"]
    negative_indices = [i for i, row in enumerate(data.rows) if row[key] == "no"]
    
    print(f"Dataset: {len(data.rows)} total rows")
    print(f"Running experiment with norm={norm} for {n_repeats} repeats...")

    # Lists to store results from each run
    ezr_recalls, ezr_false_alarms = [], []
    sk_recalls, sk_false_alarms = [], []
    compliance_count = 0

    # --- 2. REPEATED EXPERIMENT ---
    for i in range(n_repeats):
        print(f"  Run {i+1}/{n_repeats}...")
        # A. Sample a different training set for each run
        train_positive_indices = random.sample(positive_indices, 8)
        train_negative_indices = random.sample(negative_indices, 32)
        train_indices = train_positive_indices + train_negative_indices
        train_rows = [data.rows[i] for i in train_indices]
        
        # B. Train both models on the *exact same* sampled data
        ezr_stats = cnb_stats(train_rows, data)
        ezr_weights = cnb_weights(ezr_stats, norm=norm) # Pass norm flag
        
        X_train = X.iloc[train_indices]
        y_train = y.iloc[train_indices]
        cnb = ComplementNB(norm=norm) # Pass norm flag
        cnb.fit(X_train, y_train)

        # C. Test models on the entire dataset
        ezr_tp, ezr_fn, ezr_fp, ezr_tn = 0, 0, 0, 0
        sk_tp, sk_fn, sk_fp, sk_tn = 0, 0, 0, 0
        
        for idx, row in enumerate(data.rows):
            actual = row[key]
            ezr_pred = cnb_best(ezr_weights, row, data)
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
        
        # D. Calculate and store metrics for this run
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

    # --- 3. REPORTING ---
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

#--------------------------------------------------------------------
# UNCHANGED BENCHMARKING EXAMPLE FUNCTIONS
#--------------------------------------------------------------------

def eg__perfect_compliance_norm():
  "Run the perfect compliance check with weight normalization enabled."
  print("--- Running NORMALIZED Complement Naive Bayes Test ---")
  return perfect_compliance_check(norm=True)

def eg__perfect_compliance_Hall():
  "Run perfect compliance check on Hall dataset."
  return perfect_compliance_check("../moot/text_mining/reading/processed/Hall.csv")

def eg__perfect_compliance_kitchenham():
  "Run perfect compliance check on Kitchenham dataset."
  return perfect_compliance_check("../moot/text_mining/reading/processed/Kitchenham.csv")

def eg__perfect_compliance_wahono():
  "Run perfect compliance check on Wahono dataset."
  return perfect_compliance_check("../moot/text_mining/reading/processed/Wahono.csv")

def eg__perfect_compliance_radjenovic():
  "Run perfect compliance check on Radjenovic dataset."
  return perfect_compliance_check("../moot/text_mining/reading/processed/Radjenovic.csv")