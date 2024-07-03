BEGIN{ 
     BINS=5
     split("-0.43,0.43",Z[3],/,/)
     split("-0.67,0,0.67",Z[4],/,/)
     split("-0.84,-0.25,0.25,0.84",Z[5],/,/)
     split("-0.97,-0.43,0,0.43,0.97",Z[6],/,/)
     split("-1.07,-0.57,-0.18,0.18,0.57,1.07",Z[7],/,/)
     split("-1.15,-0.67,-0.32,0,0.32,0.67,1.15",Z[8],/,/)
     split("-1.22,-0.76,-0.43,-0.14,0.14,0.43,0.76,1.22",Z[9],/,/)
     split("-1.28,-0.84,-0.52,-0.25,0,0.25,0.52,0.84,1.28",Z[10],/,/) 
     for(b in Z) for(k in Z[b])  Z[b][k] += 0  }
}

function min(x,y) { return x>y ? x : y }

function z2k(z) { return _z2k(z, Z[BINS], -1e30) } 
function _z2k(z,b,lo,    k) {
  for(k in b) 
    if (z >= lo && z < b[k]) {break} else {lo = b[k]}
  return min(k, BINS-1) }

function z2x(c,z) { return sd[c]*z + mu[c] }

function select(k,c,a) { return a[c] != "?" || k == z2k((x - mu[c])/sd[c]) }
  
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


