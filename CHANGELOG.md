# Changelog

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
