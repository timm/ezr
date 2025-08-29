BEGIN { FS=","   }
      { gsub(/[[:space:]]/, "");
	stats()  }
END   { report() }

function report(   rxs,ns) {
  for(n in N) for(rx in N[n]) { rxs[rx] = rx; ns[n] = n+0 }
  asort(ns,nums)
  head=" "
  for(n in nums) head = head "," nums[n]
  print("\n.\n.\nBESTS", head)
  for (rx in rxs) {
    s=rx
    for (n in ns) 
      s= s "," (N[n][rx] > 0 ? int(100*N[n][rx]/NR) : ".")
    print s}
  print("\n----\nWINS", head)
  for (rx in rxs) {
    s=rx
    for (n in ns) 
      s= s "," (N[n][rx] > 0 ? int(SUM[n][rx]/N[n][rx]) : ".")
    print s}
}
function stats(    i,a){
  for(i=12;i<=NF;i+=2)  {
    split("",a,"")
    split($i,a,"_");  
    N[  a[1]][a[2]]++
    SUM[a[1]][a[2]]+= $(i+1)
    }}

