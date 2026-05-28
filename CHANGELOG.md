# Changelog

## [0.9.4] — 2026-05-27

### Changed
- Collapsed star-topology layout into two files: `ezr.py` (library)
  and `cli.py` (CLI dispatch + demos/tests). All apps inlined.

### Removed
- Modules `classify.py`, `tree.py`, `cluster.py`, `search.py`,
  `acquire.py`, `textmine.py`, `stats.py` (merged into `ezr.py`).
- `tests/` directory (pytest scaffolding). Tests now live in
  `cli.py` as `eg_test_*` functions, invoked via `ezr test_<name>`
  or `ezr test_all`.
- `rebalance()` renamed from `dont_let_Best_grow_too_big()`.

### Added
- `ezr.py` section banners for each app (Stats, Tree, Cluster,
  Classify, Search, Acquire, Textmine).
- `cli.py` self-describing dispatcher: `ezr --list` shows all
  `eg_*` commands with one-line docs.
- `eg_test_all`: runs every `eg_test_*` and reports pass/fail count.


## [0.9.3] — 2026-03-28

### Added
- Section 8 (`1+1 optimization`) in `ezr.py`, introducing a generic
  `oneplus1` search loop framework
- Simulated Annealing (`sa`) and Local Search (`ls`) optimization
  algorithms
- Optimization helper functions: `picks()`, `nearest()`, `last()`,
  and `oracleNearest()`
- Section 9 (`Search`) in `ezeg.py` containing tests for the new
  optimization algorithms: `test_sa()`, `test_ls()`, `test_compare()`

### Changed
- `the.seed`: 31451 → 1
- `pick()` how has optional second arg for prior value. Used when
  mutating around existing numeric values.


## [0.9.2] — 2026-03-27

### Changed
- `the.seed`: 1 → 31451
- `the.few`: 512 → 128 (smaller unlabeled pool for acquire)
- `pick()` clamp: was `max(mu-3*sd, min(mu+3*sd, z))` (raw value),
  now `max(-3, min(3, z))` (z-score). Different semantics.
- `wins()` parenthesiza
### Added
- `test_acquire()`: single-strategy active learning benchmark
- `test_acquire3()`: three-way comparison (rand/bayes/centroid)
- "Types" section marker in ezr.py header comments
- "Ready, set, go" section marker in ezr.py

### Removed
- `any` variable in old `eg_acquire` (was unused duplicate of
  `lab1`)
- Second return value (`fn`) from `acquire()`

## [0.9.1] — 2026-03-XX

Initial tracked release.
