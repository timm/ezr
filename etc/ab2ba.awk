{ a = b 
  b = $0 
  if (b ~ /^  "/) {
    gsub(/"/,"",b) 
    sub(/^[ ]*/,"",b)
    printf("# " b "\n")
    printf(a)
  } else { printf(a "\n") }}
    
