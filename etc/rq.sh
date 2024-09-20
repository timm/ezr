report() {
  gawk -F, '
/#/ { records++; next } 
{ if ( $1 > maxRank) maxRank=$1
  count[$2][$1]++
  evals[$2][$1][++x]=$3
  if ($2 != "asIs") delta[$2][$1][x]= (baseline - $4)/(baseline  + 1E-30) 
}
/asIs/ { baseline = $4 }

function mu(a,    i,sum) {
  if (length(a) <1) return ""
  asort(a)
  for(i in a) {sum += a[i] }
  return sum/length(a) }

function sd(a,    n) {
  if (length(a) <1) return ""
  asort(a)
  n = int(length(a)/10)
  return (a[9*n] - a[n])/2.56 }

function per(x) {x= int(0.5+ 100*x/records) ; return x<1? "" : x}

function evaluations(    rank,rx,r0_count) {
   for(rx in evals) {
     r0_count[rx] = length(evals[rx][0])
   }
   n = asorti(r0_count, sorted_rx, "@val_num_desc")
   printf("\n#\n#EVALS\nRANK")
   for(rank=0; rank<=maxRank;rank++) {printf(" ,%9s",rank)};
   print("");

   for(i = 1; i <= n; i++) {
     rx = sorted_rx[i]
     printf(rx)
     for(rank=0; rank<=maxRank;rank++) 
       printf(" ,%3s (%3s)", int(0.5 + mu(evals[rx][rank])), int(0.5 + sd(evals[rx][rank])) )
     print("")
   }
}

function improvement(    rank,rx,r0_count) {
   for(rx in delta) {
     r0_count[rx] = length(delta[rx][0])}
   n = asorti(r0_count, sorted_rx, "@val_num_desc")
   printf("\n#\n#DELTAS\nRANK")
   for(rank=0; rank<=maxRank;rank++) {printf(" ,%9s",rank)};
   print("");
   
   for(i = 1; i <= n; i++) {
     rx = sorted_rx[i]
     printf(rx)
     for(rank=0; rank<=maxRank;rank++) 
       printf(" ,%3s (%3s)", int(0.5 + 100 * mu(delta[rx][rank])), int(0.5 + 100 * sd(delta[rx][rank])) )
     print("")
   }
}

function ranks(   rank,rx,r0_count) {
   for(rx in count) {
     r0_count[rx] = count[rx][0]}
   n = asorti(r0_count, sorted_rx, "@val_num_desc")
   printf("RANK")
   for(rank=0; rank<=maxRank;rank++) printf(" ,%3s",rank)
   print("")
   
   for(i = 1; i <= n; i++) {
     rx = sorted_rx[i]
     printf(rx)
     for(rank=0; rank<=maxRank;rank++) 
        printf(" ,%3s",  per(count[rx][rank])  )
     print("")
     }
}

END { ranks() ; print("");  evaluations();  improvement() }
   ' - | column -s, -t
}
 
for i in *.csv; do
  echo "#"
  cat $i \
  | sed 's/[ \t]//g'  \
  | sort -t, -nk 1 -nk 3   \
  | gawk -F, 'NF> 1 && !($2 in a) && NF > 5 { OFS=","; print $1,$2,$3,$4;  a[$2]}' \
  | gawk '{a[++n]=$0} END {print(length(a)); for(i=length(a);i>=1;i--) print a[i] }'
done | report
