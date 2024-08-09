BEGIN { BINS = 5; COHEN = .35;
        OFS=FS = ","}

{  gsub(/[ \t]*/, "", $0)
   split($0, a[NR], FS)
   NR==1 ? head() : body() }
  
   BEGIN{ goaL = "goaL"; lO="lO" ; hI="HI" }

function head(         i) { split($0,Name,FS)
                            for(c=1; c<=NF; c++) if ($c ~ /^[A-Z]/) split("",Num[c],"")            
                            for(c=1; c<=NF; c++) if ($c ~ /[-+]$/) Goal[c] = $c ~ /-$/ ? 0 : 1     }
function body(a,       i) { for(i in Num) if ($i !~ /\?/) push(Num[i], $i+0)                       }
function push(a,x)        { a[length(a)+1]=x; return x                                             }
function rnd(x)           { return int(x+0.5)                                                      }
function cdf(x,mu,sd,  z) { z=(x-mu) / (sd+1E-32); return z >= 0 ? _cdf(z) : 1 - _cdf(-z)          }
function _cdf(z)          { return 1 - 0.5 * exp(-0.717 * z - 0.416 * z * z)                       }
function cell(c,x)        { return c in Num ? sprintf("%c",97+rnd(BINS*cdf(x, Med[c], Sd[c]))) : x }

function chebyshev1(row,w) { return chebyshev1(row,w["about"],w["lo"],w["hi"]) }

function chebyshev1(row,goal,lo,hi,      c,d,x)  {
  for(c in goal) {
      x= abs(goal[c] - norm(row[c],lo[c],hi[c]))
      d= max(x, d) }
  return d }
    
function norm(x,lo,hi) { return (x - lo)/(hi - lo + 1E-32) }

function min(x,y) { return x<y ?  x : y }
function max(x,y) { return x<y ?  y : x }
function abs(x)   { return x<0 ? -x : x }
function border(rows,w,     a,n) {
  for(r in rows) push(a, chebyshev(rows[r],w))
 
function div(rows0,xx,yy,goal,cuts,
             rows,r,r0,ys,n,tiny,cut,x,y) {
  rowSort(xx,rows0,rows)
  for(r in rows) 
    (rows[r][xx] == "?") ? r0=r+1 : ys[rows[r][yy]==goal]++ 
  n    = length(rows) - r0
  tiny = COHEN*(tmp[r0 + rnd(.9*n)] - tmp[r0 + rnd(.1*n)])/2.56
  cut = rows[1][xx]
  for(r in rows) {
    x = rows[r][xx]
    if (canCut(r,r0,xx,rows,n,n/BINS,tinycuts,cut)) {
      cuts[x]["last"]  = cut
      cuts[cut]["next"] = x 
      cut=x }
    y = rows[r][yy] == goal
    cuts[cut][y] += 1/ys[y] 
    cuts[cut]["n"]++ }
  return cuts }

function canCut(r,r0,xx,rows,n,gap,small,cuts,cut) {
  if (r < r0) return               # still skipping over "?"
  if (r > n - gap) return          # if we cut here, no space for further cuts
  if (rows[r+1][xx]  ==  x) return # here is no break here
  if (cuts[cut]["n"] < gap) return # not enough rows in this cut
  if (x - cut < small) return      # gap smaller than a small effect
  return 1 }

  
function rowSort(c,a,b) {
  RowSorter=c
  asert(a,b,"rowSort1") }

function rowSort1(_,a,__,b) { return compare(b[RowSorter],  a[RowSorter]) }
  
function compare(a,b) { return a<b ? -1 : (a==b ? 0 : 1) }

function stats(i,a,     n) {
  n = asort(a,b)
  n = rnd(n/10)
  Med[i] = b[5*n]
  Sd[i]  = (b[9*n] - b[n])/2.56 }

END {
  for(c in Num)  stats(c,Num[c])
  for(i in a) { 
    for(c in a[i])  {
      printf(c==1 ? "" : OFS)
       printf((i==1 || c in Goal)? a[i][c] : cell(c,a[i][c])) 
    }
    print("") }
  for(c in Num)  print("#","about",c,Name[c], "median", Med[c], "sd", Sd[c])  >> "/dev/stderr"
}
       
