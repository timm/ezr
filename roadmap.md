# inference
every section needs definiton, tutorial , applciation (references), something about state of the art

preamble
there are SYMs (=, !=) and there are NUMs (=,!=,+,-,*,/, etc)

MID: central (middle) tendency   of a distribution (mean, median, mode)

DIV: measure of diversity around the mid (entropy, standard deviation)

    def SIMPLER1(bin1,bin2):
      both = bin1+bin2
      n1,n2=len(bin1), len(bin2)
      if DIV(both) <= (n1*DIV(bin1) + n2*DIV(bin2)) / (n1+n2): return both

    rand()=0..1
    seed = something. # reset me to regenerate same "random" numbers.

    cf=.3,f=.5 (say)
    def MUTATES1(A,B,C): # to mutate A, pick B,C at random  
      return [MUTATE1(A.x[i], B.x[i], C.x[i]) for i in #A]

    def MUTATE1(a,b,c): 
      if rand() > cf: return a
      if numeric(a): return a + f*(b-c)
      return b if rand() > .5 else c

dist
like

y=f(x)
y1,y2,y3=f(x1,x2,x3,x4,x5,x6,...)

dists # change code
likes # change code

regression, classification: |y|=1, y values are numeric, symbolic.

multi-regression, multi-classification: |y|>1

optimization: y values are numeric, each of which needs to be minimized or maximized

association: some of y or x are missing and we need to fill them in

distance: return the distance between two examples

cluster: return sets of similar (X,Y) examples

locate: given clusters, find which one is most similar to some new (X,Y)

def PARTIAL\_MATCH(eg): apply distance, but only on some fields. return nearest items
def ASSOCIATE(eg): cluster, locate, 

def ASSOCIATE1(eg): cluster, locate(eg), find 
 
def COMPRESS1(): cluster, then return just a few samples per cluster

mutate: generate a new (X,Y) example 

def MUTATE1(): add to example1 some point in-between example2 and example3

synthesis: mutate some  (X,Y) examples to invent new ones

def SYNTHESIS1(): run 


an

contrast: report the difference between to cluster


def KNN1(): cluster



# smarter

- are you meek? (writing intro examples)?
- are you mighty (writing research papers, comparing this stuff to SOTA). 
  - before you can be mighty you have to be meek

- are you writing for systems, shell, script, smarts, or story
  - systems: install, standards (contribute.md), packaging, deep background
  - shell: make, command line
  - script: coding ninja stuff
  - smarts: AI level stuff
  - story: documentation

- team or solo? either is fine

- use fewer labels.

- not writing code, writing demos
Separate mechanisms from policy (write a DSL for policy)
Small is beautiful: Write simple programs
Write small programs
Write transparent programs
Avoid unnecessary output

Make each program/function do one thing well.
Build a prototype as soon as possible.
Choose portability over efficiency.
Store data in flat text files.
Use shell scripts to increase leverage and portability.
(\*) Make every program a filter. we';l be internal
"worse is better":  simplicity of interface and/or implementation more important than (e.g.)
     correctness, consistency, and completeness


set seed once, run 20 repeats. compare distributions, not points
not 0.4356172 but 44
44 is (probably) not greater than 42
bunching; i.e., a large number of treatments can be grouped into a small number of effectively similar units.
blurring: many/all treatments  statistically indistinguishable.

- lua or python?

- 5 lines (ish) per method
- 100 chars wide
- no OO
- constructors in UPPER CASE (constructors define types)
  - use type names in var names for functions
  - optional (2 spaces)
  - local (4 sspaces)
- page length chunks (or less)

-standards
 - no globals
 - help
 - settings
 - constructors
 - code
 - misc functions (towards end)
 - egs at end
 - check for main, otherwise call an eg from the command line
 - eg
   - set up: reset random number seed and settings to defaults
   - tear down: ditto. and return false is something crashes
   - eg.all counts how many return false, returns that number to the operating system

- issue how we manage nested help and egs.... lets not solve that till we get enough experience

- md standards
  - consoder not changing para1. auto copied from /README.md

## Exercises

- Data
- nearest neighbor and random HPO (30 random)
- naive bayes and  SMO HPO
- and directed HPO

## Why basic
- https://world.hey.com/dhh/finding-the-last-editor-dae701cc
- Doug McIlroy : We used to sit around in the Unix Room saying, 'What can we throw out? Why is there this option?' It's often because there is some deficiency in the basic design — you didn't really hit the right design point. Instead of adding an option, think about what was forcing you to add that option.
- The more you code the more you have to maintain, upgrade, port to other systems.

### Counter case
- simplicity takes time (Bliase Pacal: 
  <em>Je n'ai fait celle-ci plus longue que parce que je n'ai pas eu le loisir de la faire plus courte.</em>
  I would have written a shorter letter, but I did not have the time.)
- Complexity sells (or, more accurately, the maintaince income associated with complexity sells).
- Complexity is attractive (lures in the unwary, locks them in with so many decisions they mever want to remake)
- less is a bore
- teaching package manager, codespaces, vscode. markmap


## The Basics

### Python

- safe parsing
- Sequences
  - sets
    - Removing duplicates
    - [disjunction](#stats)
    - Conjunction
  - Slicing
  - Dictionary: and, or
    - Counter
  - Comprehensions
    - List
    - Set
    - Dictionary
- Ternary
- Printing
  - Secrets of print (sep,end), flush
  - Fstring
  - super print (from the parent)
- Swap in place
- Start-up (__name__ == “__main__”)
- Exception handling
- Args & Kwargs
- lambda (closures)
- toto: complete this from ase24/docs/ninjas

### stats

- normal
  - incremental update
- triangular
- cdf
- [entropy](entropy.md) 
- discretization (simple) recall doherty icml'95
- difference
  - effect size
  - significance
  - ranking (SK)

### Shell

- Regex
- awk
- Makefile
- shebang
- pipes

## Smarter Scripting

- little languages (regx, data models headers, __d__2options)
- DRY, not WET
- licensing
- packaging
- information hiding
  - [API](https://www.hyrumslaw.com/) (you get one chance to write an API)

### scripting

- script101
  - technical debt
    - less is more
  - documentation
    - doc strings
    - types
    - badging
  - configuration
    - exposed control parameters
  - testing
    - test driven development
    - test pattern test suite
      - setup, reset, tear down
      - $?
    - static code analysis
      - language server protocol
  - source control
    - config in source control. eg. my fav tmus start up
    - workflow
      - pre-commit hooks
        - e.g. badging
  - decomposition
    - piping
      - shut the heck up (quiet execution)
      - standard files STDIN, STDERR, STDOUT
  - seed control
- automate everything (makefile: insert awkward stuff there)

## Easier AI

- active learning (one thing per leaf)
Data
- clustering
- nearest neighbor
- kernels (linear, triangular)

classifier:

- Naive bayes
- knn (no clustering) <== can be regressions as well
- decision tree

clustering:

- one sample per leaf (tiny training)
- regression and classification
- sample plus propagate

- lessons:
  - data reduction (just one sample per leaf)
  - when recursively clustering, use less and less to find poles.

## KE

W1: data.

- Little languages: data headers (bigger: regular expressions)
- Test suite
- documentation
- Pipe and filter/ architecture

W2: classification

- Bayes
- Labelling

## Read More
