    { a[NR]=$0 }
END {n=length(a);
     while(++i<n) {
       if (a[i+1] ~ /^[ \t]+"/) {
         gsub(/"/,     "", a[i+1]);
         sub(/^[ \t]*/,"", a[i+1]);
         print "# " a[i+1] ;
         print a[i];
         i++ ;
       } else
         print a[i] ;
    }}

