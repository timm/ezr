.

# Lessons

## Science

- **Open science:** Used DOIs to publish papers, and the scripts and data used in this papers.

## SE

### Open source

Make code freely usable.

### Software 2.0

SE projects are now divided into team1, team2 where team1 does convectional SE, while team2
   is in charge of the care and feeding on an optimizer/model builder

### Separate policy from mechanism

Your current code is but an example of one product within a large space of similar prodicts

Make much use or domain-specific notations (e.g. regx, our
  __doc__ strings, our little language for column headers).

### Doc, Config

At top of file, add in all settings to the __doc__ string. 
  Parse that string to create `the` global settings.
  Also, every function gets a one line doc string. For documentation longer than one line,
  add this outside the function.
- Config matters
  - fast growth in config options
  - slower growth in the options we use
  - gap in the middle (beween we do and what we can do)

###  TDD 

hald tthe time in testing

Lots of little tests. At end of file, add in demos/tests as methods of the `eg` class 
  Report a test failure by return `False`. Note that `eg.all()` will run all demos/tests
  and return the number of failures to the operating system.

- set up (reset seed, save settings)
- tear down (restore)

### Composition

Allow for reading from standard input (so this code can be used in a pipe).

-  Pipelines
   - my testing pre-commit hook

### Abstraction

Make much use of error handling and iterators.

e.g LSP

e.g. lambdas

### Types

Use type hints for function args and return types.
Don't use type names for variables or function names.  E.g. use `rows1` not `rows`. E.g. use `klasses` not `classes`; 

- Bythe way, Python typs system is a msss. upated all the times. tools not keeping up with the updates. lots of things undefined
  - for a real types language, see rust. but be warned "fight with compiler". to be fair, lots of programemrs report happiness with rust. and lots of cool new tools coming out of the rust universe. so definitely one to look at.

### OO? Hell no!

write less classes

does oo sync with the say we thing?

Group together similar functionality for difference types (so don't use classes).
And to enable polymorphism, add a `this=CONSTRUCTOR` field to all objects.

### Functional programming? heck yeah!

lots of comprehensions and lambda bodies.

### Information hiding

Mark private functions with a leading  "_". 
  (such functions  should not be called by outside users).

modules

packaging

containers

### Refactoring

Functions over 5 lines get a second look: can they be split in two?
  Also, line length,  try not to blow 90 characters.

## KE

### Less is more

The model is already there, within the data.
     We  just have to chisel away the superfluous material. 

Druzdel

All my small models

### Labelling is a problem

Do everything we can, with fewer labels.

### Trees are just recursive ranges

### Naive Bayes is just N DATA
- **Worse is better:** Simpler code has better survival characteristics than the-right-thing.
- ** learning in the long tail**

----------
# Just enough SE



#### CLI

ss.sbyecode=true

## Randomizes algorihtms

seed
