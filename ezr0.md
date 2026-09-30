In the beginning was the row, and it was not
known if it was good.
The row has columns for the y values and the x observable or
controllables. And we wanted to learn the function `y=f(x)`.

Columns were  two types: N

```py
def candidates(col, rows, at):
  "What splits to try: one per symbol, or CUTS per num."
  if "has" in col:
    for v in sorted({r[at] for r in rows if r[at] != "?"}):
      yield v, lambda r,v=v,at=at: r[at] == v
  else:                # by rank, not value: THESE rows are dense
    xs = sorted(r[at] for r in rows if r[at] != "?")
    k  = max(1, len(xs)//the.Cuts)     # cuts, spaced by rank
    for v in xs[k-1:-1:k]:
      yield v, (lambda r,v=v,at=at: r[at] != "?" and r[at] <= v)
```

hello

# Notes

Here is how we add:

```py
def add(col, v):
  "Show V to COL.  `?` means unknown, so it changes nothing."
  if v != "?":
    col.n += 1
    if "has" in col:
      col.has[v] = col.has.get(v, 0) + 1
    else:
      d = v - col.mu                      # Welford, for `div`
      col.mu += d / col.n
      col.m2 += d * (v - col.mu)
      col.sd  = 0 if col.n < 2 else (col.m2/(col.n-1))**.5
  return v
```

And the middle:

```py
def mid(col):
  "Middle: the mean, or the most common symbol."
  return max(col.has,key=col.has.get) if "has" in col else col.mu
```

Prose that mentions ```py inline should be left alone.

