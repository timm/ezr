# Default is show help; e.g.
#
#    make 
#
# prints the help text.

SHELL     := bash
MAKEFLAGS += --warn-undefined-variables
.SILENT:

Top=$(shell git rev-parse --show-toplevel)

help      :  ## show help
		gawk -f $(Top)/etc/help.awk $(MAKEFILE_LIST) 

pull    : ## download
	git pull

push    : ## save
	echo -en "\033[33mWhy this push? \033[0m"; read x; git commit -am "$$x"; git push; git status

~/tmp/%.pdf: %.py  ## make doco: .py ==> .pdf
	mkdir -p ~/tmp
	echo "pdf-ing $@ ... "
	a2ps                 \
		-Br                 \
		--chars-per-line=90 \
		--file-align=fill      \
		--line-numbers=1        \
		--pro=color               \
		--left-title=""            \
		--borders=no             \
	    --left-footer="$<  "               \
	    --right-footer="page %s. of %s#"               \
		--columns 3                 \
		-M letter                     \
	  -o	 $@.ps $<
	ps2pdf $@.ps $@; rm $@.ps
	open $@

~/tmp/%.md : %.py ## make doco: py -> md
	sed -e '1,2d' -e 's/^# //' $^  > $@

~/tmp/%.html : ~/tmp/%.md ## make doco: md -> html
	cp etc/ezr.css ~/tmp
	pandoc --toc -c ezr.css --number-sections  --highlight-style tango -o $@  $^
	sh etc/header.sh $(notdir $(subst .html,,$@)) > tmp
	cat $@ >> tmp
	echo "</body></html>" >> tmp
	mv tmp $@

mqs: ## experiment: mqs
	$(foreach f, $(wildcard data/misc/*.csv),    ./ezr.py -t $f -e mqs  ; )
	$(foreach f, $(wildcard data/process/*.csv), ./ezr.py -t $f -e mqs  ; )
	$(foreach f, $(wildcard data/hpo/*.csv),     ./ezr.py -t $f -e mqs  ; )
	$(foreach f, $(wildcard data/config/*.csv),  ./ezr.py -t $f -e mqs  ; )
