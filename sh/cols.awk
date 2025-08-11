BEGIN{pre="  "; B="\033[1m";R="\033[0m";P="\033[48;5;217m"}

FNR==1 { print " "
         for(i=1;i<=NF;i++) w[i] = length($i)
           gsub(",","  ")
           print pre B $0 R ; next }

{ printf pre
  b=($0~/#/ || FNR==1) ? B:""
  for(i=1;i<=NF;i++){
     raw = sprintf("%-*s", w[i]+2, $i)  # pad plain text
     if($i~/9/) raw = P $i R sprintf("%*s", w[i]+2 - length($i), "")
     printf "%s%s", b, raw
  }
  print R
}


