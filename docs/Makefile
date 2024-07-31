
eg?=data

RED := \033[31m
GREEN := \033[32m
NC := \033[0m# No Color

testLua: $(eg).lua  ## run a tests/*.md file as Lua code; e.g. make eg=Data
	LUA_PATH="../src/?.lua;;" lua $(eg).lua; \
	if [ $$? -eq 0 ]; then  echo -e "$(GREEN)!! PASS$(NC) : $(subst .lua,,$<)"; \
	                  else  echo -e "$(RED)!! FAIL$(NC) : $(subst .lua,,$<)"; fi
	rm $(eg).lua

clean:
		rm *.lua

all: 
	$(foreach f,$(subst .md,,$(wildcard [A-Z]*.md)),$(MAKE) eg=$f;) ## run all */md files as lua

-include ../Makefile

~/tmp/%.pdf : %.md 
	pandoc  \
	-s  -V fontsize=10pt \
	-t beamer  \
	-V theme:Warsaw \
	-V fontfamily=libertine \
	-V "header-includes:\usepackage{xcolor}" \
	-V "header-includes:\usecolortheme{whale}\definecolor{customred}{HTML}{CC0000}" \
	-V "header-includes:\setbeamercolor{structure}{fg=customred}" \
  -V "header-includes:\setbeamercolor{palette primary}{bg=customred, fg=white}" \
	-V "header-includes:\setbeamertemplate{navigation symbols}{}\setbeamertemplate{footline}[page number]" \
	-V "header-includes:\usepackage{graphicx}" \
	-V -highlight=tango  \
	 -V monofontoptions='Scale=0.2' \
	$< -o $@



# $R/docs/%.pdf : $R/docs/%.md  ## make pdf
# 	@mkdir -p $R/docs
# 	@echo "pdf-ing $@ ... "
# 	pandoc "$<"  -o "$@" --from markdown --template "$R/etc/eis.tex" --listings
#
# 	@open $@
