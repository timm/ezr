## SE ideas in y3.py

Eleven software-engineering ideas hiding in y3.py, easiest
first. Each shown big (a real-world system) then small
(this code).

### 1. Single source of truth

State each fact once; derive every other appearance. Copies
drift; derivations cannot.

**Big.** Google's monorepo enforces a one-version rule: each
third-party library exists exactly once, so ten thousand
projects cannot disagree about what "protobuf" means. Lock
files (package-lock, Cargo.lock) are the same idea shipped
to everyone.

**Small.** y3's docstring *is* its settings *is* its help:

```py
the = o(**{k: atom(v) for k,v in re.findall(pat, __doc__)})
```

### 2. Little languages

A ten-line notation can replace a thousand-line subsystem.
y3 has three: column headers as schema, one regex as a
config parser, `-Key val --demo` as a CLI grammar.

**Big.** SQL, regex, printf formats, Makefiles: each a tiny
language that outlived generations of the "real" languages
around it. Bell Labs called this the highest form of reuse —
reusing a *notation*.

**Small.**

```py
tbl.cols[at] = Num() if s[0].isupper() else Sym()
```

### 3. Convention over configuration

Let names carry meaning and the machinery configures itself.

**Big.** Ruby on Rails coined the phrase: put the model in
app/models with the conventional name and everything wires
itself. Maven, Next.js routing, and pytest's own `test_`
discovery all inherit the idea.

**Small.** Any function named `test_*` is automatically a
demo, listed by help and callable from the shell:

```py
if s[:2] == "--": n += run(globals().get("test_" + s[2:]))
```

### 4. Separation of concerns

Each layer knows as little as possible about its neighbors.

**Big.** LLVM's whole design is one separation: front ends
compile *to* an intermediate representation, back ends
compile *from* it, and neither knows the other exists. That
one boundary lets a new language reach twenty CPUs for free.

**Small.** By the time rows reach `tree`, nothing remembers
whether they came from disk, a clone, or an acquire loop —
they are just tuples.

```py
def tree(tbl, rows, edge="", y=None):
```

### 5. Tools, not products

A product answers one request. A tool composes with other
tools to answer requests not yet imagined.

**Big.** Unix. Fifty years on, the pipe remains the most
successful integration mechanism in computing — no schema
negotiations, no SDK, just text between small programs.

**Small.** y3's entire 127-dataset laboratory:

```sh
ls */*.csv | xargs -P 10 -I{} python3 y3.py -File {} \
    --holdout | sort -n | fmt -60
```

### 6. Demos as tests as docs

One artifact, three jobs: `test_*` functions run the code
(test), print worked examples (demo), and list themselves
with docstrings under --help (docs).

**Big.** Rust compiles and runs the code examples inside its
documentation; a doc that rots fails the build. Python's
doctest pioneered the same bargain: examples that lie are
caught, so examples stay true.

**Small.**

```py
def test_holdout():
  "Mean win over 20 train/test holdouts"
```

### 7. Golden-master regression

When rewriting working code, freeze its outputs first; after
each change, byte-compare. Seeded randomness makes even
stochastic code freezable.

**Big.** SQLite ships to every phone on earth behind a test
harness with 100% branch coverage plus fuzzing plus stored
golden outputs; its authors rewrite internals freely because
the masters will catch any drift.

**Small.** y1, y2, y3 were each proved output-identical over
127 datasets before being trusted:

```sh
diff old.wins new.wins && echo IDENTICAL
```

### 8. Polymorphism without classes

One type test plus functions-as-values buys what class
hierarchies buy, without the hierarchy.

**Big.** The Linux kernel is object-oriented C: every
filesystem fills a struct of function pointers
(file_operations), and the VFS calls through it. Thirty
years, hundreds of filesystems, no classes.

**Small.**

```py
what = cutNum if is_num(tbl.cols[at]) else cutSym
```

### 9. Small everything

Reading is the dominant cost of code. Size limits (65
columns here; 14 lines in the longest function) are not
asceticism — they are a bet that whatever cannot fit in one
eyeful will hide bugs.

**Big.** The Linux kernel style guide caps indentation at
three levels and says functions should "do one thing and fit
on one or two screenfuls", on the stated grounds that if you
need more, you are lost. Google's style guides make the same
bet across millions of engineer-hours.

**Small.** The longest function in y3.py is `tree`, at 14
lines, and it is the whole learner.

### 10. Fail loud, exit honest

A crash is a gift: it names the line. Silent wrongness costs
weeks. And report failure where machines can see it — the
exit code.

**Big.** Erlang's "let it crash" philosophy runs telecom
switches at 99.9999999% availability: processes die loudly
and supervisors restart them, instead of limping on
corrupted state.

**Small.** `run` counts crashes; `cli` exits with the count,
so a Makefile can gate on it:

```py
sys.exit(n)
```

### 11. Configuration is a feature

Most systems ship dozens of knobs; most users touch none;
many defaults are wrong. At minimum, expose every parameter
and document it where users will look. Better: treat your
own config as an optimization problem.

**Big.** Studies of Hadoop, MySQL and Apache found hundreds
of parameters of which over 80% are rarely or never set,
while misconfiguration rivals code bugs as an outage cause —
a mistyped parameter took down AWS S3, and much of the
internet, for four hours in 2017. Half the datasets in this
site's benchmarks (the SS-* files) are exactly this problem:
find good settings for someone else's software.

**Small.** Every y3 magic number lives in the docstring,
overridable from the shell — and tuning one of them
(`Check`, labels reserved for verification) raised the
127-dataset median win by six points in an afternoon of
sweeps.

```py
  -Stop=50   acquire: total labelling budget
  -Check=5   holdout: top picks to label
```
