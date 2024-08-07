% A quick peek at exr.py
% Tim Menzies
% August 5, 2024

## Introduction

### Words to watch for

- SE Notes: _DRY, WET, refactoring, function-oriented, decorators, little languages, configuration_, 
- AI Notes: _active learning, Y,  dependent, X,  independent, goals, labeling, aggregation function, chebyshev, multi-objective
             regression, classification, Bayes classifier, entropy, standard deviation_
- Classes: _DATA, COLS, NUM, SYM_
- Variables:  _row_, _rows_, _done_ (which divides into _best_ and _rest_); _todo_
- Synonyms: 
    - _features_,  _attributes_, _goals_
    - _Y goals dependent_
    - _X independent_

### Quick notes: 

- Download this code: [ezr](https://github.com/timm/ezr/blob/main/ezr.py)
- Down sample 60+ example dadta files: [moot](https://github.com/timm/moot) (MOOT= Multi-Objective Optimization Tests)
- Macro structure of this code:
  - Starts with __doc__ string, from which we parse out the control settings.
  - Ends with a set of examples in the `egs` class which can be called from the command line. E.g. `-e mqs` called `egs.mqs()`.
  - Uses a  [a function-oriented style](#decorators),  where methods are grouped by name, not class.

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
- _Labeling_ is the process of finding the $Y$ values, before we know the $f$ function 
   - So we have to do something slow and/or expensive to find the label;s; e.g.  ask an expert, go hunt for them in the real world.
   - The first time we find the $Y$ values, that incurs a one-time cost
   - After that, the labels can be access for free.



So, an active learner
tries to learn $f$ using a lot of cheap  $X$ values, but very few
$Y$ values-- since they are more expensive to access.
Active learners know that they can learn better (faster, with fewer $Y$ values)
if they can select their own training data:

- Given
what we have seen so far...
- Active learners  guess what is be the next more informative
$Y$ labels to collect.. 

Active learners spend much time reasoning about the $X$  values (which are cheap
to collect) before deciding which dependent variables to collect next.
A repeated result is that this tactic can produce good models, with minimal
information about the dependent variables.

## Training Data

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

### Classes
This  code has only a few main classes:  DATA, COLS, NUM, SYM

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
### Configuration
Other people define their command line options separate to the settings.
That is they have to define all those settings twice

This code parses the settings from the __doc__ string (see the SETTINGS class). So  the help
text and the definitions of the options can never go out of sync.

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

### Patterns 

Programming _idioms_ are low-level patterns specific to a particular programming language. For example,
see [decorators](#decorators) which are a Python construct

Idioms are small things. Bigger than idioms are  _patterns_ : elegant solution to a recurring problem. 
Some folks have proposed [extensive catalogs of patterns](https://en.wikipedia.org/wiki/Software_design_pattern). 
These are worth reading. As for me, patterns are things I reuse whenever I do development in any languages.
This code uses many patterns (see below). 

An _architectural style_ is a high-level conceptual view of how the system will be created, organized and/or operated.
This code is `pipe and filter`. It can accept code from some prior process or if can read a file directly. These
two calls are equivalent (since "-" denotes standard input). This pile-and-filter style is important since

```
python3.13 -B ezr.py -t ../moot/optimize/misc/auto93.csv -e _mqs
cat ../moot/optimize/misc/auto93.csv | python3.13 -B ezr.py -t -  -e _mqs
```
(Aside: to see how to read from standard input or a file, see `def csv` in the source code.)

Pipe-and-filters are a very famous artitectural style:

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

#### Pattern: All code need doco

Code has much auto-documentation
- functions have type hints and doc strings
- help string at front (from which we parse out the config)
- worked examples (at back)

Seen a ,ot in modern languges.e .g. in "R". Cpmpare how many gallons of gas I would need for a 75 mile trip among 4-cylinder cars:

```r
library(dplyr) # load dplyr for the pipe and other tidy functions
data(mtcars) # load the mtcars dataset

df <- mtcars %>%               # take mtcars. AND THEN...
    filter(cyl == 4) %>%       # filter it to four-cylinder cars, AND THEN...
    select(mpg) %>%            # select only the mpg column, AND THEN...
    mutate(car = row.names(.), # add a column for car name and # gallons used on a 75 mile trip
    gallons = mpg/75)
```

#### Pattern: All code needs tests

> Maurice Wilkes recalled the exact moment he realized the importance of debugging: 
<em>“By June 1949, people had begun to realize that it was not so easy to get a program right as 
had at one time appeared. It was on one of my journeys between the EDSAC room and the 
punching equipment that the realization came over me with full force that a good part of the 
remainder of my life was going to be spent in finding errors in my own programs.”</em>

Code has tests (worked examples at back); about a quarter of the code base

- any method eg.method can be called from the command line using. e.g. to call egs.mqs:
  - python3 ezr.py -e mqs

#### Pattern: Function vs Object-Oriented

Object-oriented code is groups by class. But some folks doubt that approach:

- [Does OO Sync With the Way we Think?](https://www.researchgate.net/publication/3247400_Does_OO_sync_with_how_we_think)
- [Stop writing classes](https://www.youtube.com/watch?v=o9pEzgHorH0)

My code is function-oriented: methods are grouped via method name (see the [of](#decorators) decorator).
This makes it easier to teach retlated concepts (since the concepts are together in the code). 

Me doing this way was insrued by some words of Donal Knth who pointed out that the order with which we want to explains omce code may not be the samas the order needed by the compiler.
So he wrote a "tangle" system where code, ordered for expalanation, was rejigged at load time into
what the compiler needs. I found I could do much the same like with a [5 line decorator](#decorators).


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

#### Pattern: Regular Expressions

- Example of a "little language"
- Used here to extract settings and their defaults from the `__doc__` string
  - in SETTINGS, using `r"\n\s*-\w+\s*--(\w+).*=\s*(\S+)` (a leading "r" tells Python to define a regular expression)
- Other, simpler Examples:
  - leading white space `^[ \t\n]*` (spare brackets means one or more characters; star means zero or more)
  - trailing white space `[ \t\n]*$` (dollar  sign means end of line)
  - IEEE format number `^[+-]?([0-9]+[.]?[0-9]*|[.][0-9]+)([eE][+-]?[0-9]+)?$` (round brackets group expressions;
    vertical bar denotes "or"; "?" means zero or one)
  - Beautiful example, [guessing North Amererican Names using regualr epxressions](https://github.com/timm/ezr/blob/main/docs/pdf/pakin1991.pdf)
    - For a cheat sheet on regular expressions, see p64 of that article)
    - For source code, see [gender.awk](https://github.com/timm/ezr/blob/main/etc/gender.awk)
  - For other articles on regular expressions:
    - At their core, they can be [surprisingly simple](http://genius.cat-v.org/brian-kernighan/articles/beautiful)
    - Fantastic article: [Regular Expression Matching Can Be Simple And Fast](https://swtch.com/~rsc/regexp/regexp1.html),


####  Pattern: Configuration
- All code has config settings. Magic numbers should not be buried in the code. They should be adjustable
      from the command line (allows for easier experimentation).
- BTW, handling the config gap is a real challenge. Rate of new config grows much faser than rate of people's
      understanding those options[^Takwal]. Need active learning  To explore that exponentially large sapce!

### Idioms

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

Here's one for loading tab-separated files with optional comment lines starting with a hash mark:

```
data = [line.strip().split("\t") for line in open("my_file.tab") \
        if not line.startswith('#')]
```

Comprehensions can be to filter data:
```
>>> [i for i in range(10) if i % 2 == 0]
[0, 2, 4, 6, 8]
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

```
sudo apt update
sudo  apt upgrade
sudo apt install software-properties-common -y
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install python3.13
python3.13 -B --verion
```

### Try one run

```
git clone https://github.com/timm/moot
git clone https://github.com/timm/ezr
cd ezr
python3.13 -B erz.py -t ../moot/optimize/misc/auto93.csv -e _mqs
```

### Try a longer run

Do a large run (takes a few minutes: output will appear in ~/tmp/mqs.out; assumes a BASH shell):

```
python3.13 -B ezr.py -e _MQS ../moot/optimize/[chmp]*/*.csv | tee ~/tmp/mqs.out
```

### Write your own extensions

Here's a file `extend.py` in the same directory as ezr.py

```py
import sys,random
from ezr import the, DATA, csv

def nth(k): return lambda z: z[k]

def myfun(i,train):
  random.seed(the.seed) #  not needed here, bt good practice to always take care of seeds
  d    = DATA().adds(csv(train))
  x    = len(d.cols.x)
  size = len(d.rows)
  dim  = "lo"     if x < 5     else ("med" if x < 10    else "hi")
  size = "small" if size< 500 else ("med" if size<5000 else "hi")
  return [i,dim, size, x, len(d.cols.y), len(d.rows), train]

print("n", "dim", "size","xcols","ycols","rows","file",sep="\t")
print(*["----"] * 7,sep="\t")
[print(*myfun(i,arg),sep="\t") for i,arg in enumerate(sys.argv)  if arg[-4:] == ".csv"]
```
On my machine, when I run

```py
python3.13 -B extend.py ../moot/optimize/[comp]*/*.csv
```
This prints some stats on the data files: 
```
n   dim    size    xcols  ycols    rows    file
---  ----  ----    ----   ----    ----    ----
1    med    small  9      1       192    ../moot/optimize/config/Apache_AllMeasurements.csv
2    hi     med    14     1       3456    ../moot/optimize/config/HSMGP_num.csv
3    hi     med    38     1       4653    ../moot/optimize/config/SQL_AllMeasurements.csv
4    lo     med    3      2       1343    ../moot/optimize/config/SS-A.csv
5    lo     small  3      2       206    ../moot/optimize/config/SS-B.csv
6    lo     med    3      2       1512    ../moot/optimize/config/SS-C.csv
```

Try modifying the output to add columns to report counts of
the number of symbolic and numeric columns.
