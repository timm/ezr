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

md:
	gawk -F, -f $(Top)/etc/xpand.awk ezr.py ezr.md


%.md: ## include source code
	gawk -f $(Top)/etc/include.awk $< > .tmp && mv .tmp $@

~/tmp/%.pdf: %.py
	echo "pdf-ing $@ ... "
	a2ps                          \
		--file-align=virtual         \
		--line-numbers=1              \
		--pro=color                    \
		--pretty=python \
		--chars-per-line=70 \
		--left-title=""                 \
		--borders=no                     \
	  --right-footer="page %s. of %s#"  \
		--portrait                        \
		--columns 2                          \
		-M letter                             \
		-o - $^ | ps2pdf - $@
	open $@

#----------------------------------------------------------------
# Local tricks

T=cd $(Top)/tests; python3 -B

all: o csv the cols num sym data addSub dist kpp fmap tree

o      :; $T eg_lib.py   --o       ## demo simple classes
csv    :; $T eg_lib.py   --csv     ## demo reading csv files
the    :; $T eg_lib.py   --the     ## demo showing config
cols   :; $T eg_data.py  --cols    ## demo csv files --> Data
num    :; $T eg_query.py --num     ## demo Nums
sym    :; $T eg_query.py --sym     ## demo Syms
data   :; $T eg_query.py --data    ## demo Data
addSub :; $T eg_query.py --addSub  ## demo incremetal adds, deletes
dist   :; $T eg_dist.py  --dist    ## demo incremetal dist
kpp    :; $T eg_dist.py  --kpp     ## demo diversity sampling with kpp
fmap   :; $T eg_landscape.py --fastmap ## demo fastmap
tree   :; $T eg_tree.py --tree     ## tree demo
rank   :; $T eg_stats.py --rank
rank2  :; $T eg_stats.py --rank2

stats: $(Top)/../moot/optimize/[hmpbc]*/*.csv
	$(foreach f, $^, gawk -f $(Top)/etc/stats.awk $f;)
