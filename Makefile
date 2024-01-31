SSHELL     := bash 
MAKEFLAGS += --warn-undefined-variables
.SILENT: 

help          :  ## show help
	awk 'BEGIN {FS = ":.*?## "; print "\nmake [WHAT]" } \
			/^[^[:space:]].*##/ {printf "   \033[36m%-10s\033[0m : %s\n", $$1, $$2} \
			' $(MAKEFILE_LIST)

saved         : ## save and push to main branch 
	read -p "commit msg> " note; git commit -am "$$note"; git push;git status

FILES=$(wildcard *.py)
docs: $(addprefix ~/tmp/, $(FILES:.py=.pdf))  $(addprefix ../docs/, $(FILES:.py=.html))

 
~/tmp/%.pdf   : %.py  ## py ==> pdf
	mkdir -p ~/tmp
	echo "$@" 
	a2ps                           \
		-qBR                          \
		--chars-per-line 100           \
		--file-align=fill               \
		--line-numbers=1                 \
		--borders=no                      \
		--pro=color                        \
		--columns  2                        \
		-M letter                            \
		-o ~/tmp/$^.ps $^ ;                   \
	ps2pdf ~/tmp/$^.ps $@ ;  rm ~/tmp/$^.ps; \

../docs/%.html: %.py  ## py ==> html
	mkdir -p ../docs
	pdoc3 --html --force  --template-dir ../docs  -o ../docs $^
