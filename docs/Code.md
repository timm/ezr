# Coding AI Experiments

Get the code

    git clone http://github.com/timm/ezr

Make sure you select the right branch:

      % git branch -r
      origin/24Jun14
      origin/24feb28
      origin/24feb6
      origin/24may19
      origin/25may12
      origin/HEAD -> origin/main
      origin/Stable-EMSE-paper
      origin/main
      origin/sneak

You will told which `BRANCh` to go to use in lectures

     git checkout BRANCH

Once you get there, make sure the code runs

    cd ezr/tests
    make f=Numsym lua

This should  print some help text.

## Roll your own

Copy `tests/Code.lua` to `tests/myCode.lua`.

Edit that tile to do anything ant all with my code.

Run the code, add the output as a comment string at bottom of that code.
Note, you may have to do tricky things with pathnames (e.g. adding "../"). The file `tests/Makefile` 
has a command `test` that handles that for lua:

     -include ../Makefile
     one?=Code
     
     lua: docs2lua $(one).lua
     	LUA_PATH='../src/?.lua;;' lua $(one).lua

With the code, the command

    cd ezr/tests
    make f=Numsym lua

will update all the `tests/*.lua` files (from any `docs/[A-Z]*.md` files), then
runs lua on `tests/Numsym.lua` with a `LUA_PATH` that means lua can find `../src/*.lua` files.

**TODO** What does the equivalent rule for Python look like? So code in `/tests` can read
source Python files from `/src`. Hints:

- [Read the  Python manual](https://www.geeksforgeeks.org/sys-path-in-python/#)
- If you want, don't worrying about the `docs/*.md` to `tests/*.lua` thing. That's a little tricky.

**SUBMIT** 
- `tests/Makefile`
- a screenshot of your vscode-like environment where on the same
  screen is the code you are editing and a terminal showing the  output
  from `make f=Numsym lua`.


