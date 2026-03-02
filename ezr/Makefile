-include  ../Makefile
P=python3 -B 
O=$(HOME)/gits/moot/optimize/misc/auto93.csv
C=$(HOME)/gits/moot/classify/diabetes.csv

R=$(HOME)/gits/moot/text_mining/reading/raw/Hall.csv
T=$(HOME)/gits/moot/text_mining/reading/processed/Hall.csv

fast: class cluster kmeans bayes tree xplain xplainr acquire prep textmine 

slower: localsSlow prepSlow textmineSlow

slowest: XXX

all: fast slower slowest

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

localsSlow:
	$P locals.py --data $O

prep:
	$P prep.py --tokenize $R
	$P prep.py --nostop $R
	$P prep.py --stem $R

prepSlow:
	$P prep.py --tfidf $R

sa:
	$P sa.py --data $O

textmine:
	$P textmine.py --like $T
	$P textmine.py --sweep $T
	$P textmine.py  --data $T

textmineSlow:
	$P textmine.py --active $T

tree:
	$P tree.py --data $O
	$P tree.py --test $O

xplain:
	$P xplain.py --data $O

xplainr:
	$P xplainr.py --data $O
