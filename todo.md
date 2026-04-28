# ezr/ezeg split

## ezr.py keeps (engine)
- [ ] Types
- [ ] Columns: Num, Sym, mid, spread, norm
- [ ] Data: Data, Cols, clone, add, sub, adds, mids
- [ ] Distance: minkowski, disty, distx, aha, nearest
- [ ] Bayes primitives: like, likes
- [ ] Trees: Tree, treeCuts/Split/Grow/Leaf/Nodes/Show
- [ ] 1+1 optimization: picks, oneplus1, oracleNearest
- [ ] Stats: same, bestRanks
- [ ] Utilities: o, table, thing, nest, csv, pick
- [ ] Config: the, parsing

## Move to ezeg.py (applications)
- [ ] Classification: classify, Confuse, confuse
- [ ] Tree planning: treePlan
- [ ] Active learning: acquire, warm_start, rebalance, acquireWithBayes, acquireWithCentroid
- [ ] Search: sa, ls (already in ezeg)

## Rules
- One-way deps only: ezeg -> ezr, never reverse
- If moving forces callback or forward ref, it stays in ezr
- `from ezr import *` covers all ezeg needs

## After split
- [ ] Verify `python3 -c "import ezr"` clean
- [ ] Verify `python3 -c "import ezeg"` clean
- [ ] Run pytest ezeg.py
- [ ] Check no line > 70 chars in ezr.py



# todo

## Kernel / spoke refactor (open)

Goal: shrink ezr.py to ~250 LOC kernel at 65-wide. Move algorithm
families into `eg_*.py` spokes. Apply rule: a symbol stays in kernel
iff >=2 spokes use it.

### Stays in ezr.py (kernel, ~25 names + 4 classes)

- Globals / utils:
  `the, isa, o, thing, csv, nest, table`
- Structs:
  `Num, Sym, Cols, Data`
- Polymorphic stats:
  `Col, add, sub, adds, mid, spread, norm, pick`
- Data ops:
  `clone, mids, ready`
- Distance kernel:
  `minkowski, aha, distx, disty`
- Bayes likelihood (used by classify spoke + active spoke):
  `like, likes`
- Stat tests (used by treePlan + bestRanks + sa-vs-ls compare):
  `same, bestRanks`

Target: ezr.py ~250 LOC, 65-wide, no algorithm families.

### Moves out (5-10 spokes)

1. `eg_tree.py` — Tree, treeCuts, treeSplit, treeGrow, treeLeaf,
   treeNodes, treeShow, treePlan
2. `eg_bayes.py` — classify, Confuse, confuse, confused
3. `eg_cluster.py` — kmeans, kpp, half, rhalf, neighbors, clustering
4. `eg_active.py` — acquireWithBayes, acquireWithCentroid, rebalance,
   warm_start, active, acquire, wins
5. `eg_search.py` — oneplus1, picks, nearest, last, oracleNearest,
   sa, ls
6. `eg_fastmap.py` — Dim, proj, index, poles, newDim, dims,
   clusters (port from rash.py)
7. `eg_text.py` — thin wrapper over textmine.py

Optional (if growth warrants):
8. `eg_compare.py` — head-to-head benchmarks
9. `eg_anomaly.py` — leaf-distance flagging from rung 2
10. `eg_explain.py` — SHAP-lite via tree path attribution

### Spoke contract

- `from ezr import *` only. Never spoke -> spoke imports.
- 30-60 LOC algorithm + main() <=10 LOC. >60 LOC = "is this two
  lessons?" -- split.
- Tests inline (`test_X(file=eg)` annotation-driven).
- Runnable: `python -m ezr.eg_tree data.csv`
- Callable: `ezr tree data.csv` via single dispatcher.

### Style for the refactor

- Width: 65 (forces small fns, pushes shared math into kernel).
- Self name: `it` (not `i`; reserve `i` for int loops).
- Polymorphism: `match it: case Data(): ...` over `if T == type(it)`.
- Var names: rash.py table wins on collisions.
- Section headers: `# ---- N. Name ----`.
- One-line `"docstring"` per fn unless ship-to-pytest spoke.
- Form feeds (`\f`) before sections that warrant column breaks for
  a2ps printing.

### Promotion rule (re-audit before any release)

A symbol lives in `ezr.py` iff removing it would break >=2 files in
`eg/`. If only one spoke uses it, push it down into that spoke. No
sentimental promotions.

### Currently in ezr.py that the rule says to move

- `wins` -- only `active` uses it; demote to eg_active.py
- `like, likes` -- if `eg_active.py` is the only consumer besides
  `eg_bayes.py`, kernel still wins (>=2). Confirm before refactor.

## Style precedence (for new files)

| Concern               | Win source           |
|-----------------------|----------------------|
| Variable names        | code1style (rash)    |
| Polymorphism          | code1 (match/case)   |
| Self name             | code1 (`it`)         |
| Docstring length      | code1 (one line)     |
| Hints in single file  | code1 (none)         |
| Hints in kernel API   | code2 (full)         |
| Multi-file structure  | code2 (kernel/spoke) |
| Nested config         | code2 (when needed)  |
| Width                 | 65 (printable)       |
