# Contrubute

This code has the following format.

Here is the **Tim-Style Python (TSP)** coding prompt in Markdown format:


# 🐍 Tim-Style Python (TSP) Coding Prompt

Use this prompt to rewrite general Python code in **Tim-Style Python (TSP)** — a minimal, data-driven, functional style tailored for compact modeling and analysis tasks.


## 1. Minimalism

* Minimize **lines of code (LOC)** while keeping clarity.
* Avoid boilerplate and verbose class structures.
* Use `SimpleNamespace` (`from types import SimpleNamespace as o`) for grouping attributes.
* Prefer concise `lambda`, list comprehensions, and function expressions.


## 2. Data-Centric Design

* Use plain `list` and `dict` objects for storage.
* CSV header defines data types:

  * Lowercase → symbolic (`Sym`)
  * Uppercase → numeric (`Num`)
* Column metadata is stored in nested namespaces like:

```python
data.cols.all  # all columns
data.cols.x    # independent columns
```


## 3. Functional Preference

* Avoid OOP inheritance; define behavior using functions.
* Emphasize pure functions with no side effects.
* Avoid mutation unless local and obvious.


## 4. Compact Data Processing

* Input handled via a minimalist `csv()` generator.
* Use a `coerce()` function to convert strings to `int`, `float`, or stripped strings.
* Use `?` as the marker for missing values.


## 5. Statistical Sketches

* Numeric stats: computed incrementally using Welford’s algorithm.
* Symbolic stats: counted in `dict` histograms.
* Use `rx(c, rows)` to compute a statistical summary for column `c`.


## 6. Tree and Model Building

* Build recursive trees using a nested `go()` function.
* Nodes are `SimpleNamespace` with fields like:

```python
o(c=c, lo=lo, hi=hi, left=leaf, right=...)
```
* Leaf nodes store stats (`mu`, `n`, etc.) or return values.


## 7. Pretty Printing and Introspection

* Display functions print directly with formatted `f""` strings.
* Output is readable with indentation and conditional labels.
* Use `mid(col)` to summarize a column (mean or mode).


## 8. Scriptable CLI Entry

* Add `if __name__ == "__main__":` block with:

  * CLI file input via `sys.argv`
  * Random seed setting (`random.seed(...)`)
  * Defaults fall back to safe local CSV file
* Constants optionally extracted from the script's docstring:

```python
the = o({k: eval(v) for k,v in [d.split("=") for d in __doc__.split() if "=" in d]})
```


## 9. Magic Constants and Defaults

* Use constants like:

```python
BIG = 1E32  # simulate infinity
```
* Set default tree depth (e.g., `depth=4`) and default file paths.
* Allow easy override via CLI or docstring parsing.

## 10. Naming Conventions

* Favor **short, meaningful names**:
  * Functions: `rx`, `add`, `fft`, `go`, `mid`, `bins`
  * Variables: `c`, `r`, `x`, `y`, `n`, `mu`, `sd`
* Avoid over-abstraction — clarity through structure, not verbosity.


### ✅ Summary

TSP code is:

* **Compact and readable**
* **Data-table-centric**
* **Statistical and recursive**
* **Devoid of unnecessary abstractions**

It’s perfect for **tabular modeling, active learning, and interpretable trees** — written in fewer lines, but rich in purpose.


