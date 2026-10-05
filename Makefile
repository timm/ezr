# ==============================================================================
# eZR.ai - Minimal Task Runner
# ==============================================================================

SHELL := /bin/bash
# py3.13 ignores a runtime `sys.dontWriteBytecode = True`; only
# startup settings (this, or -B) actually stop __pycache__.
export PYTHONDONTWRITEBYTECODE := 1
GIT_ROOT := $(shell git rev-parse --show-toplevel 2>/dev/null)
ETC := $(GIT_ROOT)/,

# Only file recipes live here; the verbs (ok push lint sweep
# weave) moved to ./rc, which has positional args and no $$.
# .PHONY so a same-named file cannot shadow a verb -- which
# `docs/` very nearly did.
.PHONY: help update manual

help: ## show help
	@gawk 'BEGIN { FS=":.*?##"; \
	   printf "\nUsage:\n  make \033[36m<target>\033[0m\n\ntargets:\n" } \
	 /^[~a-z0-9A-Z_%.\/-]+:.*?##/ { \
	   printf("  \033[36m%-25s\033[0m %s\n", $$1, $$2) | "sort" }' \
	 $(MAKEFILE_LIST)

# ---- paper ---------------------------------------------------
Font ?= 4.5 # pdf font size
Cols ?= 3   # pdf columns

# a formfeed (ctrl-v ctrl-l in vim) = hard column break
~/tmp/%.pdf: %.py $(MAKEFILE_LIST) ## .py ==> .pdf (Font= Cols=)
	@mkdir -p ~/tmp
	@echo "pdf-ing $@ ... "
	@a2ps -Bj --quiet --landscape --line-numbers=1 \
	   --highlight-level=heavy --borders=no --pro=color \
	   --right-footer="" --left-footer="" \
	   --pretty-print=python --footer="$< :: page %p." \
	   -M letter --center-title="" \
	   --font-size=$(Font) --columns $(Cols) -o - $< \
	 | ps2pdf - $@
	@open $@

# ---- web ---------------------------------------------------
# docs/ is served at timm.github.io/ezr, so the manual gets a url
# you own and can hand out, unlike the claude.ai artifact.
Manual := https://timm.github.io/ezr/manual.html

docs/manual.html: ezr.py ezr_eg.py $(ETC)/manual.py $(ETC)/manual.html ## the five-tab reference
	@python3 -B $(ETC)/manual.py

manual: docs/manual.html ## build it, then open it
	@open $(Manual) 2>/dev/null || echo $(Manual)

docs/ezr.html: ezr.py $(ETC)/lit.py ## literate page via pycco
	@python3 -B $(ETC)/lit.py ezr.py
	@open $@

docs/ezr_eg.html: ezr_eg.py $(ETC)/lit.py ## literate page, demos
	@python3 -B $(ETC)/lit.py ezr_eg.py
	@open $@

# ezr.md is skipped: pycco owns ezr.html.  CHANGELOG and LICENSE
# are documents, not tutorials.
Skip := $(addprefix docs/,CHANGELOG.md LICENSE.md ezr.md)
Tuts := $(patsubst %.md,%.html, \
          $(filter-out $(Skip),$(wildcard docs/*.md)))

docs/%.html: docs/%.md $(ETC)/tut.html ## .md ==> .html tutorial
	@echo "md-ing $@"
	@pandoc -s --syntax-highlighting=none \
	  --template=$(ETC)/tut.html -M pagetitle=$* -o $@ $<

update: docs/ezr.html docs/ezr_eg.html docs/manual.html $(Tuts) ## rebuild html; commit; push
	@read -p "Reason? " msg; git commit -am "$$msg"; git push; git status
