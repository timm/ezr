D="../out/SNEAKB"
for f in $D/*.out
do  
  echo ""
  cat $f |
    gawk -F, 'NF>7 {gsub(/[ \t]*/,"");print} '  | 
  sort -t,  -n -k1,1  -n -k3,3  | #grep -v xrand #| grep -v x2rrp | grep -v xbase | grep -v xbonr | grep -v xSNEAK | grep -v xrrp|
  gawk -F, 'BEGIN {_=" , "} {gsub(/[ \t\n]/,"")}  {if (! ($2  in a)) a[$2]= $1 _ $2 _ $3 _ $4} END {for(i in a) {print a[i]}; }' |
  sort -t,  -n -k1,1  -n -k3,3   #grep -v xrand #| grep -v x2rrp | grep -v xbase | grep -v xbonr | grep -v xSNEAK | grep -v xrrp
done | gawk -F, '/^$/{++para; next} {a[$2][$1]++;  N[$2][$1][para]=$3 } END {
     OFS=","
     print("Method","rank","frequency","labels-mu","labels-sigma")
     for(i in a) {
       print "#"
        for (j in a[i]) 
          print i,j,int(100*a[i][j]/31),  int(.5+mu(N[i][j])), int(+5+sd(N[i][j])) }}

   function mu(a,   i,n) {
     for(i in a) n+= a[i]
     return n/length(a) }

  function sd(a,   i,n,nud) {
    mid=mu(a)
    for(i in a) n+=(a[i] - mid)^2
    return sqrt(n/(length(a) - 1 + 0.0001)) }' |sed 's/bonr/uncertain/g' | sed 's/2rrp/ignore/g' | sed 's/rrp/SWAY/g' | sed 's/ b / certain/g' |
    column -s, -t
#
