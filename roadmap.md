# Easier Analytics

<img alt="jewel" align=right width=400 src="/docs/jewel.png">

by the EZ gang<br>
yourNameHere<br>
and Tim Menzies

## Summary

This book show ways to simplify the process of analytics, which
involves extracting high-quality  insights from large quantities
of data. We advocate for more efficient and  accessible analytical
methods that require fewer data samples and less  complexity. This
allows for easier verification and understanding of results. We
highlights the benefits of using incremental methods  in building
models that can provide valuable insights with minimal data.

This  book is also a critique the prevailing preference for complex solutions
in the industry,  suggesting that simplicity could offer more
practical and appreciable benefits but is often overlooked due to
commercial interests. The call is for a shift towards simplicity
in analytics, making it faster, smarter, and more flexible, to
better serve practical needs and enhance comprehensibility.

## Introduction

Suppose we want to use data to make policies-- about what to do,
what to avoid, what to do better, etc etc. How to do that?

This process is called _analytics_, i.e. the reduction of large
amounts of low-quality data into tiny high-quality statements. Think
of it as "finding the diamonds in the dust".

Many people have been doing data-driven analytics for decades.  So
it seems the right time  to ask how can we make  analytics  simpler,
smarter, faster, more flexible and more understandable?

For example,  according to Tom Zimmermann (from Microsoft Research),
there are many things we want to do with analytics:

<img alt="[tasks]" src="docs/buse.png" width=750 align=center>

Note all the different algorithms in all the boxes.  Before I knew
better:

- I used to study those algorithms as separate  things. Now I see
them as very similar things, all of which call the same underling
structure. This means that  once we code one of them, we can quickly 
code up the rest. 
- I'd explore 100,000s of possibilities to find patterns in
the data (e.g. during a "what-if" query).  But these days, I can
do the same analysis with 30 samples, or less [^smo1]. This means
if someone wants to check my conclusions, they only need to review
a few dozen samples.  Such a review was impossible using prior
methods since the reasoning was so complicated.

[^smo1]: Using semi-supervised multi-objective optimization via
sequential model optimization (which is all described, later in
this document).

Why can I do things so easily? Well,  based on three decades of work
on analytics [^pigs] (which includes the work of 20 Ph.D. students,
hundreds of research papers and millions of dollars in research
funding) I say:

- When building models, there are incremental methods that can find
those models after very few samples.
- This is because the main message of most models is contained in
just a few variables [:keys].

[^keys]: Menzies, Tim, David Owen, and Julian Richardson. "The
strangest thing about software." Computer 40.1 (2007): 54-60
https://ieeexplore.ieee.org/stamp/stamp.jsp?arnumber=4069195

I'm not the first to say these things [^semi]. So it is a little
strange that someone else has not offer something like this simpler
synthesis. But maybe our culture prefers complex solutions:

> Simplicity is a great virtue but it requires hard work to achieve
it and education to appreciate it. And to make matters worse:
complexity sells better: Edsger W. Dijkstra

By making things harder than they need to be, companies can motivate
the sale  of intricate tools to clients who wished there was a
simpler way. Well, maybe there is.

[^semi]: From Wikipedia: The manifold hypothesis posits that many
high-dimensional data sets that occur in the real world actually
lie along low-dimensional latent manifolds inside that high-dimensional
space. As a consequence of the manifold hypothesis, many data sets
that appear to initially require many variables to describe, can
actually be described by a comparatively small number of variables,
likened to the local coordinate system of the underlying manifold.

<img src="docs/blue.png" height=100 width=1000>

## In the beginning ...


### ... There was data

This code reads comma-separated-files whose first line described
each column.

Clndrs|Volume|Model|origin|Lbs-|Acc+|Mpg+
------|-----|------|------|-----|---|----
4|97|82|2|2130|24.6|40
4|96|72|2|2189|18|30
4|140|74|1|2542|17|30
------|-----|------|------|-----|---|----
4|119|78|3|2300|14.7|30
8|260|79|1|3420|22.2|20
4|134|78|3|2515|14.8|20
6|231|78|1|3380|15.8|20
8|302|77|1|4295|14.9|20
8|351|71|1|4154|13.5|10

Just to explain the column names:

- Names starting with `Uppercase` are numeric and the other columns
are symbolic.  
- Names ending with "-","+" or "!" are the _goals_
which must  be minimized, maximized or predicted. The other columns
are observables or controllables used to reach the goals.

The rows are all examples of some function $Y=F(X)$ where:

- $Y$ are the goals (also called the dependents)
- $X$ are the observables or controllables (also called the independents)
- $F$ is the model we want to generate.

For example,  the above table is about motor cars:

- Lighter cars cost less to build since they use less metal.
  Hence `Lbs-` (minimize weight).
- Faster, fuel effecient cars  are easier to sell. Hence `Acc+` (maximize
   acceleration) and `Mpg+` (maximize miles per gallon).

The rows of this table are sorted by the distance of each row to
some mythical best car with least weight, most acceleration and
miles per hour.  Those rows are then divided into a _smallN_ best rows
(the first three rows) and rest (the other rows).

- _smallN_ is our shorthand for   $\sqrt{N}$.
- We have another term,  _tinyN_, which  denotes a dozen  ($N=12$) examples.  

This rows of this table have all the $X$ and $Y$ values  for each
row. _Labeling_ is the processing of reading a row's $X$ value,
then working out the $Y$ value.  Labeling  can be very slow and/or expensive and/or error
prone. For example, if your labelling needs a human subject matter
expert, then those are very busy people who are need to be somewhere
else, applying their expertise. And even SMEs make mistakes
(particularly if you them too many things, too quickly).

To say that another way, we need to do analytics without much labelling.
In practice, it is often much easier/cheaper/faster to collect
the $X$ values.  For example:

- When you go fishing, you can glance up and down the river
looking at all the places where you might go fishing.
But working out where the fish are biting today might mean waiting
for hours in each spot.
- When buying a car, you can glance around a car yar to  
quickly count the car color, car manufacturers  and model, number of
doors, number of seats, road clearance and many other independent
$X$ values.  But if you want to know which can corner the best,
or their acceleration on that hill outside your house, or their
miles per gallon on your route to work, you will have to take the
time to go drive the cars, one at a time.
- When testing software, you can quickly
generate millions  of test inputs.  But it could take a lifetime
to look at each one to work out what should be the expected output.
- When exploring  cost
estimation, it is relatively easy to count the size of some product.
What can be much harder is getting a  contracting company
to tell you their secrets about  who actually worked for how long on
different parts of that product.

The good news here is that $Y=F(X)$; i.e. the
$Y$ values are connected to the $X$ values.
This means that by
looking at a lot of $X$ values (which is cheap), we can guess the $Y$
values without actually labeling them all. 
There are many other ways to do this-- see the review
in [^cotrain]. Methods  that can work with very few labels are:

[^spectral]: Nair, V., Menzies, T., Siegmund, N. et al. Faster
discovery of faster system configurations with spectral learning.
Autom Softw Eng 25, 247–277 (2018).  https://arxiv.org/abs/1701.08106

[^stealth]: Alvarez, Lauren, and Tim Menzies. "Don’t Lie to Me:
Avoiding Malicious Explanations With STEALTH." IEEE Software 40.3
(2023): 43-53.  https://arxiv.org/pdf/2301.10407

- In _label propergation_, we cluster the data into small groups (say, of size smallN or tinyN),
  label one row from each group,
  then share than label around that cluster  [^spectral] [^stealth]. 
- In _recursive projections_, we recursively bi-cluster the data. At each step
  in the recursion, we label two distant examples then prune away half the data
  associated wthe worst label.  
  If each step reuses one label from the parent, then recursive projections
  can find  good
  parts of the data using $1+\log_2{N}$ labels [^sway].
- in _sequential model optimization_, we use what we have learned so far to guide
  what to label next. This means:
  -  dividing  a few labelled examples into (say)
  smallN `best` and `rest`; 
  - building a classifier that can report the likelihood $b,r$ of
  that an unlabelled example belongs to     `best` or `rest`; 
  - sorting the unlabelled data
  by (say) $b/r$; 
  - labeling the top item in that sort and adding that to the labelled examples; 
  - and repeat.

[^sway]: J. Chen, V. Nair, R. Krishna and T. Menzies, "“Sampling”
as a Baseline Optimizer for Search-Based Software Engineering," in
IEEE Transactions on Software Engineering, vol. 45, no. 6, pp.
597-614, 1 June 201 https://arxiv.org/pdf/1608.07617

[^cotrain]: Majumder, Suvodeep, Joymallya Chakraborty, and Tim
Menzies. "When less is more: on the value of “co-training” for
semi-supervised software defect predictors." Empirical Software
Engineering 29.2 (2024): 1-33.  https://arxiv.org/pdf/2211.05920


[^active1]: Active learning is an incremental learning tactic where,
usually, each new example is assessed by a human. The goal of such
learning is avoid wearing out the humans by asking them too many
questions.



A really good way to explore a large number of examples.

-  we want to 
minimize (), maximize and maximize
The above rows are sorted by _distance to heaven_
which we can see or change in order tor eac


[^pigs]: Menzies, Tim, John Black, Joel Fleming, and Murray Dean. "An expert system for raising pigs." In The first Conference on Practical Applications of Prolog’.  1992. http://aturing.umcs.maine.edu/~meadow/courses/cos301/raising-pigs.pdf

what to add to what we currently do,  policy from data. 
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
