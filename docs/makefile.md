# Makefiles in Software Engineering

## Introduction
In software engineering, Makefiles are crucial for automating the build and test processes. Using multiple Makefiles can help in organizing and modularizing these processes. Here, we will explore two interconnected Makefiles, highlighting their key principles and functionalities.

## Key Concepts

### Makefile 1: Primary Makefile

#### Variables
```makefile
eg?=data

RED := \033[31m
GREEN := \033[32m
NC := \033[0m # No Color
```
- `eg?=data`: Sets the default value for `eg` to `data` if not provided.
- `RED`, `GREEN`, and `NC` are used for colored output in the terminal.

#### Targets and Rules
```makefile
testLua: $(eg).lua
	LUA_PATH="../src/?.lua;;" lua $(eg).lua; \
	if [ $$? -eq 0 ]; then  echo -e "$(GREEN)!! PASS$(NC) : $(subst .lua,,$<)"; \
	else  echo -e "$(RED)!! FAIL$(NC) : $(subst .lua,,$<)"; fi
	rm $(eg).lua
```
- **Target**: `testLua`
- **Dependency**: `$(eg).lua`
- **Commands**: Runs the Lua script, importing code from ../src, then and outputs whether the test passed or failed, then removes the Lua script file.

#### Wildcards and Pattern Rules
```makefile
all: 
	$(foreach f,$(subst .md,,$(wildcard [A-Z]*.md)),$(MAKE) eg=$f;)
```
- **Wildcard**: `$(wildcard [A-Z]*.md)` finds all Markdown files starting with an uppercase letter.
- **Substitution**: `$(subst .md,,$(wildcard [A-Z]*.md))` removes the `.md` extension.
- **Foreach Loop**: Iterates over each found file and runs `make` with `eg` set to the file name.

#### Including Another Makefile
```makefile
-include ../Makefile
```
- This line includes another Makefile from the parent directory, allowing code reuse and organization.

### Makefile 2: Secondary Makefile

#### Basic Settings and Silent Mode
```makefile
SHELL     := bash
MAKEFLAGS += --warn-undefined-variables
.SILENT:
```
- **SHELL**: Specifies the shell to be used.
- **MAKEFLAGS**: Adds a flag to warn about undefined variables.
- **.SILENT**: Suppresses command output for cleaner logs.

#### Variables and Help Target
```makefile
Top=$(shell git rev-parse --show-toplevel)

help:  ## show help
	gawk -f $(Top)/etc/help.awk $(MAKEFILE_LIST)
```
- **Top**: Retrieves the top-level directory of the git repository.
- **help**: Uses `gawk` to generate help text from the Makefile comments.

#### Git Commands
```makefile
pull: ## download
	git pull

push: ## save
	echo -en "\033[33mWhy this push? \033[0m"; read x; git commit -am "$$x"; git push; git status
```
- **pull**: Runs `git pull` to update the local repository.
- **push**: Prompts for a commit message, commits changes, and pushes to the remote repository.

#### Pattern Rules and File Conversion
```makefile
%.lua : %.md
	gawk 'BEGIN { code=0 }  \
		sub(/^```.*/,"") { code = 1 - code } \
		{ print (code ? "" : "-- ") $$0 }' $^ > $@
	luac -p $@
```
- Converts Markdown files to Lua files by removing code blocks.

#### Lua to PDF Conversion
```makefile
~/tmp/%.pdf: %.lua  ## .lua ==> .pdf
	mkdir -p ~/tmp
	echo "pdf-ing $@ ... "
	a2ps -BR -l 100 --file-align=fill --line-numbers=1 --pro=color --left-title="" --borders=no --pretty-print="$(Top)/etc/lua.ssh" --columns 2 -M letter --footer="" --right-footer="" -o $@.ps $<
	ps2pdf $@.ps $@; rm $@.ps
	open $@
```
- Converts Lua files to PDF using `a2ps` and `ps2pdf`, and opens the PDF.

## Conclusion
These Makefiles illustrate how to automate and organize build processes efficiently. By understanding the interaction between multiple Makefiles, software engineers can maintain modular, reusable, and clean build systems.
