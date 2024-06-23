# Shell and Makefile Programming Tutorial Notes

XXX add ida. graph of rules

## Introduction

Makefiles are essential tools in software engineering, primarily used for managing build automation. They help in compiling code, linking programs, and managing dependencies automatically. This tutorial will introduce shell programming and Makefile concepts used in the provided Makefile.

## Makefile Structure

A Makefile consists of a series of rules. Each rule defines how to convert files from one format to another or how to update files when dependencies change.

### Basic Syntax

A rule in a Makefile typically looks like this:
```makefile
target: dependencies
    command
```

- **target**: The file to be generated.
- **dependencies**: Files that the target depends on.
- **command**: The shell command to generate the target.

## Shell Programming in Makefiles

### Setting the Shell

The shell used to interpret commands in a Makefile can be specified using the `SHELL` variable:
```makefile
SHELL := bash
```

### Shell Commands

Shell commands are used extensively in Makefiles. For example, the `git` commands:
```makefile
pull: ## download
    git pull

push: ## save
    echo -en "\033[33mWhy this push? \033[0m"; read x; git commit -am "$$x"; git push; git status
```

- **git pull**: Updates the local repository with changes from the remote repository.
- **echo**: Prints a message to the terminal.
- **read**: Reads user input.
- **git commit -am "$$x"**: Commits changes with a message.
- **git push**: Pushes commits to the remote repository.
- **git status**: Shows the status of the working directory.

### Variable Assignment

Variables can be assigned using the `:=` operator:
```makefile
Top=$(shell git rev-parse --show-toplevel)
```
- **Top**: Assigns the top-level directory of the git repository to the variable `Top`.

## Makefile Targets and Recipes

### Help Target

A common target in Makefiles is `help`, which provides information on how to use the Makefile:
```makefile
help: ## show help
    gawk -f $(Top)/etc/help.awk $(MAKEFILE_LIST)
```
- **gawk**: A pattern scanning and processing language.
- **$(Top)/etc/help.awk**: The awk script used to generate the help message.

### Pattern Rules

Pattern rules specify how to build targets that match a certain pattern:
```makefile
%.lua : %.md
    gawk 'BEGIN { code=0 } \
        sub(/^```.*/,"") { code = 1 - code } \
                           { print (code ? "" : "-- ") $$0 }' $^ > $@
    luac -p $@
```
- **%.lua : %.md**: Converts `.md` files to `.lua` files.
- **$^**: All dependencies.
- **$@**: The target.
- **luac -p**: Syntax checks Lua programs.

### Directory and File Operations

Creating directories and manipulating files:
```makefile
~/tmp/%.pdf: %.lua ## .lua ==> .pdf
    mkdir -p ~/tmp
    echo "pdf-ing $@ ... "
    a2ps \
        -BR \
        -l 100 \
        --file-align=fill \
        --line-numbers=1 \
        --pro=color \
        --left-title="" \
        --borders=no \
        --pretty-print="$(Top)/etc/lua.ssh" \
        --columns 2 \
        -M letter \
        --footer="" \
        --right-footer="" \
      -o $@.ps $<
    ps2pdf $@.ps $@; rm $@.ps
    open $@
```
- **mkdir -p ~/tmp**: Creates the directory `~/tmp` if it doesn't exist.
- **a2ps**: Converts the Lua file to PostScript with specific formatting options.
- **ps2pdf**: Converts PostScript to PDF.
- **open $@**: Opens the generated PDF.


## References

- [GNU Make Manual](https://www.gnu.org/software/make/manual/make.html)
- [Bash Reference Manual](https://www.gnu.org/software/bash/manual/bash.html)
- [Gawk User's Guide](https://www.gnu.org/software/gawk/manual/gawk.html)

