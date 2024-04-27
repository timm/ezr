D="/Users/timm/gits/andre/ez/out/SNEAKB"
for f in $D/*.out
do  
  echo ""
  tac $f | gawk -F, 'NF>7' $f | 
  sort -t, -n -k 1 -k 2 -k 3   |#grep -v xrand | grep -v x2rrp | grep -v xbase | grep -v xbonr | grep -v xSNEAK | grep -v xrrp|
  gawk -F, 'BEGIN {_=" , "} {gsub(/[ \t\n]/,"")}  {if (! ($2  in a)) a[$2]= $1 _ $2 _ $3 _ $4} END {for(i in a) {print a[i]}; }' | sort -n 
done | 
  gawk -F, '/^$/{++para} {a[$2][$1]++;  N[$2][$1][para]=$3 } END {
     for(i in a) 
        for (j in a[i]) 
          print i,j,int(100*a[i][j]/31), "$", int(.5+mu(N[i][j])), int(+5+sd(N[i][j])) }
   function mu(a,   i,n) {
     for(i in a) n+= a[i]
     return n/length(a) }

  function sd(a,   i,n,nud) {
    mid=mu(a)
    for(i in a) n+=(a[i] - mid)^2
    return sqrt(n/(length(a) - 1 + 0.0001)) }'
#
