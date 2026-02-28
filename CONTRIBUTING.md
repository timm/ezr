# EZR Coding Style Guide

## Philosophy

Minimal LOC, maximal readability. Shortest correct expression.
Zero external dependencies. Python 3.11+.

## Line Rules

- Max **85 characters** wide
- **2-space** indentation
- Short bodies on **same line**: `def sub(i, v): return add(i, v, w=-1)`
- **Semicolons** chain related statements: `k=r[key]; klasses.add(k)`
- Multi-line: break after operators, align continuations

## File Skeleton

```python
#!/usr/bin/env python3 -B
"""module.py: one-line description"""
import stdlib_modules
from ez_class import Data, csv, main, align, the

#---- section name ---------------------------------------------------
def function(...): ...

#---- demos ----------------------------------------------------------
def eg__demo(file:filename):
  "one-line description shown in help"
  assert (out:=function(file)), "crash in eg__demo"
  print(out)

if __name__=="__main__": main(globals())
```

- Shebang + docstring at top
- Flat imports: `from ez_class import X, Y, Z`
- Section dividers: `#---- name` padded to ~65 chars
- Demos at bottom, then `main(globals())`
- No narrating comments — code speaks for itself

## Data Structures

Classes with methods (`Sym(dict)`, `Num(list)`, `Data`, `Cols`).
Column naming: uppercase first = `Num`, lowercase = `Sym`.
Suffixes: `+` maximize, `-` minimize, `!` klass, `X` ignore.
Missing values: `"?"`. Type dispatch: `isinstance(col, Sym)`.

## Type Hints

```python
Qty = int | float
Val = Qty | str
Row = list[Val]

def mid(i) -> Val:
def cnb(data:Data, rows:list=None) -> dict:
def _stem1(w:str, sufs:list, cache:dict) -> str:
```

- Always annotate parameters and return types
- Short names: `c:Col`, `d:Data`, `r:Row`, `f:str`, `k:str`
- Walrus operator freely: `if (v:=row[at])!="?"`

## Functions

- **Small**: 1–10 lines typical, ~20 max
- **No docstrings** on regular functions (only on `eg__`)
- **Private** helpers prefixed `_`: `_cells`, `_stem1`, `_warm`
- Prefer expressions: comprehensions, ternaries, `or` defaults
- **Generators** (`yield`) for lazy pipelines: `csv()`, `_csv()`

## Algorithm Decomposition

Layered pattern (per-feature → per-class → classify → train):

| Layer | NB | CNB |
|-------|-----|------|
| Per-feature | `col.like(v, prior)` | `cnbLike(ws, at, row, k)` |
| Per-class | `data.like(row, ...)` | `cnbLikes(ws, data, row, k)` |
| Classify | `max(ks, key=best)` | `max(ws, key=lambda k:...)` |
| Train | `nbayes(src)` | `cnb(data, rows)` |

## CLI System

Config `the` parsed from `ez_class.py` docstring:

```python
"""Options:
  -B Budget=50       training evaluation budget
  -N Norm=0          CNB weight normalization (0/1)"""
the = o(**{k:cast(v) for k,v in re.findall(...)})
```

| Pattern | Purpose | Example |
|---------|---------|---------|
| `eg_X(n:type)` | Setter (`-X`) | `def eg_s(n:int): the.seed=n` |
| `eg__name(file:filename)` | Demo (`--name`) | `def eg__tree(f:filename):` |
| `eg_h()` | Help | prints docstring + demo list |

- Annotations drive arg parsing (`f.__annotations__`)
- New param: add to `ez_class.py` docstring, add `eg_X`
  setter in consuming module

## Demo Functions (`eg__`)

**Every new function/feature MUST have a corresponding `eg__`
demo.** Demos are the project's tests and documentation — if
a capability exists, it must be demonstrable from the CLI.

Rules:
- **Crash-guard** with assert: `assert (out:=fn(file)), "crash"`
- **Before/after** output showing transformation:

```python
def eg__nostop(file:filename):
  p=tokenize(file); b=p.docs[0].words[:12][:]
  assert nostop(p), "crash in eg__nostop"
  print(f"before:  {b}")
  print(f"after:   {p.docs[0].words[:12]}")
```

- **One-line docstring** (shown in `--help`):
  `def eg__active(file:filename): "active learning"`
- Use `align()` for tables, `say()` for formatted values
- Demos double as tests: crash = visible failure

## Printing

- `align(rows)` — auto-width tabular output
- `say(x)` — format one value (respects `the.decs`)
- `says(lst, w)` — formatted list with fixed width
- Prefer `align`/`say` over raw `print(f"x={x}")`

## Error Handling

- Inline `try/except` for coercion:
  `try: v=float(r[at]) ... except ValueError: v=0`
- `...` (Ellipsis) instead of `pass` in empty excepts
- Asserts for preconditions:
  `assert txt in hdr, f"need '{txt}' col"`

## Resource Files

Files under `ezr/resources/`, loaded via `Path(__file__).parent`:

```python
_DIR = Path(__file__).parent
def _load(pkg:str) -> set:
  try: s = (_DIR / pkg).read_text()
  except Exception: s = ""
  return {w.strip().lower()
          for w in s.splitlines() if w.strip()}
```

## Module Ownership

| Module | Owns |
|--------|------|
| `ez_class.py` | `Data`, `Num`, `Sym`, `Cols`, `csv`, `main`, `the` |
| `stats.py` | `Confuse`, `same`, `top` |
| `prep.py` | `tokenize`, `nostop`, `stem`, `tfidf`, `prepare` |
| `textmine.py` | `cnb`, `cnbLike`, `cnbLikes`, `active` |

- Cross-module useful → `ez_class.py`
- Domain-specific → own module (prefix `_` if internal)

## Adding a New Module

1. Create `ezr/newmod.py` using file skeleton above
2. Import from `ez_class.py` + siblings as needed
3. Functions under ~15 lines each
4. **`eg__` demo for every public function** with assert guard
5. End with `if __name__=="__main__": main(globals())`
6. Add CLI entry in `pyproject.toml`

## Package Layout

```
ezr/
  ez_class.py       # core: Data, Num, Sym, csv, main, the
  stats.py          # Confuse, same, top
  bayes_class.py    # naive Bayes
  tree_class.py     # decision trees
  acquire_class.py  # active learning
  sa_class.py       # simulated annealing
  kmeans_class.py   # k-means clustering
  prep.py           # text preprocessing pipeline
  textmine.py       # complement naive Bayes + active learning
  resources/text/   # stop_words.txt, suffixes.txt
pyproject.toml      # build config + CLI entry points
```

## What NOT to Do

- No external dependencies
- No long comments explaining what code does
- No 4-space indentation
- No docstrings on non-`eg__` functions
- No lines over 85 characters
- No flat `import ezr.ez` — use `from ez_class import ...`
- No manual column printing — use `align()`
- No hardcoded params — use `the.X` from docstring
- No new feature without an `eg__` demo
