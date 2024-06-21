
# Running tests

The test code of this site is written  in `ezr/docs` inside markdown files. To run them:

     cd ezr/docs
     make eg=Code

> [!IMPORTANT]
| Note that only markdown file with leading upper case names have tests.

The above idiom will convert Code.md to Code.lua, then execute it
(importing what it needs from `/src/*.lua`).

