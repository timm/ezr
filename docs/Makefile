
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
