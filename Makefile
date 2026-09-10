# ==============================================================================
# eZR.ai - Minimal Task Runner
# ==============================================================================

SHELL := /bin/bash
GIT_ROOT := $(shell git rev-parse --show-toplevel 2>/dev/null)
ETC := $(GIT_ROOT)/etc
RUN_TEST := python3 -B ezr.py --all

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
	@mkdir -p $(dir $@)
	@[ -d $@/.git ] || git clone http://tiny.cc/moot $@

push: ## save to cloud
	@read -p "Reason? " msg; git commit -am "$$msg"; git push; git status

ghReset: # GH esotericia
	git remote set-url origin https://timmenzies@github.com/timmenzies/ez.git

lint: $f.py ## Lint python file x.py using `make lint f=x`
	@pylint --rcfile=$(ETC)/pylintrc $f.py

Font ?= 4.5 # pdf font size
Cols ?= 3   # pdf columns
LPC  ?= 120 # lines per pdf column; packs formfeed sections

~/tmp/%.pdf: %.py $(MAKEFILE_LIST) ## .py ==> .pdf (Font= Cols= LPC=)
	@mkdir -p ~/tmp
	@echo "pdf-ing $@ ... "
	@a2ps -Bj --quiet --landscape --line-numbers=1 \
	   --highlight-level=heavy --borders=no --pro=color \
	   --right-footer="" --left-footer="" \
	   --pretty-print=python --footer="$< :: page %p." \
	   -M letter --center-title="" \
	   --font-size=$(Font) --columns $(Cols) -o - \
	   <(awk -v C=$(LPC) 'BEGIN{RS="\f"; ORS=""} \
	      {n=split($$0,L,"\n")-1; \
	       if($$0==""){printf "\f"; pos=0; next} \
	       if(NR>1 && pos>0 && pos+n>C){printf "\f"; pos=0} \
	       printf "%s",$$0; pos+=n}' $<) \
	 | ps2pdf - $@
	@open $@

stats: ## generate stats
	@bash $(ETC)/stats.sh $(HOME)/gits/moot/optimize

# Test runner targets
CSVS = ls $(HOME)/gits/moot/optimize/*/*.csv | sort -R | xargs -P 24 -I{} sh -c

~/tmp/ezr_acq.log: ok ## run ez_acq tests
	@mkdir -p ~/tmp
	@$(CSVS) 'python3 -B ezr.py -File "{}" --holdout' | tee $@
	@cut -d \  -f 2 $@ | sort -n | fmt -71

runs: ## run random test loop
	@mkdir -p ~/tmp
	bash $(ETC)/runs.sh | tee ~/tmp/runs.log

Html := $(GIT_ROOT)/docs

docs: $(Html)/ezr.html $(Html)/ezr_eg.html ~/tmp/ezr.pdf

$(Html)/%.html: %.py
	@mkdir -p $(Html)
	@awk -f $(ETC)/py.awk $< > $(Html)/$<
	@cd $(Html) && pycco -d . $<
	@cat $(ETC)/custom.css >> $(Html)/pycco.css
	@awk -v HEADER=$(ETC)/header.html -f $(ETC)/html.awk $@ > $@.tmp && mv $@.tmp $@
	@rm $(Html)/$<

tosem: ## rebuild docs/tosem10.pdf from ezr.py sections
	@gawk 'BEGIN{RS="\f"} {sub(/^\n/,""); \
	   printf "%s",$$0 > sprintf("docs/sec%02d.py",NR-1)}' ezr.py
	@cd docs && \
	  pdflatex -shell-escape -interaction=batchmode tosem10.tex >/dev/null 2>&1 && \
	  pdflatex -shell-escape -interaction=batchmode tosem10.tex >/dev/null 2>&1
	@pdfinfo docs/tosem10.pdf | grep Pages
	@open docs/tosem10.pdf 2>/dev/null || true

pushpdf: tosem ## rebuild paper, commit it, push
	@git add docs/sec*.py docs/tosem10.pdf docs/tosem10.tex
	@git commit -m "rebuild tosem pdf"; git push

docs/ezr.html: ezr.py etc/lit.py ## literate page via pycco
	@python3 -B etc/lit.py ezr.py
	@open $@

docs/ezr_eg.html: ezr_eg.py etc/lit.py ## literate page, demos
	@python3 -B etc/lit.py ezr_eg.py
	@open $@

Tuts := $(patsubst %.md,%.html,$(wildcard $(Html)/*.md))

$(Html)/%.html: $(Html)/%.md $(ETC)/tut.html ## .md ==> .html tutorial
	@echo "md-ing $@"
	@pandoc -s --syntax-highlighting=none --template=$(ETC)/tut.html -M pagetitle=$* -o $@ $<

update: docs/ezr.html $(Html)/ezr_eg.html $(Tuts) ## rebuild all html; commit; push
	@read -p "Reason? " msg; git commit -am "$$msg"; git push; git status

comments: ## claude adds missing comments; review diff, then "make update"
	claude -p "$$(cat $(ETC)/prompt.txt)"
	@git diff --stat
