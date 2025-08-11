BEGIN { W=33; Max=14 }
      { for(i=2;i<=Max;i+=2) if($i!="?") { name[i]=$(i-1); a[i][NR]=$i+0} }
END   { for(i=2;i<=Max;i+=2) {
          n=asort(a[i],b); t=int(n/10)
          b10=b[t]; b30=b[3*t]; b50=b[5*t]; b70=b[7*t]; b90=b[9*t]
    
          for(j=1;j<=W;j++)  J[j]=" "; J[int(W/2)]="|"
          split(b10" "b30" "b50" "b70" "b90,v)
    
          for(k=1   ; k<=5    ; k++)       v[k] = int(v[k]*W/100)
          for(j=v[1]; j<=v[2] ; j++) J[j] = "-"
          for(j=v[4]; j<=v[5] ; j++) J[j] = "-"
          J[v[3]]="*"
    
          s=""; for(j=1 ; j<=W ; j++) s =s J[j]
          print b10,b30,b50,b70,b90,s,name[i] | "sort -n -k 3" } }
