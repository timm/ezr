fred:
	echo  $(wildcard *.out)

d.pl: $(wildcard *.out)
	gawk -f reports.awk *.out  > $@

report:
	swipl -f report.pl  | column -s, -t \
	| gawk '$$1 != old {print ""} {print; old=$$1}'
