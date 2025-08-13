BEGIN {FS=","}
NR==1 {s=sep=""
       for(i=1;i<=NF;i=i+2)  {
         s   = s sep $i
         sep = " & " }
       print s
      }
      {for(i=2;i<=NF;i=i+2) n[i] += $i ~/!/
       s=sep=""
       for(i=2;i<=NF;i=i+2)  {
         s   = s sep $i
         sep = " & " }
       print s "\\\\"
      }
END   {s=sep=""
       for(i=2;i<=NF;i=i+2)  {
         s   = s sep (n[i] ? int(100*n[i]/NR) : " ")
         sep = " & " }
       print s "\\\\"
      }
