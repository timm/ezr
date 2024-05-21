.

# How to Contribute

1. Fork the repo
2. In the /src directory, write your extension, the first line of which should be
   `import ezr`.
3. While most of your work should be in your own extension free to modify ezr.py for
   bug fixes and functionality extensions.

## ezr.py

This is the core file of the system. In that file:

- Private functions are labeled with a leading dash. These should should only ever  be called except via some special control function
- Do not use classes. Why? Classes bust up functionality as polymorphic methods in many classes.
- UPPERCASE functions are constructors. There are two types. The private constructors are written with a leading dash, like _EG. 
  These public constructor used to create instances are all upper case, like EG. These constructors are now a reserved type name. So a variable
  `eg`  or `eg1` would be of type EG. Also `egs` denotes a list of EGs.
- Code width 90 lines or rest. Why? We aim to include this code into a book.
- Use few or no comments in function doc strings or comments. Comments should be above 
  each function, maybe with points like 
  e.g. `#[A]`  in the code. Why? Easier to port into a book. 
- Functions are ideally 5 lines or less. For anything 6 or above, try to pull out   two or more functions.

- use type hints. why? better doco.
- use `i` to denote self. Why? cgood replace for self or this. never use `i` as a counter
= never use a type name as a variable name. so no col by `col1`
Traps:
- remember to gaurd against "?" (i.e. don't know variables)
