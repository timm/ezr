PDOC=/Library/Frameworks/Python.framework/Versions/3.11/bin/pdoc

saved:
	git commit -am saved; git push; git status

~/tmp/%.html : %.py
	pycco -d ~/tmp $<
	# @echo "$< ==> $@"
	# @$(PDOC)  --logo 'https://raw.githubusercontent.com/timm/ezr/main/docs/img/less.png' -o ~/tmp $<
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

