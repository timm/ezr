#!/usr/bin/env gawk -f
BEGIN {
  print "\\section*{Index} {\\scriptsize \\begin{tabular}{lrp{2in}}"

  print "\\textbf{name} & \\textbf{LOC} & \\textbf{kind} & \\textbf{help} \\\\ \\hline" }
END { print "\\end{tabular}}" }

# doc line: grab text after <br>
/^--/ {
  split($0, parts, "<br>")
  helptext = (length(parts) > 1 ? parts[2] : "")
  sub(/^-- */, "", helptext)
  gsub(/^ +| +$/, "", helptext)
  pending = helptext
}

/^function/ {
  sym = $2
  sub(/\(.*/, "", sym)    # strip args
  n = split(sym, p, ":")
  COM="sort"
  if (n == 2) {
    printf("\\verb|%s| & %s & meth & %s %s \\\\\n", p[2], NR, p[1], pending) | COM
  } else {
    printf("\\verb|%s| & %s & func & %s \\\\\n", sym, NR, pending) | COM}
  pending="" }
