BEGIN   {FS="[,:/]"}
        { gsub(/[ \t]*/,"")}
/^tiny/ {tiny=$NF}
/^file/ {f=$(NF-1)}
FNR>9 &&
NF> 6   {printf("d('%s', %s, '%s', %s, %s, %s).\n",f,$1,$2,$3,$4,tiny)}
