BEGIN { BINS = 5; COHEN = .35;
        OFS=FS = ","}

{  gsub(/[ \t]*/, "", $0)
   split($0, a[NR], FS)
   NR==1 ? head() : body() }
   
function head(         i) { split($0,Name,FS)
                            for(c=1; c<=NF; c++) if ($c ~ /^[A-Z]/) split("",Num[c],"")            
                            for(c=1; c<=NF; c++) if ($c ~ /[-+]$/) Goal[c]                         }
function body(a,       i) { for(i in Num) if ($i !~ /\?/) push(Num[i], $i+0)                       }
function push(a,x)        { a[length(a)+1]=x; return x                                             }
function rnd(x)           { return int(x+0.5)                                                      }
function cdf(x,mu,sd,  z) { z=(x-mu) / (sd+1E-32); return z >= 0 ? _cdf(z) : 1 - _cdf(-z)          }
function _cdf(z)          { return 1 - 0.5 * exp(-0.717 * z - 0.416 * z * z)                       }
function cell(c,x)        { return c in Num ? sprintf("%c",97+rnd(BINS*cdf(x, Med[c], Sd[c]))) : x }

function div(rows,c) {
  for(r in rows) 
    if ((x=rows[c]) != "?") push(tmp,x);  
  n   = asort(tmp) 
  gap = rnd(n/BINS)
  lo  = tmp[1]
  hi  = tmp[n]
  small  = COHEN * (tmp[rnd(.9*n)] - tmp[rnd(.1*n)])/2.56
  for(i in tmp) {
    x=tmp[i]
    if ((i < n - gap)              && cuts[cut] > gap && \
        tmp[i+1] - x > (hi-lo)/100 && x - cut >=  small) 
           cut=x;
    cuts[cut]++
    
          
  
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
       
