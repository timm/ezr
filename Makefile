#.   
#.   .-.
#.  (o o)     go ahead ...
#.  | O \     ... make my day
#.   \   \
#.    `~~~'

HUME       = <a href="http://github.com/timm/ezr">home</a>
CONTRIBUTE = <a href="https://github.com/timm/ezr/blob/main/CONRIBUTE.md">contribute</a>
LICENSE    = <a href="https://github.com/timm/ezr/blob/main/LICENSE.md">license</a>
ISSUES     = <a href="http://github.com/timm/ezr/issues">issues</a>

MENU       = $(HUME) | $(CONTRIBUTE) | $(ISSUES) | $(LICENSE)

IMAGE      = <img src="img/ezr.png" align=right width=150>
CSS        = p { text-align: right; } pre,code {font-size: x-small;}

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

name:
	read -p "word> " w; figlet -f mini -W $$w  | gawk '$$0 {print "#        "$$0}' |pbcopy

install   : ## install as  a local python package
	pip install -e  . --break-system-packages 

tests:
	-python3 -B ezr.py -R all; if [ $$? -eq 0 ];               \
	then printf "\n\033[1;32m==> PASSES\033[0m\n";              \
	     sed -i '' '1 s/failing-red/passing-green/' README.md;   \
	else printf "\n\033[1;31m==> FAILS\033[0m\n";                 \
			 sed -i '' '1 s/passing-green/failing-red/' README.md;     \
  fi

docs/%.html : %.py ## .py --> .html
	gawk -f etc/ab2ba.awk $< > docs/$<
	cd docs; pycco -d . $<; rm $<
	echo "$(CSS)" >> docs/pycco.css
	sed -i '' 's?<h1>?$(MENU)<hr>$(IMAGE)&?' $@
	@open $@

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



ALLS= $(subst data/config,var/out/alls,$(wildcard data/config/*.csv)) \
      $(subst data/misc,var/out/alls,$(wildcard data/misc/*.csv)) \
      $(subst data/process,var/out/alls,$(wildcard data/process/*.csv)) \
      $(subst data/hpo,var/out/alls,$(wildcard data/hpo/*.csv))

var/out/alls/%.csv : data/config/%.csv  ; echo $<; ./ezr.py -t $< -R alls | tee $@
var/out/alls/%.csv : data/misc/%.csv    ; echo $<; ./ezr.py -t $< -R alls | tee $@
var/out/alls/%.csv : data/process/%.csv ; echo $<; ./ezr.py -t $< -R alls | tee $@
var/out/alls/%.csv : data/hpo/%.csv     ; echo $<; ./ezr.py -t $< -R alls | tee $@

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
