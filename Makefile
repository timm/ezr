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

python313 : ## install cool stuff
    # everyone needs an onstall scriot
	sudo apt -y -qq update  
	sudo apt -y -qq upgrade  
	sudo apt -y -qq install software-properties-common  
	sudo add-apt-repository ppa:deadsnakes/ppa  -y   
	sudo apt -y -qq update  
	sudo apt -y -qq install python3.13 

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
  		     --css ezr.css --highlight-style monochrome \
					 --metadata title="$<" \
	  			 -o $@ 

# another commaned
Out=$(HOME)/tmp
Act ?= _mqs
acts: ## experiment: mqs
	mkdir -p ~/tmp
	$(MAKE)  actb4  > $(Tmp)/$(Act).sh
	bash $(Tmp)/$(Act).sh

actb4: ## experiment: mqs
	echo "mkdir -p $(Out)/$(Act)"
	echo "rm $(Out)/$(Act)/*"
	$(foreach d, config hpo misc process,         \
		$(foreach f, $(wildcard $(Data)/$d/*.csv),   \
				echo "python3 $(PWD)/ezr.py  -D -t $f -e $(Act)  | tee $(Out)/$(Act)/$(shell basename $f) & "; ))

fred:
	echo $x
