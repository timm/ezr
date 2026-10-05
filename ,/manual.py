#!/usr/bin/env python3 -B
"""manual.py: ezr.py + ezr_eg.py --> docs/manual.html.
A five tab reference: the man page, the library, the demos,
install notes, the licence.  Every function and docstring is
read out of the source with `ast`, so this cannot drift."""
# pylint: disable=bad-indentation,multiple-statements
# pylint: disable=invalid-name,missing-function-docstring
import ast, html, json, re, os

#-- what goes where ----------------------------------------
# ezr.py's own `#--` banners put tree, holdout and stats under
# `acquire`, which reads oddly in a table.  Regroup by hand.
GROUPS = [
 ("Shell",    "coerce text, print it, read a csv",
  "say atom csv"),
 ("Columns",  "one running summary per column; `?` never counts",
  "Col Num Sym add mid mids div norm"),
 ("Tables",   "a header row routes every column to x, y or skip",
  "Tbl Cols addRow addCols clone"),
 ("Distance", "how far two rows are, and how far a row is from perfect",
  "minkowski ydist gap xdist"),
 ("Acquire",  "spend the labelling budget where it buys the most",
  "oracle acquire grabs"),
 ("Tree",     "split on whatever tightens the goals; leaves explain",
  "cut candidates tree leaf leafs show"),
 ("Holdout",  "train on half, guess on the rest, score the guess",
  "wins holdout"),
 ("Stats",    "is this difference real, or is it noise?",
  "adds cohen cliffs ks same"),
 ("Cli",      "-Key val sets a setting; --name runs a demo",
  "run main"),
]
ROLES = [("+", "a goal to maximize"), ("-", "a goal to minimize"),
         ("!", "the class column"),   ("X", "ignore this column"),
         ("",  "no suffix: an x column")]

#-- read the source ----------------------------------------
def defs(file):
  "Every top-level def: name, signature, docstring, source."
  src   = open(file, encoding="utf-8").read()
  lines = src.split("\n")
  out   = {}
  for n in ast.parse(src).body:
    if not isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
      continue
    sig, k = lines[n.lineno-1].strip(), n.lineno
    while not sig.endswith(":") and k < len(lines):
      sig, k = sig + " " + lines[k].strip(), k + 1
    out[n.name] = dict(
      name=n.name, sig=sig.removeprefix("def ").rstrip(":"),
      doc=" ".join((ast.get_docstring(n) or "").split()),
      src="\n".join(lines[n.lineno-1:n.end_lineno]),
      n=n.end_lineno - n.lineno + 1)
  return out

#-- render -------------------------------------------------
def esc(s): return html.escape(str(s))

def hi(src):
  "Three-way highlight: comments, strings, keywords."
  s = esc(src)
  s = re.sub(r"(#[^\n]*)", r"<em>\1</em>", s)
  s = re.sub(r"(&quot;[^&\n]*&quot;|&#x27;[^&\n]*&#x27;)",
             r"<b>\1</b>", s)
  return re.sub(r"\b(def|return|if|else|elif|for|while|in|not|and"
                r"|or|lambda|import|from|type|class|None|True|False"
                r"|yield)\b", r"<i>\1</i>", s)

def row(f):
  "One table row, with the source folded into a <details>."
  sig = re.sub(r"^(\w+)", r"<b>\1</b>", esc(f["sig"]))
  return (f'<tr><td class="n"><code>{f["name"]}</code></td>'
          f'<td class="d">{esc(f["doc"])}'
          f'<details><summary>{f["n"]} lines</summary>'
          f'<pre><code>{hi(f["src"])}</code></pre></details></td>'
          f'<td class="s"><code>{sig}</code></td></tr>')

def library(fns):
  out = []
  for title, blurb, names in GROUPS:
    out += [f'<tr class="g"><th colspan="3"><span>{title}</span>'
            f'<span class="blurb">{esc(blurb)}</span></th></tr>']
    out += [row(fns[n]) for n in names.split() if n in fns]
  return "\n".join(out)

def demos(fns):
  return "\n".join(
    row(dict(f, name="--" + f["name"][3:], sig=""))
    for k, f in fns.items() if k.startswith("eg_"))

def options(doc):
  "The -Key=val block of ezr.py's docstring, as a table."
  return "\n".join(
    f'<tr><td class="n"><code>-{k}</code></td>'
    f'<td class="v"><code>{esc(v)}</code></td>'
    f'<td class="d">{esc(why.strip())}</td></tr>'
    for k, v, why in re.findall(
      r"-(\w+)=(\S+)\s*(.*)", doc or ""))

def roles():
  return "\n".join(
    f'<tr><td class="n"><code>{esc(k) or "&nbsp;"}</code></td>'
    f'<td class="d">{esc(d)}</td></tr>' for k, d in ROLES)

#-- main ---------------------------------------------------
def main():
  here = os.path.dirname(os.path.abspath(__file__))
  os.chdir(os.path.dirname(here))
  ezr, egs = defs("ezr.py"), defs("ezr_eg.py")
  doc = ast.get_docstring(ast.parse(open("ezr.py").read()))
  page = open(f"{here}/manual.html", encoding="utf-8").read()
  for k, v in dict(TABLE=library(ezr), DEMOS=demos(egs),
                   OPTROWS=options(doc), ROLEROWS=roles()).items():
    page = page.replace("{{" + k + "}}", v)
  open("docs/manual.html", "w", encoding="utf-8").write(page)
  print(f"docs/manual.html  ({len(page)//1024}K, "
        f"{len(ezr)} functions, "
        f"{sum(k.startswith('eg_') for k in egs)} demos)")

main()
