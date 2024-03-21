BEGIN { FS   = ","
        m    = 1
        k    = 2
        e    = 2.71828
        pi   = 3.14159
        big  = 1E30
        tiny = 1/big }

      { gsub(/ \t\r/,"") }
NR==1 { for(i=1;i<=NF;i++) {
          if ($i ~ /^A-Z/) nump[i]
          if ($i ~ /X$/)   ignorep[i]
          if ($i ~ /!$/)   klass = i 
          name[i] = $i }}
NR>10 { print($klass, classify()) }
NR>1  { for(i=1;i<=NF;i++)  {
          N[$klass]++ 
          if (i != goal)
            if ($i != "?") 
              i in nump ? numAdd(i,$i,$klass) : symAdd(i,$i,$klass) }}

function numAdd(i,x,c,    d) {
  n[c][i]++
  d         = x - mu[c][i]
  mu[c][i] += d / n[c][i]
  m2[c][i] += d * (x - mu[c][i])
  sd[c][i]  = (m2[c][i]/(n[c][i] - 1 + tiny))^.5 }

function symAdd(i,x,c) {
  n[c][i]++
  has[c][i][x]++ }
              
function numLice(i,x,c,      v,nom,denom) {
  v= sd[c][i]^2 
  nom = e^(-1*(x-mu[c][i]^2)/(2*v))
  denom = (2*pi*v)^.5
  return nom/denom }

function symLike(i,x,c,m,prior) {
  return (has[c][i][x] + m*prior) / (N[c] +  m) }

function logLike(c,nall,nh,     prior,i,tmp) {
  prior = (n[c][i] + k ) / (nall + k * nh)
  for(i=1;i<NF;i++)
    if (i != goal) 
      if ($i != "?")
        tmp += log(i in num ? numLike(i,$i,c) : symLike(i,x,c,m,prior));
  return tmp }

function classify(   c,x,out,most) {
  most = -big
  for(c in N) {
    x = logLike(c, length(N), NR-1)
    if (x>most) {
      most=x; out=c }}
  return out }
 
