BEGIN   { FS=OFS="," }
/^asIs/ { split($0,line,":"); asIs = line[2]+=0 }
/^div/  { split($0,line,":"); div  = line[2] * 0.2 }
 NF>7   { gsub(/[ \t]*/,"")                    
          split($0, a[NR], ",") }              
 END    { n = asort(a,b,"nlabels")              
          for(i in b) {                          
            rank[ b[i][2]]= b[i][1]
            evals[b[i][2]]= b[i][3] 
            delta[b[i][2]]= rnd((asIs-b[i][4])/(div + 1E-32))}
          print("")
          for(i in rank) {
            printf("%5.0f, %5.0f, %5.0f, %s\n",
                   rank[i], evals[i], delta[i],i) }
        }

function rnd(x) { return int(0.5+x) }

function nlabels(_,a,__,b) {    
  #a[1] += 0;  a[3] += 0
  #b[1] += 0;  b[3] += 0
  if (a[1] < b[1]) return 1     
  if (a[1] == b[1]) {  
    if (a[3] <  b[3]) return   1    
    if (a[3] == b[3]) return   0     
    if (a[3] >  b[3]) return  -1  }   
  if (a[1] > b[1]) return -1 }         
