BEGIN{RS="";FS="\n"}
FNR==NR { gsub(/\n/,"\n    "); para[NR]="    " $0;next}
sub(/^    # /,"",$1){
  print "    # " $1
  for(p in para) if(para[p]~$1){print para[p];break}
  next
}
{print; print ""}
