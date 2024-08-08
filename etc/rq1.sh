 NF>7 { gsub(/[ \t]/,"")                    
        split($0, a[NR], ",") }              
 END  { n = asort(a,b,"nlabels")              
        for(i in b) {                          
          for(k in b[i]) printf("%6s",b[i][k]) 
          print "" }}                            
                               
function nlabels(_,a,__,b) {    
  if (a[1] < b[1]) return -1     
  if (a[1] == a[1]) {             
    if (a[3] < b[3]) return   1    
    if (a[3] == b[3]) return  0     
    if (a[3] > b[3]) return  -1  }   
  if (a[1] > b[1]) return - }         
