D="/Users/timm/gits/andre/ez/out/SNEAK"
for f in $D/*.out
do  
  echo ""
  tac $f | gawk -F, 'NF>7' $f | 
  sort -t, -n -k 1 -k 2 -k 3   | 
  grep -v rand | 
  grep -v 2rrp | 
  grep -v base | grep -v bonr | grep -v xSNEAK | grep -v rrp|
  gawk -F, 'BEGIN {_=" , "} {gsub(/[ \t\n]/,"")}  {if (! ($2  in a)) a[$2]= $1 _ $2 _ $3 _ $4} END {for(i in a) {print a[i]}; }' | sort -n 
done #
  #gawk -F, '{a[$2][$1]++} END {for(i in a) for (j in a[i]) {print i,j,a[i][j]}}'

