# weave.awk -- pull code out of a .py, into a .md
#
#     gawk -f weave.awk x.py x.md > tmp && mv tmp x.md
#
# Pass 1 keys every paragraph of the .py by its first two
# words, with anything from "(" or ":" onwards trimmed off:
# so "def fred(a, b):" is filed under "def fred".  Pass 2
# rewrites any ```py block in the .md whose first code line
# has that same key.
#
# A truly blank line ends a paragraph.  A line holding one
# space does not -- so that is how you group N functions
# into one snippet.

function key(a, b) { sub(/[(:].*/, "", b); return a " " b }

BEGIN { RS = ""; ORS = "\n\n" }

FNR == NR { snip[key($1, $2)] = $0; next }    # pass 1: the .py

/^```py/ {                                    # pass 2: the .md
  split($0, line, "\n")
  split(line[2], word, /[ \t]+/)
  k = key(word[1], word[2])
  if (k in snip) { print "```py\n" snip[k] "\n```"; next } }

{ print }
