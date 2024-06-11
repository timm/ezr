# A Tutorial on Easier XAI

by Tim Menzies and the EZRites  
(c) 2024, CC-SA 4.0  
http://github.com/timm/ezr


> [!NOTE]
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

## Before we begin
FYI: this code uses the standard type hints plus the following:

```python
from typing import Any as any
from typing import Callable 

xy,cols,data,node,num,sym,node,want = # my own classes

col     = num    | sym
number  = float  | int
atom    = number | bool | str # and sometimes "?"
row     = list[atom]
rows    = list[row]
classes = dict[str,rows] # `str` is the class name
```
Also, this work is in two parts. 

#### Part 1 : Standard Learning

The first part shows how to  write code that

- reads in data, summarizes it in interesting ranges,
- then poke around the data to generate a succinct decision tree that tells you how
to best achieve multiple goals

#### Part 2  : Active Learning

That first part is fun since it shows how much can be done with so little.
On the other hand, that code has certain flaws.
Firstly, it does not break new ground.
It is all
standard stuff. And, all in all, we like doing  do new stuff. So in  the second part, we
will push the envelope of what is known in machine learning to come up with a novel approach.

Secondly, the analysis in the first part
suffers from 
a generalization problem. In that code,  we will reason about some
data, then applied
the learned model _to the same data_. A more convincing approach would be test
the current model against data _not seen in training_
(which means that when new data arrives, we need to
test the model on that new data
before changing and biasing that model
with that new information). So in part two,  we will apply an incremental learning strategy
where  a model learned from the first  $ i \lt N $ examples is applied to 
all the remaining $ (i+1)  \le j \le N $.

Thirdly, the first part assumes we can access correct labels for all the data-- which may not be true.
For example, suppose we are standing in a used car yard with 400 cars.
Suppose further we want a car that is light (since they cost less),  and which has
good acceleration and miles per gallon:
Since these are used cars, we cannot be sure what those
values might be (especially miles per hour and acceleration). 

To get those labels, one thing we could do
is take out all 400 cars one at at time,  drive them around for a while, and label
(e.g.)
the miles per hour.
But that would take too long. So instead, in part two, we will employ active
learning to look at everything unlabelled, then pick the least number of potentially
most informative things to label next. As we shall these, this will allow us to explore
10,000s of examples with just a few dozen labels.


## In the Beginning
In the beginning there was the data and the data was without form,
and void; and confusion was upon the face of the humans.  And the
programmer  said, let there be workflows that 
succinctly  explain the contrast between good and bad things [[^whycon],[^conplan]].
And then there was light.

[^whycon]: difference between things can be shorter than the things
[^conplan]: apply the contrast. does it change anything? ktest. lime,

And in that workflow there was tabular data whose first row defined
column types. And upper case words were numeric and the others were
symbols. And some of the words were goals have special marks
denoting things we wanted to predict ("!") or  minimize ("-") or maximize ("+").  So
If our data was about cars then it might look like this:

```python
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


```python
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

Of the two questions, the second one is far more interesting.  Life is short and the road is long. So where to go? There are many tasks in this world and only
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

Our programmer looked at the data and say that there are different kinds
of columns. So she wrote code to turn these names (on line one) into NUMeric and
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

Note that:

- To distinguish NUMs from SYMs, the programmer added a `this=NUM` and
`this=SYM` flag.
- `NUM`s have a `maximize` flag telling us which direction is best for a particular `NUM`eric column. For `Lbs-` and `Acc+` `maximize` is False and True, respectively.

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

In the `DATA()` function (above), rows are sorted via the datt `DATA(sec, rank=True)`.
That call would result in the row sort order shown above.

So now out task is to find the  contrast between "best" and "rest"?
That is to say, what attribute ranges select for "best" and let us avoid the "rest"?
To answer that, lets turn to discretizatiom.

## Dsicretization : Condensing Knowledge to Just  a Few Ranges

One way to understand data is to ask which parts of it select from what classes (in our case, "best" and
"rest"). For example, if we are always awake when we go to work, and if "at work" is what we are trying
to predict, then 24 hours in a day might be descretized into two  bins:

- another for 8am to 6pm
- one for 6pm to 8am

### Bins are held in `XY` objects

Our bins are held in `XY` objects (we cannot call them "bin"s since that word is already in use
in our Python systems).
 `XY`s stores the `lo` and `hi` of one
column (the "x" column) as well as the symbols see in that range
in another column (see the `ys` counts). 

```python
def XY(at,txt,lo,hi=None,ys=None) -> xy:
  return o(this=XY, n=0, at=at, txt=txt, lo=lo, hi=hi or lo, ys=ys or {})
```

One thing we do, a lot, is to `merge()` adjacent bins (and the new bin runs from
the `lo` of the first bin to the `hi` of the second bin).

```python
def merge(xys : list[xy]) -> xy:
  out = XY(xys[0].at, xys[0].txt, xys[0].lo)
  for xy1 in xys:
    out.n += xy1.n
    out.lo = min(out.lo, xy1.lo)
    out.hi = max(out.hi, xy1.hi)
    for y,n in xy1.ys.items(): out.ys[y] = out.ys.get(y,0) + n
  return out
```
Bins are  `mergeable()` if either:

- [1] the merged bins are simpler than the parts. 
- [2] the bins  hold less than some `small` amount. For example, if we are dividing the data into $N$ bins,
       they each bin should hold at least $1/N$th of the data.

```python
def mergable(xy1: xy, xy2: xy, small:int) -> xy | None:
  maybe = merge([xy1,xy2])
  e1  = entropy(xy1.ys)
  e2  = entropy(xy2.ys)
  if xy1.n < small or xy2.n < small: return maybe        # [1]
  if entropy(maybe.ys) <= (xy1.n*e1 + xy2.n*e2)/maybe.n: # [2]
    return maybe

def entropy(d:dict) -> float:
  N = sum(v for v in d.values())
  return -sum(v/N*math.log(v/N,2) for v in d.values())
```

Entropy is a way of measuring the simplicity of a distribution.
Simpler distributions have lower entropy and mention  smaller number
of different things.
Hence they are better at predicting things
(since there are fewer choices to make).
To compute entropy, we ask "what is the effort required to recreate a signal:

- Suppose we had an array
with 32 items, the first 8 items of which represent elephants and the last
4 items represent lions.
- the probabilities of our two animals are $p_1=8/32=0.25$ and
$p_2=4/32=1/8$ respectively. 
- If we search our animals using a binary chop, then that search  require up to $\log_2(p_i)$ steps.
- When recreating a signal, the prevalance of (say) lions will control often we search for them.
   Hence, the expected value of the effort required to recreate our animals is $\sum_i p_i\log_2(p_i)$
    (which is comptued in `entropy()`).

### An Example of Discretization

There  are many ways to discretize data (e.g. see the 100+  methods discussed in Garcia et. al. [^garcia12] [^rama2025]). 
Here, just do something simple:

- We sort the numbers of one column;
- Divide those numbers into some very small bins with borders _(max-min)/16_. 

[^garcia12]: Garcia, S., Luengo, J., Sáez, J. A., Lopez, V., & Herrera, F. (2012). A survey of discretization techniques: 
Taxonomy and empirical analysis in supervised learning. IEEE transactions on Knowledge and Data Engineering, 25(4), 734-750.
https://ieeexplore.ieee.org/stamp/stamp.jsp?arnumber=6152258

[^rama2025]: Ramírez-Gallego, Sergio, Salvador García, Héctor Mouriño-Talín, David Martínez-Rego, Verónica Bolón-Canedo, 
Amparo Alonso-Betanzos, José Manuel Benítez, and Francisco Herrera. "Data discretization: taxonomy and big data challenge." (2015).
https://citeseerx.ist.psu.edu/document?repid=rep1&type=pdf&doi=760d884819877959b6a3e1176ed30633e6fdb1f8


For `SYM`bolic columns, we create one bin for each value. Otherwise, we `norm()`alize those
values 0..1 (over the range min..max) then multiple that by the number of bins:

```python
def _divideIntoBins(i:col,x:atom, y:str, bins:dict) -> None:
  k = x if i.this is SYM else min(the.xys -1, int(the.xys * norm(i,x)))
  bins[k] = bins[k] if k in bins else XY(i.at,i.txt,x)
  add2xy(bins[k],x,y)

def add2xy(i:xy, x: int | float , y:atom) -> None:
  if x != "?":
    i.n    += 1
    i.lo    =  min(i.lo, x)
    i.hi    =  max(i.hi, x)
    i.ys[y] = i.ys.get(y,0) + 1
```

If we `_divideIntBins` the "Volumne" column from our data, this generate the following.
Recall that "best" were our $\sqrt{N}$ best rows and "rest" were all the other 378 rows.:

```python
score   bin                      holds
-----   -----------              -------------------------  
0.748   68 <= Volume < 91        {'best': 16, 'rest': 40}
0.037   96 <= Volume < 116       {'best': 2, 'rest': 74}
0.013   119 <= Volume < 140      {'best': 1, 'rest': 59}
0.0     141 <= Volume < 163      {'rest': 26}
0.0     168 <= Volume < 183      {'rest': 9}
0.0     198 <= Volume < 200      {'rest': 13}
0.0     225 <= Volume < 232      {'rest': 32}
0.0     250 <= Volume < 260      {'rest': 25}
0.0     262 <= Volume < 267      {'rest': 3}
0.0     302 <= Volume < 307      {'rest': 25}
0.0     Volume == 318            {'rest': 17}
0.0     340 <= Volume < 351      {'rest': 27}
0.0     Volume == 360            {'rest': 4}
0.0     383 <= Volume < 400      {'rest': 16}
0.0     Volume == 429            {'rest': 3}
0.0     440 <= Volume < 455      {'rest': 6}
```

Here,  `holds` shows how many rows were selected (out of 20
`bests` and 378 `rests`). Also `score` shows the probability times
support that any bin offers for selecting for best. This `score`
is calculated by passing the dictionary from the `holds` column
into `wanted()` (with `bests=20` and `rests=278`). 

```python
def WANT(best="best", bests=1, rests=1) -> want:
  return o(this=WANT, best=best, bests=bests, rests=rests)

def wanted(i:want, d:dict) -> float :
  b,r = 1E-30,1E-30 # avoid divide by zero errors
  for k,v in d.items():
    if k==i.best: b += v/i.bests
    else        : r += v/i.rests
  support     = b        # how often we see best
  probability = b/(b+r)  # probability of seeing best, relative to  all probabilities
  return support * probability
```

Looking at these bins, there any many we can reduce and clarify the ranges for "Volume".
Firstly, we can check  if any of them are `mergeable()` (using the above code).

Secondly, there "gaps" between the ranges where our training data
does not mention certain values.  For example, in the above there
are many gaps such as the gap seen from 429 to 440.  To fill those
gaps, we increase the span of  our bins from the `hi` point of one
bins to the `lo` value of its neighbor. 

```python
def _span(xys : list[xy]) -> list[xy]:
  "Ensure there are no gaps in the `x` ranges of `xys`. Used by `discretize()`."
  for j in range(1,len(xys)):  xys[j].lo = xys[j-1].hi
  xys[0].lo  = -1E30
  xys[-1].hi =  1E30
  return xys
```

Thirdly,  if two adjacent bins are not `wanted()` much, then there no value if keeping them separate.
In our code, for each column, we find maximum `wanted()` then try to merge adjacent bins
with less than 10% of
max `wanted()`.  Note that purging these unwanted bins  has to  be happen _after_ we do all the other merges (since, otherwise,
we will not know what the max bin is):

```python
def _combine(i:col, xys: list[xy], small, want1) -> list[xy] :
  def mergeDull(a,b,n):
    if wanted(want1,a.ys) < n and wanted(want1,b.ys) < n:
      return merge([a,b])

  if i.this is NUM:
    xys = _span(_merges(xys, lambda a,b: mergable(a,b,small))) 
    n   = the.enough * sorted([wanted(want1,xy1.ys) for xy1 in xys])[-1]
    xys = _merges(xys, lambda a,b: mergeDull(a,b,n)) # final merge of the unwanted ranges.
  return  [] if len(xys)==1 else xys
```
(Note the last line `[] if len(xys)==1 else xys`. This says that is all our merging
results in a single range, then we are unable to find a useful division of this column.
Hence we should return nothing at all.)

The actual mechanics of merging is handled by `_merges`. This function
is based a list of bins and a `fun` function that returns a new bin (if two bins can be merged) or `None`.
If anything can be merged with its neighbor
then this code keeps the merged bin, then  jumps forward one bin (over the merged item),  looking for anything else mergeable.
If this leads to a shorter list of bins, then call `_merges()` (at which point we go back to the beginning
of the list and look for any other merges).

```python
def _merges(b4: list[xy], fun):
  j, now  = 0, []
  while j <  len(b4):
    a = b4[j]
    if j <  len(b4) - 1:
      b = b4[j+1]
      if ab := fun(a,b):
        a = ab
        j = j+1  # if i can merge, jump over the merged item
    now += [a]
    j += 1
  return b4 if len(now) == len(b4) else _merges(now, fun)
```
Putting this all together, , we need the high-level controller for the discretisation:
```python
def discretize(i:col, klasses:classes, want1: Callable) -> list[xy] :
  "Find good ranges for the i-th column within `klasses`."
  bins = {}
  [_divideIntoBins(i, r[i.at], klass, bins) for klass,rows1 in klasses.items()
                                  for r in rows1 if r[i.at] != "?"]
  return _combine(i, sorted(bins.values(), key=lambda z:z.lo),
                     sum(len(rs) for rs in klasses.values()) / the.xys,
                     want1)
```
When this is caled on the car data, we get a very different set of ranges. Note that, in the following,
"Volime" now has just 2 bins instead of the 16 shown above.
Also, its first bin now selects for $16/19=approx84$%  of the "best" rows and just $40/379\approx 10$%
of the other rows.

```python
baseline                        {'best': 19, 'rest': 379}

0.62	Clndrs < 4          	{'rest': 190, 'best': 18}
0.005	Clndrs >= 4         	{'best': 1, 'rest': 189}

0.748	Volume < 91         	{'best': 16, 'rest': 40}
0.024	Volume >= 91        	{'best': 3, 'rest': 339}

0.022	Model < 74          	{'rest': 150, 'best': 2}
0.032	74 <= Model < 77    	{'rest': 90, 'best': 2}
0.057	77 <= Model < 78    	{'best': 2, 'rest': 34}
0.0	78 <= Model < 79    	{'rest': 29}
0.318	79 <= Model < 80    	{'best': 7, 'rest': 22}
0.11	80 <= Model < 81    	{'best': 3, 'rest': 26}
0.108	Model >= 81         	{'best': 3, 'rest': 28}

0.015	origin == 1         	{'best': 2, 'rest': 247}
0.254	origin == 2         	{'best': 7, 'rest': 63}
0.391	origin == 3         	{'best': 10, 'rest': 69}
```

And we can go even further. Tbe highest `wanted()` score in the above is 0.748. Ignoring everything with
less than 10% of that, takes us to:

```python
0.62	Clndrs < 4          	{'rest': 190, 'best': 18}

0.748	Volume < 91         	{'best': 16, 'rest': 40}

0.0	78 <= Model < 79    	{'rest': 29}
0.318	79 <= Model < 80    	{'best': 7, 'rest': 22}
0.11	80 <= Model < 81    	{'best': 3, 'rest': 26}
0.108	Model >= 81         	{'best': 3, 'rest': 28}

0.254	origin == 2         	{'best': 7, 'rest': 63}
0.391	origin == 3         	{'best': 10, 'rest': 69}
```

## Trees

The above example with ranges looks interesting. We saw how
the problem of multi-objective analysis can be reduced to decisions about just a few ranges.
But there is a way to do even better.
Often, useful bins from different attributes select for the same rows. So as a final step in
this process, we should ignore bins that cover the same things as other bins.

Enter decision trees.  In the following we talk about `klasses` which are rows stored in a dictonary
(and the klass names are the keys of the different dictionaries). 


### `tree()`

The `tree()` algorithm is pretty simple since, as it turns
out, most of the heavy lifting has already been done during discretization.
In the following, we say the `XY` bins are called `cuts`. 

- Using discretiization, find  all the ways we can  `cuts` the data.
- Using those `cuts`, then `_grow()` the tree
  - Cut  the  data into the rows that are/aren't covered by that bin;
  - Recurse on each cut.

This code returns a tree of `NODE`s where each `NODE` has `left` and `right` pointers
to sub-trees.

```python
def NODE(klasses: classes,  left=None, right=None) -> node:
  return o(this=NODE, klasses=klasses, left=left, right=right, cut=None)

def tree(i:data, klasses:classes, want1:Callable, stop:int=4) -> node:
  # For details on these three functions, see below
  def _grow(klasses:classes, lvl:int=1) -> node:
  def _branch(here:node, lvl:int,  total:int, most:int) -> node:
  def _want(cut:xy, klasses:classes) -> float :

  cuts = [cut for col1 in i.cols.x for cut in discretize(col1,klasses,want1)]
  return _grow()

def _cut(cut:xy, klasses:classes) -> tuple[classes,classes]:
  are  = {klass:[] for klass in klasses}
  arent = {klass:[] for klass in klasses}
  for klass,rows1 in klasses.items():
    [(are if selects(cut,row1) else arent)[klass].append(row1) for row1 in rows1]
  return are,arent

def selects(i:xy, r:row) -> bool:
  x = r[i.at]
  return x=="?" or i.lo==x if i.lo==i.hi else i.lo <= x < i.hi
```

### Details

Just to fill in some details, `_tree()` calls `_grow()` (to collects some statistics on rows
in the current cut) which  then calls `_branch()` (to do the actual work). 

```python
 def _grow(klasses:classes, lvl:int=1) -> node:
    "Collect the stats needed for branching, then call `_branch()`."
    counts = {k:len(rows1) for k,rows1 in klasses.items()}
    total  = sum(counts.values())
    most   = counts[max(counts, key=counts.get)]
    return _branch(NODE(klasses), lvl, total, most)

  def _branch(here:node, lvl:int,  total:int, most:int) -> node:
    "Divide the data on tbe best cut. Recurse."
    if total > 2*stop and  most < total: #most==total means "purity" (all of one: class)
      here.cut = max(cuts,  key=lambda cut0: _want(cut0, here.klasses))
      left,right = _cut(here.cut, here.klasses)
      leftn = sum(len(rows1) for rows1 in left.values())
      rightn = sum(len(rows1) for rows1 in right.values())
      if leftn < total and rightn < total:
         here.left  = _grow(left,  lvl+1)
         here.right = _grow(right, lvl+1)
    return here
```
The `if` statements in `_branch()` tell us when it is useful to  grow subtrees.
If `total` is the number of rows seen before the cuts, and `leftn`,`rightn` are the number
of rows in each cut, then:

- `total > 2*top` : there are enough examples to generate two more subtrees;
- `most < total` : not all the data is in one class since, if it where, that would mean
    this branch had managed to isolate on class (which would be a  reason to stop growing this branch);
- `leftn < total` and `rightn <  total`: the new subtrees reduce the number of examples in the
    sub-tree by at least one item per branch.

As to `_want()`, this applies the `wanted()` logic (discussed above) to each cut:

```python
  def _want(cut:xy, klasses:classes) -> float :
    return wanted(want1, {k:len(rows1) for k,rows1 in _cut(cut,klasses)[0].items()})
```
### Trees, Example
For our cars,if we create a `classes` containing  $\sqrt{N}$ "best" rows  and $1-\sqrt{N}$` "rest" rows,
then we can generate the following tree:

```python
$ ./ezr.py -R tree

                                    (:best 19 :rest 379)
if Volume < 91                      (:best 15 :rest 29)
|.. if Clndrs >= 4                  (:best 15 :rest 25)  <== best outcome
|.. else                            (:best 0 :rest 4)
else                                (:best 4 :rest 350)
|.. if Model >= 81                  (:best 3 :rest 52)
|.. else                            (:best 1 :rest 298)
|.. |.. if 80 <= Model < 81         (:best 1 :rest 19)
|.. |.. |.. if origin == 2          (:best 1 :rest 4)
|.. |.. |.. else                    (:best 0 :rest 15)
|.. |.. else                        (:best 0 :rest 279)
```

Note our best outcome:

- Given 19 and 379 best and rest cars,
- Given three goals "Weight-,Acc+, Mpg+"
- Then with two tests on "Volume" and "Cylndrs", we can find 15 and 29 best and  rest cars.
- So, initially, the "best"s where a tiny minority and now we can find  83\% of them.


## Part2: Active Learning

Ok. So now we know how to 
The first part shows how to write code that
reads in data, summarizes it in interesting ranges,
then poke around the data to find
a succinct decision tree that tells you how to best achieve multiple goals.
And as we said before, this is all well and good but it has certain problems
that we need to fix:

- Innovation: we want to push the sate of the art, not just reepat old stuff;
- Minimum labels: instead of looking at all labels, we will do what we can with fewest labels.
- Generaliztion: we want to test our results, using data not used in training.

Our main trick will be as follows.
When learning some model $f$ of the form $y=f(x)$, while 
the
$y$ values can be very expensive to obtain,
we
can often access $x$ very cheaply.
Returnign to that used car lot at the top of this page, finding the mileage for each car
can take a while (since it could mean driving each car around for a day).
But we can glance around the cars
to quickly write down the model numbers and their eyar of manufactoer. 
So what we will do is look at a lot of $x$ values before looking at the $y$.

### Classifier

More specifically, we will

1. Label a few things (say, four)
2. Divided the labelled things into `best` and `rest`
3. Build a classifier that can guess the probability $b,r$ that something belongs to `best` or `rest`
4. Sort all the unlabelled examples by `b/r`;
5. Label the top thing in that sort;
6. Loop back to step2.

For the classifier we will use Naive Bayes since it handles small data problems and missing values.
Given ${\mathit nh}=2$ classes ("best" and "rest"), the likelihood
of a row belonging to a class is the probablity of that class things the likelihood of that row's attributes
belonging to that class. We will add the log of these probabilities (rather than miltiplying them) since debugging
with (say) -22 is much easier than debugging with 2.3841857910156e-07.


```python
def loglikes(i:data, r:row|dict, nall:int, nh:int) -> float:
  prior = (len(i.rows) + the.k) / (nall + the.k*nh)
  likes = [like(c, r[c.at], prior) for c in i.cols.x if r[c.at] != "?"]
  return sum(math.log(x) for x in likes + [prior] if x>0)

def like(i:col, x:any, prior:float) -> float:
  return _like4num(i,x) if i.this is NUM else (i.has.get(x,0) + the.m*prior) / (i.n+the.m)

def _like4num(i:num,x):
  v     = div(i)**2 + 1E-30
  nom   = math.e**(-1*(x - mid(i))**2/(2*v)) + 1E-30
  denom = (2*math.pi*v) **0.5
  return min(1, nom/(denom + 1E-30))
```
Note that for `loglikes()` does its work by asking each column to report how much it `likes()`  each `cols.x` val.
Also, in the above, there are magic the.k` and `the.m` values that handle certain low-frequency cases
(see section 3.1 of (this paper)[https://i.giwebb.com/wp-content/papercite-data/pdf/yangwebb03.pdf]). These `m,k`
values are very small and default to $m=2,k=1$. This means their effect disappears once we collect more than, say, 20 examples.

Anyway, with this classifier, we can run "sequential model" optimizer that learns a little, guesses a lot, then labels its best guess.
In the following, for testing purposes, our `data` comes with y labels on everything. But we  only every look at the y-labels
used in `_ranked()` which in sorts the rows. 

```python
def smo(i:data, score=lambda B,R: B-R):
  def _ranked(lst:rows) -> rows:
    return sorted(lst, key = lambda r:d2h(i,r))

  def _guess(todo:rows, done:rows) -> rows:
    cut  = int(.5 + len(done) ** the.N)
    best = clone(i, done[:cut])
    rest = clone(i, done[cut:])
    key  = lambda r: score(loglikes(best, r, len(done), 2),
                           loglikes(rest, r, len(done), 2))
    random.shuffle(todo) # optimization: only sort a random subset of todo 
    return sorted(todo[:the.any], key=key, reverse=True) + todo[the.any:]

  def _smo1(todo:rows, done:rows) -> rows:
    for _ in range(the.Last - the.label):
      if len(todo) < 3: break
      top,*todo = _guess(todo, done)
      done += [top]
      done = _ranked(done)
    return done

  random.shuffle(i.rows) # remove any  bias from older runs
  return _smo1(i.rows[the.label:], _ranked(i.rows[:the.label]))
```
In summary, this code first shuffles the rows (to get rid of any pre-existing bias) them divides the shuffled rows
into the first `the.label=4$ rows, and the rest.  These first four items are `_ranked()` and become the `done` set passed
to `_smo()`, then to `guess()`. Inside `guess()`, the `done` list is divided into $\sqrt{N}$ "best" and the "rest" which 
is used by a customization `score` function
to 
generate porbabilities that some 
unlabbeled example is best or otherwise.  Early versions of this code then sorted all the  unlabelled examples by `score`.
A ten-fold speed up in execution time was achieved when we realized we only need to say, say, `the.any=100` items looking for a
good one.

When `guess()` returns, theose results are divied into `top,*todo` where `top` is the example that seems most likely to best.
This is then moved from `todo` to `done` and the process repeats.

Here we see the mean and standard deviation of the `d2h()` score of the unabelled examples selected by `smo()` and moved to "good"
(and here _smaller_ values are _better_. Note that most of the improvements is seen in the first ten examples.

```python

./ezr.py -R smo
labels  mu    (sd)
------  ----- -----
    4 :  0.61 (0.169)                                                    --------++++++++
    5 : 0.583 (0.158)                                                   -------+++++++
    6 : 0.548 (0.165)                                              --------++++++++
    7 : 0.528 ( 0.16)                                             -------+++++++
    8 : 0.497 (0.173)                                         --------++++++++
    9 : 0.479 ( 0.17)                                       --------++++++++
   10 : 0.474 (0.161)                                       --------++++++++
   11 : 0.476 (0.153)                                        -------+++++++
   12 : 0.464 (0.152)                                       -------+++++++
   13 : 0.461 (0.146)                                       -------+++++++
   14 : 0.457 (0.141)                                      -------+++++++
   15 : 0.452 (0.137)                                       ------++++++
   16 : 0.448 (0.134)                                      ------++++++
   17 : 0.441 (0.133)                                      ------++++++
   18 : 0.448 (0.133)                                      ------++++++
   19 : 0.445 ( 0.13)                                      ------++++++
   20 : 0.443 (0.127)                                      ------++++++
   21 : 0.448 (0.126)                                      ------++++++
   22 : 0.439 (0.131)                                     ------++++++
   23 : 0.428 (0.138)                                    ------++++++
   24 :  0.43 (0.135)                                     ------++++++
   25 : 0.421 (0.141)                                   -------+++++++
   26 : 0.421 (0.138)                                    ------++++++
   27 : 0.413 (0.142)                                  -------+++++++
   28 : 0.415 ( 0.14)                                   ------++++++
   29 : 0.411 (0.139)                                   ------++++++
   30 : 0.412 (0.137)                                   ------++++++
```

Just to finsih up, we took the `done` list that is returned from `smo()`, divided into
$\sqrt{N}$ best and rest, then called our decision tree learner on those two sets.
Here's what it came up with:

```
                                    (:best 5 :rest 25)
if Volume < 91                      (:best 4 :rest 5)
else                                (:best 1 :rest 20)
|.. if Model >= 81                  (:best 1 :rest 8)
|.. else                            (:best 0 :rest 12)
```
This is very similar to the tree found above (that needed 398 labels)
whereas this one only needed 30. And just to hammer home the point, 
$30/398 \approx 8$% of the data. 

To say that another way, you don't need to crazy on data collection. There are ways
to dramatically reduce the cost of reasoning about data.


[^rowRoder:] There are many ways to rank examples with multiple objectives.  _Binary domination_ says...  The _Zitler says__ Peter Chen.
