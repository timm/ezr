-include  ../Makefile
P=python3 -B 
O=$(HOME)/gits/moot/optimize/misc/auto93.csv
C=$(HOME)/gits/moot/classify/diabetes.csv

tests: class cluster kmeans bayes tree xplain xplainr acquire locals

acquire:
	$P acquire.py --compare $O

bayes:
	$P bayes.py __data $C

cluster:
	$P cluster.py --data $O

class:
	$P ez.py --the
	$P ez.py --csv $O
	$P ez.py --data $O
	$P ez.py --disty $O
	$P ez.py --addsub $O
	$P ez.py --like $O

kmeans:
	$P kmeans.py --data $C

locals:
	$P locals.py --data $O

sa:
	$P sa.py --data $O

tree:
	$P tree.py --data $O
	$P tree.py --test $O

xplain:
	$P xplain.py --data $O

xplainr:
	$P xplainr.py --data $O
