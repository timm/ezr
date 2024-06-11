function trim(s) {sub(/^[ \t\n]*/,"",s); sub(/[ \t\n]*$/,"",s); return s} 

PASS==1 && /^##/      { f=FILENAME
                        sub(/^.*\//,"",f)
                        sub(/\.jl/,"",f)
                        k="<"f" "$2">"; next }  
PASS==1               { SNIP[k] = SNIP[k] sep $0 ; sep="\n" } 
PASS==2               { print }
PASS==2 && /```julia/ { k=$2" "$3
                        print(trim(SNIP[k])"\n```")
                        USED[k]++
                        while(getline x >0) if (x ~ /^```/) break }
