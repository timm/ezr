SHELL     := bash
MAKEFLAGS += --warn-undefined-variables
.SILENT:
.ONESHELL:

LOUD = \033[1;34m##
HIGH = \033[1;33m#
SOFT = \033[0m#

Top=$(shell git rev-parse --show-toplevel)
Tmp ?= $(HOME)/tmp 
Data=$(Top)/../moot/optimize

help: ## show help.
	@gawk '\
		BEGIN {FS = ":.*?##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n\nHelp:\n"}  \
    /^[a-z0-9A-Z_%\.\/-]+:.*?##/ {printf("  \033[36m%-15s\033[0m %s\n", $$1, $$2) | "sort" } \
	' $(MAKEFILE_LIST)

pull: ## update from main
	git pull

push: ## commit to main
	echo -en "$(LOUD)Why this push? $(SOFT)" 
	read x ; git commit -am "$$x" ;  git push
	git status

sh: ## run custom shell
	clear; tput setaf 3; cat $(Top)/etc/hi.txt; tput sgr0
	sh $(Top)/etc/ell

setup: ## initial setup - clone moot data
	[ -d $(Data) ] || git clone http://github.com/timm/moot $(Top)/../moot

install: ## install in development mode (when ready)
	pip install -e .

clean:  ## find and delete any __pycache__ dirs
	files="$$(find $(Top) -name __pycache__ -type d)"; \
	for f in $$files; do rm -rf "$$f"; done

~/tmp/dist.log:  ## run ezrtest on many files
	$(MAKE) todo=dist files="$(Top)/../moot/optimize/*/*.csv" run | tee $@ 

run:
	@mkdir -p ~/tmp
	time ls -r $(files) \
	  | xargs -P 24 -n 1 -I{} sh -c 'cd $(Top)/ezr; python3 -B ezrtest.py -f "{}" --$(todo)'

eg1: ## run init tests
	cd $(Top)/ezr; python3 -B ezrtest.py -f $(Data)/misc/auto93.csv --tree

eg2: ## run init tests
	cd $(Top)/ezr; python3 -B ezrtest.py -f $(Data)/misc/auto93.csv --all
