## Maths idioms in ezr.py

Ten pieces of maths in ezr.py that can puzzle newcomers,
easiest first. Each gets a plain statement, then the ezr
usage.

### 1. Mean and mode as "the middle"

Numbers summarize to their mean; symbols, having no order,
summarize to their most common value (the mode). One idea —
"typical member" — two formulas.

```py
mean = sum(xs) / len(xs)
mode = max(counts, key=counts.get)
```

ezr's `mid` picks per type:

```py
def mid(c):
  return c[1] if is_num(c) else max(c, key=c.get)
```

### 2. Incremental mean (Welford, part 1)

You need not store numbers to know their mean. Keep a count
and a mean; each new value nudges the mean by its distance,
scaled by the count.

```py
n += 1
mu += (x - mu) / n
```

ezr's `add` does this, so a column summarizes a million rows
in three numbers.

### 3. Incremental variance (Welford, part 2)

Alongside the mean, keep `m2`, the sum of squared distances
to the (moving) mean. Then variance is `m2/(n-1)` and the
standard deviation is its square root. One pass, no stored
list, no catastrophic cancellation.

```py
d = x - mu; mu += d/n; m2 += d*(x - mu)
```

ezr derives sd on demand:

```py
def sd(c): return 0 if c[0] < 2 else (c[2]/(c[0]-1)) ** .5
```

### 4. Un-adding a number (reverse Welford)

Run the same updates with a negative increment and a value
leaves the summary. ezr's sweeps use this to slide one value
at a time from the "right" pile to the "left" pile.

```py
here, there = add(here, y), add(there, y, -1)
```

### 5. Z-scores, and clamping

`z = (x - mu)/sd` measures "how many standard deviations
from typical". Almost everything lies in -3..3, so ezr clamps
there before squashing — one wild outlier should not crush
everyone else onto a dot.

```py
z = max(-3, min(3, (v - c[1]) / (1e-32 + sd(c))))
```

(The `1e-32` dodges divide-by-zero when a column is
constant.)

### 6. Squashing with a logistic

`1/(1 + e^(-1.7z))` maps any z to 0..1, smoothly: typical
values land near 0.5, extremes near 0 or 1. The 1.7 makes
the logistic curve approximate the normal distribution's
CDF. Now numeric columns with wildly different units all
speak the same 0..1 language.

```py
return 1 / (1 + math.exp(-1.7 * z))
```

### 7. Minkowski distance

Generalized distance between two points: sum the per-axis
gaps raised to power P, then take the P-th root. P=1 is
city-block distance; P=2 is Euclidean.

```py
d = (sum(abs(a-b)**P for a,b in zip(p1,p2)) / n) ** (1/P)
```

ezr uses it twice: `xdist` between rows, and:

### 8. Distance to heaven

Multi-objective scoring without weights-fiddling: normalize
every goal to 0..1, imagine the ideal point ("heaven": each
goal at its best), and score a row by its distance to it.
Lower is better; goals to maximize use ideal 1, minimize
use ideal 0.

```py
def ydist(t, row):
  return (sum(abs(norm(t.cols[at], row[at]) - w) ** the.P
              for at, w in t.y.items()) / len(t.y))**(1/the.P)
```

### 9. Diversity, twice: sd and entropy

How mixed-up is a set? For numbers, standard deviation. For
symbols, entropy: `-sum(p * log2 p)` — 0 when all agree,
larger the more evenly the votes split. ezr's `div` unifies
them, so tree-splitting code never asks which type it holds.

```py
def div(c):
  if is_num(c): return sd(c)
  n = sum(c.values())
  return -sum(v/n * math.log2(v/n) for v in c.values())
```

### 10. Expected diversity after a split

To score a proposed split, take the diversity of each half,
weighted by its size — the expected diversity of a random
member afterwards. Trees greedily pick the split minimizing
this; repeating that recursively is most of what "decision
tree learning" means.

```py
def xpect(a, b):
  return ((div(a)*size(a) + div(b)*size(b))
          / (size(a) + size(b)))
```

Bonus, hiding in `label`: keep the elite pool at about the
square root of all labelled rows (`b*b > 1 + b + r`) — big
enough to aim with, small enough to stay elite.
