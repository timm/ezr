BEGIN     { FS=","; OFS=" & " }
$0 !~ /#/ { n++
            for(i=1;i<=NF;i++) 
              if (sub(/!/,"",$i)) {
                $i= "\\R" $i
                bang[i]++ }
              else  {
                $i= "  " $i
                }}
NR<4 && /#/ { $1 = $1; sub(/#/,"",$1); print OFS " reg" OFS " " $0 " \\\\" }
NR>3 && $0 !~ /#/ { $1 = $1; print OFS " " $0 " \\\\" }
END {s=""
     for(i=1;i<=NF;i++) 
       s = s OFS (bang[i] ? sprintf("%6s",int(100*bang[i]/n)) : "    ")
     print s}

# NR <= 3 { prints(1, 1, 0) }
#         { for(i=2; i<=NF; i++) n[i] += $i ~/!/
#           prints(2, 1, 0) }
# END     { for(i=1;i<=NF;i++) {
#             s = s sep name[i]
#             sep = ", " }
#           print(s)
#           prints(2, 1, 1) }
#
# function prints(start, step, use_data) {
#   for(i=start; i<=NF; i+=step) {
#     val = use_data ? (n[i] ? int(100*n[i]/NR) : " ") : $i
#     printf "%s%s", val, (i < NF-step+1 ? " & " : "") }
#   print (NR==1 ? "" : "\\\\") }
