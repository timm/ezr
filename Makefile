SHELL     := bash
MAKEFLAGS += --warn-undefined-variables
.SILENT:

Top=$(shell git rev-parse --show-toplevel)

help      :  ## show help
		awk 'BEGIN {FS = ":.*?## "; print "\nmake [WHAT]" } \
	                /^[^[:space:]].*##/ {printf "   \033[36m%-18s\033[0m : %s\n", $$1, $$2} ' \
	        $(MAKEFILE_LIST)
		awk 'sub(/#\. /,"") { printf "  \033[36m%-20s\033[0m \n", $$0}' Makefile

pull    : ## download
	git pull

push    : ## save
	echo -n "> Say, why are you saving? "; read x; git commit -am "$$x"; git push; git status

md=$(wildcard $(Top)/docs/[A-Z]*.md)
lua=$(md:.md=.lua)

doco: $(subst docs,tests,$(lua))

$(Top)/tests/%.lua : $(Top)/docs/%.md
	gawk 'BEGIN { code=0 } sub(/^```.*/,"")  \
			  { code = 1 - code } \
							{ print (code ? "" : "-- ") $$0 }'  $^ > $@
	luac -p $@
