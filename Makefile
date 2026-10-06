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

$(TMP)/rq1_ezr.txt: rq.py ezr0.py ezr.py
	@mkdir -p $(TMP)
	seq 10 | xargs -P 10 -I@ sh -c \
	  '$(PY) rq.py -alg ezr  -runs 2500 -Seed @ > $(TMP)/rq1_ezr_@.txt'
	cat $(TMP)/rq1_ezr_*.txt > $@

.PHONY: rq00 rq0 rq1 help
