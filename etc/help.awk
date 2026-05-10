# Usage: gawk -f etc/help.awk Makefile
BEGIN {
    FS = ":.*?##"; 
    printf "\nUsage:\n  make \033[36m<target>\033[0m\n\ntargets:\n"
} 
/^[~a-z0-9A-Z_%\.\/-]+:.*?##/ { 
    printf("  \033[36m%-25s\033[0m %s\n", $1, $2) | "sort"
}
