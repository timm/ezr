![Python 3.12+](https://img.shields.io/badge/Python-3.12+-blue?logo=python&logoColor=white&labelColor=1D4ED8&color=0A2A7A)
![Purpose XAI](https://img.shields.io/badge/Purpose-XAI-orange?logo=openai&logoColor=white&labelColor=FB8C00&color=A85A00)
![Goal Multi-Obj](https://img.shields.io/badge/Goal-Multi--Obj-purple?logo=target&logoColor=white&labelColor=C026D3&color=6D1780)
![Teaching](https://img.shields.io/badge/Teaching-CSC591-red?logo=graduationcap&logoColor=white&labelColor=DC2626&color=7F1D1D)
![Deps 0](https://img.shields.io/badge/Deps-0-green?logo=checkmarx&logoColor=white&labelColor=00C853&color=006B29)
![LOC ~1100](https://img.shields.io/badge/LOC-~1100-yellow?logo=codecov&logoColor=white&labelColor=FDE047&color=C3A700)
![License](https://img.shields.io/badge/©_2026-timm-black?logo=github&logoColor=white&labelColor=24292e&color=000000&link=http://timm.fyi)


# EZR(1) - Explainable Multi-Objective Optimization

## NAME

**ezr** — explainable multi-objective optimization via decision trees,
clustering, Naive Bayes, and active learning

## SYNOPSIS

    ezr [--key=val ...] CMD [args]
    ezr --list
    ezr --help

## DESCRIPTION

**ezr** is a lightweight toolkit for multi-objective optimization
and explainable AI. It summarizes CSV data into Num/Sym columns,
builds decision trees that minimize distance to ideal outcomes,
clusters rows via k-means or recursive halving, and supports
active learning with Naive Bayes or centroid-based acquisition.

**ezr** is an experiment in "how low can you go?" — how little
data is needed for effective AI. The code uses active learning
to label a small number of (say) 50 informative examples. These
build a regression tree which sorts the unlabelled test data.
Repeated studies show that by labelling just the first ~5 examples,
the selected row optimizes as well or better than state-of-the-art
optimizers like SMAC (which runs two orders of magnitude slower).

Input is CSV. The header row defines column roles:

    [A-Z]*    Numeric (e.g. "Age")
    [a-z]*    Symbolic (e.g. "job")
    [A-Z]*+   Maximize goal (e.g. "Pay+")
    [A-Z]*-   Minimize goal (e.g. "Cost-")
    [a-z]*!   Class label (e.g. "sick!")
    *X        Ignored (e.g. "idX")
    ?         Missing value (in data rows, not header)

## LAYOUT

Two files. No package structure, no test scaffolding.

    ezr.py    Library. Section banners for each app.
    cli.py    CLI dispatch. `eg_<app>` demos + `eg_test_<app>` tests.

`ezr.py` sections: **Types**, **Col** (Num, Sym), **Data**, **Distance**,
**Bayes**, **Comparison** (pick, picks, extrapolate), **Format**,
**Stats** (same, bestRanks, confused), **Tree**, **Cluster**,
**Classify**, **Search** (sa, ls, de, oneplus1), **Acquire**,
**Textmine** (tokenize, stem, tfidf, cnb).

`cli.py` exposes everything in `ezr.py` as `eg_<name>` commands.
Tests are `eg_test_<name>` and run as plain function calls — no
pytest dependency.

## INSTALLATION

    git clone http://github.com/timm/ezr
    cd ezr
    pip install -e .

Creates the global `ezr` command. Edits to `ezr.py` or `cli.py`
take effect immediately. Python 3.12+. Zero runtime dependencies.

To uninstall:

    pip uninstall ezr

### Run without installing

    git clone http://github.com/timm/ezr
    cd ezr
    python3 cli.py --list

### Sample data

    mkdir -p $HOME/gits
    git clone http://github.com/timm/moot $HOME/gits/moot

## COMMANDS

List everything:

    ezr --list

Common commands:

    ezr classify FILE       Incremental Naive Bayes; print confusion
    ezr tree FILE           Grow regression tree; show structure
    ezr cluster FILE        kmeans++ + kmeans; one row per cluster
    ezr search sa FILE      Simulated annealing
    ezr search ls FILE      Local search
    ezr search de FILE      Differential evolution
    ezr acquire FILE        Active learning; print best labeled rows
    ezr textmine FILE       CNB text classification
    ezr stats               Demo of same/bestRanks/confused

Tests (assertions over real data files):

    ezr test_core
    ezr test_tree
    ezr test_cluster
    ezr test_search
    ezr test_acquire
    ezr test_classify
    ezr test_textmine
    ezr test_stats
    ezr test_all            Run every test, report pass/fail count

## OPTIONS

Flags update the global config namespace `the`. Use `--key=value`.
Nested keys use dots.

### Learning & Trees

    --learn.leaf=3      Minimum examples per leaf
    --learn.budget=50   Number of rows to evaluate
    --learn.check=5     Number of guesses to check
    --learn.start=4     Initial number of labels

### Distance & Bayes

    --p=2               Distance metric (1=Manhattan, 2=Euclidean)
    --bayes.m=2         m-estimate for Naive Bayes
    --bayes.k=1         k-estimate (Laplace smoothing)
    --few=128           Max unlabelled rows in active learning

### Statistics

    --stats.cliffs=0.195  Cliff's Delta threshold
    --stats.conf=1.36     KS test confidence coefficient
    --stats.eps=0.35      Margin of error multiplier

### Textmine

    --textmine.top=100    Top TF-IDF features kept
    --textmine.yes=20     Positive warm-start samples
    --textmine.no=20      Negative warm-start samples
    --textmine.valid=20   Repeats for stats testing

### Display

    --seed=1            Random number seed
    --show.show=30      Tree display width
    --show.decimals=2   Decimal places for floats

Flags and commands interleave. Flags apply to all subsequent
commands in the same invocation:

    ezr --seed=42 --learn.budget=30 acquire auto93.csv

## LIBRARY USAGE

```python
from ezr import *

d = Data(csv("auto93.csv"))
win = wins(d)
t = treeGrow(d, d.rows)
treeShow(t)

for r in sorted(d.rows, key=lambda r: disty(d, r))[:5]:
    print(win(r), r)
```

Sample tree output. `D` is distance to heaven (lower is better),
`N` is examples in branch, `Goals` shows centroid:

```
$ ezr tree ~/gits/moot/optimize/misc/auto93.csv
                               D       N     Goals
                               ====  =====   =====
                              ,0.66 ,( 50), {Acc+=15.51, Lbs-=2888.64, Mpg+=24.60}
Clndrs <= 5                   ,0.61 ,( 26), {Acc+=16.43, Lbs-=2204.46, Mpg+=30.38}
|   Volume <= 98              ,0.59 ,( 14), {Acc+=17.15, Lbs-=2024.64, Mpg+=33.57}
|   |   Volume <= 91          ,0.59 ,(  9), {Acc+=17.09, Lbs-=1927.67, Mpg+=35.56}
|   |   |   origin != 3       ,0.58 ,(  4), {Acc+=17.35, Lbs-=1908.00, Mpg+=37.50}
|   |   |   origin == 3       ,0.59 ,(  5), {Acc+=16.88, Lbs-=1943.40, Mpg+=34.00}
|   |   Volume > 91           ,0.60 ,(  5), {Acc+=17.26, Lbs-=2199.20, Mpg+=30.00}
|   Volume > 98               ,0.64 ,( 12), {Acc+=15.58, Lbs-=2414.25, Mpg+=26.67}
Clndrs > 5                    ,0.72 ,( 24), {Acc+=14.52, Lbs-=3629.83, Mpg+=18.33}
|   origin != 1               ,0.63 ,(  3), {Acc+=14.93, Lbs-=3000.00, Mpg+=26.67}
|   origin == 1               ,0.73 ,( 21), {Acc+=14.46, Lbs-=3719.81, Mpg+=17.14}
...
```

Key exports (all from `ezr.py`):

- **Data**: `Data`, `Num`, `Sym`, `Col`, `Cols`, `adds`, `add`,
  `sub`, `clone`, `mid`, `spread`, `mode`, `entropy`, `norm`
- **Distance**: `distx`, `disty`, `nearest`, `minkowski`, `aha`, `wins`
- **Bayes**: `like`, `likes`
- **Comparison**: `pick`, `picks`, `extrapolate`
- **Format / IO**: `csv`, `o`, `table`, `nest`, `thing`, `the`
- **Stats**: `same`, `bestRanks`, `confused`
- **Tree**: `Tree`, `treeGrow`, `treeCuts`, `treeSplit`, `treeLeaf`,
  `treeNodes`, `treeShow`, `treePlan`
- **Cluster**: `kmeans`, `kpp`, `half`, `rhalf`, `neighbors`
- **Classify**: `classify`
- **Search**: `oneplus1`, `sa`, `ls`, `de`, `oracleNearest`, `last`
- **Acquire**: `acquire`, `warm_start`, `rebalance`,
  `acquireWithBayes`, `acquireWithCentroid`
- **Textmine**: `tmPrepare`, `tmTokenize`, `tmNostop`, `tmStem`,
  `tmTfidf`, `tmData`, `cnb`, `cnbLike`, `cnbLikes`, `tmRandom`,
  `tmActive`

## FILES

    ezr/
      ezr.py          Library (all algorithms, section-banner organized)
      cli.py          Dispatcher + eg_* demos + eg_test_* tests
      pyproject.toml  Package config (ezr binary, version, deps)
      README.md       This file
      CHANGELOG.md    Release notes
      LICENSE.md      MIT
      resources/      Text-mining stop-words + suffix lists
      etc/            Build helpers, docs scaffolding (non-runtime)

## AUTHOR

Tim Menzies <timm@ieee.org>, 2026. MIT License.

## SEE ALSO

- Repository: http://github.com/timm/ezr
- Sample data: http://github.com/timm/moot
