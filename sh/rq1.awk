NR==1{print $0 " A";  for(i=1; i<=NF; i++) name[i]=$i; next }
/#/   {next}
      {n++ ; for(i=1;i<=NF;i++) cnt[i] += $i ~/A/}
END   { s=sep=""
        for(i=1;i<=NF;i++) {
             m = int(100*cnt[i]/n)
             #if (m) print(m "," name[i],"A") | "sort -n"
             s = s sep (cnt[i] ?  m : " ")
             sep=", " 
        }
        print(s, " A") }
