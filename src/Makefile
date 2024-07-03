# Default is to what ever the parent Makefile says to do.

-include ../Makefile

stats:
	echo "file,rows,cols,xnums,xsyms,ymin,ymax"
	cd ../data; for f in */*.csv; do                          \
    gawk 'BEGIN { OFS=FS=","; nums = ups =downs = syms = 0 } \
          NR==1 { for(i=1;i<=NF;i++) {                        \
                        if ($$i ~ /[+]$$/) {ups++} else {      \
                        if ($$i ~ /[-]$$/) {downs++} else {     \
                        if ($$i ~ /^[A-Z]/ ) {nums++}  else {syms++}}}}; next}  \
          END   { s=FILENAME;                                                    \
                  gsub(/.csv/,"",s);                                              \
                  print s,NR--,NF,nums,syms,ups,downs}' $$f ; done

bins: 
	 for f in ../data/*/*.csv; do \
     gawk -F, 'NR==1{ for(i=1;i<=NF;i++) if ($$i ~ /[!+-]$$/) {y++} else {x++}; \
                      printf("%s,%s,%s", FILENAME,x,y);  exit}' $$f; \
     ./sandbox.lua --bins $$f  \
     | gawk 'BEGIN {FS="\n";RS=""; print""} {n += NF} END {print NR,n/NR}' ; done

~/tmp/%.html : %.lua
	mkdir -p ~/tmp
	cp ../docs/img/tree.png ~/tmp/tree.png
	pycco -d ~/tmp $<
	echo "p { text-align: right }" >> ~/tmp/pycco.css
	echo "info p { text-align: left }" >> ~/tmp/pycco.css
	open $@
