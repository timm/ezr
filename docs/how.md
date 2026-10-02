# How

## 0. Surface and core

A common pattern is a big surface language for humans and a tiny core
for the optimizer and the backend, with a bridge between them. The
bridge has many names. **Desugaring** in Haskell and Scheme,
**lowering** in Rust, C# and Kotlin, **elaboration** in Lean, Coq,
Idris and Agda, **macro expansion** in Lisp, **tocore** elsewhere.
Same move each time: `do`, `for`, `async`, `guard`, `cond` are deleted,
and what survives is a handful of forms the machine can reason about.
The surface is where the vocabulary lives. The core is where the work
happens, and it is always smaller than anyone expects.

Data mining has the surface. Classification, regression, clustering,
anomaly detection, retrieval, repair, synthesis, planning, monitoring,
explanation, trends, forecasting, alerts, optimization, simulation,
summarization: sixteen names, each with its own chapter, its own
conference track, its own library. What it has never written down is
the core.

So: can all sixteen desugar into under 500 words?

### The core, in under 500 words

Rows hold observations (x, left of the bar) and outcomes (y, right).
The header types every column, and that is the whole task declaration:
`Volume` (upper case) is a `Num`, `origin` a `Sym`, `Lbs-` is
minimized, `Acc+` maximized, `class!` is the klass, `HpX` is dropped.
`ydist` folds any set of `+`/`-` columns into one number, 0 = best.

Four primitives, each branching once, on column type:

| op       | `Sym` / `Num`          | means       |
|----------|------------------------|-------------|
| `mid`    | mode / mean            | summarize   |
| `_dist`  | 0-or-1 / scaled diff   | compare     |
| `sample` | roulette / gauss       | generate    |
| `delta`  | frequency shift / mean difference | extrapolate |

One learner: `cluster(rows) -> [tbl]`, group the similar. One
coordinate: `project(a,b)` places any row on the line between two
poles, out of `_dist` and nothing else. Distant rows as poles,
recursively, is `cluster`. First and last era as poles, and the same
arithmetic is TRAJECTORY.

Three ways to aim a primitive at what `cluster` returned. `relevant`
is `_dist` from a row to each cluster's `mid`s, smallest kept.
DISTINGUISH is `_dist` between two clusters' `mid`s, largest kept.
`impute` is `sample`, aimed at a chosen cluster, written back into a
row.

Everything else is those three, read differently.

From `relevant`: the `mid` of a `Sym` target is CLASSIFICATION, of a
`Num` target REGRESSION, the distance itself ANOMALY DETECTION, the
cluster's rows RETRIEVAL, a `sample` of its y cells SPREAD.

From `impute`: aim at the row's own cluster and touch empty cells,
REPAIR. At a better cluster, touching only actionable cells, PLANNING.
At any cluster, touching everything, SYNTHESIS.

From DISTINGUISH: left against right reads as EXPLANATION, worse
against better as PLANNING, better against worse as MONITORING, one
era against the next as TRENDS.

From TRAJECTORY: read at `t<=1` it is TRENDS, past `t=1` FORECAST, and
its step sizes fed to ANOMALY DETECTION are ALERTS.

Then three compositions. PLANNING and MONITORING looped is
OPTIMIZATION. SYNTHESIS then predict is SIMULATION. `same()`, gating
every row above, is DISTINGUISHABILITY. And the `mid`s of `cluster`
itself, read directly, are SUMMARIZATION.

Sixteen applications. Nothing above branches on the task. The only
branch in the system is `Num` or `Sym`, and the header row already
said which.

The rest of this document is that again, slowly, with the code.

Suppose I have a bunch of rows I want to reason about. Each row
holds some observations and some outcomes. On a sunny day, I went
walking: here day=sunny is an observation (also called an x
variable) and action=walk is an outcome (also called a y variable).
Written down, a few days look like this:

```
   day, temp | action
------------ | ------
 sunny,   25 |   walk
 sunny,   31 |   swim
 rainy,   14 |   read
 rainy,   11 |   read
```

Observations left of the bar, outcomes right of it. Some columns
hold symbols (day, action) and some hold numbers (temp), and that
difference will turn out to matter more than anything else here.

If I can cluster rows that look alike, then I can summarize the
usual values in each cluster: the mean of its numbers, the mode of
its symbols.

A cluster can be split in two by finding two distant rows, left and
right, then assigning every other row to whichever it lies closer
to. Then I can DISTINGUISH those halves by finding the one value of
the one attribute that differs most between them. That single
value, written out, is EXPLANATION: the shortest thing I can say
that tells the halves apart.

Once split, each half splits again, recursively, into a tree whose
leaves are small clusters. The tree is an index: it matches a new
row to its nearest leaf in a few questions. A slow scan of every
leaf would find the same one.

Once a new row can find its nearest cluster, I can predict its
outcomes from that cluster's summaries. This is one act, not two:
summarizing a symbolic column reports a mode, which we call
CLASSIFICATION, and summarizing a numeric column reports a mean,
which we call REGRESSION.

Prediction leaves two things lying about, and each is another
application. The distance used to pick the cluster is ANOMALY
DETECTION: a row far from every cluster is an odd one. And the
summaries can be written back instead of read. Writing a cluster's
expected value into an empty cell is imputing it. Impute every cell
and you get SYNTHESIS, a row that never happened but could have.
Impute only the empty cells of a real row and you get REPAIR. Run
ANOMALY DETECTION first, and REPAIR can also overwrite cells that
are not empty, only wrong.

Finally, suppose I score those outcomes and say which way is
better. Fun should go up, Effort should go down, and `ydist` blends
any number of such goals into one number where 0 is best:

```
   day, Temp | action, Fun+, Effort- | ydist
------------ | --------------------- | -----
 sunny,   31 |   swim,    9,       3 |  0.39  -.
 sunny,   28 |   swim,    8,       3 |  0.41   |  better half
 rainy,   14 |   read,    4,       1 |  0.59  -'
 sunny,   25 |   walk,    7,       4 |  0.60  -.
 rainy,   11 |   read,    3,       1 |  0.65   |  worse half
cloudy,   19 |   walk,    6,       5 |  0.74  -'
```

Note that reading beats walking, because a little fun for almost no
effort outscores more fun that costs more. Nobody decided that. Two
goals and one sort did.

Now I can mark one half better and the other worse, and DISTINGUISH
stops describing and starts instructing. What most separates those
halves is Temp: the better half is warmer.

And already a warning. Comparing the two halves on day scores zero,
because the commonest day is sunny on both sides -- even though the
days underneath are plainly not the same three. A number can be
averaged and compared. A symbol can only be counted. Section 2
names that crack; it never closes.

Read that forwards and it is PLANNING: the fewest changes that
would jump a row out of the worse half into the better one. Wait
for a warmer day. Read it backwards and it is MONITORING: the one
change that would drop a good row into the bad half, which is
therefore the thing most worth watching. A cold snap.

Read it as a loop and it is OPTIMIZATION, which turns out to be
PLANNING and MONITORING taking turns. Look up the outcomes of a few
rows and DISTINGUISH better from worse. Now PLAN: that split names
which unlooked-at row is most worth the next lookup. Look it up,
split again, and MONITOR: watch whether the better/worse boundary
actually moved. While it keeps moving, keep planning. When it stops
moving, more lookups buy nothing and you are done. The point is
never to look up the other thousand.

That loop has a name: ACQUIRE. It is where the lookups happen, and
it is the only place they happen. It starts from a few rows picked
at random, then keeps choosing the next one by where it sits
relative to the better and worse halves found so far -- near the
good, far from the bad.

But ACQUIRE is only half a machine. When it stops I am holding a
couple of dozen rows whose outcomes I actually know, and nothing
else. So cluster those into a tree, and now the tree can PREDICT
for rows it has never seen. Sort every row I never looked up by
what its leaf expects, take the handful at the very top, and look
up only those.

That is the whole thing. Explore a couple of dozen rows chosen by
distance, learn a tree from them, let the tree rank the hundreds I
skipped, then check a few of its best guesses. On the auto93 cars
-- 398 rows, scoring 0 for the average row and 100 for the best one
in the table -- twelve lookups score 64 and twenty score 81. Going
on to fifty is not a difference anyone can measure.

Which is the point of all of it. Everything above needs outcomes,
and outcomes are the expensive part: the crash test, the clinical
trial, the week of benchmarking. Clusters come from the x columns,
which are free. So the y columns only ever have to be read a few
dozen times, and never for the rows nobody asked about.

## 1. The language is the header row

The walk table again, in real data from `$MOOT`. Same bar, same
symbols and numbers, more rows. Sorted by `ydist` (0 = best
possible on all goals at once, 1 = worst):

```
optimize/misc/auto93.csv                            n=398
Clndrs, Volume, HpX, Model, origin | Lbs-, Acc+, Mpg+ | ydist
     4,     90,  48,    78,      2 | 1985, 21.5,   40 |  0.08
     4,     90,  48,    80,      2 | 2085, 21.7,   40 |  0.09
   ...                             |                  |
     8,    440, 215,    70,      1 | 4312,  8.5,   10 |  0.96
     8,    455, 225,    73,      1 | 4951, 11.0,   10 |  0.96

optimize/config/SS-A.csv                           n=1343
Spout_wait, Spliters, Counters | Throughput+, Latency- | ydist
        10,        6,       17 |      23075,   158.68 |  0.28
         9,        6,       17 |      22799,   156.83 |  0.28
       ...                     |                      |
     10000,        1,        1 |     310.06,     9421 |  0.99
     10000,        1,       11 |     288.56,   7908.9 |  0.99

classify/diabetes.csv                               n=768
PREG, PLAS, ..., AGE |         class! | ydist
   6,  148, ...,  50 | tested_positive|   --
   1,   85, ...,  31 | tested_negative|   --
```

Read the punctuation:

```
Volume    UPPER first letter -> Num      lower -> Sym (origin, class)
HpX       trailing X         -> dropped (still in the row, not a col)
Lbs-      trailing -         -> y, minimize
Acc+      trailing +         -> y, maximize
class!    trailing !         -> y, and it is the klass
Clndrs    no suffix          -> x, an input
```

That is the whole task declaration. `Tbl` parses it once. No
code after that asks what kind of problem this is. Note what
the first two tables share: different domains, different units,
different goal counts -- one sort order, because `ydist`
reduces any set of `+`/`-` columns to one number.

Diabetes has no `ydist` column because `!` fills `tbl.klass`,
not `tbl.y`, so there is no direction to be better in. A klass
is a goal with the geometry removed. That single missing column
is the entire difference between classification and
optimization.

## 2. Four primitives, each dual-typed

| op       | on `Sym`              | on `Num`        | means      |
|----------|-----------------------|-----------------|------------|
| `mid`    | mode                  | mean            | summarize  |
| `_dist`  | 0/1                   | scaled abs diff | compare    |
| `sample` | roulette              | gauss(mu, sd)   | generate   |
| `delta`  | frequency shift       | mu difference   | extrapolate|

Summarize, compare, generate, extrapolate. Each branches once, on
column type. Nothing else in the system branches on task.

`mid` and `_dist` are already in `ezr.py`. The other two are short
and missing:

```python
def sample(col):
  if type(col) is Sym:
    return random.choices(list(col), weights=col.values())[0]
  return random.gauss(col[1], sd(col))

def delta(a, b):                    # a earlier, b later -> forecast col
  if type(a) is Sym:
    u  = {**a, **b}                                  # every symbol seen
    pa = {v: a.get(v,0)/max(1,size(a)) for v in u}
    pb = {v: b.get(v,0)/max(1,size(b)) for v in u}
    p  = {v: max(0, 2*pb[v] - pa[v]) for v in u}     # clamp: no p<0
    n  = sum(p.values()) or 1
    return {v: c/n for v, c in p.items() if c > 0}   # renormalize
  n  = max(2, round(2*b[0] - a[0]))
  mu = 2*b[1] - a[1]
  s  = max(0, 2*sd(b) - sd(a))
  return (n, mu, s*s*(n-1))
```

### One crack, and it runs through everything

`mid` is enough for a `Num` and not enough for a `Sym`. A mean can
be differenced, extrapolated and ranked. A mode can do none of
those, so any application wanting more than a point value has to go
back to the counts.

This shows up three times and is one fact each time. A klass is a
goal with the geometry removed, so there is no `ydist` to sort by.
Two modes cannot be subtracted, so `delta` on a `Sym` works on
frequencies, not on `mid`. And `_dist` between two modes is 0 or 1,
too coarse to rank columns, so telling two clusters apart on
symbolic columns also needs the distributions. `Num` survives on
its summary; `Sym` keeps having to go back for the rest.

## 3. One operator, one coordinate

```python
cluster : tbl, rows -> [tbl]        # group the similar
```

That is the learner, and the only thing that varies (see 5).
Everything else is a primitive pointed at what it returned:

```python
relevant   : tbl, row, [tbl] -> tbl       # read:  which cluster
DISTINGUISH: tbl, tbl, tbl   -> (at, v)   # read:  how two differ
impute     : row, tbl, [at]  -> row       # write: expectations back
```

None of those is new machinery. `relevant` is `_dist` from a row to
each cluster's `mid`s, kept smallest. DISTINGUISH is `_dist` between
two clusters' `mid`s instead of between two rows, kept largest.
`impute` is `sample` aimed at a chosen cluster.

DISTINGUISH on the walk table, better half against worse:

```
col   mid(better)  mid(worse)   _dist
day        sunny       sunny     0.00
Temp        24.3        18.3     0.31   <- picked
```

That is the first half's warning, in numbers. The symbolic column
is not merely weaker here, it is invisible: both halves have the
same commonest day, so mode against mode is exactly zero.

One detail that is not arbitrary: `relevant` normalizes with the
parent `tbl`, not the cluster. Otherwise a tight cluster looks far
from everything.

### The coordinate

Given two rows a and b, the cosine rule places any third row on the
line between them, using `_dist` and nothing else:

```python
def project(tbl, a, b):       # ezr_eg.py:260, with the poles supplied
  c = xdist(tbl, a, b) + 1e-32
  return lambda r: (xdist(tbl,a,r)**2 + c*c - xdist(tbl,b,r)**2)/(2*c)
```

`t=0` at a, `t=1` at b. One function, two jobs in this paper:

| poles a, b                 | t means                | serves     |
|----------------------------|------------------------|------------|
| two distant rows           | which half you fall in | `cluster`  |
| `mid`s of first, last era  | how far along history  | TRAJECTORY |

So "split a cluster by finding two distant rows" and "walk a probe
through the eras" are the same arithmetic. They differ only in how
the poles get chosen, which is why TRAJECTORY needs no new operator:

```python
TRAJECTORY : tbl, [rows], row -> [tbl]   # probe's cluster, era by era
```

Read that list at `t<=1` and it is TRENDS, at `t>1` FORECAST, and
`delta` between its last two entries is the step you extrapolate.

## 4. Everything else, one line each

```python
targets  = lambda t: [t.klass] if t.klass is not None else list(t.y)

predict  = lambda t,r,cs: mids(relevant(t,r,cs), targets(t))
anomaly  = lambda t,r,cs: xdist(t, r, mids(relevant(t,r,cs)))
impute   = lambda r,c,ats: tuple(sample(c.cols[at]) if at in ats
                                 else v for at,v in enumerate(r))
explain  = lambda t,a,b:   routing(t, *DISTINGUISH(t,a,b))
plan     = lambda t,bad,good: DISTINGUISH(t, bad, good)
monitor  = lambda t,good,bad: DISTINGUISH(t, good, bad)
trends   = lambda t,eras,r:   [relevant(t,r,e) for e in eras]
forecast = lambda cs, at:     delta(cs[-2].cols[at], cs[-1].cols[at])
settled  = lambda b4, now:    same(b4, now)     # the stopping rule
optimize = acquire            # plan, look up, monitor, until settled
```

- **Classify** is `predict` when the target is `Sym` -- `mid`
  returns the mode.
- **Regress** is `predict` when the target is `Num` -- `mid`
  returns the mean. Same call. The `!` or the `-` in the header
  decided it.
- **Anomaly** is `predict`'s discarded byproduct: the distance
  already computed to pick the cluster. Large = odd.
- **Repair, plan, synthesize** are one `impute`, aimed at three
  different clusters: its own, a better one, any one.
- **Explain, plan, monitor, trends** are one DISTINGUISH, handed
  four different pairs. Note `plan` and `monitor` are the same
  call with the arguments swapped; that is the whole difference
  between advice and a warning.
- **Optimize** is planning and monitoring looped. `settled` is the
  first half's "when it stops moving, you are done" -- and it is
  `same()`, already in `ezr.py`, otherwise unused.

### The main loop

`ezr.py` already ships it, as `holdout`:

```python
def holdout(tbl):
  rows = random.sample(tbl.rows, len(tbl.rows))
  n = len(rows) // 2
  train, test = rows[:n][:the.Few], rows[n:]
  tr = clone(tbl, train)
  tt  = tree(tr, acquire(tr, the.Stop - the.Check))            # 1
  top = sorted(test, key=lambda r: leaf(tt,r)[2])[:the.Check]  # 2
  return min(top, key=lambda r: ydist(tr, r))                  # 3
```

Three moves. (1) ACQUIRE spends nearly all the budget, choosing
each next row by distance from the better and worse pools so far,
and `tree` turns those few labels into a PREDICTor. (2) That tree
ranks the whole test set, which costs nothing, because the ranking
is computed on x. (3) Only `the.Check` lookups are held back, to
audit the very top of that ranking.

auto93, 398 rows, 50 repeats. A win of 0 is the average row, 100 is
the best row in the table:

| budget | win | vs. previous row |
|--------|-----|------------------|
| 12     |  64 |                  |
| 20     |  81 | different        |
| 32     |  86 | same             |
| 50     |  89 | same             |

The last column is `same()` -- DISTINGUISHABILITY, the gate from
section 7 -- and it is the whole result. Twelve labels are not
enough. Twenty are. Past twenty the curve still rises, and none of
the rise survives a significance test.

That column also earns its keep. At 20 repeats this table read 90
for a budget of 32 and 87 for 50, inviting the obvious story
about spending too much. At 50 repeats it reads 86 and 89, and
`same()` says neither ordering ever meant anything.

## 5. The learner is only `cluster`

```python
def halve(t, rows):                  # the first half's own method
  if len(rows) <= the.Leaf: return [clone(t, rows)]
  a = max(rows, key=lambda r: xdist(t, r, rows[0]))   # two distant
  b = max(rows, key=lambda r: xdist(t, r, a))         # rows
  rows.sort(key=project(t, a, b))                     # nearer which
  n = len(rows) // 2
  return halve(t, rows[:n]) + halve(t, rows[n:])      # recurse

knn1   = lambda t, rows: [clone(t,[r]) for r in rows]
bayes  = lambda t, rows: groupby(rows, key=itemgetter(t.klass))
treed  = lambda t, rows: [clone(t, rs) for rs in leafRows(tree(t,rows))]
kmeans = lambda t, rows: ...          # the.K, the.N
```

Five lines, five learners: recursive halving, nearest-neighbor,
centroid Bayes, supervised tree, k-means. All feed the same
`predict`, so none of them is a rival theory of anything.

`halve` is the one the first half describes, and it never looks at
a y value -- poles and distance only. On auto93 it cuts 398 rows
into 128 leaves; the best leaf averages `ydist` 0.16 against 0.53
for the table as a whole. Distance alone found the good cars.

`treed` does look, splitting on whatever `cut` says lowers expected
`div`. Same output type, same downstream, different price: `halve`
costs no labels, `treed` costs one per row.

Either way the result is an index. `leaf(tr,row)` descends in
O(depth) what a scan over clusters does in O(clusters), and both
return the same cluster. A tree is `relevant`, made faster.

## 6. Cost

Code:

1. `mids(tbl, ats=None)` -- cache all cols, slice on read.
   Today it is x-only, and prediction needs y and klass.
2. Tree leaves keep their rows. `NODE` drops them today.
3. `sample` and `delta`, above.
4. `project` and `halve` move from `ezr_eg.py` into `ezr.py`.

Header marks, for the two applications that need something the
column names cannot yet say:

5. An order on rows -- a time or era column. Every operator here
   treats rows as a set, so TRENDS and FORECAST have nothing to
   walk along.
6. A mark for which x columns can actually be changed. Without
   it, PLANNING advises the patient to be twenty years younger.

Four small edits and two punctuation marks buy all sixteen
applications in section 7. Section 8 pays that bill in a separate
file, so `ezr.py` stays as it is.

## 7. Every application, mapped

Sixteen applications, four primitives, one operator. Everything
below is `cluster` plus a primitive aimed at what it returned. Read
these tables the way a desugarer reads its rules: the surface form on
the left, the core form on the right. CLASSIFICATION is not something
`ezr` does. It is a spelling of `mid`.

**`cluster(rows)`** -- then read the mids: SUMMARIZATION.

**`relevant(row, clusters)`** -- reading a cluster. One call, five
readings. Same arguments, same return value, every time; only the
part you look at changes.

| read off                  | application         |
|---------------------------|---------------------|
| `mid` of a `Sym` target   | CLASSIFICATION      |
| `mid` of a `Num` target   | REGRESSION          |
| the distance itself       | ANOMALY DETECTION   |
| the cluster's rows        | RETRIEVAL           |
| `sample` the y cells      | *(unnamed -- see below)* |

**`impute(row, target, cells)`** -- writing a cluster's
expectations back into a row. Same act three times over. Only the
cluster you aim at changes, and with it, which cells you may touch.

| target cluster | cells touched      | application |
|----------------|--------------------|-------------|
| its own        | empty or anomalous | REPAIR      |
| a better one   | actionable         | PLANNING    |
| any            | all of them        | SYNTHESIS   |

REPAIR aims inward and claims the data is wrong while the world is
fine. PLANNING aims across and claims the reverse. So REPAIR needs
no goals, only a cluster; PLANNING needs better and worse to know
which way across is. To overwrite cells that are not empty, only
wrong, run ANOMALY DETECTION first to find them.

Note what PLANNING needs and `ezr` does not have: a mark for which
x columns can actually be changed. `Spliters` you can set. `AGE`
you cannot. Without it, PLANNING advises the patient to be twenty
years younger.

**`DISTINGUISH(here, there)`** -- one call, four readings. Here the
arguments change and the reading follows.

| fed with           | read as                 | application |
|--------------------|-------------------------|-------------|
| left, right        | words                   | EXPLANATION |
| worse, better      | the one cheapest change | PLANNING    |
| better, worse      | a warning               | MONITORING  |
| era i, era i+1     | what moved              | TRENDS      |

PLANNING appears twice on purpose: two implementations, one target.
DISTINGUISH gives the *minimal* plan -- one attribute, one value,
the cheapest jump. `impute` gives the *total* plan -- every
actionable cell set to what the better cluster expects.

**`TRAJECTORY(eras, probe)`** -- one call, three readings.

| read at                 | application |
|-------------------------|-------------|
| t <= 1                  | TRENDS      |
| t > 1                   | FORECAST    |
| step sizes, via ANOMALY | ALERTS      |

And three that are compositions, not new machinery:

| application        | is                                |
|--------------------|-----------------------------------|
| OPTIMIZATION       | PLANNING and MONITORING, looped   |
| SIMULATION         | SYNTHESIS, then predict           |
| DISTINGUISHABILITY | `same()` -- gates every row above |

### Not exotic

No compiler writer would find any of this strange:

| Language | What the bridge is called | What stops existing |
|---|---|---|
| **Haskell** (GHC) | Desugarer (`GHC.HsToCore`), `HsSyn` -> Core | `do`, comprehensions, guards, `where`, classes |
| **Rust** | AST -> HIR "lowering" (spans tagged `DesugaringKind`) | `for` -> `loop` + `match`; `?` -> `match`; `async` |
| **Java** (javac) | `Lower`, `TransTypes` | inner classes, enhanced `for`, enums, generics |
| **Scheme / Racket** | Macro expansion to fully expanded core forms | `let`, `cond`, `and`/`or` -> `lambda`/`if` |
| **Lean / Coq / Idris** | "Elaboration" to a small kernel calculus | `do`, implicit args, classes, tactics |
| **Swift** | SILGen (AST -> SIL) | `guard`, optional chaining, `defer` |

Scala, C#, Kotlin, OCaml, Clojure and C++ all do the same under their
own names. In every one of them the sugar is what people write and the
core is what the machine reasons about, and the core stays small
because that is what makes the reasoning tractable.

The tables above are that table, for data mining. The left column is
what gets written on a grant application. The right column is what
runs.

### The hole this table found

Row five of the first table has no name. `sample` the y cells and
you get a *distribution* over outcomes instead of a single one --
not "this car does 30mpg" but "this kind of car does 28 to 34,
usually 30." Every other prediction row throws that away by calling
`mid`. It costs nothing, it is strictly more than CLASSIFICATION or
REGRESSION return, and no cell of the standard picture asks for it.

## 8. Built

`how.py`, 284 lines, `import ezr`. It is this document in order:
the four primitives section 6 called missing, then `halve`, then
`relevant` / DISTINGUISH / `impute`, then one function per
application in capitals, then a demo for each. `ezr.py` is not
touched.

```
python3 how.py --all
```

What that prints, on `$MOOT` data, unedited:

**TRENDS and FORECAST.** Eras cut by `Model` year, one probe row
walked through them:

```
era mpg   12.5 -> 15.38 -> 20 -> 25
era lbs   4271 -> 4109  -> 3693 -> 3028
next mpg  30      next lbs  2363
next origin  {1: 0.5, 3: 0.5}
```

Cars got lighter and more efficient from 1970 to 1982, and the
extrapolated era is 30mpg at 2363lbs. Nobody mentioned the oil
crisis. The last line is the `Sym` case: US share falling, Japanese
share rising, extrapolated from frequencies because modes cannot be
subtracted.

**OPTIMIZATION.** Twenty lookups of 398 rows, win 97.

**SPREAD**, the unnamed row of section 7:

```
Mpg+   point 15.83   10th-90th  10.8 .. 22.5
```

The point is what CLASSIFICATION and REGRESSION return. The range is
what they throw away.

**EXPLANATION, PLANNING, MONITORING**, one DISTINGUISH between the
best and worst clusters, restricted to columns a designer controls:

```
explain   origin = 3
plan      Volume 351 -> 87
monitor   Volume  70 -> 402
```

The best cars are Japanese; the cheapest way up is a smaller
engine; the thing to watch is a bigger one.

### Two defects the demos exposed

`sample` ignores integrality. Synthesized cars have `Clndrs 3.68`.
A gauss over a `Num` does not know the column only ever held whole
numbers, and nothing in section 2 says it should. This is a defect
in the primitive, not in the file that calls it.

ANOMALY bottoms out at exactly 0, because a row sits inside its own
cluster and the distance to its own summary can vanish. Fine for
ranking rows against each other, useless as an absolute threshold
-- which is what ALERTS wants. ALERTS therefore compares each step
against the spread of earlier steps rather than against any fixed
number, and that is a workaround, not an answer.
