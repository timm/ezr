sort -t, -nk 1 -nk 3   \
| gawk -F, 'NF> 1 && !($2 in a) { print $1,$2,$3;  a[$2]}'
