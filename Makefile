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


~/tmp/%.pdf: %.lua  ## .lua ==> .pdf
	mkdir -p ~/tmp
	echo "pdf-ing $@ ... "
	a2ps                 \
		-Br                 \
		-l 100                 \
		--file-align=fill      \
		--line-numbers=1        \
		--pro=color               \
		--left-title=""            \
		--borders=no             \
		--pretty-print="$(Top)/etc/lua.ssh" \
		--columns 3                  \
		-M letter                     \
		--footer=""                    \
		--right-footer=""               \
	  -o	 $@.ps $<
	ps2pdf $@.ps $@; rm $@.ps
	open $@
