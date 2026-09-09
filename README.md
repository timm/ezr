![Python 3.10+](https://img.shields.io/badge/Python-3.10+-blue?logo=python&logoColor=white&labelColor=1D4ED8&color=0A2A7A)
![Purpose XAI](https://img.shields.io/badge/Purpose-XAI-orange?logo=openai&logoColor=white&labelColor=FB8C00&color=A85A00)
![Goal Multi-Obj](https://img.shields.io/badge/Goal-Multi--Obj-purple?logo=target&logoColor=white&labelColor=C026D3&color=6D1780)
![Deps 0](https://img.shields.io/badge/Deps-0-green?logo=checkmarx&logoColor=white&labelColor=00C853&color=006B29)
![LOC ~600](https://img.shields.io/badge/LOC-~600-yellow?logo=codecov&logoColor=white&labelColor=FDE047&color=C3A700)
![License](https://img.shields.io/badge/©_2026-timm-black?logo=github&logoColor=white&labelColor=24292e&color=000000&link=http://timm.fyi)

# EZR(1) - Minimal XAI for Multi-Objective Reasoning

## NAME

**ezr** — explainable multi-objective optimization: label a few
rows, grow a tiny tree, let it explain the rest. Plus naive
bayes classification, clustering, classic optimizers, and the
stats to check them.

## SYNOPSIS

    ezr    [-Key val ..] [--demo ..]
    ezr-eg [-Key val ..] [--demo ..]
    ezr --help

## DESCRIPTION

**ezr** is an experiment in "how easy is AI?" (see the paper
*Can AI be Easy? Lessons from the EZR.py Toolkit*,
arXiv:2606.03640). Labels are dear: reading a row is free but
scoring one costs a build, a test, an experiment. So ezr's
active learner labels ~50 informative rows, grows a small
regression tree from them, and uses that tree to rank
everything else. Across the 120+ tasks of the MOOT repository
this matches state-of-the-art optimizers that run orders of
magnitude slower.

The whole substrate is two tiny types — a Num is a tuple
`(n, mu, m2)`, a Sym is a dict of counts — plus one update
primitive (`add`, whose `inc=-1` also undoes). Trees, bayes,
distance, active learning, and stats are all short questions
asked of those summaries.

Input is CSV. The header row defines column roles:

    [A-Z]*    Numeric        (e.g. "Age")
    [a-z]*    Symbolic       (e.g. "job")
    *+        Maximize goal  (e.g. "Mpg+")
    *-        Minimize goal  (e.g. "Lbs-")
    *!        Class label    (e.g. "sick!")
    *X        Ignored        (e.g. "idX")
    ?         Missing value  (in data rows, not the header)

## LAYOUT

Two files. No package structure, no test framework.

    ezr.py     Library + demos. Sections: structs, distance,
               acquire, bayes, tree, report, stats, start-up.
    ezr_eg.py  More demos on the same substrate: kmeans,
               kmeans++, simulated annealing, local search,
               bayes-guided acquisition.

Any function named `test_*` is a demo, a test, and a help
entry, all at once. The exit code counts crashes, so
`make tests` needs no framework.

## INSTALLATION

    pip install ezr           # the ezr and ezr-eg commands

or run from a clone:

    git clone http://github.com/timm/ezr
    cd ezr && ./ezr.py --help

Python 3.10+. Zero runtime dependencies. Sample data:

    git clone http://github.com/timm/moot ~/gits/moot

(or set `$MOOT` to wherever you put it).

## COMMANDS

Args evaluate left to right: `-Key val` updates a setting,
`--name` runs a demo with the settings as they stand then
resets them. So:

    ezr -Leaf 10 --tree -File ~/gits/moot/optimize/misc/auto93.csv --tree

Demos in ezr:

    --help       Show usage, settings, demos
    --num        Welford add matches textbook mean and sd
    --sym        Syms count; mid is mode; div is entropy
    --tbl        Headers route columns to x, y, klass, or nowhere
    --cuts       cut returns a legal, routable split
    --wins       wins grades the best row 100
    --tree       Acquire, grow and show the.File's tree
    --holdout    Mean win over 20 train/test holdouts
    --klass      Tree vs bayes, same splits: confusions, then same?
    --same       Stats tests tell noise from signal
    --all        Run every demo; exit code counts the crashes

Extra demos in ezr-eg (which inherits all of the above):

    --kmeans     Cluster the.File; per cluster: n rows, mean ydist
    --kpp        kmeans++ seeds spread wider than random picks
    --optimize   SA vs local search, nearest-neighbor oracle, wins
    --acquires   Centroid vs bayes acquisition: 20 holdouts each

## OPTIONS

Settings live once, in the docstring; `-Key val` overrides one.

    -P=2       minkowski coefficient
    -Start=4   acquire: initial random labels
    -Stop=50   acquire: total labelling budget
    -Few=128   max train rows
    -Leaf=4    tree: min rows in any leaf
    -Check=5   holdout: top picks to label
    -k=1       bayes: rare klass hack
    -m=2       bayes: rare evidence hack
    -Klass=$MOOT/classify/diabetes.csv  classify demo data
    -Repeats=30  klass: number of train/test splits
    -Seed=1234567891  random number seed
    -File=$MOOT/optimize/misc/auto93.csv

ezr-eg adds:

    -budget=1000  optimize: max oracle calls
    -restart=100  ls: retry after this many no-improvements
    -K=10         kmeans: clusters
    -N=10         kmeans: iterations

## EXAMPLE

`ezr --tree` labels 50 of auto93's 398 rows, then explains
them.  First column is distance to heaven (0..100, lower is
better); `+`/`-` mark the best and worst leaves:

    $MOOT/optimize/misc/auto93.csv n=398 mid=0.529 ezr=0.087
      d2h   n   Lbs-   Acc+   Mpg+
       36  50   2378     16     31
       25  27   2034     17     35   Volume <= 98
       18  14   1985     18     36   |  origin = 3
       14   9   1998     18     38   |  |  Volume <= 89
    +  12   5   1984     18     42   |  |  |  Model > 79
       ...

`ezr --klass` races tree vs bayes classifiers over the same
30 splits of the diabetes data, then asks the stats if the
difference is real:

    fitBayes    75  84  40   80    500  tested_negative
    fitTree 73 (3) fitBayes 75 (2) delta 2 : different

## LIBRARY USAGE

```python
from ezr import *

tbl = Tbl(csv("$MOOT/optimize/misc/auto93.csv"))
show(tbl, tree(tbl, acquire(tbl)))
```

Key exports:

- **structs**: `Tbl`, `Num`, `Sym`, `add`, `adds`, `addRow`,
  `clone`, `mid`, `div`, `sd`, `size`
- **distance**: `norm`, `mids`, `ydist`, `xdist`, `ymu`
- **acquire**: `acquire`, `label`, `pop`
- **bayes**: `like`, `likes`, `liked`, `confuse`
- **tree**: `tree`, `cut`, `cutNum`, `cutSym`, `routing`,
  `leaf`, `leafs`, `show`
- **stats**: `same`, `cliffs`, `ks`, `cohen`, `wins`
- **config**: `the`, `defaults`, `atom`, `csv`, `cli`, `run`
- **ezr_eg**: `kmeans`, `kpp`, `nearest`, `pick`, `oneplus1`,
  `sa`, `ls`, `acquireBayes`

## FILES

    ezr/
      ezr.py          Library + demos (~440 lines)
      ezr_eg.py       Clustering + optimizer demos (~170 lines)
      pyproject.toml  Package config (ezr, ezr-eg commands)
      README.md       This file
      CHANGELOG.md    Release notes
      LICENSE.md      MIT
      etc/            Paper artifacts (runs.sh, plot2.py), helpers

## AUTHOR

Tim Menzies <timm@ieee.org>, 2026. MIT License.

## SEE ALSO

- Paper: https://arxiv.org/abs/2606.03640
- Repository: http://github.com/timm/ezr
- Sample data: http://github.com/timm/moot
