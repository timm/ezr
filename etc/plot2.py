import re
import sys
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter

plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = ['Times New Roman', 'DejaVu Serif', 'Garamond', 'Computer Modern Roman']
plt.rcParams['mathtext.fontset'] = 'cm'

KEY_RE = re.compile(r':(\w+)\s+(\S+)')

def parse_log(file_path):
    rows = []
    with open(file_path) as f:
        for line in f:
            d = dict(KEY_RE.findall(line))
            if not d:
                continue
            rows.append({
                'budget': int(d['budget']),
                'check': int(d['check']),
                'train': float(d['train']),
                'test': float(d['test']),
            })
    return pd.DataFrame(rows)

def generate_heatmap(df, value_col, out_path):
    df = df[df[value_col] >= 0]
    heatmap_data = df.pivot_table(
        index='budget', columns='check', values=value_col, aggfunc='median')
    heatmap_data = heatmap_data.sort_index(ascending=False)
    data_matrix = heatmap_data.fillna(0).values
    blurred_data = gaussian_filter(data_matrix, sigma=1.2)
    blurred_df = pd.DataFrame(blurred_data, index=heatmap_data.index, columns=heatmap_data.columns)

    plt.figure(figsize=(7, 3))
    x_labels = [int(col) if int(col) % 2 == 0 else '' for col in blurred_df.columns]
    y_labels = [int(idx) if int(idx) % 10 == 0 else '' for idx in blurred_df.index]
    ax = sns.heatmap(blurred_df, cmap='viridis', annot=False,
                     xticklabels=x_labels, yticklabels=y_labels,
                     vmin=0, vmax=100)
    cbar = ax.collections[0].colorbar
    cbar.ax.tick_params(labelsize=10)
    cbar.set_label(value_col.capitalize(), size=12, weight='bold')

    X_grid, Y_grid = np.meshgrid(np.arange(blurred_data.shape[1]) + 0.5,
                                 np.arange(blurred_data.shape[0]) + 0.5)
    contours = ax.contour(X_grid, Y_grid, blurred_data, levels=[60, 75, 85, 95],
                          colors='black', alpha=0.9, linewidths=1.5)
    ax.clabel(contours, inline=True, fontsize=11, fmt='%1.0f', colors='black')

    plt.xlabel('Check', fontsize=12, fontweight='bold')
    plt.ylabel('Budget', fontsize=12, fontweight='bold')
    plt.xticks(fontsize=10, rotation=0)
    plt.yticks(fontsize=10, rotation=0)
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()

if __name__ == "__main__":
    log = sys.argv[1] if len(sys.argv) > 1 else '/Users/timm/tmp/runs.log'
    df = parse_log(log)
    generate_heatmap(df, 'train', 'train.pdf')
    generate_heatmap(df, 'test',  'test.pdf')
