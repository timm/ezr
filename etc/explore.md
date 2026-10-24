# Classifier exploration log

What was tried against LightGBM on 60 `moot/classify` sets (every
file with a SYM class column and >=100 rows), 20 seeds, 75:25
split, win/tie/loss by `same(cliffs, ks, cohen d=.35)`.

**A line marked DEAD is not to be tried again.**  LightGBM's
per-seed accuracies are cached in `etc/lgbm60.tsv` (it is
deterministic given a seed), so later arms are scored against
that rather than re-running it.

| arm | setting | vs LightGBM | vs its own baseline | verdict |
|-----|---------|-------------|---------------------|---------|
| naive bayes, gaussian | - | - | 8 points under binned NB | DEAD |
| naive bayes, binned | BINS=17 | 9/11/40, -3.3 | the baseline | baseline |
| naive bayes, binned | BINS=7 | 11/8/41, -4.0 | -1.0 vs BINS=17 | DEAD, 17 is better |
| fastmap leaves + NB | LEAF=68 | 8/12/40 | -0.9 vs NB | DEAD |
| ditto, global prior | LEAF=68 | worse still | -1.3 vs NB, 0 wins in 10 | DEAD |
| ditto, global backoff | LEAF=max(68,20k) | - | -0.4 vs NB over 60 | DEAD |
| AODE | BINS=17 | 8/12/40, -2.4 | +0.6 vs NB | DEAD, 5 bins is better |
| AODE | BINS=5 | 13/12/35, **-1.4** | +2.2 vs NB | alive |
| DFE (discriminative counts) | EPOCHS=3 BINS=17 | 10/15/35, -2.2 | +1.1 vs NB; AODE@5 beats it 29/16/15 | DEAD, AODE@5 is better |
| DFE | EPOCHS=1 | 6/11/43, -2.8 | loses to EPOCHS=3, 0 wins in 60 | DEAD |
| TAN (one parent per column) | BINS=17 | 0/12/48, -4.8 | -2.9 vs NB: loses 23 of 60 to plain NB | DEAD, 17 bins starves the pair tables |
| TAN | BINS=7 | 3/10/47, -3.9 | still -1.2 under plain NB | DEAD, the whole TAN arm |
| TAN+DFE counts (dtan) | - | not run | TAN's structure lost at every width tried | DROPPED, built on a dead arm |
| vote NB+AODE@5+TAN as posteriors | BINS=17 | 9/14/37, -2.3 | +1.0 vs NB, 14/28/18 vs AODE@5 = a wash | DEAD, the TAN member drags it back |
| A2DE (two superparents) | BINS=3 MAXSP=25 | 9/13/38, -3.6 | huge where it matters (tic-tac-toe +17, letter +15, vowel +32 over NB) but 3 bins blunts every numeric column, so the suite total sinks | alive only as a candidate inside `pick` |
| A2DE | BINS=5 MAXSP=25 | 12/9/39, -3.5 | 5/39/16 vs BINS=3: the same model | DEAD as a standalone arm |
| pick by inner holdout, candidates NB@17/AODE@5/A2DE@3 | - | 11/10/39, -2.7 | 9/39/12 vs AODE@5 = a wash | DEAD as written: the holdout is 19% of the data and keeps choosing NB |
| pick, NB dropped from the candidates | NBC=0 | 11/10/39, -2.7 | 9/40/11 vs AODE@5 | DEAD, the selection noise, not NB, was the problem |
| vote NB+AODE@5 (no TAN) | BINS=17 | 13/7/40, -2.3 | 20/28/12 vs AODE@5 but a worse median | DEAD, AODE@5 alone is better |
| pick, 3 inner holdouts on small sets | NBC=0 REPS=3 | abandoned part-run | it fits every candidate to choose one, so it can never be the fast arm | DROPPED on cost, not accuracy; the code is not kept |
| DFE | EPOCHS=8 | 10/13/37, -2.2 | 1/58/1 vs EPOCHS=3: saturated | DEAD, no more epochs to buy |

## Where it ended

Against LightGBM over 60 sets, 20 seeds, counting speed and code
as well as accuracy (per-seed train+test seconds, summed over the
suite; LOC is the method's own functions, not the harness):

| arm | w/t/l | median | within 5 points | seconds | LOC |
|-----|-------|--------|-----------------|---------|-----|
| naive bayes BINS=17 | 9/11/40 | -3.3 | 37/60 | 6.5 (lgbm/11, median x68) | 44 |
| AODE BINS=5 | 13/12/35 | **-1.4** | 43/60 | 23.9 (lgbm/2.9, median x12) | +43 |
| LightGBM | - | - | - | 69.2 | a dependency |

## Notes

- NB's deficit tracks `log rows` (r=-.37) and LightGBM's own
  accuracy (r=-.35), NOT table width (r=-.05).  So the error is
  bias on data-rich learnable problems; feature selection and
  bagging both aim at the wrong term.  NB's seed-to-seed sd is
  lowest (0.4-0.6) on the sets it loses worst, which is why
  bagging it was never tried.
- AODE's lift over NB decays as bins grow (+2.2 at 5, +0.6 at
  17): its pair tables are quadratic in bins, so resolution that
  helps NB starves AODE.
- A floor this family cannot cross: `tic-tac-toe` -27,
  `kr.vs.kp` -9, `car` -8, `nursery` -8 are exact-rule problems
  needing 3+ columns at once.
