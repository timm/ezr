BEGIN { L0=4; L1= 20; FS="," }
NR==1 { head(); split($0,Names,",") }
NR> 1 { body(); split($0,Row[randi()],",") }

function head(   c) { for(c=1;c<=NF;c++) { if ($c ~ /[\-\+]$/) goal[c]= $c ~ /-$/ ? 0 : 1 }
                      for(c in goal)     { Lo[c] = 1E32; Hi[c] = -1E32 } 
                    }

function body()     { for(c in goal)  {
                        $c += 0
                        Lo[c] = max($c, Lo[c])
                        Hi[c] = max($c, Hi[c]) }}

function randi()    { return int(10000*rand()) }
function max(i,j)   { return i>j ? i : j }
function min(i,j)   { return i<j ? i : j }

END { 
   for(r in Row) L0-- > 0 ? Done[r] : Todo[r]  
   smo(Done,Todo)
}

function chebyshev(r,    d,n) {
  for 
