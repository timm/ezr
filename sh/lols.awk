BEGIN {
  FS=","                            # CSV input
  print "\\usepackage[table]{xcolor}"
  print "\\newcommand{\\CELL}{\\cellcolor{pink}}" }

NR==1 {
  colspec = ""
  for (i=1; i<=NF; i++) colspec = colspec "r"
  print "{\\scriptsize \\begin{center} \\begin{tabular}{" colspec "}" }

{ for (i=1; i<=NF; i++) {
    val = $i
    if (sub(/\!/,"",val)) val = "\\CELL " val
    printf "%s", val
    if (i < NF) printf " & " }
  print " \\\\"
  if (NR==1) print "\\hline" }

END { print "\\end{tabular} \\end{center}}" }
