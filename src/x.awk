BEGIN{ 
     BINS=5
     split("-0.43,0.43",breaks[3],/,/)
     split("-0.67,0,0.67",breaks[4],/,/)
     split("-0.84,-0.25,0.25,0.84",breaks[5],/,/)
     split("-0.97,-0.43,0,0.43,0.97",breaks[6],/,/)
     split("-1.07,-0.57,-0.18,0.18,0.57,1.07",breaks[7],/,/)
     split("-1.15,-0.67,-0.32,0,0.32,0.67,1.15",breaks[8],/,/)
     split("-1.22,-0.76,-0.43,-0.14,0.14,0.43,0.76,1.22",breaks[9],/,/)
     split("-1.28,-0.84,-0.52,-0.25,0,0.25,0.52,0.84,1.28",breaks[10],/,/) 
     for(b in breaks) for(k in breaks[b]) breaks[b][k] += 0 
}

function min(x,y) { return x<y?x:y }

function z2k(z,   k,lo,hi,out) {
  lo = -1e30
  for(k in breaks[BINS]) {
    hi = breaks[BINS][k]
    if (z >= lo && z < hi) {break} else {lo = hi}}
  return BREAKS[BINS][min(k,BINS-1)] }

function x2z(c,x) { return z2k((x - mu[c])/sd[c]) }
function k2x(c,z) { z=breaks[BINS][z2k(z)]; return sd[c]*z + mu[c] }

function select(c,z,a,     x,k) {
  k = z2k(z)
  x = a[c]
  if (k > 1) { hi=breaks[BINS][k]; lo=breaks[BINS][k-1]; return x <= lo && x < hi }
  else       { return x < breaks[BINS][1] }}
  
NR==1 { for(i=1;i<=NF;i++) if ($i~/^[A-Z]/) num0(i) }
NR>1  { for(i in n)        if ($i != "?")   num(i,++$i) }

function num0(i) {
  lo[i]=1E30; hi[i]=-1E30; n[i]=mu[i]=m2[i]=sd[i] }

function num(i,x,     d) {
  if (x > hi[i]) hi[i]=x
  if (x < lo[i]) lo[i]=x
  n[i]  += 1
  d      = x - mu[i]
  mu[i] += d/n[i]
  m2[i] += d*(x - mu[i])
  sd[i]  = n[i] < 2 ? 0 : (m2[i]/(n[i] - 1))^0.5 }


