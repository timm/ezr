#!/usr/bin/env gawk -f
BEGIN{
  FS="("
  print "\\noindent{\\scriptsize \\begin{tabular}{r@{ : }l@{~}p{2.5in}}"
  print "\\textbf{loc}&\\textbf{name}&\\\\ \\hline" }

                     { DOC[NR-1]=trim($0) }
sub(/^def\s+/,"",$1) { FUN[NR]=trim($1) }

END{ sort="sort -k 3"
     for(i in FUN)
       printf("%d & \\verb|%s| &  %s \\\\\n", i, FUN[i], DOC[i]) | sort 
     close(sort)
     print "\\hline\\end{tabular}}" }

function trim(s){ 
  sub(/^[\t "]+/,"",s); sub(/[\t "]+$/,"",s); return s }

#-----------------------------
   #
   ##!/usr/bin/env gawk -f
# xindex_py.awk — index Python functions into a LaTeX table
# Usage: gawk -f xindex_py.awk file1.py [file2.py ...] > index.tex
#
# Output columns: name, LOC (line number of def), help (1st line of docstring)
# - Detects "def name(...):" lines; decorators are ignored.
# - Docstring must be the first statement in the body (PEP 257).
# - Supports one-line and multi-line triple-quoted docstrings (""" or ''').
# - Accepts r/u/f/rf/fr prefixes. Alphabetical sort via "sort".
#
# BEGIN {
#   COM = "sort"
#   print "\\section*{Index} {\\scriptsize \\begin{tabular}{lrl}"
#   print "\\textbf{name} & \\textbf{LOC} & \\textbf{help} \\\\ \\hline"
# }
#
# function trim(s) { sub(/^[ \t\r\n]+/,"",s); sub(/[ \t\r\n]+$/,"",s); return s }
# function texescape(s){
#   gsub(/\\/,"\\textbackslash{}",s); gsub(/&/,"\\&",s); gsub(/%/,"\\%",s);
#   gsub(/#/,"\\#",s); gsub(/\$/,"\\$",s); gsub(/{/,"\\{",s); gsub(/}/,"\\}",s);
#   gsub(/_/,"\\_",s); gsub(/\^/,"\\textasciicircum{}",s); gsub(/~/,"\\textasciitilde{}",s);
#   return s
# }
# function leadspaces(s){ match(s,/^[ \t]*/); return RLENGTH }
#
# BEGIN { in_def=0; in_doc=0; got_doc=0; base_indent=0; fname=""; docbuf=""; qdelim=""; def_line=0 }
#
# # Match function definitions like: def name(...): (with optional spaces)
# ^[ \t]*def[ \t]+[A-Za-z_][A-Za-z0-9_]*[ \t]*\( {
#   line = $0
#   sub(/^[ \t]*def[ \t]+/,"",line)
#   split(line, parts, /\()/)
#   rawname = parts[1]; gsub(/[ \t]/,"",rawname); fname = rawname
#   in_def=1; got_doc=0; in_doc=0; docbuf=""; qdelim=""; base_indent=leadspaces($0); def_line=NR
#   next
# }
#
# # Immediately after def: look for a first-statement docstring (triple-quoted).
# in_def && !in_doc && !got_doc {
#   if ($0 ~ /^[ \t]*$/) next
#   if ($0 ~ /^[ \t]*#/) next
#   if (leadspaces($0) <= base_indent) {
#     printf("\\verb|%s| & %d & %s \\\\\n", fname, def_line, "") | COM; in_def=0; next
#   }
#   # optional r/u/f prefixes + triple quotes """ or '''
#   if (match($0, /^[ \t]*([rRuUfF]{0,2})(\"\"\"|''')/, m)) {
#     qdelim = substr($0, RSTART + length(m[1]), RLENGTH - length(m[1]))
#     rest = substr($0, RSTART + RLENGTH)
#     idx = index(rest, qdelim)
#     if (idx > 0) {
#       docline = trim(substr(rest, 1, idx-1))
#       docline = texescape(docline)
#       printf("\\verb|%s| & %d & %s \\\\\n", fname, def_line, docline) | COM
#       in_def=0; got_doc=1; next
#     } else {
#       in_doc=1; docbuf=rest; next
#     }
#   } else {
#     printf("\\verb|%s| & %d & %s \\\\\n", fname, def_line, "") | COM; in_def=0; next
#   }
# }
#
# # Accumulate multi-line docstring until closing delimiter.
# in_doc {
#   pos = index($0, qdelim)
#   if (pos > 0) {
#     docbuf = docbuf "\n" substr($0, 1, pos-1)
#     n = split(docbuf, L, /\r?\n/); docline=""
#     for (i=1; i<=n; i++){ t=trim(L[i]); if (t!=""){ docline=t; break } }
#     docline = texescape(docline)
#     printf("\\verb|%s| & %d & %s \\\\\n", fname, def_line, docline) | COM
#     in_doc=0; in_def=0; got_doc=1; docbuf=""; qdelim=""
#   } else {
#     docbuf = docbuf "\n" $0
#   }
#   next
# }
#
# END { print "\\end{tabular}}" }

