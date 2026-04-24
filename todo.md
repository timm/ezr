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
