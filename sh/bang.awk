BEGIN { FS="," }
NR==1 { prints(1, 2, 0) }
      { for(i=2; i<=NF; i+=2) n[i] += $i ~/!/
        prints(2, 2, 0) }
END   { prints(2, 2, 1) }

function prints(start, step, use_data) {
  for(i=start; i<=NF; i+=step) {
    val = use_data ? (n[i] ? int(100*n[i]/NR) : " ") : $i
    printf "%s%s", val, (i < NF-step+1 ? " & " : "") }
  print (NR==1 ? "" : "\\\\") }
