BEGIN {FS=","; OFS="\t"}
NR==1 { for(i=1;i<=NF;i++) {
         if ($i~/[!+-]$/) {y++} else {x++}}}
END { s=FILENAME
      sub(/^.*\//,"",s)
      print(x,y,NR,s)} 
