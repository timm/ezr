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

push2pypi: ## push to PyPi
	pip install build twine
	python3 -B -m build
	twine upload dist/*
	rm -rf dist build *.egg-info

pyclean: ## remove python temporaries
	@find $(GIT_ROOT) -type d \( -name __pycache__ -o -name .pytest_cache -o -name "*.egg-info" \) -exec rm -rf {} +

sh: ## demo of my shell
	@-echo -e $(CLS)$(cYELLOW); figlet -W -f slant eZR.ai; echo -e $(cRESET)
	@-bash --init-file $(ETC)/bash.rc -i

install: ok ## install related repos to $HOME/gits

ok: $(HOME)/gits/moot ## set up baseline
	@-chmod +x $(GIT_ROOT)/*.py

$(HOME)/gits/moot: ## get the data
	mkdir -p $(dir $@)
	[ -d $@/.git ] || git clone http://tiny.cc/moot $@

push: ## save to cloud
	@read -p "Reason? " msg; git commit -am "$$msg"; git push; git status

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
CSVS = ls -r $(HOME)/gits/moot/optimize/*/*.csv | xargs -P 24 -I{} sh -c

~/tmp/ezr_acq.log: ok ## run ez_acq tests
	@mkdir -p ~/tmp
	@time $(CSVS) 'python3 -B ezeg.py --test "{}"' | tee $@
	@sort -n $@ | cut -d, -f 1 | fmt -80

~/tmp/runs.log: ## run random test loop
	bash $(ETC)/runs.sh > $@

Html := $(GIT_ROOT)/docs

docs: $(Html)/ezr.html $(Html)/ezr.pdf

$(Html)/%.html: %.py
	@mkdir -p $(Html)
	@awk -f $(ETC)/py.awk $< > $(Html)/$<
	@cd $(Html) && pycco -d . $<
	@cat $(ETC)/custom.css >> $(Html)/pycco.css
	@awk -v HEADER=$(ETC)/header.html -f $(ETC)/html.awk $@ > $@.tmp && mv $@.tmp $@
	@rm $(Html)/$<
