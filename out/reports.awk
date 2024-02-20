BEGIN   {FS="[,:/]"
         printf("meta(d('%s', %s, '%s', %s, %s, %s)).\n","file","rank","treatment","samples","mu","tiny")}
        
        }
        { gsub(/[ \t]*/,"")}
/^tiny/ {tiny=$NF}
/^file/ {f=$(NF-1)}
NF> 6   {printf("d('%s', %s, '%s', %s, %s, %s).\n",f,$1,$2,$3,$4,tiny)}
FNR>9 &&
