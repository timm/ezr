.

# How to Contribute

1. Fork the repo
2. In the /src directory, write your extension, the first line of which should be
   `import ezr`.
3. While most of your work should be in your own extension free to modify ezr.py for
   bug fixes and functionality extensions.

## ezr.py

This is the core file of the system. In that file:

- Do not use classes. Why? Classes bust up functionality as polymorphic methods in many classes.
- Code width 90 lines or rest. Why? We aim to include this code into a book.
- Use few or no comments in function doc strings or comments. Comments should be above 
  each function, maybe with points like 
  e.g. `#[A]`  in the code. Why? Easier to port into a book. 
- Functions ideally 5 lines or less. For anything 6 or above, try to pull out   two or more functions.



