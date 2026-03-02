-include  ../Makefile
Py=python3 -B 
Opt=$(HOME)/gits/moot/optimize/misc/auto93.csv
Klas=$(HOME)/gits/moot/classify/diabetes.csv

Raw=$(HOME)/gits/moot/text_mining/reading/raw/Hall.csv
Cooked=$(HOME)/gits/moot/text_mining/reading/processed/Hall.csv

fast: class cluster kmeans bayes tree xplain xplainr acquire prep textmine 

slower: localsSlow prepSlow textmineSlow

slowest: 
	@echo "see xxxx "

all: fast slower slowest

acquire:
	$(Py) acquire.py --compare $(Opt)

bayes:
	$(Py) bayes.py __data $(Klas)

cluster:
	$(Py) cluster.py --data $(Opt)

class:
	$(Py) ez.py --the
	$(Py) ez.py --csv $(Opt)
	$(Py) ez.py --data $(Opt)
	$(Py) ez.py --disty $(Opt)
	$(Py) ez.py --addsub $(Opt)
	$(Py) ez.py --like $(Opt)

kmeans:
	$(Py) kmeans.py --data $(Klas)

localsSlow:
	$(Py) locals.py --data $(Opt)

prep:
	$(Py) prep.py --tokenize $(Raw)
	$(Py) prep.py --nostop $(Raw)
	$(Py) prep.py --stem $(Raw)

prepSlow:
	$(Py) prep.py --tfidf $(Raw)

sa:
	$(Py) sa.py --data $(Opt)

textmine:
	$(Py) textmine.py --like $(Cooked)
	$(Py) textmine.py --sweep $(Cooked)
	$(Py) textmine.py  --data $(Cooked)

textmineSlow:
	$(Py) textmine.py --active $(Cooked)

tree:
	$(Py) tree.py --data $(Opt)
	$(Py) tree.py --test $(Opt)

xplain:
	$(Py) xplain.py --data $(Opt)

xplainr:
	$(Py) xplainr.py --data $(Opt)
