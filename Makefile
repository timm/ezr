HOME       = <a href="http://github.com/timm/ezr">home</a>
CONTRIBUTE = <a href="https://github.com/timm/ezr/blob/main/CONRIBUTE.md">contribute</a>
LICENSE    = <a href="https://github.com/timm/ezr/blob/main/LICENSE.md">license</a>
ISSUES     = <a href="http://github.com/timm/ezr/issues">issues</a>

MENU       = $(HOME) | $(CONTRIBUTE) | $(ISSUES) | $(LICENSE)

IMAGE      = <img src="img/ezr.png" align=right width=150>
CSS        = p { text-align: right;} pre,code {font-size: x-small;}

#----------------------------------------------------------
SHELL     := bash 
MAKEFLAGS += --warn-undefined-variables
.SILENT:  

Root=$(shell git rev-parse --show-toplevel)

help      :  ## show help
	awk 'BEGIN {FS = ":.*?## "; print "\nmake [WHAT]" } \
			/^[^[:space:]].*##/ {printf "   \033[36m%-20s\033[0m : %s\n", $$1, $$2} \
			' $(MAKEFILE_LIST)

saved    : ## save
	git commit -am saved; git push; git status

name:
	read -p "word> " w; figlet -f mini -W $$w  | gawk '$$0 {print "#        "$$0}' |pbcopy

install   : ## install as  a local python package
	pip install -e  . --break-system-packages 

docs/index.html :docs/ezr.html ## install our html doco
	cp $< $@

docs/%.html : %.py
	gawk -f etc/ab2ba.awk $< > docs/$<
	cd docs; pycco -d . $<; rm $<
	echo "$(CSS)" >> docs/pycco.css
	sed -i '' 's?<h1>?$(MENU)<hr>$(IMAGE)&?' $@
	@open $@

~/tmp/%.pdf: %.py  ## .py ==> .pdf
	mkdir -p $(dirname $@)
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

OUTS= $(subst data/config,var/out,$(wildcard data/config/*.csv)) \
      $(subst data/misc,var/out,$(wildcard data/misc/*.csv)) \
      $(subst data/process,var/out,$(wildcard data/process/*.csv)) \
      $(subst data/hpo,var/out,$(wildcard data/hpo/*.csv))

var/out/%.csv : data/config/%.csv  ; src/ezr.py -f $< -R smo20 | tee $@
var/out/%.csv : data/misc/%.csv    ; src/ezr.py -f $< -R smo20 | tee $@
var/out/%.csv : data/process/%.csv ; src/ezr.py -f $< -R smo20 | tee $@
var/out/%.csv : data/hpo/%.csv     ; src/ezr.py -f $< -R smo20 | tee $@

eg1: 
	$(MAKE) -j 8 $(OUTS)
