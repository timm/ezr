.

# Easier XAI

by Tim Menzies and the EZRites  
(c) 2024, CC-SA 4.0  
http://github.com/timm/ezr


kilowatt-hours per 100 miles (kWh/100m);

>[!NOTE]
> <b> We present a successful  experiment in coding XAI (explainable AI) in the fewest
lines of code. The code is written in functional style (so no classes
and lots of list comprehensions).  The work is guided by the
[5-lines-per-function](https://coderanch.com/t/733272/engineering/Lines-Code-lines)
rule (which, sometimes, we break).  Instead of coding standard AI
algorithms, we look under-the-hood to find ways to combine all that
functionality into just five classes (NUM,SYM,DATA,COLS,XY).  Further,
we assume that "less is more", both in our coding style and in our
data processing (so the first we do with  data, is throw most of
it away).</b>

In the beginning there was the data and the data was without form,
and void; and confusion was upon the face of the humans.  And the
programmer  said, let there be workflows that 
succinctly  explain the contrast between good and bad things [^whycon] [^conplan]
And then there was light.

[^whycon]: difference between things can be shorter than the things
[^conplan]: apply the contrast. does it change anything? ktest. lime,

And in that workflow there was tabular data whose first row defined
column types. And upper case words were numeric and the others were
symbols. And some of the words were goals have special marks
denoting things we wanted to predict ("!") or  minimize ("-") or maximize ("+").  So
If our data was about cars then it might look like this:

```
Clndrs  Volume  HpX  Model  origin  Lbs-  Acc+  Mpg+
8       304     193  70     1       4732  18.5  10
8       360     215  70     1       4615  14    10
8       307     200  70     1       4376  15    10
...     ...     ...  ...    ...     ...   ...   ...
```

Here,  we have decided to ignore horsepower (so it ends
with and `X`). Also, we want light cars (since they are cheaper to
build and buy), fast acceleration, and good miles per gallon. So
these get marked with `Lhs-,Acc+,Mpg+`

To be more specific, this data set has around 400 cars.
Using the `d2h` measure (see below), we can sort those cars best to worst.
Lets say the top $\sqrt{N}=20$ items in that sort are "best" and the others
are "rest". Here's every 20th car in that sort, with a line showing the border
between "best" and "rest".
We see that the "best" cars have  much lower weight,
and have much more acceleration and miles per hour. 


```
N       Clndrs   Volume   HpX   Model   origin   Lbs-   Acc+   Mpg+
--       -----   -------  ---   -----   ------   ----   ----   ----
0        4        97       52      82    2       2130    24.6   40
20       4        91       60      78    3       1800    16.4   40
--      ------   -------  ---   -----   ------   ----   ----   ----
40       4       112       88      82    1       2605    19.6   30
60       4       112       88      82    1       2395    18     30
80       4        97       88      72    3       2100    16.5   30
100      4        79       67      74    2       1963    15.5   30
120      4        98       60      76    1       2164    22.1   20
140      4       140       88      78    1       2720    15.4   30
160      4       140       72      71    1       2408    19     20
180      8       260       90      79    1       3420    22.2   20
200      6       250       78      76    1       3574    21     20
220      6       232      100      75    1       2914    16     20
240      6       225      110      78    1       3620    18.7   20
260      6       225      100      76    1       3651    17.7   20
280      6       250       88      71    1       3139    14.5   20
300      8       262      110      75    1       3221    13.5   20
320      8       318      150      70    1       3436    11     20
340      8       400      150      70    1       3761     9.5   20
360      8       351      153      71    1       4154    13.5   10
380      8       400      175      72    1       4385    12     10
```
So now we ask two questions:

1. What is in the contrast between "best" and "rest"?
  That is to say, what attribute ranges select for "best" and let us avoid the "rest"?
  The answer to this question will let us define a method for exploring the better cars and ignoring the worst ones.
2.  How can we answer Question1 with minimum effort? We ask this since there are hard ways, and much easier ways, to answer Question1. The hardest way would be to drive all 400 cars for
   a day each, then write down the observed mileage , acceleration, etc. But can we do better than that? Just
   drive a few cars and let that experience tells us what cars to try next?

Aside: formally, Question1 is a multi-objective explanation problem and Question2 is an active learning problem [^semi].

Of the two questions, the second one is far more interesting.  There are many tasks in this world and only
limited time to collect data and reason about each one. In fact, all of science (and, indeed, much of the
human condition) might
be characterized by "of all the things you we do, how to quickly find out what should we do?". For this question, It turns out we have some very
interesting answers.

The rest of this work answers these two questions. For simplicty's sake, we will explore Question1 before Question2.

[^semi]: Active learning is to a broader area called "semi-supervised
learning", As [Pooja Palod]{(https://www.linkedin.com/pulse/active-learning-same-semi-supervised-pooja-palod/)
says, "Semi supervised and Active Learning are trying to solve same
problem (learn more form unlabeled data) the way in which they do
is different.  Active learning focus on learning from important
examples from unlabeled data ( i.e. labels of some data points are
more informative than others) while semi supervised learning prefer
to use entire unlabeled dataset."

## COLS : managing sets of columns

And the programmer wrote code to turn these names into NUMeric and
SYMbolic columns, then to store all of them in `all` and (for
convenience) also maybe in `x` (for the independent variables) and maybe in `y` (for
the dependent goals that we want to predict or  minimize or maximize).

```python
def _COLS(names: list[str]) -> cols:
  return o(this=COLS, x=[], y=[], all=[], klass=None, names=names)

def COLS(names: list[str]) -> cols:
  i = _COLS(names)
  i.all = [add2cols(i,n,s) for n,s in enumerate(names)]
  return i

def add2cols(i:cols, n:int, s:str) -> col:
  new = (NUM if s[0].isupper() else SYM)(txt=s, at=n)
  if s[-1] == "!": i.klass = new
  if s[-1] != "X": (i.y if s[-1] in "!+-" else i.x).append(new)
  return new
```

## NUM, SYM : incrementally summarizing 

And the code needed some help. NUM and SYM summarize streams of number
and symbols. 

- Both these know the `txt` of their column name; what
column position they are `at`;  and how many `n` items they have
seen so far. 
- SYMs get a count of symbols seen so far in `has`, while for NUMs,
keeping the numbers in `has` is optional.  
- NUMs also track the `lo`est and
`hi`est values seen so far as well as their mean `mu`. And anything not ending
in `-` is a numeric goal to be `maximzed`.

```python
def SYM(txt=" ",at=0) -> sym:
  return o(this=SYM, txt=txt, at=at, n=0, has={})

def NUM(txt=" ",at=0,has=None) -> num:
  return o(this=NUM, txt=txt, at=at, n=0, hi=-1E30, lo=1E30, 
           has=has, rank=0, # if has non-nil, used by the stats package
           mu=0, m2=0, sd=0, maximize = txt[-1] != "-")
```

To distinguish NUMs from SYMs, the programmer added a `this=NUM` and
`this=SYM` flag.

Internally, NUM and SYM are both `o`bjects where `o` is something
that knows how to pretty-print itself.

```python
class o:
  def __init__(i,**d): i.__dict__.update(d)
  def __repr__(i): return i.__class__.__name__+str(show(i.__dict__))

def show(x:any) -> any:
  it = type(x)
  if it == o and x.this is XY: return showXY(x)
  if it == float: return round(x,the.decs)
  if it == list:  return [show(v) for v in x]
  if it == dict:  return "("+' '.join([f":{k} {show(v)}" for k,v in x.items()])+")"
  if it == o:     return show(x.__dict__)
  if it == str:   return '"'+str(x)+'"'
  if callable(x): return x.__name__
  return x
```
## DATA : storing rows, and their summaries

The programmer did place the rows in a DATA object that held the `rows`. Also,
a summary of those rows is maintained in `cols` (which is a COLS object). 

```python
def DATA(src=None, rank=False) -> data:
  i = _DATA()
  [add2data(i,lst) for  lst in src or []]
  if rank: i.rows.sort(key = lambda r:d2h(i,r))
  return i

def add2data(i:data,row1:row) -> None:
  if    i.cols: i.rows.append([add2col(col,x) for col,x in zip(i.cols.all,row1)])
  else: i.cols= COLS(row1)
```

In `add2data()`, when a `row` is added to a DATA, we walk though `i.cols.all`
columns, updating each.  When  a new `row1` is `append()`ed to NUMs,
we update the counters needed to incrementally compute mean and
standard deviation [^welford]. Also, if `num.has` exists, we use
it to cache the observed numeric values (for now, we do not need that cache-- but it will
be needed when  e talk to stats).

[^welford]: https://en.wikipedia.org/wiki/Algorithms_for_calculating_variance

```python
def add2col(i:col, x:any, n=1) -> any:
  "`n` times, update NUM or SYM with one item. Used by `add2data()`." 
  if x != "?":
    i.n += n
    if i.this is NUM: _add2num(i,x,n)
    else: i.has[x] = i.has.get(x,0) + n
  return x

def _add2num(i:num, x:any, n:int) -> None:
  "`n` times, update a NUM with one item. Used by `add2col()`."
  i.lo = min(x, i.lo)
  i.hi = max(x, i.hi)
  for _ in range(n):
    if i.has != None: i.has += [x]
    d     = x - i.mu
    i.mu += d / i.n
    i.m2 += d * (x -  i.mu)
    i.sd  = 0 if i.n <2 else (i.m2/(i.n-1))**.5
```

## Sorting Rows : best and rest

In her wisdom, the programmer added a sort function that could order the rows
best to worse using `d2h`, or distance to heaven [^rowOrder]. Given a goal
normalized to the range 0..1 for min..max, then "heaven" is 0 (if minimizing)
and 1 (if maximizing). Given N goals there there is a list of heaven points
and `d2h` is the distance from some goals to that  heaven.

[^rowOrder]: domiantion, etc

```python
def d2h(i:data, r:row) -> float:
  n = sum(abs(norm(num,r[num.at]) - num.maximize)**the.p for num in i.cols.y)
  return (n / len(i.cols.y))**(1/the.p)

def norm(i:num,x) -> float:
  return x if x=="?" else (x-i.lo)/(i.hi - i.lo - 1E-30)
```

> [!NOTE]
> This distance function is a little unusual in that it reports
distances between the dependent `y` goal values. Usually distance is defined as the
distance between the independent `x` values-- see `dists()` (below).

To sort rows, when we call `DATA(rows, ranl=True)`. 
If we sort the car data (described above)  in this way, then print ever 20th car, thos
results in the following. 

```
N       Clndrs   Volume   HpX   Model   origin   Lbs-   Acc+   Mpg+
--      ------   -------  ---   -----   ------   ----   ----   ----
0 	     4        97       52      82    2       2130    24.6   40
20 	     4        91       60      78    3       1800    16.4   40
--      ------   -------  ---   -----   ------   ----   ----   ----
40 	     4       112       88      82    1       2605    19.6   30
60 	     4       112       88      82    1       2395    18     30
80 	     4        97       88      72    3       2100    16.5   30
100 	 4        79       67      74    2       1963    15.5   30
120 	 4        98       60      76    1       2164    22.1   20
140 	 4       140       88      78    1       2720    15.4   30
160 	 4       140       72      71    1       2408    19     20
180 	 8       260       90      79    1       3420    22.2   20
200 	 6       250       78      76    1       3574    21     20
220 	 6       232      100      75    1       2914    16     20
240 	 6       225      110      78    1       3620    18.7   20
260 	 6       225      100      76    1       3651    17.7   20
280 	 6       250       88      71    1       3139    14.5   20
300 	 8       262      110      75    1       3221    13.5   20
320 	 8       318      150      70    1       3436    11     20
340 	 8       400      150      70    1       3761     9.5   20
360 	 8       351      153      71    1       4154    13.5   10
380 	 8       400      175      72    1       4385    12     10
```
This data has 398 examples
and we can call the top $\sqrt{398} \approx 20$ rows the "best" and the remainder
the "rest". In the above, we see that the "best" cars have  much lower weight,
and have much more acceleration and miles per hour. 

So now the question becomes, what is in the contrast between "best" and "rest"?
That is to say, what attribute ranges select for "best" and let us avoid the "rest"?
To answer that, lets turn to discretizatiom.

## Dsicretization : Condensing Knowledge to Just  a Few Ranges

One way to understand data is to ask which parts of it select from what classes (in our case, "best" and
"rest"). For example, if we are always awake when we go to work, and if "at work" is what we are trying
to predict, then 24 hours in a day might be descretized into two  bins:

- another for 8am to 6pm
- one for 6pm to 8am

There  are many ways to discretize data (e.g. see the 100+  methods discussed in Garcia et. al. [^garcia12]).
Here, just do something simple:

- Sort the numerics of one column then divide them into some very small bins with borders _(max-min)/16_. 

[^garcia12]: Garcia, S., Luengo, J., Sáez, J. A., Lopez, V., & Herrera, F. (2012). A survey of discretization techniques: Taxonomy and empirical analysis in supervised learning. IEEE transactions on Knowledge and Data Engineering, 25(4), 734-750.
https://ieeexplore.ieee.org/stamp/stamp.jsp?arnumber=6152258

[^rama2025]: Ramírez-Gallego, Sergio, Salvador García, Héctor Mouriño-Talín, David Martínez-Rego, Verónica Bolón-Canedo, Amparo Alonso-Betanzos, José Manuel Benítez, and Francisco Herrera. "Data discretization: taxonomy and big data challenge." (2015).
https://citeseerx.ist.psu.edu/document?repid=rep1&type=pdf&doi=760d884819877959b6a3e1176ed30633e6fdb1f8


in that sort
proFor the car dat described above,
t
doty. fing deta between best and rest.



## Some Details

### Other Distance Functions

XXX otehr kinds of d
The general Minkowski distance  says that the distance between things
comes from the distance between their independent `x` columns,  raised to some power $p$.
Boring old Euclidean distance uses $p=2$, but our programmer knew that
this is a parameter that can be tuned. She stored all such tuneables
in a `the` variable. So our Minkowski distance function is:

$$d(x,y)=\left(\sum^n_i (x_i - y_i)^p /n\right)^{1/p}$$

We divide by $n$ so all our distances fall between zero and one.

This disance is defined bif nuermisa dn is XXX
Which, in Pythons is:

```python
# Distance between two rows
def dists(data,row1,row2):
  n = sum(dist(col, row1[col.at], row2[col.at])**the.p for col in data.cols.x)
  return (n / len(data.cols.x))**(1/the.p)

# Distance between two values (called by dists).
def dist(col,x,y):
  if  x==y=="?": return 1
  if not col.isNum: return x != y
  x, y = norm(col,x), norm(col,y)
  x = x if x !="?" else (1 if y<0.5 else 0)
  y = y if y !="?" else (1 if x<0.5 else 0)
  return abs(x-y)
```	

### Olace to store the config

## Difference to Other Approaches

`Y=f(x)`. the rave from IEEE  trans

[^rowRoder:] There are many ways to rank examples with multiple objectives. 
_Binary domination_ says...
The _Zitler says__
Peter Chen.
