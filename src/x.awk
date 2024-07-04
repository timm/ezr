# X,Y for independent and depedndent columns
# Lo,Hi,Mu,N  for numerics
# B for bins
BEGIN { BINS=5 }
      { NR==1 ? head() : body() }

function head(     c)  {
  for(c=1;c<=NF;c++)  {
    if ($c~/^[A-Z]/) num0(c)
    if ($c~/-$/)   Y[c]=0
    if ($c~/+$/)   Y[c]=1
    if (!(c in Y)) X[c] }}

function body(    c,d) {
  for (c in N) if ($c != "?") {$c += 0; num(c,$c) }
  d=0;
  for(c in Y) d = max(d, abs(norm(c,$c) - Y[c]))
  for(c in X) B[c][bin(c,$c)] += d }

function bin(c,x) { return int(BINS*cdf(x,Lo[c],Hi[c],Mu[c]) }

function cdf(x,a,b,c) {
  if (a < x && x <= c) return     (x-a)^2/((b-a)*(c-a))
  if (c < x && x <= b) return 1 - (b-x)^2/((b-a)*(b-c))
  return 0 }

function num0(c) {
  N[c]=0; Lo[c]=1E32; Hi[c]=-1E32 }

function num(c,x,     d) {
  if (x > Hi[c]) Hi[c]=x
  if (x < Lo[c]) Lo[c]=x
  N[c]  += 1
  d      = x - Mu[c]
  Mu[c] += d/N[c] }

function norm(c,x) { return (x-Lo[c])/(Hi[c]-Lo[c] + 1E-32) }
function max(i,j)  { return i>j? i : j }
function abs(i)    { return i>0? i : -i }

# https://real-statistics.com/other-key-distributions/uniform-distribution/triangular-distribution/
function fdc(c,p) { return fdc1(p, lo[c],hi[c],mu[c]) }
function fdc1(p,a,b,c) {
  return (0 <= p && p < (c-a)/(b-a)) ? a+sqrt((b-a)*(c-a)*p) : b-sqrt((b-a)*(b-c)*(1-p)) }



