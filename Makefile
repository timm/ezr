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

%.lua : %.md
	gawk 'BEGIN            { code=0 }  \
		    sub(/^```.*/,"") { code = 1 - code } \
			                   { print (code ? "" : "-- ") $$0 }' $^ > $@
	luac -p $@
	
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

~/tmp/%.pdf: %.lua  ## male doco: .lua ==> .pdf
	mkdir -p ~/tmp
	echo "pdf-ing $@ ... "
	a2ps                 \
		-Br                 \
		--lines-per-page=100 \
		--file-align=fill      \
		--line-numbers=1        \
		--pro=color               \
		--left-title=""            \
		--borders=no             \
		--pretty-print="$(Top)/etc/lua.ssh" \
	    --left-footer="$<  "               \
	    --right-footer="page %s. of %s#"               \
		--columns 2                  \
		-M letter                     \
	  -o	 $@.ps $<
	ps2pdf $@.ps $@; rm $@.ps
	open $@

~/tmp/%.md : %.py ## make doco: py -> md
	gawk -f etc/py2html.awk $^ > $@

~/tmp/%.html : ~/tmp/%.md ## make doco: md -> html
	cp etc/ezr.css ~/tmp
	pandoc --toc -c ezr.css \
         --metadata title="Scripting AI (just the important bits)"  \
			   -s --highlight-style tango -o $@  $^


