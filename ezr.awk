BEGIN { FS=","; BINS=7; E=193/71 }

NR==1 {
  print $0
  for(c=1;c<=NF;c++) {
    if ($c ~ /X$/) skip[c]
    if ($c ~ /^[A-Z]/) {
      if ($c ~ /[+-]$/) w[c] = $c !~ /-$/
      hi[c]=-(lo[c]=1e32); n[c]=mu[c]=m2[c]=sd[c]=0 } } }

NR > 1 {
  for(c=1;c<=NF;c++) {
    if(c in hi && $c != "?") num(c, ($c = $c+0))
    data[c, NR-1] = $c } }

END {
  for(r=1; r<NR; r++) {
    s = data[1, r]
    for(c=2; c<=NF; c++) s = s "," norm(c, data[c,r])
    print s } }

function norm(c,v,       bin,x) {
  if (v == "?") return v
  if (c in skip) return v
  if (c in w) return v
  bin = (hi[c] - lo[c]) / (BINS - 1)
  x = int(cdf(c, v) * (BINS - 1) + 0.5)
  return lo[c] + x * bin }

function num(c,v,    d) {
  n[c]++
  lo[c] = min(v, lo[c])
  hi[c] = max(v, hi[c])
  d = v - mu[c]
  mu[c] += d / n[c]
  m2[c] += d * (v - mu[c])
  sd[c] = (n[c] < 2) ? 0 : sqrt(m2[c] / (n[c] - 1)) }

function cdf(c,v,      tmp) {
  z = (v - mu[c]) / (sd[c] + 1e-32)
  return (z >= 0 ? _cdf(z) : 1 - _cdf(-z)) }

function _cdf(z) { return 1 - 0.5*E ^ (-0.717*z - 0.416*z*z) }

function min(x,y) { return x < y ? x : y }
function max(x,y) { return x > y ? x : y }
