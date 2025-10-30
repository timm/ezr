BEGIN { FS=","    
        SEEK="win" # or msec
        OFS=" & "
      }

      { gsub(/[ \t\r\n]+/, "") }
NR==1 { for(i=1;i<=NF;i++) if ($i==SEEK ) {want[i]}}
NR==2 { for(i=1;i<=NF;i++) if (i in want) {yname[i]=$i; ys[$i]}}
NR==3 { for(i=1;i<=NF;i++) if (i in want) {xname[i]=$i; xs[$i]}}
/^[0-9]/{ 
  Data++
  for(i in want) {
      x=xname[i]
      y=yname[i]
      if (sub(/!/,"",$i)) N[x][y]++
      A[x][y][length(A[x][y])+1] = $i+0 }}

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
  print("\n.\n"SEEK"\nmid", head)
  for (y in ys) {
    s=y
    for (x in xs)  {
      n="."
      if (x in A) if (y in A[x]) n=int(mid(A[x][y]));
      s= s OFS n }
    print s }
  print SK
}

function mid(a,   n,m) {
  n=asort(a)
  m=int(.5 + n/2)
  return a[m] }
