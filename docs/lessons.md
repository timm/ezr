# Lessons

- Merging PRs in GitHub
- Diffing on the command line
- Running code on the command line
- Using a command line editor like vim
- Resolving merge conflicts in GitHub
- Rebasing on GitHub
- Describing a data set using descriptive statistics
- Using a debugger this: https://www.youtube.com/watch?v=oCcTiRGPogQ
t

## Science

- **Open science:** Used DOIs to publish papers, and the scripts and data used in this papers.

## SE

### Open source

Make code freely usable.

### Software 2.0

SE projects are now divided into team1, team2 where team1 does conventional SE, while team2
   is in charge of the care and feeding on an optimizer/model builder
o
### Product lines / Separate policy from mechanism

Your current code is but an example of one product within a large space of similar products

So:
- Make much use or domain-specific notations (e.g. regx, our
  __doc__ strings, our little language for column headers).

### Config, matters

- Config matters
  - fast growth in config options
  - slower growth in the options we use
  - gap in the middle (beween we do and what we can do)

### Doc, matters
Every pieces of software needs documentation.

So:
- At top of file, add in all settings to the __doc__ string. 
-  Parse that string to create `the` global settings.
  Also, every function gets a one line doc string. For documentation longer than one line,
  add this outside the function.
- pycco

###  Test-driven development 

Half the development time is in tessting

Standard patterns for tests:
- set up (reset seed, save settings)
- tear down (restore)

so:
- write Lots of little tests. At end of file, add in demos/tests as methods of the `eg` class 
-  Report a test failure by return `False`. Note that `eg.all()` will run all demos/tests
  and return the number of failures to the operating system.

it is difficult to teach debugging on non-trivial examples; students
need domain knowledge about the SUT to make a judgement on whether
a location is buggy or not.

- run tests. re-run tests. beck's watch command
- black-box, white-box, formal: fuzzing, clustering, safety critical systems
- shaperio: https://damorim.github.io/publications/li-etal-icse2018.pdf
- whylines: needs specific tool support. but it does teach us that testing has a search structure
- delta debugging

testing big is very different to testing small
- know the location is not even relevant (zhe's work)
- test prioritizaition strategies 
  - saved google 2015 (sebastian etc)
  - test new, test things that failed, test things that have not been tested lately
- big test is like big explore
  - sequential model optimizaion. how to test a little then go forth and hunt down the rest.

## Principles and Patterns:

What can we  learn from one applciations that might
apply to others?



### Principles:
Principles, which if taught to newbies can might simplify their code
might make them better programmers/managers, faster

- DRY, 
- YAGNI, 
- Do1Thing
  - Curly's Law: A entity (class, function, variable) should mean one thing, and one thing only. It should not mean one thing in one circumstance and carry a different value from a different domain some other time. It should not mean two things at once. It should mean One Thing and should mean it all of the time 
- Conway's Law
  - Any piece of software reflects the organizational structure that produced it.
  - it's hard for someone to change something if the thing he/she wants to change is owned by someone else.
  - So, structure teams to look like your target architecture, or structure
     your architecture according to your current teams
  - practical consquences: bird/basili, icse 2008
- Brooks' Law"Adding (staff) to a late software project makes it later."
- Hyrum's Law With a sufficient number of users of an API, it does not matter what you promise in the contract: all observable behaviors of your system will be depended on by somebody.

### Patterns

1. An architectural pattern expresses a fundamental structural organization schema for software systems. It provides a set of predefined subsystems, specifies their responsibilities, and includes rules and guidelines for organizing the relationships between them.
2. A design pattern provides a scheme for refining the subsystems or components of a software system, or the relationships between them. It describes a commonly-recumng structure of communicating com- ponents that solves a general design problem within a particular context
3. Idiom: An idiom is a low-level pattern specific to a programming language. An idiom describes how to implement particular aspects of components or the relationships between them using the features of the given language.
4. Anti-patterns: common examples of worst-practice.
   - WET
   - Premature optimization is the root of all evil





### Composition

Allow for reading from standard input (so this code can be used in a pipe).

So: 
-  Pipelines
   - my testing pre-commit hook

Note limiataions with pipels (cant go backwards)

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

### Debugging

See marcello's comments at  https://mail.google.com/mail/u/2/#inbox/KtbxLxGPlKwzqGZDqgxdFsdxcMGtdpdJNV

## KE

### Less is more

The model is already there, within the data.
     We  just have to chisel away the superfluous material. 

Druzdel

All my small models

### Labelling is a problem

Do everything we can, with fewer labels.

### Trees are just recursive ranges

### Naive Bayes is just N DATA*
- **Worse is better:** Simpler code has better survival characteristics than the-right-thing.
- ** learning in the long tail**

# Just enough SE



#### CLI

ss.sbyecode=true

## Randomizes algorihtms

seed



### Idioms
#### Config from __doc__
#### Types
#### Tests
test driven development;

- set up
  - reset seed, save settings
- tear down
  - reset settings

## abstraction
iterators, error hadlers

## Config, mattters
- fast growth in config options
- slower growth in the options we use
- gap in the middle (beween we do and what we can do)

## Documentation, matters

### Pipelines

#### CLI

### Type hints
type hints
- types. errors. comilation
- documentatiion
- complexities (nested types)

ss.sbyecode=true
- interretation vs compilation
- problems with traspiling

## Randomizes algorihtms

keep you seed


# Scripting tricks

##  50  cool python one liners
Comprehensions, destructing, etc etc
##  100 cool shell one liners

- The Enlightened Ones say that....

  - You should never use C if you can do it with a script;
  - You should never use a script if you can do it with awk;
  - Never use awk if you can do it with sed;
  -  Never use sed if you can do it with grep.



- 25  cool shell (bash/zsh) one liners
- 25  cool Make one liners
- 25 cool awk one liners
- 25 cool sed one liners




