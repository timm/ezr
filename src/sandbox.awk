BEGIN {FS=","}
 {for(i=1;i<=NF;i++) 
    if (NR==1) {
        name[i]=$i
        if ($i~/^[A-Z]/) isNum[i]
        if ($i~/[!+-]$/) isGoal[i] = $i ~ /-$/ ? 0 : 1 
    } else {
        if ($i != "?") col[i][NR] = $i = coerce($i)
        row[NR-1][i] = $i }}
END {
  for(i in col) asort(col[i]) 
  main() }

function o(a,  pre,    i,s,sep) {
  for(i in a) { s= s sep a[i]; sep=", "}
  return pre "(" s ")" }

function bin(c,x,ranges,     z,area) {
  if (! (c in isNum)) return x
  z = (x - median(c)) / sd(c)
  area  = z >= 0 ? cdf(z) : 1 - cdf(-z) 
  return  max(1, min(ranges, 1 + int(area * ranges))) } 
   
function cdf(z)           { return  1 - 0.5*2.718^(-0.717*z - 0.416*z*z) }
function median(c,     n) { n=int(length(col[c])/10); return col[c][5*n]}
function sd(    c,     n) { n=int(length(col[c])/10); return (col[c][9*n]-col[n])/2.56}
 
ranges[c][r] += d2h 
 40     r = col:range(x,the.ranges)
 41     col.ranges[r] = col.ranges[r] or RANGE.new(col,r)
 42     col.ranges[r]:add(x,d) end end

function max(x,y)        { return x>y ? x : y }
function min(x,y)        { return x<y ? x : y }
function coerce(x,    y) { y=x+0; return  x==y ? y : x} 
