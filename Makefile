# ater much recursive make file nonsense, i finally went with
# one entralized make

#----------------------------------------------------------------
# General tricks

SHELL     := bash
MAKEFLAGS += --warn-undefined-variables
.SILENT:

SHOUT = \033[1;34m#
QUIET = \033[0m#

Top=$(shell git rev-parse --show-toplevel)

help:  ## show help
	gawk 'BEGIN { FS   = ":.*## "; print "\nmake [WHAT]" }            \
	      /^[^ \t].*##/ {                                              \
	        printf("   $(SHOUT)%-10s$(QUIET) %s\n", $$1, $$2) | "sort"} \
	' $(MAKEFILE_LIST)

pull: ## update from main
	git pull

push: ## commit to main
	- echo -en "$(SHOUT)Why this push? $(QUIET)" 
	- read x ; git commit -am "$$x" ;  git push
	- git status

sh: ## run my shell
	Top=$(Top) bash --init-file $(Top)/etc/init.sh -i

%.md: ## inlude 
	gawk '\
		in==0 && match($$0, /^```[a-zA-Z]+\s+\S+/) {                 \
			print; split($$0,f," ");                                    \
			while ((getline < f[2]) > 0) print; close(f[2]); in=1; next }\
		in && /^```/ { print; in=0; next }\
		in { next }\
		1 ' $< > .tmp && mv .tmp $@

#----------------------------------------------------------------
# Local tricks

T=cd $(Top)/tests; python3 -B

all: o csv cols

o    :; $T lib.py o   ## demo simple classes
csv  :; $T lib.py csv ## demo reading csv files
cols :; $T data.py cols ## demo csv files --> Data
	
