# etc/bench — ten ports of the ezr.py kernel

Is Python the wrong language for `ezr.py`? This answers it by measurement:
the load-bearing middle of `ezr.py` ported to ten languages, each verified
against one reference output, then sized and timed.

## What is ported

`slice.<ext>` in each language carries the same functions:

| | |
|---|---|
| columns | Welford `add`/`adds`, `size`, `div` (sd and entropy), `mid` |
| tables  | `Tbl` header parsing (trailing `+ - ! X`), `clone`, `addRow` |
| distance| logistic `norm`, Minkowski `mink`, `ydist`, `xdist`, `mids` |
| acquire | `centroid`, `label` (sqrt-capped best pool), `acquire` |
| stats   | `cliffs`, `ks`, `cohen`, `same` |

`drive.<ext>` is the harness — CSV parsing, printing, timing loops. It is
**not** counted; only `slice.*` is.

## Why the ports agree

Every port shares one deterministic generator, the MINSTD Lehmer `rand`
already used in `ezr-lisp`:

    seed = seed * 16807 % 2147483647

driving one Fisher-Yates shuffle. That makes `acquire` reproducible across
languages rather than merely plausible. A port counts as verified only when
it reproduces all ten lines of `ref.txt` byte-for-byte, including the final
RNG state — so a port that diverges anywhere in 60 `acquire` runs is caught.

## Running it

    make sizes    # loc/char table; needs only python3
    make          # build, verify and time everything

`run.py` skips any language whose toolchain is missing, so a partial run is
fine. Both must be run from this directory — the drivers open `data.csv`
and `gauss.txt` by relative path.

Toolchains used: Python 3.13, Ruby 3.3.6, Node 22, Lua 5.4, Perl 5, PHP 8,
gawk 5.2, SBCL 2.2.9, GHC 9.4.7, OCaml 4.14.1.

## Results

| Language | LOC | Chars | vs Python | Secs | Rel. |
|---|---:|---:|---:|---:|---:|
| Ruby        | 124 | 2,891 |  -7% | 4.98 | 0.6x |
| **Python**  | **112** | **3,112** | — | **3.05** | **1.0x** |
| JavaScript  | 113 | 3,314 |  +6% | 3.33 | 0.9x |
| Perl        | 148 | 4,080 | +31% | 6.84 | 0.4x |
| PHP         | 139 | 4,234 | +36% | 1.40 | 2.2x |
| Haskell     | 154 | 4,244 | +36% | 0.71 | 4.3x |
| Lua         | 146 | 4,300 | +38% | 2.03 | 1.5x |
| AWK (gawk)  | 149 | 4,404 | +42% | 8.80 | 0.3x |
| OCaml       | 162 | 4,548 | +46% | 0.62 | 4.9x |
| Common Lisp | 154 | 4,672 | +50% | 6.72 | 0.5x |

Ruby is the only language that beats Python, by 7% of characters — and it
spends 12 extra lines to do it. Python has the fewest lines of all ten.
Size spans 1.6x; runtime spans 14x.

## What Python gives you free

Found by making each port *match*, not merely run:

- **Ruby: booleans are not numbers.** `tbl.y[at] = s[-1] == "+"` works in
  Python because `bool` subclasses `int`, and `ydist` subtracts it directly.
  Ruby raises `TypeError`. `_dist`'s `a != b` returning 0/1 rides on the
  same trick.
- **Ruby: integer division silently broke Welford.** `mu += inc * d /
  max(1, n)` truncated; `div` returned 3.04 where Python gives 1.89. No
  error, just wrong sd and wrong distances downstream.
- **JavaScript: objects reorder integer-like keys.** Sym counts keyed
  `1,2,3` come back numerically sorted, not in insertion order, so ties in
  `mid` break differently and `acquire` diverges. Needs `Map`.
- **Everywhere: `max(col, key=col.get)` keeps the FIRST maximum.** A natural
  `reduce` keeps the last. With counts `{1:1, 2:0, 3:1}` — which
  `add(..., inc=-1)` produces routinely — that picks a different mode and
  silently changes which rows get labelled.
- **Common Lisp, awk: hash tables have no insertion order.** Both ports
  carry Sym counts as an ordered alist to reproduce that tie-break. Python
  `dict`, Ruby `Hash` and PHP arrays keep order for free.
- **awk: no closures, no default arguments, no references.** `centroid`
  cannot be returned as a function, so it reads globals; `inc=1` is tested
  by hand; rows live once in a global `ROWS` and tables pass indices.
- **Haskell, OCaml: heterogeneous rows need a declared sum type.**
  `data Atom = N Double | S String` plus wrapping and unwrapping at every
  cell access is most of why the two fastest languages are two of the
  three longest.

## Notes

- The Common Lisp port follows the `ezr-lisp` house style (`$` reader
  macro, `aif`/`it`, `&aux` locals, CLOS dispatch over type tests). It was
  the only port that matched the reference on its first run.
- Haskell and OCaml are compiled `-O2`; their times exclude compilation.
- The JavaScript figure was 30.5s until the harness stopped loading the
  library through `eval` — a ~9x penalty unrelated to the code measured.
  See the `run.js` rule in the Makefile.
- Runtimes are best-of-three wall clock and drift ~15% between runs
  on a shared machine; the ordering is stable, the third digit is not.
- `data.csv` and `gauss.txt` are committed so results are stable;
  `make data` regenerates them from `mkdata.py` if ever needed.

## The point

The `26sep8` branch cut `ezr.py` from 858 lines to 404, and the comparable
kernel from 541 code lines to 308 — 43% — by collapsing `Num`/`Sym`/`Data`/
`Cols` into a tuple and a dict, making a tree node a plain list, and
flattening the settings namespace. Representation, not syntax.

Against that, the best any of ten languages offers is 7%. The next real
shrink is another scope decision, not another language.
