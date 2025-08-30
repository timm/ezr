BEGIN { FS=","   
        _ = SUBSEP}
      { gsub(/[[:space:]]/, "");
	      for(i=12;i<=NF;i+=2) stats(i)  }
END   { 
  for(x in xs) head = head "," xs[x]
  print("\n.\nBEST", head)
  for (y in ys) {
    s=y
    for (x in xs)  {
      n="."
      if (x in ALL)
        if (y in ALL[x])
          n=int(100*length(ALL[x][y])/NR);
      s= s "," n }
    print s}
  print("\n.\nMOST", head)
  for (y in ys) {
    s=y
    for (x in xs)  {
      n="."
      if (x in ALL)
        if (y in ALL[x])
          n=int(mid(ALL[x][y]));
      s= s "," n }
    print s}
}

function stats(i,    a) {
  split($i,a,"_");  
  push2(ALL, a[1], a[2], $(i+1)) }

function mid(a,   n,m) {
  n=asort(a)
  m=int(.5 + n/2)
  return a[m ? m : 1] }

function push2(a,x,y,z) { 
  xs[x] = x 
  ys[y] = y
  a[x][y][length(a[x][y])+1]=z }
