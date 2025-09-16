BEGIN { FS=","    
        SEEK="win" # or msec
        OFS=" & "}

      { gsub(/[ \t\r\n]+/, "") }
NR==1 { for(i=1;i<=NF;i++) if ($i==SEEK ) {want[i]}}
NR==2 { for(i=1;i<=NF;i++) if (i in want) {yname[i]=$i; ys[$i]}}
NR==3 { for(i=1;i<=NF;i++) if (i in want) {xname[i]=$i; xs[$i]}}
/^[0-9]/{ 
  Data++
  for(i in want) if (sub(/!/,"",$i)) {
      add2(A,xname[i],yname[i], $i) }}

END { 
  print Data
  for(x in xs) {head = head sep x; sep=OFS}
  print("\n.\npercent", head)
  for (y in ys) {
    s=y
    for (x in xs)  {
      n="."
      if (x in A) if (y in A[x]) n=int(100*N[x][y]/Data);
      s= s OFS n }
    print s}
  print("\n.\nmid", head)
  for (y in ys) {
    s=y
    for (x in xs)  {
      n="."
      if (x in A) if (y in A[x]) n=int(mid(A[x][y]));
      s= s OFS n }
    print s }
}

function mid(a,   n,m) {
  n=asort(a)
  m=int(.5 + n/2)
  return a[m] }

function add2(a,x,y,z) { 
  N[x][y]++
  a[x][y][length(a[x][y])+1]=(z +0)}
