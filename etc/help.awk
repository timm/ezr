BEGIN { COLOR= "\033[36m"  
		    RESET= "\033[0m"     
			  FS   = ":.*?## "        
			  print "\nmake [WHAT]" 
      }
/^[^[:space:]].*##/ {          
		    printf("   %s%-12s%s : %s\n", COLOR, $1, RESET, $2) | "sort"  }
