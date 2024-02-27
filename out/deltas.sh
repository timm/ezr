for i in $*
do
  tac $i | gawk 'BEGIN {FS=","
                        split("b,2b,rand,bonr,rrp,2rrp",t,/,/) 
                        for(i in t) u[t[i]] = i
                        }
                 /base/ {mu=$4}
                 /^ / { gsub(/[ \t]*/,"")
                        d[$3][ u[$2] ] = $4/mu 
                      }
                  END { report(t,d) }

function report(t,d,    a,s,sep) {
  s="n"; 
  for(i=1;i<=6;i++)  s=s "," t[i]
  print(s)
  for(i in d) {
    s=i; sep=""
    for(j=1;j<=6;j++) {
      d[i][j] += 0;
      s = s "," (d[i][j]==0? " " : d[i][j]) }
    print s}}

' 
done
