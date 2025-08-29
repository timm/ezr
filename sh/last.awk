BEGIN {FS=","}
{gsub(/ /,"",$0); stats()}
END{
  asort(ns,nums)
  s=" "
  for(n in nums) s = s "," nums[n]
  print(s)
  for (rx in rxs) {
    s=rx
    for (n in ns) 
      s= s "," (seen[n][rx] > 0 ? int(100*seen[n][rx]/NR) : ".")
    print s}}

function stats(    i,a){
  for(i=12;i<=NF;i++) {
    split("",a,"")
    split($i,a,"_");  #print(a[1],a[2])
    ns[a[1]] = a[1]
    rxs[a[2]]
    seen[a[1]][a[2]]++ }}

