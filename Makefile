# Default is show help; e.g.
#
#    make 
#
# prints the help text.

SHELL     := bash
MAKEFLAGS += --warn-undefined-variables
.SILENT:

Top=$(shell git rev-parse --show-toplevel)
Data ?= $(Top)/data/optimize
Tmp  ?= $(HOME)/tmp

help      :  ## show help
	gawk -f $(Top)/etc/help.awk $(MAKEFILE_LIST) 

pull    : ## download
	git pull

push    : ## save
	echo -en "\033[33mWhy this push? \033[0m"; read x; git commit -am "$$x"; git push; git status

$(Top)/docs/%.pdf: %.py  ## make doco: .py ==> .pdf
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

docs/%.html : docs/%.md etc/b4.html docs/ezr.css Makefile ## make doco: md -> html
	echo "$< ... "
	pandoc -s  -f markdown --number-sections --toc  --toc-depth=5 \
					-B etc/b4.html --mathjax \
  		     --css ezr.css --highlight-style tango \
	  			 -o $@  $<

docs/%.html : %.py etc/py2html.awk etc/b4.html docs/ezr.css Makefile ## make doco: md -> html
	echo "$< ... "
	gawk -f etc/py2html.awk $< \
	| pandoc -s  -f markdown --number-sections --toc --toc-depth=5 \
					-B etc/b4.html --mathjax \
  		     --css ezr.css --highlight-style tango \
					 --metadata title="$<" \
	  			 -o $@ 

# another commaned
Out=$(HOME)/tmp
Act ?= _mqs
Root=$(shell git rev-parse --show-toplevel)

acts: ## experiment: mqs
	mkdir -p $(Out)
	$(MAKE) actb4 > $(Tmp)/$(Act).sh
	bash $(Tmp)/$(Act).sh
	bash $(Out)/$(Act)/run_all.sh
	cd $(Out)/$(Act); bash $(Root)/etc/rq.sh | column -s, -t | tee $(Out)/$(Act).txt

actb4: ## experiment: mqs
	mkdir -p $(Out)/$(Act)
	@echo "#!/bin/bash" > $(Out)/$(Act)/run_all.sh
	@$(foreach d, config hpo misc process, \
		$(foreach f, $(wildcard $(Data)/$d/*.csv), \
			echo "python3 $(PWD)/ezr.py -t $f -e $(Act) | tee $(Out)/$(Act)/$(shell basename $f) &" >> $(Out)/$(Act)/run_all.sh;))
	@echo "wait" >> $(Out)/$(Act)/run_all.sh
	@chmod +x $(Out)/$(Act)/run_all.sh

fred:
	echo $x
