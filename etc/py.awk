# Pre-processor for Python -> Markdown headers
/^#[ \t]*[-—]{4}/ {
  sub(/^#[ \t]*[-—]+[ \t]*/, ""); sub(/[ \t]*[-—]+.*$/, "");
  print "# ## " $0 "\n\n"; next
}
/^#[ \t]*[-—]{3}/ {
  sub(/^#[ \t]*[-—]+[ \t]*/, ""); sub(/[ \t]*[-—]+.*$/, "");
  print "# ### " $0 "\n\n"; next
}
/^#[ \t]*[-—]{2}/ {
  sub(/^#[ \t]*[-—]+[ \t]*/, ""); sub(/[ \t]*[-—]+.*$/, "");
  print "# #### " $0 "\n\n"; next
}
/^[ \t]*(def|class)/ { h=$0; next }
h && /"""/           { gsub(/"""/,""); print "#"$0; print h; h=""; next }
h                    { print h; h="" }
1
