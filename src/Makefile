HOME=<a href="http://github.com/timm/ezr">home</a>
CONTRIBUTE=<a href="https://github.com/timm/ezr/blob/main/CONRIBUTE.md">contribute</a>
LICENSE=<a href="https://github.com/timm/ezr/blob/main/LICENSE.md">issues</a>
ISSUES=<a href="http://github.com/timm/ezr/issues">issues</a>


PDOC=/Library/Frameworks/Python.framework/Versions/3.11/bin/pdoc

saved:
	git commit -am saved; git push; git status

../docs/index.html : ../docs/ezr.html
	cp $< $@

../docs/%.html : %.py
	gawk -f ../etc/ab2ba.awk $< > ../docs/$<
	cd ../docs; pycco -d . $<; 
	echo "p  { text-align: right; }" >> ../docs/pycco.css
	echo "pre,code { font-size: x-small; }" >> ../docs/pycco.css
	sed -i '' 's?$< : ?<img src="img/$(basename $<).png" width=490><br clear=all>&?' $@
	sed -i '' 's?<h1>?$(HOME) | $(CONTRIBUTE) | $(ISSUES) | $(LICENSE)<hr> &?' $@
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



docs/%.html : %.py %.png ## .py ==> .html
	mkdir -p $(dir $@)
	pycco -d $(dir $@) $<
	echo 'p {text-align: right;}' >> $(dir $@)/pycco.css
