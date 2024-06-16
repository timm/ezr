SHELL     := bash
MAKEFLAGS += --warn-undefined-variables
.SILENT:

Top=$(shell git rev-parse --show-toplevel)

help      :  ## show help
		gawk -f $(Top)/etc/help.awk $(MAKEFILE_LIST) 

pull    : ## download
	git pull

push    : ## save
	echo -n "> Why this push? "; read x; git commit -am "$$x"; git push; git status

md=$(wildcard $(Top)/docs/[A-Z]*.md)

docs2lua: $(subst docs,tests,$(md:.md=.lua)) ## run updates docs/[A-Z]*.md ==> tests/x.lua

$(Top)/tests/%.lua : $(Top)/docs/%.md
	gawk 'BEGIN { code=0 } sub(/^```.*/,"")  \
			{ code = 1 - code } \
			{ print (code ? "" : "-- ") $$0 }' $^ > $@
	luac -p $@
