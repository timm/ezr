# rq: research questions for ezr/ezr0

Data: `rq.py`; each run draws a random moot/optimize dataset,
Budget (10..200 labels), Check (1..10 test probes); score = win
(100 = found the best row, 0 = no better than average).

## RQ1: how much does a labelling budget buy?

25,000 paired runs per algorithm (pypy3.12, 10-way xargs, ~5
min/arm).

**Fig 1: ezr0** (whole budget spent at random, up front)

![ezr0 mean win over budget and check](docs/rq.png)

**Fig 2: ezr** (one label picked after each label)

![ezr mean win over budget and check](docs/rq_ezr.png)

**Fig 3: ezr minus ezr0** (red: ezr wins; blue: ezr0 wins)

![win difference, ezr minus ezr0](docs/rq_diff.png)

- **Check dominates Budget.** Win climbs steeply with Check
  everywhere; past Budget ~50, more labels barely help.
- **Very little delta ezr vs ezr0.** Over most of the map the
  difference is within noise (±3 wins). Sequential labelling
  buys nothing once labels are even modestly plentiful.
- Both exceptions sit at Budget < 25: ezr wins (+20) at Check
  9..10; ezr0 wins (-20) at Check 1..5. Active learning only
  pays when labels are very scarce, and hurts there if too few
  checks are held back.

### RQ1a: how stable are these wins?

**Fig 4, 5: sd of win** (ezr0, ezr); **Fig 6: se of the mean**

![ezr0 win sd](docs/rq_sd.png)

![ezr win sd](docs/rq_ezr_sd.png)

![standard error of mean win](docs/rq_se.png)

- **The means are solid.** Standard error is 2..5 wins almost
  everywhere (Fig 6), so the 5-win contour steps of Figs 1..2
  are resolved; more runs would change nothing.
- **The spread is real, and it mirrors the mean.** Run-to-run
  sd is 20..25 on the high-win plateau but 40..50 in the
  label-starved corner: low-budget runs are not just worse on
  average, they are lottery tickets. Most of that sd is
  dataset heterogeneity (per-dataset means run 60..100), not
  sampling noise.

## RQ2: what do interpreter, parallelism, and layout cost?

500 runs per cell (small, so fixed costs understate the
parallel gain; at 25,000 runs xargs-10 gave ~5x).  All sixteen
cells were measured in one pass on one machine, so they are
mutually comparable; they supersede an earlier run whose
absolute times ran ~15% faster.

Each cell reads `o(dict)` -> `__slots__`: the same program with
`Num`/`Sym` as plain classes rather than dict subclasses, and
`type(col) is Sym` rather than `"has" in col`.  Only the columns
changed; `the`, tables and tree nodes are still `o(dict)`, which
needs `in`, `[]` and `.update` on what it also reads with a dot.
Byte-identical output on all 127 datasets, and on every demo and
rig.

Cells are seconds:

| dict→slots | ezr0 serial | ezr0 x10  | ezr serial | ezr x10   |
|------------|-------------|-----------|------------|-----------|
| python3    | 109.6→75.5  | 56.7→39.3 | 135.6→89.4 | 66.0→41.3 |
| pypy3.12   |  27.8→18.6  | 15.7→12.0 |  34.4→22.0 | 19.3→13.8 |

- Four independent levers that multiply: pypy3.12 ~4x; xargs-10
  1.6-2.2x here (more at scale); ezr0 over ezr ~1.2x;
  `__slots__` 1.3-1.5x for ezr0, 1.5-1.6x for ezr.
- pypy does *not* absorb `__slots__` (1.49x on pypy serial for
  ezr0, 1.56x for ezr), which is the opposite of what we
  expected.  Escaping `o(dict)` wins on writes -- Welford sets
  four fields on every numeric add -- as much as on reads, and
  a JIT cannot specialise away a `__setattr__` that must run.
- ezr gains more than ezr0: its tree builder adds into fresh
  `Num()` accumulators for every candidate split, so it leans
  on column writes even harder.
- Worst to best, (serial, python3, ezr, dicts) to (xargs-10,
  pypy3.12, ezr0, slots): **11x** (135.6s to 12.0s).  Without
  `__slots__` that same span is 8.6x (135.6s to 15.7s).

## Conclusion

Label a few dozen rows any way at all, hold back a handful of
checks, and pick on validation: that simple recipe matches the
clever one except in the label-starved corner (RQ1). And the
whole study is cheap: pypy plus ten processes turns an
afternoon of compute into minutes (RQ2).
