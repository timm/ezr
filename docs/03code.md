% A quick peek at exr.py
% Tim Menzies
% August 5, 2024

## What is active learning?

The human condition is that we have to make it up as we go along.
We are always acting with partial knowledge,
before all the facts are in. 

For example,
if we want to buy a used car then  a single glance at a car lot
tells us much about hundreds of 
car make, model, color, number of doors, ages of cars, etc.
But it takes much longer to work out  know acceleration or
miles per hour (you have to drive  each car around
for the afternoon).
So the question becomes, what is the best strategy for exploring the fast-to-find features (e.g. car color)
in order to build predictors from the slower-to-find features (e.g. car acceleration)

Active learners say that we learn better if we can select our own training data. Given
what we have seen so far, active learners  guess what is be the next more informative
question. 
Active learners spend much time reasoning about the independent variables (which are cheap
to collect) before deciding which dependent variables to collect next.
A repeated result is that this tactic can produce good models, with minimal
information about the dependent variables..

### Words to watch for:

- Terms: _dependent, independent, goals, aggregation function, chebyshev_
- Classes: _DATA, COLS, NUM, SYM_
- Variables:  _row_, _rows_, _done_ (which divides into _best_ and _rest_); _todo_
- Synonyms: _features_,  _attributes_, _goals_

## Training Data

For training purposes we explore all this using consists of csv files where "?" denotes missing values.
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

- Multi-objective learners find a model that selects for the best rows.
- Active learning, applied to the same task, does the same thing but
  does so with very few peeks at the goal y values.
  - Why? Since it usually very cheap to get `x` but very expensive to get `y`.

### Aggregation Functions
To sort the data, all the goals have to be aggregated into one function. THis code uses the 
Chebyshev function that returns the max difference between the goal values and the
best possible values.

```py
@of("Compute Chebyshev distance of one row to the best `y` values.")
def chebyshev(self:DATA,row:row) -> number:
  return  max(abs(col.goal - col.norm(row[col.at])) for col in self.cols.y)
```
Note that

- `goal` is set to 0,1 for goals we want to minimize or maximize.
- `abs(col.goal - col.norm(row[col.at]))` returns a distance in the range 0..1 for  distance to best. 
- `norm` is short form "normalization" and makes goals 0..1 for lo...hi. So

```py
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
### Configuraion
Other people define their command line options separate to the settings.
That is they have to define all those settings twice

This code parses the settings from the __doc__ string (see the SETTINGS class). So  the help
text and the definitions of the options can never go out of sync.

### Decorators

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


### Active Learner

The active learner uses a Bayes classifier.

- ALl the unlabeled data is split into a tiny `done` set and a much larger `todo` set
- All the `done`s are labeled and ranked and divided into $\sqrt{N}$ _best_ and $1-\sqrt{N}$ _rest_.
- Some sample of the `todo`s are the sorted by their probabilities of being _best_ (B), not _rest_ (R)
  - The following code uses $B-R$
  - But these values ore logs so this is really $B/R$.
- The top item in that sort is then labelled.
- And the cycle repeats

```py
@of("active learning")
def activeLearning(self:DATA, score=lambda B,R: B-R, generate=None, faster=True ):
  def ranked(rows): return self.clone(rows).chebyshevs().rows

  def todos(todo):
    if faster: # swap back half of the buffer with later items
       n= the.buffer//2
       a1,a2 = todo[:n], todo[n:2*n]
       b1,b2 = todo[2*n:3*n], todo[3*n:]
       return a1 + b1, b2 + a2
    else:
      return todo,[]

  def guess(todo:rows, done:rows) -> rows:
    cut  = int(.5 + len(done) ** the.cut)
    best = self.clone(done[:cut])
    rest = self.clone(done[cut:])
    a,b  = todos(todo)
    if generate: # don't worry about this bit
      return self.neighbors(generate(best,rest), a) + b # todo[:some]) + todo[some:] 
    else:
      key  = lambda r: score(best.loglike(r, len(done), 2), rest.loglike(r, len(done), 2))
      return  sorted(a, key=key, reverse=True) + b

  def loop(todo:rows, done:rows) -> rows:
    for k in range(the.Last - the.label):
      if len(todo) < 3 : break
      top,*todo = guess(todo, done)
      done     += [top]
      done      = ranked(done)
    return done

  return loop(self.rows[the.label:], ranked(self.rows[:the.label]))
```
The default configs here are the.label=4 and the.Last=30; i.e. four initial evaluations, then 26
evals after that.

TL;DR: to explore better methods for active learning:

- change the `guess()` function 
- and  do something, anything with the unlabelled `todo` items (looking only at the x values, not the y values).

## SE notes:

- Code has doco : functions have type hints and doc strings;  help string at front, worked examples (at back)
- My code is function-oriented: methods are grouped via method name. Many language are function-oriented; e.g.
  Julia, CLOS.
- Code has tests (worked examples at back); about a quarter of the code base
  - any method eg.method can be called from the command line using. e.g. to call egs.mqs:
      - python3 ezr.py -e mqs
- My settings are  DRY, not WET
  - WET = Write everything twice. 
    - Other people define their command line options separate to the settings.  
    - That is they have to define all those settings twice
  - DRY = Dont' repeat yourself. 
    - This code parses the settings from the __doc__ string (see the SETTINGS class)
    - That is, my settings options are DRY.
- Little languages
  - Operate policy from mechanisms; i.e. the spec from the machinery that uses the spec
  - Allows for faster adaption
  - In this code:
    - The column names is a "little language" defining objective problems.
    - Parsing __doc__ string makes that string a little language defining setting options.
    - The SETTINGS class uses regular expressions to extract the settings
      - regular expressions are other "little languages"
    - Another "not-so-little" little language: Makefiles, handles dependencies and updates
- Configuration
  - All code has config settings. Magic numbers should not be buried in the code. They should be adjustable
      from the command line (allows for easier experimentation).
  - BTW, handling the config gap is a real challenge. Rate of new config grows much faser than rate of people's
      understanding those options[^Takwal]. Need active learning  To explore that exponentially large sapce!

[^Takwal]: [Hey you have given me too many knobs](https://www.researchgate.net/publication/299868537_Hey_you_have_given_me_too_many_knobs_understanding_and_dealing_with_over-designed_configuration_in_system_software), FSE'15

## Try it for your self

Install test data. Open up a bash shell prompt (e.g. got to Github and open a  codespaces)

```
git clone https://github.com/timm/moot
git clone https://github.com/timm/ezr
cd ezr
chmod +x ezr
./erz -t ../moot/optimize/misc/auto93.csv -e mqs
```
Do a large run (takes a few minutes: output will appear in ~/tmp/mqs.out; assumes a BASH shell):

```
for i in  `ls  ../moot/optimize/[chmp]*/*.csv` ; do python3 ./ezr.py  -t  $i -e mqs ; done  | tee ~/tmp/mqs.out
```

