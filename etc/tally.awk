BEGIN { FS=","    
        SEEK="win"
        OFS=" & "}
      { gsub(/[ \t\r\n]+/, "") }
NR==1 { for(i=1;i<=NF;i++) if ($i==SEEK ) {want[i]}}
NR==2 { for(i=1;i<=NF;i++) if (i in want) {yname[i]=$i; ys[$i]}}
NR==3 { for(i=1;i<=NF;i++) if (i in want) {xname[i]=$i; xs[$i]}}
/^[0-9]/{ 
  Data++
  for(i in want) if (sub(/!/,"",$i))  add2(a,xname[i],yname[i], $i) }

END { 
  for(x in xs) head = head "," x
  print("\npercent", head)
  for (y in ys) {
    s=y
    for (x in xs)  {
      n="."
      if (x in a) if (y in a[x]) n=int(100*length(a[x][y])/Data);
      s= s "," n }
    print s}

  print("\nmid", head)
  for (y in ys) {
    s=y
    for (x in xs)  {
      n="."
      if (x in a) if (y in a[x]) n=int(mid(a[x][y]));
      s= s "," n }
    print s}
}

function mid(a,   n,m) {
  n=asort(a)
  m=int(.5 + n/2)
  return a[m ? m : 1] }

function add2(a,x,y,z) { 
  a[x][y][length(a[x][y])+1]=z }
