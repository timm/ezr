## Script-file patterns in y3.py

How to organize one Python file so config, tests, docs and
CLI stay in sync forever. Fifteen patterns, plus the one
idea underneath them all.

### 1. Docstring is the config is the help

State every option once, in `__doc__`, as `-Key=default`
plus a comment. One regex births the settings; `--help`
prints the same text. Three artifacts cannot drift, because
they are one artifact.

```py
pat = r"(\w+)=(\S+)"
the = o(**{k: atom(v) for k,v in re.findall(pat, __doc__)})
```

### 2. Coerce at the border

`atom` turns strings into int, float, bool once, where data
enters. Everything downstream trusts its types; no coercion
sprinkled through the logic.

```py
def atom(s, bools={'True': True, 'False': False}):
  try: return int(s)
  except ValueError:
    try: return float(s)
    except ValueError:
      s = s.strip()
      return bools.get(s, s)
```

### 3. CLI grammar = config keys

`-Key val` writes straight into the settings dict. Adding a
line to the docstring *is* adding the flag. No argparse
table to keep in sync.

```py
elif s[1:] in d: d[s[1:]] = atom(args.pop(0))
```

### 4. Tests by naming convention

Any `test_*` function is a demo: `--name` runs it, `--all`
runs them all, `--help` lists each with its docstring.
A `globals()` lookup is the whole test framework.
Demos = tests = docs: one artifact again.

```py
if s[:2] == "--": n += run(funs.get("test_" + s[2:]))
```

### 5. Reseed per test

`run` resets the random seed before every test, so
stochastic code gives reproducible demos, and any test runs
alone or in any order.

```py
def run(f=None):
  try: random.seed(the.Seed); (f or test_help)()
  except Exception: traceback.print_exc(); return 1
  return 0
```

### 6. Exit code = crash count

Machines read the results. `make test` gates for free;
CI needs no plugin.

```py
sys.exit(n)
```

### 7. File layout is a dependency order

Config, then primitives, then composites, then tests, then
the main guard. Every name is defined before it is
referenced, reading top-down; the call graph in
[y3_map](y3_map.html) shows the layers.

### 8. Main guard keeps it importable

The same file is a script and a library: a harness can
import the functions the shell runs.

```py
if __name__ == "__main__":
  cli(vars(the), globals(), sys.argv[1:] or ["--help"])
```

### 9. Env expansion in config values

`$MOOT` in a path means per-machine data without
per-machine edits.

```py
file = file.replace("$MOOT", os.environ.get("MOOT")
                    or os.path.expanduser("~/gits/moot"), 1)
```

### 10. Stdlib only

Zero installs: the script runs on any Python, forever.
Dependency-free is a feature you cannot retrofit.

```py
import os, random, re, sys, traceback
from math import exp, log, log2, pi, sqrt
```

### 11. Shebang carries flags

`./y3.py` just works, and `-B` never litters `__pycache__`.

```py
#!/usr/bin/env python3 -B
```

### 12. The arg list is a tiny program

Args evaluate left to right: set, run, set, run. No
"config phase then command phase" — order is the power.

```sh
./y3.py -Leaf 16 --klassTree -Leaf 4 --holdout
```

### 13. Unknown args warn, never die

A typo in flag three should not waste what flags one and
two set up.

```py
else: print(f"unknown arg: {s}")
```

### 14. Section banners are a greppable TOC

`grep '#--' y3.py` is the table of contents — and tools
(the pdf packer, the map generator) key off the same
banners. Structure that is data.

```sh
#-- structs -----------------------------------------------
#-- distance ----------------------------------------------
#-- acquire -----------------------------------------------
```

### 15. Tests print evidence, not "ok"

`mu 5.0 sd 2.138` beats a green dot: the demo teaches, the
output is diffable, and a wrong number stays visible even
when an assert is too loose.

```py
def test_num():
  "Welford add matches textbook mean and sd"
  c = adds([2, 4, 4, 4, 5, 5, 7, 9])
  assert c[0] == 8 and c[1] == 5 and abs(sd(c)-2.138) < .01
  print(f"mu {c[1]} sd {round(sd(c), 3)}")
```

### The idea underneath

Patterns 1, 4 and 14 share a secret: **conventions are
load-bearing**. A name — `test_`, an uppercase column
header, a `#--` banner — is machinery, not decoration.
That is how 360 lines is enough: every convention replaces
a subsystem.
