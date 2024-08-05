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

- Terms: _dependent, independent, goals, accusation function_
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

### Classes
This  code has four main classes:

- NUM, SYM, COL (the super class of NUM,SYM). These classes summarize each column.
  - NUMs know mean and standard deviation (a measure of average distance of numbers to the mean)
    - $\sigma=\sqrt{\frac{1}{N-1} \sum_{i=1}^N (x_i-\overline{x})^2}$
  - SYMs know mode (most common symbol) and entropy (a measure of how often we see different symbols)
    - entropy = $-\sum_{i=1}^n p(x_i) \log_2 p(x_i)$
  - Mean and mode are both measures of central tendency
  - Entropy and standard deviation are measures of confusion.
    - The lower their values, the more likely we can believe in the central tendency
- DATA which stores `rows`, summarized  in `cols` (columns).
- COLS is a factory that takes a list of names and creates the columns. 
  All the columns are stored in `all` (and some are also stored
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
To build the columns, COLS looks at each name's  `a,z` (first and last letter):
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

### Configuraion


## SE notes:

- Code has doco : functions have type hints and doc strings;  help string at front, worked examples (at back)
- My code is function-oriented: methods are grouped via method name. Many language are function-oriented; e.g.
  Julia, CLOS.## Python notes
- Code has tests (worked examples at back); about a quarter of the code base
  - any method eg.method can be called from the command lie using
      - python3 ezr.py -e method

## Try it for your self

Install test data. Open up a bash shell prompt (e.g. got to Github and open a  codespaces)

```
git clone https://github.com/timm/moot
git clone https://github.com/timm/ezr
cd ezr
chmod +x ezr
./erz -t ../moot/optimize/misc/auto93.csv -e mqs
```
Do a large run (takes a few minutes)

for i in  `ls  ../moot/optimize/*/*.csv` ; do d=~/tmp/moot/$i ; mkdir python3 ./ezr.py  -t  $i -e mqs | tee ~/tmp/mo; done

```
git clone http://gith

