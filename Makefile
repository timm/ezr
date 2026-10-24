# research-question targets for ezr/ezr0 (see rq.py, rq.md)
SHELL := /bin/bash
PY    := pypy3.12
DIR   := $(HOME)/gits/moot/optimize
TMP   := $(HOME)/tmp
J     := $(shell sysctl -n hw.ncpu 2>/dev/null || nproc)

help: ## list targets
	@grep -E '^[a-z0-9]+:.*##' Makefile | \
	  awk -F':.*## ' '{printf "  %-6s %s\n", $$1, $$2}'

rq00: $(TMP)/rq00.txt ## per-dataset mean wins, ezr0 (sorted, wrapped)
	@cat $<

rq0: $(TMP)/rq0.txt ## per-dataset mean wins, ezr
	@cat $<

rq1: $(TMP)/rq1_ezr0.txt $(TMP)/rq1_ezr.txt ## six figures from 25k paired runs per arm
	python3 rq.py -plot $(TMP)/rq1_ezr0.txt -png docs/rq.png
	python3 rq.py -plot $(TMP)/rq1_ezr.txt -png docs/rq_ezr.png
	python3 rq.py -plot $(TMP)/rq1_ezr.txt -diff $(TMP)/rq1_ezr0.txt \
	  -png docs/rq_diff.png
	python3 rq.py -plot $(TMP)/rq1_ezr0.txt -sd 1 -png docs/rq_sd.png
	python3 rq.py -plot $(TMP)/rq1_ezr.txt -sd 1 -png docs/rq_ezr_sd.png
	python3 rq.py -plot $(TMP)/rq1_ezr0.txt -sd 2 -png docs/rq_se.png

$(TMP)/rq00.txt: rq.py ezr0.py
	@mkdir -p $(TMP)
	find $(DIR) -name '*.csv' | \
	  xargs -P $(J) -I@ $(PY) rq.py -rq0 1 -dir @ | \
	  cut -d: -f1 | sort -n | fmt -60 | tee $@

$(TMP)/rq0.txt: rq.py ezr0.py ezr.py
	@mkdir -p $(TMP)
	find $(DIR) -name '*.csv' | \
	  xargs -P $(J) -I@ $(PY) rq.py -rq0 1 -alg ezr -dir @ | \
	  cut -d: -f1 | sort -n | fmt -60 | tee $@

$(TMP)/rq1_ezr0.txt: rq.py ezr0.py
	@mkdir -p $(TMP)
	seq 10 | xargs -P 10 -I@ sh -c \
	  '$(PY) rq.py -alg ezr0 -runs 2500 -Seed @ > $(TMP)/rq1_ezr0_@.txt'
	cat $(TMP)/rq1_ezr0_*.txt > $@

rq2: $(TMP)/rq2_ezr0_rand.txt $(TMP)/rq2_ezr_ezr0.txt ## sorted-delta charts: ezr0 vs rand, ezr vs ezr0
	python3 rq.py -plot2 $(TMP)/rq2_ezr0_rand.txt \
	  -rq2 ezr0,rand -png docs/rq2_ezr0_rand.png
	python3 rq.py -plot2 $(TMP)/rq2_ezr_ezr0.txt \
	  -rq2 ezr,ezr0 -png docs/rq2_ezr_ezr0.png

$(TMP)/rq2_ezr0_rand.txt: rq.py ezr0.py
	@mkdir -p $(TMP)
	find $(DIR) -name '*.csv' | \
	  xargs -P $(J) -I@ $(PY) rq.py -rq2 ezr0,rand -dir @ > $@

$(TMP)/rq2_ezr_ezr0.txt: rq.py ezr0.py ezr.py
	@mkdir -p $(TMP)
	find $(DIR) -name '*.csv' | \
	  xargs -P $(J) -I@ $(PY) rq.py -rq2 ezr,ezr0 -dir @ > $@

$(TMP)/rq1_ezr.txt: rq.py ezr0.py ezr.py
	@mkdir -p $(TMP)
	seq 10 | xargs -P 10 -I@ sh -c \
	  '$(PY) rq.py -alg ezr  -runs 2500 -Seed @ > $(TMP)/rq1_ezr_@.txt'
	cat $(TMP)/rq1_ezr_*.txt > $@

.PHONY: rq00 rq0 rq1 rq2 help

#-- percent-rank sweep (min.py --rank) --------------------------------
PY2    := $(shell command -v pypy3.12 || command -v pypy3 || echo python3)
RANKN  := 20
RANKS  := 20

rank: ## --rank over $(RANKN) optimize sets x $(RANKS) seeds, $(J) cores
	@find $(DIR) -name '*.csv' | sort | awk -v n=$(RANKN) \
	   '{a[NR]=$$0} END{for(i=0;i<n;i++) print a[1+int(i*(NR-1)/(n-1))]}' | \
	 xargs -P $(J) -n1 sh -c 'for s in $$(seq 1 $(RANKS)); do \
	    $(PY2) min.py -File "$$0" -Seed $$s -Stop 37 -Check  5 --rank; \
	    $(PY2) min.py -File "$$0" -Seed $$s -Stop 25 -Check 20 --rank; \
	  done'

#-- ezr trees vs LightGBM (etc/cmp_fft_lgbm.py) -----------------------
REG  := $(HOME)/gits/moot/regression

fft: ## ezr vs lgbm over moot/regression, $(J) cores
	@find $(REG) -name '*.csv' | sort | tr '\n' '\0' | \
	 xargs -0 -P $(J) -n1 sh -c \
	   'SEEDS=20 RAW=1 PRUNE=any BUDGET=256 \
	    python3 etc/cmp_fft_lgbm.py "$$0"' 2>/dev/null | \
	 python3 etc/cmp_fft_lgbm.py --stats

fig: ## redraw docs/ezr_vs_lgbm.png from the cached run
	@python3 etc/plot_ezr_lgbm.py etc/big50.tsv docs/ezr_vs_lgbm.png

#-- RQ4: regression (see rq.md) ---------------------------------------
rq4: ## redraw both RQ4 figures from the cached runs
	@python3 etc/plot_regress.py

frugal: ## attic.py --fft over moot/regression -> etc/frugal56.tsv
	@{ echo -e "data\tvariants\tfrugal_train\tfrugal_test\ttree0_train\ttree0_test"; \
	   ls $(REG)/*.csv | xargs -P $(J) -I@ python3 etc/frugal1.py @ \
	   2>/dev/null | sort; } > etc/frugal56.tsv
	@wc -l < etc/frugal56.tsv
