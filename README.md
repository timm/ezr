# ezr

Semi-supervised explanations for incremental multi-objective 
optimization.

## Motivation

**The Labeling Problem:** In optimization, choices are easy to spot 
but consequences are slow to measure. You can scan hundreds of 
configurations in minutes, but evaluating their real-world performance 
may require hours or days of testing.

**Questioning "Bigger is Better":** Recent research shows only 5% of 
software engineering papers using LLMs consider simpler alternatives - 
a major methodological oversight. UCL researchers found SVM+TF-IDF 
methods outperformed "Big AI" by 100x in speed with greater accuracy 
for effort estimation.

ezr embraces **"funneling"** - the principle that despite internal 
complexity, software behavior converges to few outcomes, enabling 
simpler reasoning. Where LLMs require planetary-scale computation and 
specialized hardware, ezr achieves state-of-the-art results through 
smarter questioning on standard laptops.

This approach fosters **human-AI partnership**: unlike opaque LLMs, 
ezr's small labeled sets and tiny regression trees offer explainable, 
auditable reasoning that humans can understand and guide.

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

## Performance

ezr delivers strong optimization results from remarkably small 
labeling budgets:

- **12 samples**: 60% of optimal
- **25 samples**: 74% of optimal  
- **50 samples**: 90% of optimal

Tested on 118 datasets spanning software configuration, cloud tuning, 
project health, feature models, process modeling, analytics, finance, 
healthcare, reinforcement learning, sales, testing, and text mining.

**Speed:** Typical runtimes under 100ms. Large datasets (128 
attributes, 100,000 rows) process in ~3 seconds.

## Output Format

- `#rows`: Number of data rows matching the rule
- `win`: Performance percentage for that branch
- `|`: Hierarchical rule structure (nested conditions)

## Algorithm Pseudocode

ezr follows an **A,B,C pattern**:
- **A=Any**: Start with 4 randomly labeled examples (minimum for 
  best/rest split)
- **B=Budget**: Label up to B total examples using elite search
- **C=Check**: Test top 5 predictions, return best result

```
function ezr_main(data, A=4, B=25):
    1. Split data into train/test, hide y-values in train
    2. Label A random examples, sort by distance-to-heaven
    3. Split into √A "best" examples, rest in "rest" 
    4. While budget < B:
       a. Find unlabeled row closest to "best" centroid
       b. Label it, add to "best" if promising
       c. Maintain |best| ≤ √|labeled| (demote worst to "rest")
    5. Build decision tree from labeled examples
    6. Sort test set, examine top C=5, return best

function distance_to_heaven(goals):
    # Normalize goals to [0,1], with heaven = 0 for minimize, 1 for maximize
    return euclidean_distance(normalized_goals, heaven) / √2

function win_percentage(found, best_known, average):
    return 100 * (1 - (found - best_known) / (average - best_known))
```

**Key insight:** Elite sampling with √N keeps "best" set small and 
focused, while greedy search toward "best" centroid avoids expensive 
exploration/exploitation calculations.

## License

BSD-2-Clause

## Background

Traditional multi-objective optimization faces a critical challenge: 
the labeling problem. While identifying potential configurations is 
straightforward, evaluating their real-world performance is expensive 
and time-consuming. This creates a fundamental bottleneck in 
optimization workflows.

**The Case for Simplicity:** Research by Adams et al. demonstrates 
that humans systematically overlook subtractive changes, preferring 
to add complexity rather than remove it (4:1 ratio). This cognitive 
bias affects AI research, where teams often pursue elaborate 
reinforcement learning and active learning approaches without first 
testing simpler alternatives. One such team lost two years exploring 
complex acquisition functions that yielded minimal improvements over 
basic methods.

ezr embraces the "Less, but Better" philosophy, proving that 
sophisticated optimization results can emerge from remarkably simple 
algorithms. By focusing on elite sampling (maintaining √N best 
examples) and greedy search toward promising centroids, ezr 
eliminates the need for complex exploration/exploitation balancing, 
Parzen windows, or multi-generational evolutionary approaches.

**Data Efficiency:** Historical logs are error-prone, expert labeling 
is slow and expensive, and automated labeling can be misleading. ezr's 
minimal labeling approach makes expert evaluation feasible - 25 
carefully chosen evaluations can achieve 74% of optimal performance, 
making human-in-the-loop optimization practical even for busy domain 
experts.

The tool generates hierarchical rules that partition solution spaces 
based on performance characteristics, showing both coverage (#rows) 
and expected improvement (win %) for each decision branch. This makes 
optimization results interpretable and actionable for stakeholders.

## Coding Notes

ezr consists of just ~500 lines of Python (no pandas or sklearn) 
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
