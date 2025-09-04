#!/usr/bin/env python3
"""
Generate grouped plots for each dataset from CSV results.

CSV filename pattern:
  {dataset}_{pos}_{neg}_{normalization}.csv

Where normalization is either "norm" (normalized) or omitted (non-normalized).

Each dataset group plot contains two rows (Recall, False Alarm) and one
column per (pos,neg) combination. Within each subplot, plot two lines:
normalized and non-normalized. X-axis is total samples = pos+neg+step.

All images are saved under graphs/images.
"""

import os
import re
import csv
from collections import defaultdict
from typing import Dict, List, Tuple

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D


RESULTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "results"))
IMAGES_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "images"))


FILENAME_RE = re.compile(r"^(?P<dataset>[^_]+)_(?P<pos>\d+)_(?P<neg>\d+)(_(?P<norm>norm))?\.csv$")


def list_result_files(directory: str) -> List[str]:
    if not os.path.isdir(directory):
        return []
    return [f for f in os.listdir(directory) if f.endswith(".csv")]


def parse_filename(filename: str) -> Tuple[str, int, int, bool]:
    match = FILENAME_RE.match(filename)
    if not match:
        raise ValueError(f"Unexpected filename format: {filename}")
    dataset = match.group("dataset")
    pos = int(match.group("pos"))
    neg = int(match.group("neg"))
    is_norm = match.group("norm") is not None
    return dataset, pos, neg, is_norm


def read_metrics(filepath: str) -> Tuple[List[int], List[float], List[float]]:
    steps: List[int] = []
    recall: List[float] = []
    false_alarm: List[float] = []
    with open(filepath, newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        if not rows:
            return steps, recall, false_alarm
        # Ignore last line completely
        rows = rows[:-1]
        for row in rows:
            # Columns: Step, Samples, Recall, False_Alarm
            step_val = int(row.get("Step", 0))
            steps.append(step_val)
            recall.append(float(row.get("Recall", 0.0)))
            false_alarm.append(float(row.get("False_Alarm", 0.0)))
    return steps, recall, false_alarm


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def plot_dataset_group(dataset: str, combos: Dict[Tuple[int, int], Dict[str, str]]) -> None:
    # combos: {(pos,neg): {"norm": path or None, "raw": path or None}}
    sorted_combos = sorted(combos.keys(), key=lambda pn: (pn[0]+pn[1], pn[0], pn[1]))
    num_cols = max(1, len(sorted_combos))

    # Global font settings
    plt.rcParams.update({
        "font.family": "serif",
        "font.serif": ["EB Garamond", "Garamond", "Times New Roman", "DejaVu Serif", "serif"],
        "font.size": 16,
    })

    # Scale figure size more generously per column
    fig_width = max(6, 5.5 * num_cols)
    fig_height = 10
    fig, axes = plt.subplots(nrows=2, ncols=num_cols, figsize=(fig_width, fig_height), squeeze=False)
    fig.suptitle(f"{dataset} performance.")

    legend_handles: Dict[str, Line2D] = {}

    for col_idx, (pos, neg) in enumerate(sorted_combos):
        files = combos[(pos, neg)]
        # Prepare data containers
        series = []  # list of (label, x, y_recall, y_fa)

        if files.get("raw"):
            steps, recall_vals, fa_vals = read_metrics(files["raw"])
            x = [pos + neg + s for s in steps]
            series.append(("non-normalized", x, recall_vals, fa_vals))

        if files.get("norm"):
            steps, recall_vals, fa_vals = read_metrics(files["norm"])
            x = [pos + neg + s for s in steps]
            series.append(("normalized", x, recall_vals, fa_vals))

        # Recall subplot (row 0)
        ax_recall = axes[0][col_idx]
        for label, x_vals, y_rec, _ in series:
            ln, = ax_recall.plot(x_vals, y_rec, label=label)
            if label not in legend_handles:
                legend_handles[label] = ln
            # annotate first point value
            if x_vals and y_rec:
                # first point
                ax_recall.text(x_vals[0], y_rec[0], f"{y_rec[0]:.3f}", ha="center", va="bottom", fontsize=12)
                # last point
                ax_recall.text(x_vals[-1], y_rec[-1], f"{y_rec[-1]:.3f}", ha="center", va="bottom", fontsize=12)
        ax_recall.set_title(f"pos={pos}, neg={neg}")
        ax_recall.set_xlabel("Total samples")
        ax_recall.set_ylabel("Recall")
        ax_recall.grid(True, alpha=0.3)
        # dashed line at y=0.95
        ax_recall.axhline(0.95, linestyle="--", color="gray", linewidth=1)

        # False Alarm subplot (row 1)
        ax_fa = axes[1][col_idx]
        for label, x_vals, _, y_fa in series:
            ln, = ax_fa.plot(x_vals, y_fa, label=label)
            if label not in legend_handles:
                legend_handles[label] = ln
            # annotate first point value
            if x_vals and y_fa:
                # first point
                ax_fa.text(x_vals[0], y_fa[0], f"{y_fa[0]:.3f}", ha="center", va="bottom", fontsize=12)
                # last point
                ax_fa.text(x_vals[-1], y_fa[-1], f"{y_fa[-1]:.3f}", ha="center", va="bottom", fontsize=12)
        ax_fa.set_xlabel("Total samples")
        ax_fa.set_ylabel("False Alarm")
        ax_fa.grid(True, alpha=0.3)

    # Common legend at the bottom
    if legend_handles:
        handles = [legend_handles[k] for k in sorted(legend_handles.keys())]
        labels = sorted(legend_handles.keys())
        fig.legend(handles=handles, labels=labels, loc="lower center", ncol=len(labels), fontsize=14)

    fig.tight_layout(rect=[0.02, 0.08, 0.98, 0.94])
    ensure_dir(IMAGES_DIR)
    out_path = os.path.join(IMAGES_DIR, f"{dataset}.png")
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


def main() -> None:
    ensure_dir(IMAGES_DIR)
    files = list_result_files(RESULTS_DIR)
    if not files:
        print(f"No CSV files found in {RESULTS_DIR}")
        return

    # Group files by dataset and pos/neg
    datasets: Dict[str, Dict[Tuple[int, int], Dict[str, str]]] = defaultdict(lambda: defaultdict(dict))
    for fname in files:
        try:
            dataset, pos, neg, is_norm = parse_filename(fname)
        except ValueError:
            # skip files that don't match pattern
            continue
        path = os.path.join(RESULTS_DIR, fname)
        key = (pos, neg)
        if is_norm:
            datasets[dataset][key]["norm"] = path
        else:
            datasets[dataset][key]["raw"] = path

    # Create one figure per dataset
    for dataset, combos in datasets.items():
        if not combos:
            continue
        plot_dataset_group(dataset, combos)
        print(f"Saved: {os.path.join(IMAGES_DIR, f'{dataset}.png')}")


if __name__ == "__main__":
    main()


