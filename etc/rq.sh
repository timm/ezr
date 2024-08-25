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

function evaluations(    rank,rx) {
   printf("\n#\n#EVALS\nRANK")
   for(rank=0; rank<=maxRank;rank++) {printf(" ,%9s",rank)};
   print("");
   for(rx in evals) { 
     printf(rx)
     for(rank=0; rank<=maxRank;rank++) 
       printf(" ,%3s (%3s)",   int(0.5 + mu(evals[rx][rank])), int(0.5+sd(evals[rx][rank])) )
     print("") }}

function improvement(    rank,rx) {
   printf("\n#\n#DELTAS\nRANK")
   for(rank=0; rank<=maxRank;rank++) {printf(" ,%9s",rank)};
   print("");
   for(rx in evals) { 
     printf(rx)
     for(rank=0; rank<=maxRank;rank++) 
       printf(" ,%3s (%3s)",   int(0.5+100*mu(delta[rx][rank])), int(0.5+100*sd(delta[rx][rank])) )
     print("") }}

function ranks(   rank,rx) {
   printf("RANK")
   for(rank=0; rank<=maxRank;rank++) printf(" ,%3s",rank)
   print("")
   for(rx in count) { 
     printf(rx)
     for(rank=0; rank<=maxRank;rank++) 
        printf(" ,%3s",  per(count[rx][rank])  )
     print("") }}

END { ranks() ; print("");  evaluations();  improvement() }
   ' - | column -s, -t
}

for i in *; do
  echo "#"
  cat $i \
  | sed 's/[ \t]//g'  \
  | sort -t, -nk 1 -nk 3   \
  | gawk -F, 'NF> 1 && !($2 in a) && NF > 5 { OFS=","; print $1,$2,$3,$4;  a[$2]}' \
  | tail -r
done | report


