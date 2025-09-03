# ezr

Semi-supervised explanations for incremental multi-objective 
optimization.

## Installation

**Option 1: Install via pip**
```bash
pip install ezr
```

**Option 2: Download directly**

```bash
# Download the single file
curl -O https://raw.githubusercontent.com/timm/ezr/main/ezr/ezr.py
python ezr.py -h
```

**Data repository (for examples):**

```bash
git clone http://github.com/timm/moot
```

## Quick Start

```bash
ezr -f data.csv
```

## Usage

Command line tool for generating decision rules from CSV data.

```bash
ezr -f path/to/your/data.csv
```

## Examples

```bash
# Using data from moot repository
ezr -f ~/gits/timm/moot/optimize/misc/auto93.csv
```

**Output:**

```
 #rows  win
    17   29    if Volume <= 98
     9   40    |  if Volume > 90
     6   41    |  |  if origin == 2
     3   50    |  |  |  if Model > 72;
     3   31    |  |  |  if Model <= 72;
```

## Output Format

- `#rows`: Number of data rows matching the rule
- `win`: Performance percentage for that branch
- `|`: Hierarchical rule structure (nested conditions)

## License

BSD-2-Clause

## Background

Traditional multi-objective optimization techniques often produce 
Pareto frontiers that are difficult to interpret. While these 
solutions may be mathematically optimal, they provide little insight 
into why certain configurations outperform others. This opacity 
becomes problematic when domain experts need to understand trade-offs 
or when solutions must be justified to stakeholders.

ezr addresses this interpretability gap by combining decision tree 
learning with multi-objective optimization. Rather than simply 
finding optimal solutions, ezr explains the decision boundaries that 
separate high-performing from low-performing configurations. The 
semi-supervised approach allows incorporation of domain knowledge 
while the incremental learning capability enables adaptation as new 
data becomes available.

The tool generates hierarchical rules that partition the solution 
space based on performance characteristics. Each rule shows both the 
number of examples it covers and the expected performance improvement, 
making it easy to identify which factors most strongly influence 
success.

## Algorithm Pseudocode

```
function ezr_main(data, target_columns):
    1. Parse CSV data and identify numeric/categorical features
    2. Calculate performance metrics for multi-objective targets
    3. Build initial decision tree using recursive partitioning:
       a. For each feature, find best split point
       b. Score splits by information gain + performance delta
       c. Recursively partition data until stopping criteria
    4. Prune tree to avoid overfitting
    5. Generate human-readable rules with performance stats
    6. Output hierarchical rule structure with win percentages
    
function find_best_split(data, feature):
    best_gain = 0
    best_threshold = None
    for threshold in unique_values(feature):
        left, right = partition(data, feature <= threshold)
        gain = performance_gain(left, right)
        if gain > best_gain:
            best_gain = gain
            best_threshold = threshold
    return best_threshold, best_gain
```

## Coding Notes

ezr consists of under 400 lines of Python (no pandas or sklearn) 
organized into three main files:

### ezr.py (Core Algorithm)  
Elite greedy search implementation with incremental updates. Maintains 
separate "best" and "rest" populations using √N elite sampling rule. 
Implements two acquisition functions:

- **nearer**: Greedy distance-based selection - finds unlabeled rows 
  closer to "best" centroid than "rest" centroid
- **likelier**: Adaptive acquisition with multiple modes (xploit, 
  xplor, bore, adapt) using Bayesian likelihood scoring between 
  best vs rest populations

Uses Welford's method for incremental statistics and distance-to-heaven 
scoring for multi-objective ranking. Tree building generates 
interpretable rules via recursive partitioning with minimal leaf sizes.
Contains data structures (Sym/Num columns) and CSV parser. The main 
`likely()` function orchestrates the A,B,C pattern.

### ezrtest.py
Unit tests and example functions demonstrating ezr's capabilities. 
Includes test cases for data loading, distance calculations, tree 
building, and optimization workflows. Examples can be run directly 
from command line using the eg_* function pattern.

### stats.py
Statistical utilities for comparing treatments and ranking results. 
Implements significance testing, effect size calculations, and 
ranking algorithms used in the experimental evaluation framework.
Handles the statistical analysis needed for comparing different
acquisition functions and optimization approaches.

**Key Design Principle**: Incremental updates throughout - statistics, 
populations, and centroids are maintained incrementally rather than 
recomputed, enabling sub-second runtimes even on large datasets.
