#!/usr/bin/env python3
"""Size each port: non-blank, non-comment lines and non-whitespace chars.
Counts slice.* only -- drivers, CSV parsing and printing are excluded."""
import re, json

SPEC = {
  "slice.py": ("Python", "#"),      "slice.rb": ("Ruby", "#"),
  "slice.js": ("JavaScript", "//"), "slice.lua": ("Lua", "--"),
  "slice.pl": ("Perl", "#"),        "slice.awk": ("AWK (gawk)", "#"),
  "slice.lisp": ("Common Lisp", ";"), "Slice.hs": ("Haskell", "--"),
  "slice.ml": ("OCaml", "(*"),      "slice.php": ("PHP", "//"),
}

def measure(f, c):
  lines = []
  for l in open(f).read().split("\n"):
    s = l.strip()
    if not s or s.startswith(c): continue
    if f == "slice.php" and s.startswith("<?php"): continue
    if f == "slice.lisp" and s.startswith(";;;"): continue
    l = re.sub(r"\s{2,}" + re.escape(c) + r"\s.*$", "", l)   # trailing comment
    if f == "slice.ml": l = re.sub(r"\s{2,}\(\*.*\*\)\s*$", "", l)
    if l.strip(): lines.append(l)
  txt = "\n".join(lines)
  return dict(loc=len(lines), chars=len(re.sub(r"\s", "", txt)))

if __name__ == "__main__":
  out = {lang: measure(f, c) for f, (lang, c) in SPEC.items()}
  base = out["Python"]["chars"]
  for lang, d in sorted(out.items(), key=lambda kv: kv[1]["chars"]):
    print(f"{lang:<14} {d['loc']:>4} loc {d['chars']:>6} chars"
          f" {100*d['chars']/base - 100:+6.1f}%")
  json.dump(out, open("sizes.json", "w"), indent=1)
