# research-question targets for ezr/ezr0 (see rq.py, rq.md)
SHELL := /bin/bash
PY    := pypy3.12
DIR   := $(HOME)/gits/moot/optimize
J     := $(shell sysctl -n hw.ncpu 2>/dev/null || nproc)

rq00: ## per-dataset mean wins, ezr0 (sorted, wrapped)
	find $(DIR) -name '*.csv' | \
	  xargs -P $(J) -I@ $(PY) rq.py -rq0 1 -dir @ | \
	  cut -d: -f1 | sort -n | fmt -60

rq0: ## per-dataset mean wins, ezr
	find $(DIR) -name '*.csv' | \
	  xargs -P $(J) -I@ $(PY) rq.py -rq0 1 -alg ezr -dir @ | \
	  cut -d: -f1 | sort -n | fmt -60

rq1: ## 25k paired runs per arm, then the six figures
	seq 10 | xargs -P 10 -I@ sh -c \
	  '$(PY) rq.py -alg ezr0 -runs 2500 -Seed @ > /tmp/rq0_@.txt'
	seq 10 | xargs -P 10 -I@ sh -c \
	  '$(PY) rq.py -alg ezr  -runs 2500 -Seed @ > /tmp/rq1_@.txt'
	cat /tmp/rq0_*.txt > /tmp/rq0.txt
	cat /tmp/rq1_*.txt > /tmp/rq1.txt
	python3 rq.py -plot /tmp/rq0.txt -png docs/rq.png
	python3 rq.py -plot /tmp/rq1.txt -png docs/rq_ezr.png
	python3 rq.py -plot /tmp/rq1.txt -diff /tmp/rq0.txt \
	  -png docs/rq_diff.png
	python3 rq.py -plot /tmp/rq0.txt -sd 1 -png docs/rq_sd.png
	python3 rq.py -plot /tmp/rq1.txt -sd 1 -png docs/rq_ezr_sd.png
	python3 rq.py -plot /tmp/rq0.txt -sd 2 -png docs/rq_se.png

help: ## list targets
	@grep -E '^[a-z0-9]+:.*##' Makefile | \
	  awk -F':.*## ' '{printf "  %-6s %s\n", $$1, $$2}'

.PHONY: rq00 rq0 rq1 help
