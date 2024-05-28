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
	...
```

Here,  we have decided to ignore horsepower (so it ends
with and `X`). Also, we want light cars (since they are cheaper to
build and buy), fast acceleration, and good miles per gallon. So
these get marked with `Lhs-,Acc+,Mpg+`

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
