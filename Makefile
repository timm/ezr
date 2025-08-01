SHELL     := bash
MAKEFLAGS += --warn-undefined-variables
.SILENT:

LOUD = \033[1;34m#
HIGH = \033[1;33m#
SOFT = \033[0m#

Top=$(shell git rev-parse --show-toplevel)

help:  ## show help
	gawk -f $(Top)/etc/help.awk $(MAKEFILE_LIST) 

pull: ## update from main
	git pull

push: ## commit to main
	- echo -en "$(LOUD)Why this push? $(SOFT)" 
	- read x ; git commit -am "$$x" ;  git push
	- git status

sh: ## run my shell
	sh $(Top)/ell

lint: ## lint all python in this directory
	export PYTHONPATH="..:$$PYTHONPATH"; \
	pylint --disable=W0311,C0303,C0116,C0321,C0103 \
		    --disable=C0410,C0115,C3001,R0903,E1101 \
		    --disable=E701,W0108,W0106,W0718,W0201  *.py

docs/%.html : %.py
	pdoc -o $(Top)/docs --logo ezr.png $^ 

~/tmp/%.pdf: %.py ## pdf print Python
	echo "making $@"
	a2ps                     \
  --file-align=virtual      \
	--line-numbers=1           \
	--pro=color                 \
	--pretty=python              \
	--chars-per-line=95           \
	--left-title=""                \
	--borders=no                    \
  --right-footer='page %s. of %s#' \
	--portrait                        \
	--columns 2                        \
	-M letter                           \
	-o - $^ | ps2pdf - $@
	open $@

#------------------------------

lite20:
	mkdir -p ~/tmp
	time ls -r $(Top)/../moot/optimize/*/*.csv \
	  | xargs -P 32 -n 1 -I{} sh -c 'python3 -B ezr.py -f "{}" --likely' \
	  | tee ~/tmp/$@.log
	@echo "now call make lite20report"

lite20z:
	cat ~/tmp/lite20.log  \
		| awk '{print $$1, $$1-$$2, $$1-$$3, $$1-$$4}' \
		| sort -n \
		| awk 'BEGIN {print "klass diff_xplore diff_xploit diff_adapt"} \
		             {print} \
		             {x+=$$2; X+=$$3; a+=$$4} \
					 END   {print x/NR,X/NR,a/NR> "/dev/stderr"}' \
		| python3 $(Top)/etc/lite20z.py

