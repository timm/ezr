## Python idioms in ezr.py

Twelve idioms in ezr.py that can puzzle newcomers, easiest
first. Each gets a plain example, then the ezr usage.

### 1. Conditional expressions

One-line if: `a if test else b` is a *value*, not a
statement. Read it middle-out: test first, then left, then
right.

```py
grade = "pass" if mark >= 50 else "fail"
```

ezr picks a column type off its name:

```py
tbl.cols[at] = Num() if s[0].isupper() else Sym()
```

### 2. Chained comparisons

Math notation works: `a <= x <= b` means `a <= x and
x <= b`, and `x` is evaluated once.

```py
if 0 <= i < len(lst): ...
```

ezr keeps both sides of a split big enough:

```py
if the.Leaf <= size(here) <= len(xy) - the.Leaf:
```

### 3. Tuple unpacking

Assign several names at once from any sequence. Also swaps
without a temp var.

```py
lo, hi = hi, lo
```

ezr explodes a Num (a 3-tuple) into named parts:

```py
n, mu, m2 = c
```

### 4. dict.get with a default

`d.get(k, 0)` reads a key that may be absent, giving 0
instead of a crash. The standard counting idiom.

```py
seen[word] = seen.get(word, 0) + 1
```

ezr counts symbols the same way:

```py
c[v] = c.get(v, 0) + inc
```

### 5. zip

Walk two lists in lockstep; stops at the shorter one.

```py
for name, score in zip(names, scores): ...
```

ezr pairs each row with its precomputed y value:

```py
xy = [(x, y) for r,y in zip(rows, ys) if (x := r[at]) != "?"]
```

### 6. Comprehensions with a filter

`[f(x) for x in xs if test(x)]` builds a list in one
expression: map and filter fused. If it needs two lines of
logic, use a loop instead.

```py
evens = [x*x for x in range(20) if x % 2 == 0]
```

ezr (same line as above) both filters out `"?"` cells and
builds (x, y) pairs in one pass.

### 7. The walrus `:=`

Assign *inside* an expression, so you can test a value and
keep it, without computing it twice.

```py
if (m := re.match(pat, line)): print(m.group(1))
```

ezr names the cell while filtering on it:

```py
... if (x := r[at]) != "?"
```

and keeps a score while comparing it:

```py
if (s := xpect(here, there)) < best[0]: best = (s, at, v)
```

### 8. Functions are values

A function name without parens is just a value: store it,
pass it, pick between two of them.

```py
op = max if bigger_better else min
print(op(scores))
```

ezr dispatches on column type by choosing a function:

```py
what = cutNum if is_num(t.cols[at]) else cutSym
for here, there, v in what(xy, acc): ...
```

### 9. Lambdas as sort keys

`sorted(xs, key=f)` sorts by `f(x)`, not by `x`. A lambda
is a tiny unnamed function, perfect for keys.

```py
kids.sort(key=lambda k: k.age)
```

ezr orders unlabelled rows by "near best, far from rest":

```py
todo.sort(key=lambda z: xdist(t, z, r) - xdist(t, z, b))
```

### 10. Default arguments, and the None trick

Defaults make arguments optional. But write `it=None` then
`if it is None: it = Num()` rather than `it = it or Num()`:
an empty container is falsy, so `or` would silently replace
a fresh empty Sym with a Num.

```py
def log(msg, out=None):
  out = out if out is not None else sys.stdout
```

ezr's stream accumulator:

```py
def adds(lst, it=None):
  if it is None: it = Num()
```

### 11. Generators and yield

A function with `yield` returns a lazy stream: each value
is produced on demand, and local state persists between
values. Callers loop over it like a list.

```py
def evens():
  n = 0
  while True: yield n; n += 2
```

ezr's cut finders stream candidate splits one at a time, so
the caller can score and discard them without building a
list:

```py
def cutNum(xy, acc):
  xy.sort()
  here, there = acc(), adds((y for _, y in xy), acc())
  for i, (x, y) in enumerate(xy[:-1]):
    here, there = add(here, y), add(there, y, -1)
    if x != xy[i+1][0]: yield here, there, x
```

### 12. Reading globals() as a dispatch table

`globals()` is the module's own name-to-value dict. Looking
up computed names turns naming conventions into machinery:
every function called `test_xxx` is automatically a command.

```py
def demo(name): globals()["demo_" + name]()
```

ezr's CLI finds demos by name, defaulting to help:

```py
if s[:2] == "--": n += run(globals().get("test_" + s[2:]))
```
