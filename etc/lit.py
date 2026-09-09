"""lit.py: ezr.py --> docs/ezr.html via pycco.
Moves def-line comments above the def, adds typed signatures,
turns #-- banners into h2, injects header, justifies prose."""
import re, subprocess, os

rt = dict(atom="Atom", csv="Rows", sd="float", add="Col",
  adds="Col", size="int", div="float", Tbl="Tbl", clone="Tbl",
  addRow="Row", norm="float", mid="Atom", mids="dict[int,Atom]",
  ydist="float", _dist="float", xdist="float", ymu="float",
  ymids="list[float]", pop="Row", label="None", acquire="Rows",
  like="float", likes="float", liked="Atom", confuse="dict",
  xpect="float", cutNum="Iterator", cutSym="Iterator",
  cut="tuple|None", routing="tuple", tree="Node",
  kids="list[Node]", leaf="Node", leafs="list[Node]",
  show="None", cohen="bool", cliffs="bool", ks="bool",
  same="bool", wins="Callable[[Row],float]", holdout="Row",
  run="int", cli="None", main="None", _klass="list",
  fitTree="Callable", fitBayes="Callable", say="str",
  centroid="Callable[[Row],float]")
pt = dict(tbl="Tbl", col="Col", row="Row", rows="Rows",
  v="Atom", lst="Iterable", s="str", file="str", at="int",
  best="Tbl", rest="Tbl", todo="Rows", nall="int", nh="int",
  tbls="dict[Atom,Tbl]", pairs="list[tuple[Atom,Atom]]",
  ys="list", acc="Callable", xy="list[tuple]", a="Atom",
  b="Atom", xs="list[float]", tr="Node", d="dict",
  funs="dict", args="list[str]", fits="Callable", x="Any",
  score="Callable")
over = {("xpect","a"): "Col", ("xpect","b"): "Col",
        ("cohen","ys"): "list[float]",
        ("cliffs","ys"): "list[float]",
        ("ks","ys"): "list[float]",
        ("kids","n"): "Node", ("xdist","m"): "Row|dict"}
fb = dict(
  atom="strings become ints, floats, bools, or stay strings",
  csv="load a csv file as a list of typed tuples",
  sd="standard deviation, derived from Welford's m2",
  size="how many items in a column summary",
  Tbl="header names route columns to x, y, klass, or skip",
  clone="an empty copy of a table, sharing the header",
  norm="squash v to 0..1 via clamped z-score and logistic",
  mid="middle of a column: mean or mode",
  ydist="distance to heaven: 0 (best) to 1 (worst)",
  _dist="per-column distance between two values",
  xdist="Minkowski distance over the x columns",
  ymu="mean ydist of some rows",
  ymids="per-goal means of some rows",
  pop="next best guess: near best, far from rest",
  acquire="label a few informative rows; best first",
  routing="edge labels and a router for one split",
  tree="recursive discretization; leaves predict",
  kids="subtrees, if any",
  leaf="route a row to its leaf",
  leafs="all leaves under a node",
  show="print a tree, best (+) to worst (-) marked",
  wins="score rows 0..100: complement of regret",
  holdout="train on half; label only the tree's top picks",
  fitBayes="one table per class; predict the most likely",
  cli="-Key val sets; --name runs; exit counts crashes",
  say="round floats, hide _fields, recurse into dicts, lists")

def sig(name, args):
  out = []
  for p in [x.strip() for x in args.split(",") if x.strip()]:
    bare = p.lstrip("*")
    if "=" in p: out.append(p); continue
    t = over.get((name, bare)) or pt.get(bare)
    out.append(f"{p}: {t}" if t else p)
  return ", ".join(out)

raw = open("ezr.py").read().replace("\f", "")
raw = re.sub(r"# pylint:[^\n]*\n", "", raw)
lines = raw.split("\n")
q = [i for i, l in enumerate(lines) if l.strip() == '"""'][:2]
if len(q) == 2:
  a, b = q
  hdr = []
  for l in lines[a+1:b]:
    if l.startswith("  -"): hdr.append("#     " + l.strip())
    elif not l.strip():     hdr.append("#")
    else:                   hdr.append("# " + l)
  lines = lines[:a] + hdr + lines[b+1:]
src = lines
out = []
for i, line in enumerate(src):
  bm = re.match(r"#-- (\w[-\w, ]*?) *-{2,} *$", line)
  m = re.match(r"def (\w+)\(([^)]*)\)(.*?)(#\s*(.*))?$", line)
  if bm:
    out += ["", "# ## " + bm.group(1)]
  elif line.startswith("def ") and m:
    name, args, rest, _, cmt = m.groups()
    r = rt.get(name,
               "None" if name.startswith("test_") else "")
    r = f" -> {r}" if r else ""
    cmt = cmt.strip() if cmt else fb.get(name)
    if not cmt and i+1 < len(src):
      dm = re.match(r'\s+"(.*)"\s*$', src[i+1])
      if dm: cmt = dm.group(1)
    br = "  " if cmt else ""
    out.append(f"# `{name}({sig(name, args)}){r}`{br}")
    if cmt: out.append(f"# {cmt}")
    out.append(f"def {name}({args}){rest.rstrip()}".rstrip())
  else:
    out.append(line)
open("docs/ezr.py", "w").write("\n".join(out))

subprocess.run(["pycco", "-d", "docs", "docs/ezr.py"],
               check=True, capture_output=True)
h = open("etc/header.html").read().replace("PROJECT", "ezr")
s = open("docs/ezr.html").read()
s = re.sub(r"(<body[^>]*>)", lambda m: m.group(1) + "\n" + h,
           s, count=1)
open("docs/ezr.html", "w").write(s)
css = open("docs/pycco.css").read()
css += open("etc/custom.css").read()
css += "\n.docs p { text-align: justify; }\n"
open("docs/pycco.css", "w").write(css)
os.remove("docs/ezr.py")
print("docs/ezr.html rebuilt")
