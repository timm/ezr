![Python 3.14](https://img.shields.io/badge/Python-3.14-blue?logo=python&logoColor=white&labelColor=1D4ED8&color=0A2A7A)
![Purpose XAI](https://img.shields.io/badge/Purpose-XAI-orange?logo=openai&logoColor=white&labelColor=FB8C00&color=A85A00)
![Goal Multi-Obj](https://img.shields.io/badge/Goal-Multi--Obj-purple?logo=target&logoColor=white&labelColor=C026D3&color=6D1780)
![Teaching](https://img.shields.io/badge/Teaching-CSC591-red?logo=graduationcap&logoColor=white&labelColor=DC2626&color=7F1D1D)
![Deps 0](https://img.shields.io/badge/Deps-0-green?logo=checkmarx&logoColor=white&labelColor=00C853&color=006B29)
![LOC 300](https://img.shields.io/badge/LOC-300-yellow?logo=codecov&logoColor=white&labelColor=FDE047&color=C3A700)
![License](https://img.shields.io/badge/©_2026-timm-black?logo=github&logoColor=white&labelColor=24292e&color=000000&link=http://timm.fyi)
![tests](https://github.com/timm/ezr/actions/workflows/tests.yml/badge.svg)


# EZR(1) - Explainable Multi-Objective Optimization

## NAME

**ezr** — explainable multi-objective optimization via decision trees,
clustering, Naive Bayes, and active learning

## SYNOPSIS

    ezr [OPTIONS] COMMAND [FILE]
    python ezeg.py [OPTIONS] COMMAND [FILE]
    pytest ezeg.py [-v] [-k PATTERN]

## DESCRIPTION

**ezr** is a lightweight toolkit for multi-objective optimization
and explainable AI. It summarizes CSV data into Num/Sym columns,
builds decision trees that minimize distance to ideal outcomes,
clusters rows via k-means or recursive halving, and supports
active learning with Naive Bayes or centroid-based acquisition.

**ezr** is an experiment in "how low can you go?". i.e. how little
data do you need for effective AI. THe code using active learning
to label a small number of (say) 50 informative examples. These are
used to build a regression tree which, in turn, is used to sort the
unlabelled test data. Repeated studies show that by labelling the
first (say) 5 examples, then the selected row optimzies as well or
better than the conclusions mae by state of the art optimizers SMAC
(which runs two orders of magnitice slower than **ezr**).


Input is CSV. The header row defines column roles:

    [A-Z]*    Numeric (e.g. "Age")
    [a-z]*    Symbolic (e.g. "job")
    [A-Z]*+   Maximize goal (e.g. "Pay+")
    [A-Z]*-   Minimize goal (e.g. "Cost-")
    [a-z]*!   Class label (e.g. "sick!")
    *X        Ignored (e.g. "idX")
    ?         Missing value (in data rows, not header)

The codebase is two files:

- **ezr.py** — the library (columns, data, distance, trees,
  clustering, Bayes, active learning, stats)
- **ezeg.py** — the CLI driver and all test/demo functions

## INSTALLATION

### Option A: Install as a package

    git clone http://github.com/timm/ezr
    cd ezr
    pip install -e .

This creates the global `ezr` command. Edits to `ezr.py`
and `ezeg.py` take effect immediately.

    ezr --h
    ezr --see auto93.csv
    ezr --seed=42 --test auto93.csv

To uninstall:

    pip uninstall ezr

### Option B: Run from the directory

    git clone http://github.com/timm/ezr
    cd ezr
    python ezeg.py --h
    python ezeg.py --see auto93.csv

No installation required. Just needs Python 3.12+.

### Sample data

    mkdir -p $HOME/gits
    git clone http://github.com/timm/moot $HOME/gits/moot

## COMMANDS

    --h                 Show help text
    --list              List all available demos and tests
    --egs FILE          Run all demos sequentially on FILE
    --see FILE          Show grown decision tree (Rung 1: association)
    --funny FILE        Test rows against tree leaves, flag anomalies (Rung 2)
    --plan FILE         Generate counterfactual plans (Rung 3: what-if)
    --test FILE         Run full train/predict/score pipeline
    --classify FILE     Run incremental Naive Bayes classification
    --cluster FILE      Run clustering benchmark table
    --acquire FILE      Compare active learning strategies

## OPTIONS

Options update the global configuration. Use `--key=value` syntax.

### Learning & Trees

    --learn.leaf=3      Minimum examples per leaf
    --learn.budget=50   Number of rows to evaluate
    --learn.check=5     Number of guesses to check
    --learn.start=4     Initial number of labels

### Distance & Bayes

    --p=2               Distance metric (1=Manhattan, 2=Euclidean)
    --bayes.m=2         m-estimate for Naive Bayes
    --bayes.k=1         k-estimate (Laplace smoothing)
    --few=512           Max unlabelled rows in active learning

### Statistics

    --stats.cliffs=0.195  Cliff's Delta threshold
    --stats.conf=1.36     KS test confidence coefficient
    --stats.eps=0.35      Margin of error multiplier

### Display

    --seed=1            Random number seed
    --show.show=30      Tree display width
    --show.decimals=2   Decimal places for floats

Options and commands can be interleaved. Options apply to
all subsequent commands:

    ezr --seed=42 --learn.budget=30 --test auto93.csv --see auto93.csv

## TESTING

### Run all tests with pytest

    pip install pytest
    pytest ezeg.py -v

### Run a single test

    pytest ezeg.py -k test_num

### Run all demos via the CLI

    ezr --egs auto93.csv

### Available test functions

    test_o          String formatting
    test_table      Tabular output
    test_thing      Type coercion
    test_nest       Nested namespace setting
    test_csv        CSV reading
    test_h          Help text
    test_the        Config parsing
    test_list       List all demos
    test_egs        Run all demos
    test_num        Num column statistics
    test_sym        Sym column entropy
    test_pick       Random sampling from distributions
    test_cols       Column extraction logic
    test_data       Data object population
    test_addsub     Incremental add/subtract rows
    test_classify   Naive Bayes classification
    test_distx      Independent variable distance
    test_disty      Dependent variable distance
    test_tree       Decision tree (Rung 1)
    test_funny      Anomaly detection (Rung 2)
    test_plan       Counterfactual plans (Rung 3)
    test_test       Train/predict/score pipeline
    test_cluster    Clustering benchmarks
    test_acquire    Active learning comparison

## LIBRARY USAGE

**ezr.py** exports everything needed to use the toolkit
programmatically:
```python
from ezr import *

d = Data(csv("auto93.csv"))
win = wins(d)
t = treeGrow(d, d.rows)
treeShow(t)

for r in sorted(d.rows, key=lambda r: disty(d, r))[:5]:
    print(win(r), r)
```

This generates the following where _D_ is distance to heaven (lower values are better),
_n_ is the number of examples in that branch, and _goals_ shows the rows in that branch.

```
$ ezr --tree ~/gits/moot/optimize/misc/auto93.csv
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
|   |   origin != 2           ,0.61 ,(  5), {Acc+=15.64, Lbs-=2344.00, Mpg+=30.00}
|   |   origin == 2           ,0.66 ,(  7), {Acc+=15.54, Lbs-=2464.43, Mpg+=24.29}
Clndrs > 5                    ,0.72 ,( 24), {Acc+=14.52, Lbs-=3629.83, Mpg+=18.33}
|   origin != 1               ,0.63 ,(  3), {Acc+=14.93, Lbs-=3000.00, Mpg+=26.67}
|   origin == 1               ,0.73 ,( 21), {Acc+=14.46, Lbs-=3719.81, Mpg+=17.14}
|   |   Volume <= 302         ,0.71 ,( 12), {Acc+=15.88, Lbs-=3385.92, Mpg+=19.17}
|   |   |   Clndrs <= 6       ,0.71 ,(  8), {Acc+=16.94, Lbs-=3308.25, Mpg+=20.00}
|   |   |   |   Model <= 75   ,0.71 ,(  5), {Acc+=16.20, Lbs-=3219.40, Mpg+=20.00}
|   |   |   |   Model > 75    ,0.71 ,(  3), {Acc+=18.17, Lbs-=3456.33, Mpg+=20.00}
|   |   |   Clndrs > 6        ,0.73 ,(  4), {Acc+=13.77, Lbs-=3541.25, Mpg+=17.50}
|   |   Volume > 302          ,0.75 ,(  9), {Acc+=12.57, Lbs-=4165.00, Mpg+=14.44}
|   |   |   Model > 73        ,0.71 ,(  3), {Acc+=13.37, Lbs-=4171.33, Mpg+=20.00}
|   |   |   Model <= 73       ,0.76 ,(  6), {Acc+=12.17, Lbs-=4161.83, Mpg+=11.67}
```



Key exports: `Data`, `Num`, `Sym`, `Cols`, `Tree`,
`adds`, `clone`, `mid`, `spread`, `norm`, `disty`, `distx`,
`treeGrow`, `treeLeaf`, `treeShow`, `treePlan`,
`kmeans`, `kpp`, `rhalf`, `half`,
`like`, `likes`, `classify`, `acquire`,
`wins`, `ready`, `csv`, `o`, `table`, `the`.

## FILES

    ezr.py          Library (columns, data, trees, clustering, Bayes, stats)
    ezeg.py         CLI driver, demos, and test functions
    pyproject.toml  Package configuration

## AUTHOR

Tim Menzies <timm@ieee.org>, 2026. MIT License.

## SEE ALSO

- Repository: http://github.com/timm/ezr
- Sample data: http://github.com/timm/moot
