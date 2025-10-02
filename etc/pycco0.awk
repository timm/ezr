BEGIN { FS="\"" }
            { sub(/-----.*/,"") }
b4 ~ /^def[ \t]/ && NF >= 3 { 
              print "\n# " $2; print(b4); b4=""; next}
            { if(b4) print b4; b4=$0 }
        END { if(b4) print b4 }
