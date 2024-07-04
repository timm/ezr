BEGIN { BINS=5 }
NR==1 { NR==1 ? head() : body() }

func head(     c)  {
  for(c=1;c<=NF;c++)  {
    if ($c~/^[A-Z]/) num0(c)
    if ($c~/-$/)   Y[c]=0
    if ($c~/+$/)   Y[c]=1
    if (!(c in Y)) X[c] }}

func body(    c,d) {
  for (c in N) if ($c != "?") {$c += 0; num(c,$c) }
  d=0;
  for(c in Y) d = max(d, abs(norm(c,$c) - Y[c]))
  for(c in X) B[c][bin(c,$c)] += d }

func bin(c,x) { return int(BINS*cdf(x,Lo[c],Hi[c],Mu[c]) }

func cdf(x,a,b,c) {
  if (a < x && x <= c) return     (x-a)^2/((b-a)*(c-a))
  if (c < x && x <= b) return 1 - (b-x)^2/((b-a)*(b-c))
  return 0 }

func num0(c) {
  Lo[c]=1E32; Hi[c]=-1E32; N[c]=0}

func num(c,x,     d) {
  if (x > Hi[c]) Hi[c]=x
  if (x < Lo[c]) Lo[c]=x
  N[c]  += 1
  d      = x - Mu[c]
  Mu[c] += d/N[c] }

func norm(c,x) { return (x-Lo[c])/(Hi[c]-Lo[c] + 1E-32) }
func max(i,j)  { return i>j? i : j }
func abs(i)    { return i>0? i : -i }

# https://real-statistics.com/other-key-distributions/uniform-distribution/triangular-distribution/
func fdc(c,p) { return fdc1(p, lo[c],hi[c],mu[c]) }
func fdc1(p,a,b,c) {
  return (0 <= p && p < (c-a)/(b-a)) ? a+sqrt((b-a)*(c-a)*p) : b-sqrt((b-a)*(b-c)*(1-p)) }



