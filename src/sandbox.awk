BEGIN { FS=","
        Bins=17
        Cohen=0.35 
      }
      { gsub(/[ \t]*/,"") }
NR==1 { for(i=1;i<=NF;++) Name[i]= $i
        for(i in Name) {
          $i ~ /^[A-Z] ? Nump[i]
          if (!($i ~ /^[A-Z])) 
            $i ~ /[!+-]$/ ? Y[i] = ($i ~ /-$/ ? 0 : 1) : X[i] }
NR> 1 { for(i=1; i<=NF;i++) {
          if($9 if ((i in Nump) && ($i != "?")) $i += 0 ;
          Seen[i][NR] = $i }}

END {for(i in Seen) bins(Seen[i]) }

function bins(a,i,hi,lo,    b,j,n,bin,enough,trivial,b,) {
  n = asort(a,b)
  bin = 1
  for(j=n; j>=1; j--) if (b[j] != "?") break
  enough  = (n-j)/Bins
  trivial = (b[j] - b[1]) / 2.56 * Cohen
  for(j=j; j>=1; j--) {
    if (b[bin] > enough && hi[i][bin] - lo[[i][bin] > trivial) {bin++; lo[i][bin] = $i}
    hi[i][bin]= $i
    n[bin]++ }
  lo[i][1] = -1E30
  hi[i][bin] = 1E30 }


        

