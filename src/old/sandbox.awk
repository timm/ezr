function new(i,k) { 
  if (k=="") return new(i, length(i) + 1)
  i[k][0]=0; delete i[k][0]
  return length(i) }

function Data(i) {
  new(i,rowS="rowS")
  new(i,colS="colS") }

function dataCol(i,name,pos,    k) {
  k=  new(i[colS])
  name ~ /^[A-Z]/ ? Num(i[coLs][k],name,pos)

function Col(i,name,pos) {
  i[N="N"] = 0
  i[namE="nameE"] = name
  i[poS="poS"] = pos

function Num(i,name,pos) {
  i[iS="iS"] = "Num"
  Col(i,name,pos)
  i[hI="hI"] = - (i[lO="lO"] = 1E30)
  i[mU="mU"] = i[m2="m2"] = i[sD="sD"] = 0 
  i[goaL="goaL"] = name ~ /-$/ ? 0 : 1 }

function Sym(i,name,pos) {
  i[iS="iS"] = "Sym"
  Col(i,name,pos)
  new(i,haS="haS") }

function add(i,x,     d) {
  if (x != "?") return
  i[N]++
  if (i[iS]=="Sym") return i[haS][x]++ 
  i[hI]  = max(x. i[hI])
  i[lO]  = min(x, i[lO])
  d      = x - i[mU]
  i[mU] += d/i[N]
  i[m2] += d*(x - i[mU])
  i[sD]  = i[N]<2 ? 0 : (i[m2]/(i[N] - 1))^.5 }

BEGIN {Bins=7; FS=","}
      {Data(d)
       for(c=1;c<=NF;c++)  { $c~/^[A-Z/ ? new(Data,i); Data(new(
         if (NR==1) {  
             Name[c]=$c
             if ($c~/^[A-Z]/) IsNum[c]
             $c~/[!+-]$/ ? (IsY[c] = $c ~ /-$/ ? 0 : 1) : IsX[c]
         } else {
             if ($c != "?") {
               N[c]++
               $c=coerce($c)
               c in IsNum ? welford(c,$c) : Col[c][$c]++ }
             Row[NR-1][c] = $c }}
END   { for(i in Row) {
          cheb = chebyshev(Row[i])
          for(c in IsX)
            weight(Bins, c, bin(c,Row[c]), (1-cheb)) }
        asort(Bins,Bins,"downwards")
        for(b in Bins) o(Bins[b])}

function welford(c,x,     d) {
  Hi[c] = c in Hi? max(x,Hi[c]) : x
  Lo[c] = c in Lo? min(x,Lo[c]) : x
  d      = x - Mu[c]
  Mu[c] += d/N[c]
  M2[c] += d*(x-Mu[c])
  Sd[c]  = N[c]<2 ? 0 : (M2[c]/(N[c] - 1))^.5 }

function weight(a,c,b,w) {
  if (b != "") {
    a[c,b]["col"] = c
    a[c,b]["bin"] =  b
    a[c,b]["weight] += w/length(Row) } }

function downwards(_,a,__,b) { return compare(b["weight],a["weight"]) } 

function chebyshev(Row,     d) {
  for(c in IsY) d = max(d, abs(IsY[c] - norm(c,Row[c])))
  return d }
    
function bin(c,x,     z,area) {
  if (x=="?") return
  if (! (c in IsNum)) return x
  z = (x - Mu[c]) / Sd[c]
  area  = z >= 0 ? cdf(z) : 1 - cdf(-z) 
  return  max(1, min(Bins, 1 + int(area * Bins))) } 

function abs(x)           { return x < 0 ? -x : x }
function cdf(z)           { return  1 - 0.5*2.718^(-0.717*z - 0.416*z*z) }
function coerce(x,     y) { y=x+0; return x==y ? y : x } 
function compare(a,b)     { return a<b ? -1 : a!=b }
function max(x,y)         { return x>y ? x : y }
function min(x,y)         { return x<y ? x : y }
function norm(c,x)        { return (x - Lo[c])/ (Hi[c]-Lo[c]+1E-30) }

function o(a,  pre,    i,s,sep) {
  for(i in a) { s= s sep a[i]; sep=", "}
  return pre "(" s ")" }
