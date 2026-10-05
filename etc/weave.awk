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
#
# A ```py block opening with "def" or "class" that matches
# nothing gets MARK pinned to that line, so stale snippets
# show up in the .md instead of rotting there unnoticed.
# The mark is stripped before every lookup, so running this
# twice never doubles it, and a snippet that comes back
# loses its mark on the next pass.

function key(a, b) { sub(/[(:].*/, "", b); return a " " b }

BEGIN { RS = ""; ORS = "\n\n"
        MARK = "  <==== SNIPPET NOT FOUND" }

FNR == NR { snip[key($1, $2)] = $0; next }    # pass 1: the .py

/^```py/ {                                    # pass 2: the .md
  gsub(MARK, "")                              # drop any earlier mark
  n = split($0, line, "\n")
  split(line[2], word, /[ \t]+/)
  k = key(word[1], word[2])
  if (k in snip) { print "```py\n" snip[k] "\n```"; next }
  if (word[1] == "def" || word[1] == "class") {
    line[2] = line[2] MARK
    missing++ }
  $0 = line[1]
  for (i = 2; i <= n; i++) $0 = $0 "\n" line[i] }

{ print }

END { if (missing) printf "weave: %d snippet(s) not found\n",
                          missing > "/dev/stderr" }
