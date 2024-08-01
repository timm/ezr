/^# ## / { slurp("etc/" tolower($3) ".md"); next }
NR> 2   

function slurp(f) {
  print b4
  while((getline line < f) > 0) { lines++ ; print line }
  close(f)
  if (!lines) print "!!! Missing " f > "/dev/stderr"
  print("\n```python")
  b4="```\n" }
