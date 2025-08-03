SHELL     := bash
MAKEFLAGS += --warn-undefined-variables
.SILENT:

Top=$(shell git rev-parse --show-toplevel)

~/tmp/lite.log: 
	$(MAKE) files="$(Top)/../moot/optimize/*/*.csv" lite | tee $@ ; \
  gawk '{print $4}' $@ | sort -n | gnuplot -p -e "plot '<cat' with linespoints"

lite:
	@mkdir -p ~/tmp
	echo 11
	time ls -r $(files) \
	  | xargs -P 32 -n 1 -I{} sh -c 'python3 -B lite.py -B 32 -f "{}" --near'

