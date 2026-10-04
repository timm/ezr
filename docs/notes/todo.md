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

## Tiny metaheuristics (from Brownlee/Luke TOC survey)

Context: surveyed "Clever Algorithms" (Brownlee 2011, 45 algos)
and "Essentials of Metaheuristics" (Luke 2013). Core canon (~20
algos) in both; neither covers surrogate/Bayesian optimization --
the gap ezr lives in. Luke ch.9 (LEM, model-fitting-by-
classification) is basically `acquire`'s best/rest loop.

Already have: sa, de, oneplus1 (1+1 ES), ls (hill climb),
acquire (~LEM active learning).

### Candidates, ranked by fit (est LOC given kernel primitives)

- [ ] UMDA (~15): adds() elite rows into clone, sample each col
      from mid/spread. Cols ARE the distribution model.
- [ ] Cross-Entropy Method (~15): UMDA + elite fraction +
      smoothing. Near-duplicate.
- [ ] PBIL (~20): per-col prob vector nudged toward best row.
- [ ] Iterated Local Search (~10): wrap ls, perturb via one
      extrapolate kick, accept rule.
- [ ] (mu+lambda) ES (~15): generalize oneplus1; keep mu best by
      disty, spawn lambda.
- [ ] Memetic (~10): de/ga step then ls polish.
- [ ] CLONALG (~20): clone best, mutate rate ~ rank. Silly
      metaphor, tiny code.
- [ ] LVQ (~15): nearest + nudge centroid; kmeans cents exist.
- [ ] GA (~25): tournament by disty, per-col uniform crossover.
- [ ] Fitness sharing (~10): penalize disty by distx crowding.
- [ ] Island model (~15): k pops, swap best occasionally.

Best bang: UMDA/CEM/PBIL trio (~40 LOC total). Fills EDA gap;
directly comparable to acquire -- both "learn distribution of
good rows, sample it". Natural xaiplus experiment.

Poor fit / big: GP, grammatical evolution, LCS/XCS, ACO (wants
graphs not tables), BOA, backprop. NSGA-II questionable: disty
distance-to-heaven already collapses multi-objective.

### Soft tabu = Bayes over the visited (~10 LOC)

Reframe: tabu list -> `seen = clone(data)` of visited rows;
reject candidate when likes(seen, new, ...) too high ("been
near here"). Closer to guided local search / frequency memory
than strict tabu, but smoother. Aspiration = keep best-so-far
check. Warm up ~10 rows before enforcing jail (likes noisy on
tiny seen; like() divides by sd).

Fading (forget old tabus) via sub() -- retraction already in
kernel:

- FIFO: `if len(seen.rows) > tenure: sub(seen, seen.rows.pop(0))`
  = classic tenure, sharp horizon.
- Random: low prob, `sub(seen, seen.rows.pop(randrange(...)))`
  = exponential decay; same math as ACO pheromone evaporation.
- Stable size, soft: fade prob = len(seen.rows)/cap.

Only sub rows actually in seen.rows (else Num mu/m2 corrupt).

Unification: tabu, tenure, ACO evaporation all collapse to one
idea -- a Bayes model you add fresh sins to, sub old sins from.
