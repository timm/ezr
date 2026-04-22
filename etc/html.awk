# Post-processor for Pycco HTML. Pass -v HEADER=path/to/header.html
BEGIN { s=0 }
/<body/ {
  print
  while ((getline line < HEADER) > 0) print line
  close(HEADER)
  next
}
/<h2>/ { s=1 }
/class=.section/ {
  if(!s) sub(/class=\047section\047/, "class=\047section intro\047")
}
1
