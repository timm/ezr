NR==1 { for(i=1;i<=NF;i++) if ($i~/^[A-Z]/) num0(i) }
NR>1  { for(i in n)  if ($i != "?")  {num(i,++$i) }

function cdf(c,x) {return cdf1(x,lo[c],hi[c],mu[c]) }

function cdf1(x,a,b,c) {
  if (a < x && x <= c) return     (x-a)^2/((b-a)*(c-a))
  if (c < x && x <= b) return 1 - (b-x)^2/((b-a)*(b-c))
  return 0 }

function fdc(c,p) {return fdc1(p, lo[c],hi[c],mu[c])}

# https://real-statistics.com/other-key-distributions/uniform-distribution/triangular-distribution/
function fdc1(p,a,b,c) {
  return  (0 <= p && p < (c-a)/(b-a)) ? a+sqrt((b-a)*(c-a)*p) : b-sqrt((b-a)*(b-c)*(1-p)) }

function bin(c,x) { return int(BINS*cdf(c,x) }
function num0(c) {
  lo[c]=1E32; hi[c]=-1E32; n[c]=0}

function num(c,x,     d) {
  if (x > hi[c]) hi[c]=x
  if (x < lo[c]) lo[c]=x
  n[c]  += 1
  d      = x - mu[c]
  mu[c] += d/n[c] }


