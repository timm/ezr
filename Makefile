SHELL := /bin/bash
GIT_ROOT := $(shell git rev-parse --show-toplevel 2>/dev/null)
CLS    := '\033[H\033[J'
cRESET := '\033[0m'
cRED   := '\033[1;31m'
cGREEN := '\033[1;32m'
cBLUE  := '\033[1;34m'
cYELLOW:= '\033[1;33m'

help: ## show help.
	@gawk  '\
		BEGIN {FS = ":.*?##"; \
           printf "\nUsage:\n  make \033[36m<target>\033[0m\n\ntargets:\n"} \
    /^[~a-z0-9A-Z_%\.\/-]+:.*?##/ { \
           printf("  \033[36m%-15s\033[0m %s\n", $$1, $$2) | "sort " } \
		'$(MAKEFILE_LIST)

sh: ## demo of my shell
	@-echo -e $(CLS)$(cYELLOW); figlet -W -f slant eZR ai; echo -e $(cRESET)
	@-bash --init-file $(GIT_ROOT)/etc/bash.rc -i

ok: $(HOME)/gits/moot ## set up baseline
	@-chmod +x $(GIT_ROOT)/ezr/*.py

$(HOME)/gits/moot:  ## get the data
	mkdir -p $@
	git clone http://tiny.cc/moot $@

push: ## save to cloud
	@read -p "Reason? " msg; git commit -am "$$msg"; git push; git status

clean: ## remove pycadhe
	@-rm -rf `find $(GIT_ROOT) -name  __pycache__`

ghReset:  # GH esotericia. ignore
	git remote set-url origin https://timmenzies@github.com/timmenzies/ez.git

lint: $f.py  ## Lint python file x.py using `make lint f=x`    
	# disable naming, docstring, and formatting rules
	@pylint --disable=C0103,C0104,C0105,C0115,C0116,C0321,C0410 \
	 	      --disable=E0213 \
	 				--disable=R1735 \
	 				--disable=W0106,W0201,W0311 $f.py

~/tmp/%.pdf: %.py  Makefile ## .py ==> .pdf
	@mkdir -p ~/tmp
	@echo "pdf-ing $@ ... "
	@a2ps               \
		-Br               \
		--quiet            \
		--portrait          \
    --lines-per-page=100  \
		--font-size=6 \
		--line-numbers=1      \
		--borders=no           \
		--pro=color             \
		--columns=2              \
		-M letter                 \
		-o - $< | ps2pdf - $@
	@open $@


#------------------------
Class=~/gits/moot/classify/diabetes.csv

NB: ok $(Class); @./nb.py --nb $(Class)

# repo speicif stuff
Car=~/gits/moot/optimize/misc/auto93.csv

SA    : ok $(Car); ./sa.py 1 $(Data) ## simulated annelling
KMEANS: ok $(Car); ./kmeans.py 1 $(Data) ## K-Means
KDTREE: ok $(Car); ./kdtree.py 1 $(Data) ## KD-Tree
FASTMAP: ok $(Car); ./fastmap.py 1 $(Data) ## Fastmap

YS: ## show y shorting
	@./ez.py --ys $(Car) | column -t

TREE: ## show y shorting
	@./ez.py --tree ~/gits/moot/optimize/misc/auto93.csv  

~/tmp/ez_test.log:  ## run ezrtest on many files
	@mkdir -p ~/tmp
	@$(MAKE) todo=test files="$(HOME)/gits/moot/optimize/*/*.csv" run | tee $@ 
	@echo; date
	@python3 -B ez.py --the
	@sort -n $@  | cut -d, -f 1 | fmt

run:
	@time ls -r $(files) \
		| xargs -P 24 -n 1 -I{} sh -c 'python3 -B ez.py --$(todo) "{}"'

#--------------------------
MY=@bash sh/ell

mytree: ## demo of my tree
	$(MY) tree

ls: ## demo of my ls
	$(MY) ls

tmux: ## demo of my tmux
	$(MY) tmux

grep: ## demo of my grep
	$(MY) grep es Makefile

col: ## demo of my col
	printf "name,age,city\nalice,30,raleigh\nbob,25,boston\ncarol,40,denver\n" \
		| bash $(GIT_ROOT)/sh/ell col


