HOME       = <a href="http://github.com/timm/ezr">home</a>
CONTRIBUTE = <a href="https://github.com/timm/ezr/blob/main/CONRIBUTE.md">contribute</a>
LICENSE    = <a href="https://github.com/timm/ezr/blob/main/LICENSE.md">license</a>
ISSUES     = <a href="http://github.com/timm/ezr/issues">issues</a>
MENU       = $(HOME) | $(CONTRIBUTE) | $(ISSUES) | $(LICENSE)
IMAGE      = <img src="img/ezr.png" align=right width=150>
CSS        = p { text-align: right;} pre,code {font-size: x-small;}

saved:
	git commit -am saved; git push; git status

../docs/index.html : ../docs/ezr.html
	cp $< $@

../docs/%.html : %.py
	gawk -f ../etc/ab2ba.awk $< > ../docs/$<
	cd ../docs; pycco -d . $<; rm $<
	echo "$(CSS)" >> ../docs/pycco.css
	sed -i '' 's?<h1>?$(MENU)<hr>$(IMAGE)&?' $@
	@open $@

~/tmp/%.pdf:  %.py
	@echo "pdf-ing $@ ... "
	@a2ps                 \
		-Br                  \
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
	@ps2pdf $@.ps $@; rm $@.ps    
	@open $@

