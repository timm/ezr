# Desugar

Languages run a big surface for humans over a tiny core for the
machine. The bridge is called **desugaring** (Haskell, Scheme),
**lowering** (Rust, C#, Kotlin), **elaboration** (Lean, Coq,
Idris), **macro expansion** (Lisp), **tocore**. Same move every
time: `do`, `for`, `async`, `guard`, `cond` stop existing, and a
handful of forms survive. Surface is where the vocabulary lives.
Core is where the work happens, and it is always smaller than
anyone expects.

Data mining is all surface. Here is its core.

## The core

```
Four primitives, each branching once, on column type:

  mid     mode / mean               summarize
  _dist   0-or-1 / scaled diff      compare
  sample  roulette / gauss          generate
  delta   freq shift / mu diff      extrapolate

One learner     cluster(rows) -> [tbl]   group the similar
One coordinate  project(a,b)  -> t       place row between poles

Three aimings
  relevant      _dist, row to cluster mids, smallest
  DISTINGUISH   _dist between two clusters' mids, largest
  impute        sample a chosen cluster, write it back
```

Goals need no operator. The header row says `Lbs-`, `Acc+`,
`class!`, and `ydist` folds any set of those into one number,
0 = best.

## The rules

```
cluster(rows)          => SUMMARIZATION  read the mids

relevant(row, cs)      => CLASSIFICATION mid of a Sym target
                       => REGRESSION     mid of a Num target
                       => ANOMALY        the distance itself
                       => RETRIEVAL      the cluster's rows
                       => SPREAD         sample the y cells

impute(row, cluster)   => REPAIR         own cluster, empty cells
                       => PLANNING       better, actionable cells
                       => SYNTHESIS      any cluster, all cells

DISTINGUISH(here,there)=> EXPLANATION    left vs right
                       => PLANNING       worse vs better
                       => MONITORING     better vs worse
                       => TRENDS         era i vs era i+1

TRAJECTORY(eras,probe) => TRENDS         read at t <= 1
                       => FORECAST       read at t > 1
                       => ALERTS         steps, via ANOMALY

compositions           => OPTIMIZATION   PLAN + MONITOR, looped
                       => SIMULATION     SYNTHESIS, then predict
                       => DISTINGUISHABILITY   same()
```

Nothing there branches on the task. The only branch in the system
is `Num` or `Sym`, and the header row already said which.

## The nine

Buse and Zimmermann, *Information Needs for Software Development
Analytics* (ICSE 2012), list nine analysis techniques: three
activities, three tenses. That table is the surface language.
Here is what each cell desugars to.

|            | Past             | Present          | Future        |
|------------|------------------|------------------|---------------|
| Explore    | Trends           | Alerts           | Forecasting   |
|            | `TRAJECTORY t<=1`| steps + ANOMALY  | `delta`       |
| Analyze    | Summarization    | Overlays         | Goals         |
|            | `mid`s           | *unclaimed*      | `ydist`       |
| Experiment | Modeling         | Benchmarking     | Simulation    |
|            | `cluster`        | `same()`         | SYNTHESIS     |

Eight of nine, and Goals is not a technique here, it is
punctuation in the header row. Only Overlays has no core form.

Classic machine learning covers a different slice of the same
surface -- classify, regress, cluster, detect, retrieve, repair,
synthesize, explain, plan -- and desugars to the same core.

Details, code and costs: `how.md`.
