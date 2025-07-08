-include ../Makefile

egs: *.py
	$(foreach f, $^, python3 -B $f --all;)

sways: ../../moot/optimize/[pmhc]*/*.csv
	{ $(foreach f, $^, (python3 dist.py 30 -f $f --sway);) } | tee ~/tmp/$@

