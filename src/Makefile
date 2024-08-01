#.   
#.   .-.
#.  (o o)     go ahead ...
#.  | O \     ... make my day
#.   \   \
#.    `~~~'

#----------------------------------------------------------
SHELL     := bash 
MAKEFLAGS += --warn-undefined-variables
.SILENT:  

Root=$(shell git rev-parse --show-toplevel)

help      :  ## show help
	awk 'BEGIN {FS = ":.*?## "; print "\nmake [WHAT]" } \
			/^[^[:space:]].*##/ {printf "   \033[36m%-18s\033[0m : %s\n", $$1, $$2} ' \
		$(MAKEFILE_LIST)
	awk 'sub(/#\. /,"") { printf "  \033[36m%-20s\033[0m \n", $$0}' Makefile
	
pull    : ## download
	git pull

push    : ## save
	echo -n "> Say, why are you saving? "; read x; git commit -am "$$x"; git push; git status

~/tmp/%.md : %.py  ## make doco: py -> md
	gawk -f inc/py2html.awk $^ > $@

~/tmp/%.html : ~/tmp/%.md ## make doco: md -> html
	cp inc/ezr.css ~/tmp
	- cp -f inc/*.png ~/tmp/
	pandoc --toc -c ezr.css \
         --metadata title="Scripting AI (just the important bits)"  \
			   -s --highlight-style tango -o $@  $^

~/tmp/%.pdf: %.py  ## .py --> .pdf
	mkdir -p ~/tmp
	echo "pdf-ing $@ ... "
	a2ps                 \
		-Br                 \
		--chars-per-line 100  \
		--file-align=fill      \
		--line-numbers=1        \
		--borders=no             \
		--pro=color               \
		--left-title=""            \
		--columns  3                 \
		-M letter                     \
		--footer=""                    \
		--right-footer=""               \
	  -o	 $@.ps $<
	ps2pdf $@.ps $@; rm $@.ps    
	open $@

#----------------------------------------------------------
mqs : ## experiment:  assess mqs policies  
	$(foreach f,$(wildcard ../data/*/*.csv), ./ezr.py -t $f -e smos &; )

#---------------------------------------------------------------------------------
ALLS= $(subst data/config,var/out/alls,$(wildcard data/config/*.csv)) \
      $(subst data/misc,var/out/alls,$(wildcard data/misc/*.csv)) \
      $(subst data/process,var/out/alls,$(wildcard data/process/*.csv)) \
      $(subst data/hpo,var/out/alls,$(wildcard data/hpo/*.csv))

var/out/alls/%.csv : data/config/%.csv  ; echo $<; ./ezr.py -t $<  -R alls | tee $@
var/out/alls/%.csv : data/misc/%.csv    ; echo $<; ./ezr.py -t $<  -R alls | tee $@
var/out/alls/%.csv : data/process/%.csv ; echo $<; ./ezr.py -t $<  -R alls | tee $@
var/out/alls/%.csv : data/hpo/%.csv     ; echo $<; ./ezr.py -t $<  -R alls | tee $@

alls: 
	mkdir -p var/out/alls
	$(MAKE) -j $(ALLS)

SMOS= $(subst data/config,var/out/smos,$(wildcard data/config/*.csv)) \
      $(subst data/misc,var/out/smos,$(wildcard data/misc/*.csv)) \
      $(subst data/process,var/out/smos,$(wildcard data/process/*.csv)) \
      $(subst data/hpo,var/out/smos,$(wildcard data/hpo/*.csv))

var/out/smos/%.csv : data/config/%.csv  ; echo $<; ./ezr.py -t $< -R smos | tee $@
var/out/smos/%.csv : data/misc/%.csv    ; echo $<; ./ezr.py -t $< -R smos | tee $@
var/out/smos/%.csv : data/process/%.csv ; echo $<; ./ezr.py -t $< -R smos | tee $@
var/out/smos/%.csv : data/hpo/%.csv     ; echo $<; ./ezr.py -t $< -R smos | tee $@

smos: 
	mkdir -p var/out/smos
	$(MAKE) -j $(SMOS)


