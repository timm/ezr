# Data (stores rows and columns)

Tabular data stores rows that are examples of some function:

$$Y=f(X)$$

where $X$ are the independent columns and $Y$ are the dependent
goals and our goal is to learn $f$ from the $X,Y$ examples.

```lua
l  = require"lib"   ; local o,oo    = l.o,l.oo
ns = require"numsym"; local NUM,SYM = ns.NUM, ns.SYM
d  = require"data"  ; local DATA    = d.DATA

local function eg_csv()
  print""
  n=0
  for row in l.csv("../data/misc/auto93.csv") do
    n = n + 1
    if n == 1 or n % 50 == 0 then print("csv",n, l.o(row)) end end end

eg_csv()
```

Rows contain multiple $X,Y$ features where $X$ are the independent
variables (that can be observed, and sometimes controlled) while
$Y$ are the dependent variables (e.g. number of defects).

```lua
local function eg_names(  cols,prefix)
  cols = cols or d.COLS.new{"Age","Weight","Wealth+","Weight-"}
  for k,lst in pairs(cols) do
    print""
    for _,col in pairs(lst) do 
      print(prefix or "name", k, l.o(col)) end end end 

eg_names()
```

Columns are also known as features, attributes,  
variables or, for
the more important ones, goals or klasses.

Data tables can be built from csv files.

```lua
local function eg_fromFiles(      data)
  print""
  data = d.DATA.new():read("../data/misc/auto93.csv")
  for n,row in pairs(data.rows) do
    if n%50==0 then print("fromFiles", l.o(row)) end end 
  eg_names(data.cols,"from") end
```
Data tables can also be built to mimic existing tables
(by copying over the names that define the existing
tables): 

```lua
or from other tables.
local function eg_fromTables(       data)
  print""
  data1 = d.DATA.new():read("../data/misc/auto93.csv")
  data2 = d.DATA.new(data1.cols.names):load(data1.rows) 
  for n, col1 in pairs(data1.cols.x) do
    col2 = data2.cols.x[n]
    assert(col1:mid() == col2:mid(),"mid differet")
    assert(col1:div() == col2:div(),"sd different")  end end

eg_fromFiles()
eg_fromTables()
```

When the $Y$ columns are absent, then unsupervised learners seek
mappings between the $X$ values. For example, clustering algorithms
find groupings of similar rows (i.e. rows with similar $X$ values).
The opposite of unsupervised learning is supervised learner that
assunes
 all rows have $Y$.

Sometimes, all rows have $X$ values for all columns. But with text
mining, the opposite is true. In principle, text miners have one
column for each word in text’s language. Since not all documents
use all words, these means that the rows of a text mining data set
are often “sparse”; i.e. has mostly missing values.

When $Y$ is present and there is only one of them (i.e. $|Y| = 1$)
then supervised learners seek mappings from the $X$ features to the
$Y$ values. For example, logistic regression tries to fit the $X,Y$
mapping to a particular equation.

$$p(x)={\frac {1}{1+e^{-(\beta _{0}+\sum_i\beta _ix_i)}}}$$

When there are many $Y$ values (i.e.  $|Y| > 1$), then another array
$W$ stores a set of weights indicating what would be the best value
in each column. After normalized column numerics to the range
min..max to 0..1, then

- $W_i=0$ means we want to minimize this goal to zero;
- $W_i=1$ means we want to maximize this goal to one;

Multi-objective optimizers seek $X$ values that most minimize or
maximize their associated $Y$ values. Other algorithms work as
follows:

- Clustering algorithms find groups of rows; 
- and Classifiers (and regression algorithms) find how those groups 
  relate to the target $Y$ variables; 
- and Optimizers are tools that suggest “better” settings for the $X$ 
  values (and, here, “better” means settings that improve the expected 
  value of the $Y$ values). 

Apart from $W,X,Y$, we add $Z$, the hyperparameter settings that
control how learners performs regression or clustering. For example,
a KNeighbors algorithm needs to know how many nearby rows to use
for its classification (in which case, that $k \in Z$). Usually the
$Z$ values are shared across all rows (exception: some optimizers
first cluster the data and use different $Z$ settings for different
clusters).


