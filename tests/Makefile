-include ../Makefile

egs: *.py
	$(foreach f, $^, python3 -B $f --all;)

sways: ../../moot/optimize/[hmc]*/*.csv
	{ $(foreach f, $^, (python3 dist.py -B 30 -f $f --sway &);) } | tee ~/tmp/sways.out

