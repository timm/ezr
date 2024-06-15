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


You will told which branch to go to use in lectures

 git checkout new_branch

Once you get there, make sure the code runs

    cd lite/tests
    lua code.lua # <== maybe python3.12 code.py

This should  print some help text.

## Roll your own

Copy `tests/Code.lua` to `tests/myCode.lua` (maybe `myCode.py`).

Edit that tile to do anything ant all with my code.

Run the code, add the output as a comment string at bottom of that code.
Note, you may have to do tricky things with pathnames (e.g. adding "../")

**SUBMIT** `tests/myCode.whatever`.


