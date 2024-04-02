PASS==1 && /#=/  { k = newk(basename(FILENAME))
PASS==1          { keep(k) }
PASS==2 && /^#=/ { k = $2" "$3
                   dump(k)
                   next }
PASS==2          { print }

function dump(k,    i) {
  print("\n```python")
  for(i in SNIP[k]) 
    if (SNIP[k][i] !~ /^$/) print(SNIP[k][i]);
  print("```\n") }
 
function keep(k,    n) {
  sub(/#=.*/,"")
  n = length(SNIP[k])
  SNIP[k][n+1] = $0 } 

function basename(file) { sub(/^.*\//,"",file); return file }
  
function newk(f,     i,k,tmp) {
  for(i=1;i<=NF;i++) {
   if ($i == "#=") {tmp=$(i+1); $(i+1)=$i=""; break}}
  k = "<"f" "tmp">" 
  SNIP[k][1]; delete SNIP[k][1] 
  return k }
