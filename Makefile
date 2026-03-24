# ==============================================================================
# eZR.ai - Minimal Task Runner
# ==============================================================================

SHELL := /bin/bash
GIT_ROOT := $(shell git rev-parse --show-toplevel 2>/dev/null)
ETC := $(GIT_ROOT)/etc
RUN_TEST := bash $(ETC)/run_tests.sh

CLS    := '\033[H\033[J'
cRESET := '\033[0m'
cYELLOW:= '\033[1;33m'

help: ## show help
	@gawk -f $(ETC)/help.awk $(MAKEFILE_LIST) 

sh: ## demo of my shell
	@-echo -e $(CLS)$(cYELLOW); figlet -W -f slant eZR.ai; echo -e $(cRESET)
	@-bash --init-file $(ETC)/bash.rc -i

install: ok ## install related repos to $HOME/gits

ok: $(HOME)/gits/moot ## set up baseline
	@-chmod +x $(GIT_ROOT)/ezr/*.py

$(HOME)/gits/moot: ## get the data
	mkdir -p $@
	git clone http://tiny.cc/moot $@

push: ## save to cloud
	@read -p "Reason? " msg; git commit -am "$$msg"; git push; git status

clean: ## remove pycache
	@-find $(GIT_ROOT) -name __pycache__ -exec rm -rf {} +

ghReset: # GH esotericia
	git remote set-url origin https://timmenzies@github.com/timmenzies/ez.git


lint: $f.py ## Lint python file x.py using `make lint f=x`
	@pylint --rcfile=$(ETC)/pylintrc $f.py

~/tmp/%.pdf: %.py $(MAKEFILE_LIST) ## .py ==> .pdf
	@mkdir -p ~/tmp
	@echo "pdf-ing $@ ... "
	@a2ps -Br --quiet --portrait --chars-per-line=90 --line-numbers=1  \
	          --borders=no --pro=color --columns=2 -M letter -o - $< \
						| ps2pdf - $@
	@open $@

stats: ## generate stats
	@bash $(ETC)/stats.sh $(HOME)/gits/moot/optimize

# Test runner targets
~/tmp/ez_acq.log: ok ## run ez_acq tests
	@$(RUN_TEST) $@ acquire_class.py "-B $(B) --compare"
	@sort -n $@ | cut -d, -f 1 | fmt

run: ## generic run target
	@$(RUN_TEST) /dev/null tree.py "-B $(B) --$(todo)" "$(files)"
	@sort -n $@ | cut -d, -f 1 | fmt -85

~/tmp/runs.log: ## run random test loop
	@bash $(ETC)/runs.sh > $@
