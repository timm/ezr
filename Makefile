# Default is show help; e.g.
#
#    make 
#
# prints the help text.

SHELL     := bash
MAKEFLAGS += --warn-undefined-variables
.SILENT:

Top=$(shell git rev-parse --show-toplevel)
Data=$(Top)/../data

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
	mkdir -p ~/tmp
	cp $(Top)/etc/ezr.css ~/tmp
	pandoc --toc -c ezr.css --number-sections  --highlight-style tango -o $@  $^
	sh $(Top)/etc/header.sh $(notdir $(subst .html,,$@)) > tmp
	cat $@ >> tmp
	echo "</body></html>" >> tmp
	mv tmp $@

mqs: ## experiment: mqs
	$(foreach d, config hpo misc process,        \
    $(foreach f, $(wildcard $(Data)/$d/*.csv),  \
      ls $f; ))
