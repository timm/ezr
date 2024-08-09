% A quick peek at exr.py
% Tim Menzies
% August 5, 2024

## Before We Start....

Macro structure of ezr.py:

- Starts with __doc__ string, from which we parse out the control settings.
- Ends with a set of examples in the `egs` class which can be called from the command line. E.g. `-e mqs` called `egs.mqs()`.
- Uses a  [a function-oriented style](#decorators),  where methods are grouped by name, not class.

Terminology (watch for these words):

- Classes: 
  - SETTINGS, DATA, COLS, NUM, SYM
- Variables:
  - row, rows, done (which divides into best and rest); todo
- SE Notes: 
  - refactoring, DRY, WET
  - styles, patterns, idioms, function-oriented 
  - decorators, little languages, configuration, pipes, iterators, exception handling,
  - make, regular expressions,
  - decorators, type-hints, comprehensions,  dunder methods, 
- AI Notes: 
  - Y,  dependent, X,  independent, goals, 
  - labelling, active learning, 
  - multi-objective, aggregation function, chebyshev
  - regression, classification, Bayes classifier, 
  - entropy, standard deviation, cross-validation
- Synonyms (conflations, to be aware of): 
    - features,  attributes, goals
    - Y goals dependent
    - X independent
    - styles, patterns, idioms

## Overview

### EZR is an active learning

The human condition is that we have to make it up as we go along.
Active learning is a strategy for acting with partial knowledge,
before all the facts are in. 

To understand this, suppose we wanted to learn some  model $f$ 

$$Y_1,Y_2,...\;=\;f(X_1,X_2,X_3....)$$

Any example contains zero or more $X$ and $Y$ values

- If there are no $Y$ values, we say the example is _unlabeled_. 
- If the model is any good then 
there must be some connection between the $X$s and the $Y$.
  - This  means we can explore the $X$ space to build a
loosey-goosey approximate of the $Y$ space.
- It is usually harder (slower, more expensive) to find the $Y$s
than the $X$s. 
For example,
  - If we want to buy a used car then  a single glance at a car lot
tells us much about hundreds of 
car make, model, color, number of doors, ages of cars, etc (these are the $X$ values)
  - But it takes much longer to work out  acceleration or
miles per hour (these are the $Y$ values) since that requires you have to drive  the car around
for a few hours.

### SE Examples where finding $X$ is  cheaper than $Y$

- $X$,$Y$ are our independent and dependent variables.
- Quick to mine $X$ GitHub to get code size, dependencies per function,  
  - Slow to get $Y$ (a) development time, (b) what people will pay for it
- Quick to count $X$ the number of classes in a system. 
  - Slow to get  $Y$ an organization to tell you human effort to build and maintain that code.
- Quick to enumerate $X$ many  design options (20 yes-no = $2^{20}$ options) 
  - Slow to check $Y$ those options with   the human stakeholders.
- Quick to list $X$ configuration parameters for  the  software. 
  - Slow to find $X$ runtime and energy requirements for all configurations.
- Quick to list $X$ data miner params (e.g. how many neighbors in knn?) 
  - Slow to find  $Y$ best setting for local data. 
- Quick to  make $X$ test case inputs using (e.g.) random input selection
  - Slow to run all tests and  get $Y$ humans to check each output 

### Smart Labeling

- Learning works better if the learner can pick its training data[^brochu].
- _Labeling_ is the process of finding the $Y$ values, before we know the $f$ function 
   - So we have to do something slow and/or expensive to find the label;s; e.g.  ask an expert, go hunt for them in the real world.
   - The first time we find the $Y$ values, that incurs a one-time cost
   - After that, the labels can be access for free.

- Just for simplicity, assume we a model can inputs $X$ values to predict for good $g$ or bad $b$:

|n|Task | Notes|
|-:|:-----:|:------|
|1|Sample a little  | Get a get a few $Y$ values (picked at random?) |
|2|Learn a little   | Build a tiny model from that sample|
|3| Reflect | Compute $b,r$|
|4| Acquire         | Label an example that (e.g.) maximizes $b/r$ then it to the sample.|
|5| Repeat          | Goto 2|

So, an active learner
tries to learn $f$ using a lot of cheap  $X$ values, but very few
$Y$ values-- since they are more expensive to access.
Active learners know that they can learn better (faster, with fewer $Y$ values)
if they can select their own training data:

- Given
what we have seen so far...
- Active learners  guess what is be the next more informative
$Y$ labels to collect.. 

### Training Data

Active learners spend much time reasoning about the $X$  values (which are cheap
to collect) before deciding which dependent variables to collect next.
A repeated result is that this tactic can produce good models, with minimal
information about the dependent variables.

For training purposes we explore all this using csv files where "?" denotes missing values.
Row one  list the columns names, defining the roles of the columns:

- NUMeric column names start with an upper case letter.
- All other columns are SYMbolic.
- Names ending with "+" or "-" are goals to maximize/minimize
- Anything ending in "X" is a column we should ignore.

For example, here is data where the goals are `Lbs-,Acc+,Mpg+`
i.e. we want to minimize car weight and maximize acceleration
and maximize fuel consumption.

     Clndrs   Volume  HpX  Model  origin  Lbs-  Acc+  Mpg+
     -------  ------  ---  -----  ------  ----  ----  ----
      4       90      48   78     2       1985  21.5   40
      4       98      79   76     1       2255  17.7   30
      4       98      68   77     3       2045  18.5   30
      4       79      67   74     2       2000  16     30
      ...
      4      151      85   78     1       2855  17.6   20
      6      168      132  80     3       2910  11.4   30
      8      350      165  72     1       4274  12     10
      8      304      150  73     1       3672  11.5   10
      ------------------------------      ----------------
        independent features (x)          dependent goals (y)

Note that the top rows are
better than the bottom ones (lighter, faster cars that are
more economical).

- Multi-objective learners find a model that selects for the best rows, based on multiple goal.s
  - Aside: most learners support single objective classifiers (for one symbolic column) or regression
    (for one numeric column).
- EZR's active learner, does the same multi-objective task,  but
  with very few peeks at the goal y values.
  - Why? Since it usually very cheap to get `X` but very expensive to get `Y`.

For testing  purposes here, all the examples explored here come with  all their  $Y$ values.

- We just take great care in the code to record  how many rows we use to look up $Y$ labels.

## AI Notes

### Aggregation Functions
To sort the data, all the goals have to be aggregated into one function. Inspired by the MOEA/D algorithm[^zhang07],
EZR uses the 
Chebyshev function that returns the max difference between the goal values and the
best possible values. The rows shown above are sorted top to bottom, least to most Chebyshev values
(so the best rows, with smallest Chebyshev, are shown at top).


[^zhang07]: Q. Zhang and H. Li, "MOEA/D: A Multiobjective Evolutionary Algorithm Based on Decomposition," in IEEE Transactions on Evolutionary Computation, vol. 11, no. 6, pp. 712-731, Dec. 2007, doi: 10.1109/TEVC.2007.892759. 

Chebyshev is very simple to code. We assume a lost of goal columns `self.cols.y` each of which  knows:

- its column index `col.at`
- How to `norm`alize values 0..1, min..max using `col.norm(x)`
- What is the best value `col.goal`:
  - For goals to minimize, like "Lbs-", `goal=0`.
  - For goals to maximize, like "Mpg+", `goal=1`.


```py
@of("Compute Chebyshev distance of one row to the best `y` values.")
def chebyshev(self:DATA,row:row) -> number:
  return  max(abs(col.goal - col.norm(row[col.at])) for col in self.cols.y)

@of("Returns 0..1 for min..max.")
def norm(self:NUM, x) -> number:
  return x if x=="?" else  ((x - self.lo) / (self.hi - self.lo + 1E-32))
```
When we say "rank DATA", we mean sort all the rows by their Chebyshev distance:

```py
@of("Sort rows by the Euclidean distance of the goals to heaven.")
def chebyshevs(self:DATA) -> DATA:
  self.rows = sorted(self.rows, key=lambda r: self.chebyshev(r))
  return self
```

### Configuration
Other people define their command line options separate to the settings.
That is they have to define all those settings twice

This code parses the settings from the __doc__ string (see the SETTINGS class). So  the help
text and the definitions of the options can never go out of sync.

### Classes
This  code has only a few main classes:  SETTINGS, DATA, COLS, NUM, SYM

- SETTINGS handles the config settings.
  - The code can access these settings via the `the` variable (so `the = SETTINGS()`).
- NUM, SYM, COL (the super class of NUM,SYM). These classes summarize each column.
  - NUMs know mean and standard deviation (a measure of average distance of numbers to the mean)
    - $\sigma=\sqrt{\frac{1}{N-1} \sum_{i=1}^N (x_i-\overline{x})^2}$
  - SYMs know mode (most common symbol) and entropy (a measure of how often we see different symbols)
    - entropy = $-\sum_{i=1}^n p(x_i) \log_2 p(x_i)$
  - Mean and mode are both measures of central tendency
  - Entropy and standard deviation are measures of confusion.
    - The lower their values, the more likely we can believe in the central tendency
- DATA stores `rows`, summarized  in `cols` (columns).
- COLS is a factory that takes a list of names and creates the columns. 
  - All the columns are stored in `all` (and some are also stored
    in `x` and `y`).

```py
@dataclass
class COLS:
  names: list[str]   # column names
  all  : list[COL] = LIST()  # all NUMS and SYMS
  x    : list[COL] = LIST()  # independent COLums
  y    : list[COL] = LIST()  # dependent COLumns
  klass: COL = None
```
To build the columns, COLS looks at each name's  `a,z` (first and last letter).

- e.g. `['Clndrs', 'Volume', 'HpX', 'Model','origin', 'Lbs-', 'Acc+',  'Mpg+']`


```py
  def __post_init__(self:COLS) -> None:
    for at,txt in enumerate(self.names):
      a,z = txt[0],txt[-1]
      col = (NUM if a.isupper() else SYM)(at=at, txt=txt)
      self.all.append(col)
      if z != "X":
        (self.y if z in "!+-" else self.x).append(col)
        if z=="!": self.klass = col
        if z=="-": col.goal = 0
```
### Smarts

#### Bayes classifier

When you have labels, a simple and fast technique is:

- Divide the rows into different labels,
- Collect statistics independently for each label. For us, this means building one DATA for each label.
- Then ask how likely is a row to belong to each DATA?
  - Internally, this will become a recursive call asking how likely am I to belong to each _x_ column of the data

The probability of `x` belong to a column is pretty simple:

```py
@of("How much a SYM likes a value `x`.")
def like(self:SYM, x:any, prior:float) -> float:
  return (self.has.get(x,0) + the.m*prior) / (self.n + the.m)

@of("How much a NUM likes a value `x`.")
def like(self:NUM, x:number, _) -> float:
  v     = self.sd**2 + 1E-30
  nom   = exp(-1*(x - self.mu)**2/(2*v)) + 1E-30
  denom = (2*pi*v) **0.5
  return min(1, nom/(denom + 1E-30))
```
The likelihood of a row belonging to a label, given new evidence, is the prior probability of the label times the probability of
the evidence. 
For example, if we have three oranges and six apples, then the prior on oranges is 33\%.

For numerical methods reasons, we add tiny counts to the attribute and class frequencies ($k=1,m=2$)
and treat all the values as logarithms (since these values can get real small, real fast)
```py
@of("How much DATA likes a `row`.")
def loglike(self:DATA, r:row, nall:int, nh:int) -> float:
  prior = (len(self.rows) + the.k) / (nall + the.k*nh)
  likes = [c.like(r[c.at], prior) for c in self.cols.x if r[c.at] != "?"]
  return sum(log(x) for x in likes + [prior] if x>0)
```

#### Active Learner

The active learner uses a Bayes classifier to guess the likelihood that an unlabeled example
should be labeled next.

1. All the unlabeled data is split into a tiny `done` set and a much larger `todo` set
2. All the `done`s are labeled, then ranked, then divided into $\sqrt{N}$ _best_ and $1-\sqrt{N}$ _rest_.
3. Some sample of the `todo`s are the sorted by their probabilities of being _best_ (B), not _rest_ (R)
   - The following code uses $B-R$ 
   - But these values ore logs so this is really $B/R$.
4. The top item in that sort is then labelled and move to done.
   - And the cycle repeats

```py
@of("active learning")
def activeLearning(self:DATA, score=lambda B,R: B-R, generate=None, faster=True ):
  def ranked(rows): return self.clone(rows).chebyshevs().rows

  def todos(todo):
    if faster: # Apply our sorting heuristics to just a small buffer at start of "todo"
       # Rotate back half of the buffer to end of list. Shift left to fill in the gap.
       n = the.buffer//2
       return todo[:n] + todo[2*n: 3*n],  todo[3*n:] + todo[n:2*n]
    else: # Apply our sorting heustics to all of todo.
      return todo,[]

  def guess(todo:rows, done:rows) -> rows:
    cut  = int(.5 + len(done) ** the.cut)
    best = self.clone(done[:cut])  # --------------------------------------------------- [2]
    rest = self.clone(done[cut:])
    a,b  = todos(todo) 
    if generate: # don't worry about this bit
      return self.neighbors(generate(best,rest), a) + b  # ----------------------------- [3]
    else:
      key  = lambda r: score(best.loglike(r, len(done), 2), rest.loglike(r, len(done), 2))
      return  sorted(a, key=key, reverse=True) + b # ----------------------------------- [3]

  def loop(todo:rows, done:rows) -> rows:
    for k in range(the.Last - the.label):
      if len(todo) < 3 : break
      top,*todo = guess(todo, done)
      done     += [top]   # ------------------------------------------------------------ [3]
      done      = ranked(done)
    return done

  return loop(self.rows[the.label:], ranked(self.rows[:the.label])) #------------------- [1]
```
The default configs here is  `the.label=4` and `the.Last=30`; i.e. four initial evaluations, then 26
evals after that.

TL;DR: to explore better methods for active learning:

- change the `guess()` function 
- and  do something, anything with the unlabeled `todo` items (looking only at the x values, not the y values).

## SE notes:


Programming _idioms_ are low-level patterns specific to a particular programming language. For example,
see [decorators](#decorators) which are a Python construct

Idioms are small things. Bigger than idioms are  _patterns_ : elegant solution to a recurring problem. 
Some folks have proposed [extensive catalogs of patterns](https://en.wikipedia.org/wiki/Software_design_pattern). 
These are worth reading. As for me, patterns are things I reuse whenever I do development in any languages.
This code uses many patterns (see below). 

Even bigger than patterns are _architectural style_ is a high-level conceptual view of how the system will be created, organized and/or operated.

### Architectural Styles

This code is `pipe and filter`. It can accept code from some prior process or if can read a file directly. These
two calls are equivalent (since "-" denotes standard input). This pile-and-filter style is important since

```
python3.13 -B ezr.py -t ../moot/optimize/misc/auto93.csv -e _mqs
cat ../moot/optimize/misc/auto93.csv | python3.13 -B ezr.py -t -  -e _mqs
```
(Aside: to see how to read from standard input or a file, see `def csv` in the source code.)

Pipe-and-filters are a very famous architectural style:

> Doug McIlroy, Bell Labs, 1986:
<em>“We should have some ways of coupling programs like garden hose....
Let programmers screw in another segment when it becomes necessary
to massage data in another way....
Expect the output of
 every program to become the input to another, as yet unknown,
 program. Don’t clutter output with extraneous information.”</em>

Pipes changed the whole idea of UNIX:

- Implemented in 1973 when ("in one feverish night", wrote McIlroy) by  Ken Thompson.
- “It was clear to everyone, practically minutes after the system
came up with pipes working, that it was a wonderful thing. Nobody
would ever go back and give that up if they could.”
- The next day", McIlroy writes, "saw an unforgettable orgy of one-liners
as everybody joined in the excitement of plumbing."

For example, my build files have help text after a `##` symbol. The following script prints a little help text describing
that build script. It is a pipe between grep, sort, and awk
Note the separation of concerns (which means that now our task divides into tiny tasks, each of which can be optimized separately):

- `grep` handles feature extraction from the build file;
- `sort` rearranges the contents alphabetically 
- `gawk` handles some formatting trivia.

```makefile
help: ## print help
	printf "\n#readme\nmake [OPTIONS]\n\nOPTIONS:\n"
	grep -E '^[a-zA-Z_\.-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| sort \
		| awk 'BEGIN {FS = ":.*?## "}\
	               {printf "  \033[36m%-10s\033[0m %s\n", $$1, $$2}'
```
This produces:
```
% make help

#readme
make [OPTIONS]

OPTIONS:
  README.md  update README.md, publish
  help       print help
  push       commit to Git. 
```
Pipes are seen in  scripting environments and are used a lot in
modern languages.e .g. in "R". Compare how many gallons of gas I would need for a 75 mile trip among 4-cylinder cars:

```r
library(dplyr) # load dplyr for the pipe and other tidy functions
data(mtcars) # load the mtcars dataset

df <- mtcars %>%               # take mtcars. AND THEN...
    filter(cyl == 4) %>%       # filter it to four-cylinder cars, AND THEN...
    select(mpg) %>%            # select only the mpg column, AND THEN...
    mutate(car = row.names(.), # add a column for car name and # gallons used on a 75 mile trip
    gallons = mpg/75)
```
#### Social patterns: Coding for Teams

This code is poorly structured for team work:

- For teams, better to have tests in  separate file(s) 
  - If multiple test files, then many people can write their own special tests
  - When  tests are platform-dependent, it is good to be able to modify the tests without modifying the main thing;
- For teams,  better to have code in multiple files:
  - so different people can work in separate files (less chance of edit conclusions)
- This code violates known [Python formatting standards (PEP 8)](https://peps.python.org/pep-0008/) which
  is supported by so many tools; e.g. [Black](https://github.com/psf/black) and [various tools in VScode](https://code.visualstudio.com/docs/python/formatting)
  - Consider to have commit hooks to re-format the code to something more usual
- My use of the [of](#decorators) is highly non-standard. Teams would probably want to change that.

#### Pattern: All code need doco

Code has much auto-documentation
- functions have type hints and doc strings
- help string at front (from which we parse out the config)
- worked examples (at back)

For examples of methods for adding that doco, see `make help` command above.

#### Pattern: All code needs tests

> Maurice Wilkes recalled the exact moment he realized the importance of debugging: 
<em>“By June 1949, people had begun to realize that it was not so easy to get a program right as 
had at one time appeared. It was on one of my journeys between the EDSAC room and the 
punching equipment that the realization came over me with full force that a good part of the 
remainder of my life was going to be spent in finding errors in my own programs.”</em>

Half the time of any system is spent in testing. Lesson: don't code it the night before.

Testing is more than just "finding bugs". Test suites are a great way to communicate code and to offer
continuous quality assurances.

- Tests offer little lessons on how to use the code.
- Teams sharing code can rerun the tests, all the time, to make sure their new code does not break old code.
  - Caveat: that only works if the tests are fast unit tests.

Exr.py has tests (worked examples at back); about a quarter of the code base

- any method eg.method can be called from the command line using. e.g. to call egs.mqs:
  - python3 ezr.py -e mqs

There is much more to say about tests. That is another story and will be told another time.


####  Pattern: Configuration
- All code has config settings. Magic numbers should not be buried in the code. They should be adjustable
      from the command line (allows for easier experimentation).
- BTW, handling the config gap is a real challenge. Rate of new config grows much faser than rate that  people
      understanding those options[^Takwal]. Need active learning  To explore that exponentially large sapce!

#### Pattern: Function vs Object-Oriented

Object-oriented code is groups by class. But some folks doubt that approach:

- [Does OO Sync With the Way we Think?](https://www.researchgate.net/publication/3247400_Does_OO_sync_with_how_we_think)
- [Stop writing classes](https://www.youtube.com/watch?v=o9pEzgHorH0)

My code is function-oriented: methods are grouped via method name (see the [of](#decorators) decorator).
This makes it easier to teach retlated concepts (since the concepts are together in the code). 

Me doing this way was inspired by some words of Donald Knth who pointed out that the order with which we want to explains
code may not be the same the order needed by the compiler.
So he wrote a "tangle" system where code and comments, ordered for explaining, was rejigged at load time into
what the compiler needs. I found I could do a small part of Knthu's tangle  with a [5 line decorator](#decorators).


####  Pattern: DRY, not WET
- WET = Write everything twice. 
  - Other people define their command line options separate to the settings.  
  - That is they have to define all those settings twice
- DRY = Dont' repeat yourself. 
  - This code parses the settings from the __doc__ string (see the SETTINGS class)
  - That is, my settings options are DRY.
- When to be DRY
  - If it only occurs once, then ok.
  - If you see it twice, just chill. You can be a little WET
  - if you see it thrice, refactor so "it" is defined only once, then reused elsewhere

#### Pattern: Little Languages

- Operate policy from mechanisms; i.e. the spec from the machinery that uses the spec
- Allows for faster adaption
- In this code:
  - The column names is a "little language" defining objective problems.
  - Parsing __doc__ string makes that string a little language defining setting options.
  - The SETTINGS class uses regular expressions to extract the settings
    - regular expressions are other "little languages"
  - Another "not-so-little" little language: [Makefiles](https://learnxinyminutes.com/docs/make/) handles dependencies and updates

##### Little Languages: Make

Make files let us store all our little command line tricks in one convenient location.
Make development was started by Stuart Feldman in 1977 as a Bell
Labs summer intern (go interns!). It worthy of study since it is widely available on many environments.

There are now many build tools available, for example Apache ANT,
doit, and nmake for Windows. Which is best for you depends on your
requirements, intended usage, and operating system. However, they
all share the same fundamental concepts as Make.

Make has "rules" and
the rules have three parts: target, dependents (which can be empty), and code to build
the target from the dependents.
For example, the following two rules have code that
simplifies our interaction with git. 

- The command `make pull` updates the local files (no big win here)
- The command `make push`  uses `read` to
  collect a string explaining what a git commit is for, then stages the commit, then makes
  the commit, then checks for things that are not committed.

```makefile
pull    : ## download
   git pull

push    : ## save
  echo -en "\033[33mWhy this push? \033[0m"; read x; git commit -am "$$x"; git push; git status
```

For rules with dependents,  the target is not changed unless there are newer
dependents. For example, here is the rule that made this file. Note that this process
needs a bunch of scripts, a css file etc. Make will udpate `docs/%.html` if ever any 
of those dependents change.

```makefile
docs/%.html : %.py etc/py2html.awk etc/b4.html docs/ezr.css Makefile ## make doco: md -> html
	echo "$< ... "
	gawk -f etc/py2html.awk $< \
	| pandoc -s  -f markdown --number-sections --toc --toc-depth=5 \
					-B etc/b4.html --mathjax \
  		     --css ezr.css --highlight-style tango \
					 --metadata title="$<" \
	  			 -o $@ 
```
This means that `make docs/*.html` will  update all the html files at this site. And if we call
this command twice, the second call will do nothing at all since `docs/%.html` is already up to date. This can save a lot of time during
build procedures.

The makefile for any particular project can get very big. Hence, it s good practice to add
an auto document rule (see the `make help` command, above).
Note that this is an example of the _all code needs doco_ pattern (also described above).

##### Little Languages: Regular Expressions

- Example of a "little language"
- Used here to extract settings and their defaults from the `__doc__` string
  - in SETTINGS, using `r"\n\s*-\w+\s*--(\w+).*=\s*(\S+)` (a leading "r" tells Python to define a regular expression)
- Other, simpler Examples:
  - leading white space `^[ \t\n]*` (spare brackets means one or more characters; star means zero or more)
  - trailing white space `[ \t\n]*$` (dollar  sign means end of line)
  - IEEE format number `^[+-]?([0-9]+[.]?[0-9]*|[.][0-9]+)([eE][+-]?[0-9]+)?$` (round brackets group expressions;
    vertical bar denotes "or"; "?" means zero or one)
- Beautiful example, [guessing North Amererican Names using regualr expressions](https://github.com/timm/ezr/blob/main/docs/pdf/pakin1991.pdf)
  - For a cheat sheet on regular expressions, see p64 of that article)
  - For source code, see [gender.awk](https://github.com/timm/ezr/blob/main/etc/gender.awk)
- For other articles on regular expressions:
  - At their core, they can be [surprisingly simple](http://genius.cat-v.org/brian-kernighan/articles/beautiful)
  - Fantastic article: [Regular Expression Matching Can Be Simple And Fast](https://swtch.com/~rsc/regexp/regexp1.html),


### Validation

xval
temoral
XXX

### Python Idioms

#### Magic Methods

Dunder = double underscore = "__"

XXX pos_init init repr

#### Data classes
This code uses dataclasses. These are a great shorthand method for defining classes. All dataclasses supply
their own init and pretty-print methods. For example, here is a class with dataclasses

```py
class Person():
    def __init__(self, name='Joe', age=30, height=1.85, email='joe@dataquest.io'):
        self.name = name
        self.age = age
        self.height = height
        self.email = email
```
Bt with data classes:

```py
from dataclasses import dataclass
@dataclass
class Person():
    name: str = 'Joe'
    age: int = 30
    height: float = 1.85
    email: str = 'joe@dataquest.io'

print(Person(name='Tim', age=1000))
==> Person(name='Tim', age=1000, height=1.85, email='joe@dataquest.io')
```

#### Type hints
In other languages, types are taken very seriously and are the basis for computation.

The Python type system was a bolt-on to later versions of the language. Hence, it is not so well-defined.

But it is a great documentation tools since they let the programmer tell the reader
what goes in and out of their function. 

Firstly, you can define your own types. For example, `classes` stores rows of data about (e.g.) dogs and cats
in a dictionary whose keys are "dogs" and "cats"

```py
data= dict(dogs=[['ralph','poodle',2021],['benhi','labrador',2022]]
           cats=[['miss meow', 'ginger' 2020], etc])
```
We can define these `classes` as follows:

```py
from __future__ import annotations
from typing import Any as any
from typing import List, Dict, Type, Callable, Generator

number  = float  | int   #
atom    = number | bool | str # and sometimes "?"
row     = list[atom]
rows    = list[row]
classes = dict[str,rows] # `str` is the class name
```
Then we can define a classifier as something that accepts `classes` and a new row and returns a guess
as to what class it belongs to:
```py
def classifier(data: classes, example: row) -> str:
  ...
```
Or, for a nearest neighbor classifier, we can define a function that sorts all the rows by the distance to
some new row called `row1` as follows (and here, the nearest neighbor to `row1` is the first item in the returned row.
```py
def neighbors(self:DATA, row1:row, rows:rows=None) -> rows:
  return sorted(rows, key=lambda row2: self.dist(row1, row2))
```

#### Abstraction
(Note that the following abstractions are available in many languages. So are they a pattern? Or an idiom?
I place them here since the examples are Python-specific.)

##### Exception Handling

XXX

##### Iterators

Iterators are things that do some set up, yield one thing, then wait till asked, then yield one other hing,
then wait till asked, then yield another other thing, etc. They are offer a simle interface to some under-lying
complex process.

For example, my code's `csv` function opens a file, removes spaces from each line, skips empty lines,
splits lines on a comma, then coerces each item in the row to some Python type. Note that this
function does not `return`, but it `yields`.

```py
def csv(file) -> Generator[row]:
  infile = sys.stdin if file=="-" else open(file)
  with infile as src:
    for line in src:
      line = re.sub(r'([\n\t\r ]|#.*)', '', line)
      if line: yield [coerce(s.strip()) for s in line.split(",")]

def coerce(s:str) -> atom:
  try: return ast.literal_eval(s)
  except Exception:  return s
```
We can call it this way (note the simplicity of the interface)
```py
for row in csv(fileName): 
   # row is now something like [4,86,65,80,3,2110,17.9,50]
   doSomethhing(fileName)
```
Here's another that implements a cross validation test rig where learners train on
some data, then test on some hold-out.

1. To avoid learn things due to trivial orderings in the file, we shuffle the whole list
2. The shuffled list is then split into `n` bins.
3. For each bin, yield it as the `test` and all the other bins as `rest`.
4. Optionally, only use some random sample of train, train

The following is an m-by-n cross val. That is, from `m` shuffling, yield `n` train,test set pairs.
For the default values (`m=n=5`) this yields 25 train,test set pairs.

```py
def xval(lst:list, m:int=5, n:int=5, some:int=10**6) -> Generator[rows,rows]:
  for _ in range(m):
    random.shuffle(lst)        # -------------------------------- [1]
    for n1 in range (n):
      lo = len(lst)/n * n1      # ------------------------------- [2]  
      hi = len(lst)/n * (n1+1)
      train, test = [],[]
      for i,x in enumerate(lst):
        (test if i >= lo and i < hi else train).append(x) 
      train = random.choices(train, k=min(len(train),some)) # --- [4]
      yield train,test  #---------------------------------------- [3]
```

#### Comprehensions

This code  makes extensive use of comprehensions . E.g. to find the middle of a cluster,
ask each column for its middle point.

```py
@of("Return central tendency of a DATA.")
def mid(self:DATA) -> row:
  return [col.mid() for col in self.cols.all]

@of("Return central tendency of NUMs.")
def mid(self:NUM) -> number: return self.mu

@of("Return central tendency of SYMs.")
def mid(self:SYM) -> number: return self.mode
```

Comprehensions can be to filter data:
```py
>>> [i for i in range(10) if i % 2 == 0]
[0, 2, 4, 6, 8]
```

Here's one for loading tab-separated files with optional comment lines starting with a hash mark:

```
data = [line.strip().split("\t") for line in open("my_file.tab") \
        if not line.startswith('#')]
```

e.g. here are two examples of an  implicit iterator in the argument to `sum`:

```py
@of("Entropy = measure of disorder.")
def ent(self:SYM) -> number:
  return - sum(n/self.n * log(n/self.n,2) for n in self.has.values())

@of("Euclidean distance between two rows.")
def dist(self:DATA, r1:row, r2:row) -> float:
  n = sum(c.dist(r1[c.at], r2[c.at])**the.p for c in self.cols.x)
  return (n / len(self.cols.x))**(1/the.p)
```

E.g here we

1. Use dictionary comprehensions, make a dictionary with one emery list per key,
2. Using list comprehensions, add items into those lists
3. Finally, using dictionary comprehensions, return a  dictionary with one prediction per col.

```py
@of("Return predictions for `cols` (defaults to klass column).")
def predict(self:DATA, row1:row, rows:rows, cols=None, k=2):
  cols = cols or self.cols.y
  got = {col.at : [] for col in cols}                           -- [1]
  for row2 in self.neighbors(row1, rows)[:k]:
    d =  1E-32 + self.dist(row1,row2)
    [got[col.at].append( (d, row2[col.at]) )  for col in cols]  -- [2]
  return {col.at : col.predict( got[col.at] ) for col in cols}  -- [3]
``` 



#### Decorators

- Decorated are functions called at load time that manipulate other functions.
- E.g. the `of` decorator  lets you define methods outside of a function. Here it is used to 
  group together the `mid` (middle) and `div` (diversity) functions. 
  - The `mid`(ddle) of a NUMeric and a SYMbol column are their means and modes. 
  - As to `DATA`, thsee  hold rows which are summarized in `cols`.  The `mid` of those rows is the `mid`
  of the summary for each column.

```python
def of(doc):
  def doit(fun):
    fun.__doc__ = doc
    self = inspect.getfullargspec(fun).annotations['self']
    setattr(globals()[self], fun.__name__, fun)
  return doit

@of("Return central tendency of a DATA.")
def mid(self:DATA) -> row:
  return [col.mid() for col in self.cols.all]

@of("Return central tendency of NUMs.")
def mid(self:NUM) -> number: return self.mu

@of("Return central tendency of SYMs.")
def mid(self:SYM) -> number: return self.mode

@of("Return diversity of a NUM.")
def div(self:NUM) -> number: return self.sd

@of("Return diversity of a SYM.")
def div(self:SYM) -> number: return self.ent()
```
[^Takwal]: [Hey you have given me too many knobs](https://www.researchgate.net/publication/299868537_Hey_you_have_given_me_too_many_knobs_understanding_and_dealing_with_over-designed_configuration_in_system_software), FSE'15

## Try it for yourself

### Get Python3.13

Make sure you are running Python3.13. On Linux and Github code spaces, that command is

```sh
sudo apt update
sudo  apt upgrade
sudo apt install software-properties-common -y
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install python3.13
python3.13 -B --verion
```

### Try one run

```sh
git clone https://github.com/timm/moot
git clone https://github.com/timm/ezr
cd ezr
python3.13 -B erz.py -t ../moot/optimize/misc/auto93.csv -e _mqs
```

### Try a longer run

Do a large run (takes a few minutes: output will appear in ~/tmp/mqs.out; assumes a BASH shell):

```sh
python3.13 -B ezr.py -e _MQS ../moot/optimize/[chmp]*/*.csv | tee ~/tmp/mqs.out
```

### Write your own extensions

Here's a file `extend.py` in the same directory as ezr.py

```py
import sys,random
from ezr import the, DATA, csv, dot

def show(lst):
  return print(*[f"{word:6}" for word in lst], sep="\t")

def myfun(train):
  d    = DATA().adds(csv(train))
  x    = len(d.cols.x)
  size = len(d.rows)
  dim  = "small" if x <= 5 else ("med" if x < 12 else "hi")
  size = "small" if size< 500 else ("med" if size<5000 else "hi")
  return [dim, size, x,len(d.cols.y), len(d.rows), train[17:]]

random.seed(the.seed) #  not needed here, but good practice to always take care of seeds
show(["dim", "size","xcols","ycols","rows","file"])
show(["------"] * 6)
[show(myfun(arg)) for arg in sys.argv if arg[-4:] == ".csv"]
```
On my machine, when I run ...

```sh
python3.13 -B extend.py ../moot/optimize/[chmp]*/*.csv > ~/tmp/tmp
sort -r -k 1,2 ~/tmp/tmp
```
... this prints some stats on the data files: 
```
dim   	size  	xcols 	ycols 	rows  	file
------	------	------	------	------	------
small 	small 	     4	     3	   398	misc/auto93.csv
small 	small 	     4	     2	   259	config/SS-H.csv
small 	small 	     3	     2	   206	config/SS-B.csv
small 	small 	     3	     2	   196	config/SS-G.csv
small 	small 	     3	     2	   196	config/SS-F.csv
small 	small 	     3	     2	   196	config/SS-D.csv
small 	small 	     3	     1	   196	config/wc+wc-3d-c4-obj1.csv
small 	small 	     3	     1	   196	config/wc+sol-3d-c4-obj1.csv
small 	small 	     3	     1	   196	config/wc+rs-3d-c4-obj1.csv
small 	med   	     5	     2	  1080	config/SS-I.csv
small 	med   	     3	     2	  1512	config/SS-C.csv
small 	med   	     3	     2	  1343	config/SS-A.csv
small 	med   	     3	     2	   756	config/SS-E.csv
small 	hi    	     5	     3	 10000	hpo/healthCloseIsses12mths0011-easy.csv
small 	hi    	     5	     3	 10000	hpo/healthCloseIsses12mths0001-hard.csv
med   	small 	     9	     1	   192	config/Apache_AllMeasurements.csv
med   	med   	    11	     2	  1023	config/SS-P.csv
med   	med   	    11	     2	  1023	config/SS-L.csv
med   	med   	    11	     2	   972	config/SS-O.csv
med   	med   	    10	     2	  1599	misc/Wine_quality.csv
med   	med   	     9	     3	   500	process/pom3d.csv
med   	med   	     6	     2	  3840	config/SS-S.csv
med   	med   	     6	     2	  3840	config/SS-J.csv
med   	med   	     6	     2	  2880	config/SS-K.csv
med   	med   	     6	     1	  3840	config/rs-6d-c3_obj2.csv
med   	med   	     6	     1	  3840	config/rs-6d-c3_obj1.csv
med   	med   	     6	     1	  2880	config/wc-6d-c1-obj1.csv
med   	med   	     6	     1	  2866	config/sol-6d-c2-obj1.csv
med   	hi    	    11	     2	 86058	config/SS-X.csv
med   	hi    	     9	     3	 20000	process/pom3c.csv
med   	hi    	     9	     3	 20000	process/pom3b.csv
med   	hi    	     9	     3	 20000	process/pom3a.csv
hi    	small 	    22	     4	    93	process/nasa93dem.csv
hi    	med   	    38	     1	  4653	config/SQL_AllMeasurements.csv
hi    	med   	    21	     2	  4608	config/SS-U.csv
hi    	med   	    17	     5	  1000	process/coc1000.csv
hi    	med   	    17	     3	   864	config/SS-M.csv
hi    	med   	    16	     1	  1152	config/X264_AllMeasurements.csv
hi    	med   	    14	     2	  3008	config/SS-R.csv
hi    	med   	    14	     1	  3456	config/HSMGP_num.csv
hi    	med   	    13	     3	  2736	config/SS-Q.csv
hi    	hi    	    23	     4	 10000	process/xomo_osp2.csv
hi    	hi    	    23	     4	 10000	process/xomo_osp.csv
hi    	hi    	    23	     4	 10000	process/xomo_ground.csv
hi    	hi    	    23	     4	 10000	process/xomo_flight.csv
hi    	hi    	    17	     2	 53662	config/SS-N.csv
hi    	hi    	    16	     2	 65536	config/SS-W.csv
hi    	hi    	    16	     2	  6840	config/SS-V.csv
hi    	hi    	    12	     2	  5184	config/SS-T.csv
```

Try modifying the output to add columns to report counts of
the number of symbolic and numeric columns.
