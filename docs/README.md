---
title: "Easier AI via Data Minign Algirithms Using/Used-by Optimizers"
author:  "Tim Menzies<br>timm@ieee.org"
date: "July, 2025"
---

------------------------------------------------------
_"The best thing to do with most data is throw it away."_ --me

_"YAGNI"_ (you aren't gonna need it) --Kent Beck

_"Less, but better."_  --Dieter Rams  

_"Subtract."_ --Leidy Klotz
------------------------------------------------------

## Introduction
Have we made AI too complicated? Are all AI tasks generative
tasks that 
require expensive licenses of large  models
feed by trillions of variables, requiring
centruies of CPU? Or are their simpler methods, worthy of much active
research?
Clearly, not everything can be made simpler. Generative tasks need a large
knowldge based on conditional probabilities in order to knw what to gnerate next.
But not all tasks are generative tasks. And of those non-generative tasks,
are there some that are very simple to code, easy to train, and fast to run?

To explore this issue,
this paper is about a tiny code based that implements explanation
of active learning for multi-objective optimzaion problems.
Having explore this area for over two decades, I can assert that there are many
complex ways to adress explanaton, active learning, and optimization.
Here, we step away from thos methods, seeking very simple approaches.

This work began with a
question for a graduate student in an AI class:

> Why do our models need so much data?

“Maybe they don’t,” I replied. “Maybe we just have not learned how
to ask the right questions yet.”

My claim led to a dare which led to a prototype. Given a database of past examples sorted in "best" and "rest"
EZR is a Bayesian
contrast set learner that prefers new examples
if they are more likely to be best than rest. The most preferred example
then updates "best" and "rest" and the cycle repeats.  At runtime,
EZR avoids data that is noisey
(i.e. is clearly not
"best" or "rest") and  superfluous  (i.e. is not
not relevant for "better" behavior). In this way it ignores most of the data and builds
its models using just a few dozens samples. A regression tree learner uses those exampeles to build a tiny tree
that not only explains how to acheive good results, but also what to do to imroe those results.


EZR has been tested on  dozens problems from recent SE research papers that :

- Try to build design that minimize cost, defects, development time and mazimize functionality;
- Select the magic control parameters that data miners use to guide thei learning (e.g. how many trees in a random forest?);
- Configure cloud or database software
- Predict the health of open source software rojects in one eyar's time; 
- Optimize the management of software proects
- And others.

We also look at other tasks:

- Select teams of good football players;
- Retrain employees for a longer period of time;
- Reduce student sdtop our fro school
- Balance a pole on a cart
- Decide which house to biy or loan applicant to approave
- Predict life expectancy or predict patters or infectios diseases or patience re-admittance.
- Design cars, select wine
- Determine what advertising campaigns camight be successufl
- And others.

For these tasks, EZR was found to be effective at selecting optimal solutions.
Its recommendations are completitove
with alternate
technologies Gaussian process models, reinforement learning, iterated racing etc etc. It
also runs two to four orders of magnitude faster.

Lastly, it has a tiny code base. This paper includes a complete source code listing for EZR. This code makes
no use of complex Python packages like Pandas or scikit-learn. 
Yet in under th300 lines it implements explanation
of active learning for multi-objective optimzaion problems. Such a small code base makes it useful
material for teaching the basics of AI and SE scripting. We have also found it a productive
workbench within which we can explore state-of-the-art research.

This experience wuth EZR has  shifted our thinking. The  sucess of
EZR  was not luck- it points to something deeper: an approach to
software engineering and AI where, often, a few well-chosen examples
outperform brute-force data collection.  For centuries, researchers
have told us that that key variable selection, and strategic sampling
can solve complex problems efficiently (see Table 1).

Yet despite this legacy of elegant minimalism, today’s trends often
favor the opposite: ever-larger models, more data, and growing
complexity. There are many reasons for this[^subtract], but a major
one is inertia: we tend to add rather than subtract, mistaking bloat
for progress. Complex products impress the marketplace and so can
drive sales (even if, later,   that also drives up maintainance costs).

| Year     | What                     | Who / System         | Notes                                                                                   |
|----------|--------------------------|-----------------------|-----------------------------------------------------------------------------------------|
| 1902     | PCA                      | Pearson               | Larger matrices can be projected down to a few components.                                           |
| 1960s    | Narrows         | Amarel [^amarel]      | Search can be guided by tiny sets of key variable settings.                              |
| 1974     | Prototypes| Chang [^chang74] | Nearest neighbor reasoning is quicker after discarding 90% of the data and keeping  only the best exemplars.  |
| 1980s    | ATMS       | de Kleer              | Diagnoses is quicker when it focus only on the core assumptions that do not depend on other assumptions. |
| 1984     | Distance-Preseration | Johnson and Lindenstrauss [^john84] | High-dimensional data can be embedded in low dimensions while preserving pairwise distances. |
| 1996     | ISAMP                    | Crawford & Baker [^crawford] | Best solutions lie is small parts of search space. Fast random tries and frequent retries is fast way to explore that space. |
| 1997     | Feature Subset Selection | John & Kohavi [^kohavi97] | Up to 80% of features can be ignored without hurting accuracy.                          |
| 2002     | Backdoors                | Williams et al. [^backdoor] | Setting a few variables beforehand reduces exponential runtimes to polynomial.                     |
| 2005     | Semi-Supervised Learning | Zhou et al. [^zh05]   | Data often lies on low-dimensional manifolds inside high-dimensional spaces.            |
| 2008     | Exemplars                | Menzies [^me08a]      | Small samples can summarize and model large datasets.                                   |
| 2009     | Active Learning          | Settles [^settles09]  | Best results come from learners reflecting on their own models to select their own training examples. |
| 2005–20  | Key Vars in SE           | Menzies et al.        | Dozens of SE models are controlled by just a few parameters.                                |
| 2010+    | Surrogate Models         | Various               | Optimizers can be approximated from small training sets.                                |
| 2020s    | Model Distillation       | Various               | Large AI models can be reduced in size by orders of magnitude, with little performance loss.    |


[^chang74]: Chang, C. L. (1974). Finding Prototypes for Nearest Neighbor Classifiers. IEEE Transactions on Computers, C-23(11), 1179–1184.--


Using this code and data, we ask five questions:

- **RQ1: Is EZR simple?**  
  Is our code base  compact and readable and suitabke for teaching and tinkering?

- **RQ2: Is EZR fast?**  
  Can our code complete tasks in milliseconds rather than hours?

- **RQ3: Is EZR effective?**  
  Can our achieve strong results after seeing only a few examples?

- **RQ4: Is EZR insightful?**  
  Does our code support explainability, critique, and understanding?

- **RQ5: Is EZR general?**  
  Does our code apply across various tasks?

This last question deserves extra attention.  EZR is not a solution
to everythng.  Some tasks are inherently complex and need inherently
compex solutions.  or example, this document was written with 
extensive editorial support by a large language model (big AI was
used to sumamrize verbose sections into shorter and simpler segments).
In RQ5, we describe the "BINGO" test which is a way to peek at data
in order to decide they you need something more than just EZR.

All the code and data used here can be accessed as fllows

    mkdir demo; cd demo
    git clone https://github.com/timm/moot # <== data
    git clone https://github.com/timm/abc  # <== code
    cd abc
    python3 -B abc.py -f ../moot/optimize/config/SS-M.csv # <== test case 

## A Quick Example

Just to give this work some context, here’s a concrete case.

Say we want to configure a database to reduce energy use, runtime,
and CPU load. The system exposes dozens of tuning knobs—storage,
logging, locking, encryption, and more. Understanding how each
setting impacts performance is daunting.

When manual reasoning fails, we can ask AI to help.
Imagine we have a log of 800+ configurations, each showing the
settings to dozens of control settings, and their measured effects.
Some settings lead to excellent results:

```
choices                     Effects
----------------            -----------------------
control settings →            Energy-, time-,  cpu-
0,0,0,0,1,0,...               6.6,    248.4,   2.1   ← best
1,1,0,1,1,1,...              16.8,    518.6,  14.1   ← rest
...
```

Any number of AI tools could learn what separates “best”
from “rest.” But here's the challenge: **labeling** each
configuration (e.g., by running all the benchmarks for all possible configurations)
is expensive. So the EZR challenge is how to
learn an effective model with
minimal effort?

That’s where EZR comes in. We call it that since it uses a minimalist A–B–C strategy:

- **A=Any**; i.e. "ask anything".
  Randomly label a few examples (say, _A = 4_) to seed the process.

- **B=Build**; i.e.  build a model**
  In this phase, we build contrastive models for “best” and “rest,” then label up to,
  say _B = 24_ more rows by picking the unlabelled row that maximizes
  the score _b/r_ (where `b` and `r` are likelihoods that a row
  belongs to the "best" and "rest" models).

- **C=Check**; i.e. check the model.
  Apply the learned model to unlabeled data and to select a small
  set (e.g., _C=5_) of the most promising rows. After labelling
  those rows, return the best one.

In this task, after labeling just 24 out of 800 rows (∼3%), EZR
constructs a binary regression tree from those 24 examples. In that
tree, left and right branches go best and worse examples. The
left-most branch of that tree is shown here (and to get to any line
in this tree, all the things abve it have to be true).

    if crypt_blowfish == 0
    |  if memory_tables == 1
    |  |  if detailed_logging == 1
    |  |  |  if no_write_delay == 0; <== win=98%
    
These four conditions select rows that vey clone
(98%) to  optimial
Note that this branch only mentions four
options, and two of those are all about what to turn off. That
is to say, even though this databased has dozens of configuration
options, there are two bad things to avoid and only two most
important thing to enable  (_memory\_tables_ and _detailed\_logging_).

Of course, if you ever show a result like this to a subject
matter expert, they will  push back. For example, they might demand
to know what happens when `crypt_blowfish` is enabled. Blowfish in
password hashing scheme.  It makes password protection slower but
it also  increases the computational effort required for attackers
to  brute-force attack the database's security.  The full tree
generted by EZR shows what happens this feature is enabled.
(see the last two lines).
Note
all the negative "wins" which is to say, if your goals are fast
runtimes, do not `crypt_blowfish`.

     #rows  win
        17   68    if crypt_blowfish == 0
         7   94    |  if memory_tables == 1
         5   97    |  |  if detailed_logging == 1
         4   98    |  |  |  if no_write_delay == 0;
        10   49    |  if memory_tables == 0
         7   51    |  |  if encryption == 0
         5   50    |  |  |  if no_write_delay == 1
         4   50    |  |  |  |  if txc_mvlocks == 0;
         7 -165    if crypt_blowfish == 1
         4  -51    |  if memory_tables == 1;

(Aside: of course if security is an important goal then (a) add a
"security+" column to the training data shown above; (b)  re-un
EZR; (c) check what are the mpracts of that additional goal.)

EZR shows that with the right strategy, a handful of examples 
(in this case, 24) can
uncover nearly all the signal.  All of this took just a few dozen
queries—and a few hundred lines of code. It’s a striking illustration
of the Pareto principle:  **most of the value often comes from just
a small fraction of the effort**.

## Some Theory

Tihis is acode-oreitend paper but before deving into the details,
ot is usefuul to look at theintellectual origns of this work.



## Discussion

Before looking at the code, we address the questions often asked about the above exampel?

### Why not label everything?

The above code assumed we can only label 24 our of 800 examples. Why do that?

Well, labeling is costly:

- Benchmarks take time to run.
- Some configurations require complex rebuilds.
- Human evaluation is slow, expensive, and error-prone.

Prior work has shown that even with big compute, building labeled
datasets takes **months or years**. EZR sidesteps this by labeling
only what matters most.


### So how does EZR help?

EZR operates under a **tiny-AI assumption**: most of the signal is
buried under a layer of irrelevant or redundant data. It was inspred
byt George Kelly's Personal Construct Theory (from the 1950s) that
stressed the value of contrast set learning to  recognize what is
different between concepts.

Modern versions of contrast set learning include various rule-based
learners including our own previous work on TAR3 and WHICH. EZR's
variant on contrast set learning throws away most of that architecture
and repalces it with a simple two-class classification approach.
Tables of data describing the "best" and "rest" examples can compute
the likilihoods _b,r_ of of an as-yet-unclassified example belonging
to "best" or "rest". The next example to label is the one that
maximizes some _acquisiton function_ e.g. _b/r_.

### What is New About EZR?

This work builds upon the foundation laid by prior resarch, but it
removes some key barriers  that limits the practical use of thsose
methods.

Often we are asked "if EZR just' simplifies existing methods, it
is worthy of publciation?". If so many past resarechers have explored
simplifty (see Table 1), what is new and itneresting about EZR?

In reply, we say offer the observation that propr simplicity results
are alomst uneirsally ignored.  Each year we interview dozens of
propsectivegraduate students for our reserch labs. We also interact,
extensively, with industrial pracitioners and many other researchers
at conferences.  Nearly unviersally, when faced with any new AI
problem, thei default action is to reach for some alrge language
model or deep learning solution.

simplification research is valid resaerch.
A persistant human congintive basi is to under-value subtractive impormvents.
Klotz et al. report nmueris studies where

case studis where hmans are given patterns on a chess baord, then asked to change the pattern in order to make it more symmetrical.
OVerhwlemmning, humans prefer to add new squares to the pattern, rather than take squares away. 

As Klotz et al. warns:

> "Defaulting to searches for additive changes may be one reason
that people struggle to mitigate overburdened schedules, institutional red tape
and damaging effects on the planet."

### Why use a decision tree?

Decision trees are:

- **Fast to train**  
- **Sparse by nature**  
- **Easy to read**

As physicist Ernest Rutherford famously quipped:  
> “A theory that you can’t explain to a bartender is probably no damn good.”

Each path in the tree offers a **human-readable recipe for improvement**, grounded in real measurements.


### How is “win” defined?

Each row has _n_ goals that  we are trying to minimize or maximize. In
the labelled data, each
goal column has a min and max value
seen so far.  After normalizng each goal has the value 0..1 (for min..max),
we can say that minimizing goals have a best value of "0" and
maximizing goals have a best value of "1".

```
y(row) = sqrt(sum(abs(norm(goal) - goal.most)^2 for goal in cols.y))
```

We normalize utility as:

```python
win = 100 × (1 - (mean(y) - best) / (median - best))
```

- A win of **100** means we match the best.  
- A win of **0** means we’re at the median.  
- Negative scores mean we’ve regressed.  

---

### How General Is This?

The database example is just one of over 100 benchmarks in the [MOOT](https://github.com/timm/moot) repository. Each MOOT dataset has:
- Between 1,000 and 100,000 rows
- 5 to 1,000+ configuration choices
- Up to 3 goal metrics

XXXX need to explain EZR

We tested EZR 10× on each dataset. In each trial:
- _A = 4_, _B = 24_, _C = 5_
- EZR built a model from training data
- Test data was ranked by the model
- Top 5 predictions were compared to ground truth
- We recorded the “win” of the best predicted row

As a baseline, we also tested **dumb guessing**: picking 5 random test rows, and scoring the best one.

#### Result (Percentiles of Win Scores)

The results were sorted and divided into percentils (top 10%, next 10%, etc):

| Percentile | EZR | Bar Chart(of EZR)         | EZR - Dumb |
|-----------:|----:|:--------------------------|-----------:|
| 100        | 100 | ************************* | 148        |
|  90        | 100 | ************************* |  64        |
|  80        |  99 | ************************* |  43        |
|  70        |  93 | ************************  |  27        |
|  60        |  81 | *********************     |  15        |
|  50        |  70 | *******************       |   8        |
|  40        |  59 | ****************          |   3        |
|  30        |  42 | *************             |   0        |
|  20        |  35 | ************              |   0        |
|  10        |  17 | ******                    | -12        |


Note that, one time in ten, even dumb guessing gets lucky and does  surprisingly well (the 10% case where "dumb" is 12% better than EZR).
But we do not want to be "dumb"
since dumb reasoning does not generalize. On the other hand, **EZR’s trees provide both performance and understanding.** To say that another way,
dumb reasonng just says yes or now. EZR tells you how and why.

ALso,  while dumb guessing is simple, EZR is barely more complex—just a few hundred lines of code—and runs fast. The full experiment (10× on 110 datasets) took just **65 seconds** on a Mac mini with no GPU.

### And What Does All This Tell Us?

That sometimes, **complexity is unnecessary**.

With small tools, small data, and smart strategies, we can solve real-world optimization tasks—effectively, quickly, and transparently.

EZR demonstrates how to teach and practice software engineering grounded in:

- **Simplicity**
- **Critique**
- **Ownership**

—all without sacrificing performance.

[^amarel]: S. Amarel, "On representations of problems of reasoning about actions", 1960s.  
[^crawford]: C. Crawford & A. Baker, "Experimental Results with ISAMP", 1994.  
[^john84]: W. Johnson and J. Lindenstrauss, "Extensions of Lipschitz mappings...", 1984.  
[^kohavi97]: R. Kohavi and G. John, "Wrappers for feature subset selection", 1997.  
[^zh05]: D. Zhou et al., "Learning with Local and Global Consistency", 2005.  
[^backdoor]: R. Williams et al., "Backdoors to typical case complexity", 2002.  
[^me08a]: T. Menzies, "The Few Key Rows", 2008 (or your actual source).  
[^settles09]: B. Settles, "Active Learning Literature Survey", 2009.


[^tu20]: Tu, Huy, Zhe Yu, and Tim Menzies. "Better data labelling with emblem (and how that impacts defect prediction)." *IEEE TSE*, 48.1 (2020): 2

## Data

To understand the code, first we have to understand the data it processess.
Here's a typical input file.
In this example, the goal is to
to tune Spout wait, Spliters, Counters in order to maximize
Throughput (marked with a ``+'') and minimze Latency (marked
with a ``-'').


      x = independent values          | y = dependent values
      --------------------------------|----------------------
      Spout_wait, Spliters, Counters, | Throughput+, Latency-
         10,        6,       17,      |    23075,    158.68
          8,        6,       17,      |    22887,    172.74
          9,        6,       17,      |    22799,    156.83
          9,        3,       17,      |    22430,    160.14
        ...,      ...,      ...,           ...,    ...
      10000,        1,       10,      |   460.81,    8761.6
      10000,        1,       18,      |   402.53,    8797.5
      10000,        1,       12,      |   365.07,    9098.9
      10000,        1,        1,      |   310.06,    9421

EZR processes tables of data with x inputs and y goals.

- The first row shows the column names.
- Numeric columns start with uppercase, all others are
/symbolic.
- Goal columns (e.g. Fig. 3’s Throughput+, Latency-) use
  +/- to denote maximize and minimize.

For the purposes of illustration, the rows in this table
are
sorted from best to worst based on those goals
(during
experimentation, row order should initially be randomized),

For the purposes of evaluation, all rows in MOOT data sets
contain all their y values. When evaluating the outcome of an
optimizer, these values are used to determine how well the
optimizer found the best rows.

For the purposes of optimization experiments, researchers
should hide the y-values from the optimizer. Each time the
optimizer requests the value of a particular row, this “costs”
one unit. Good optimizers find
good goals at least cost (i.e. fewest labels).

## Structs

EZR does not use Python classes since this lets use spread
functionalty of structs over multiple files (this is useful since,
it lets place arcane detail out of the way of the simpler stuff). Instead,
its structs are based on `SimpleNamespace` objects that can pretty print
themselves, and which allow access to content via the standard dot notation.

    from types import SimpleNamespace as o

In EZR, rows of data are summarized into `
`Num`s (numeric) or `Sym` (symbolic) columns.
Each column knows the `txt` of its name  and its column position
(in `at`). `Sym`s keep a count of the symbols seen so far
(in `has`). 

    def Sym(at=0, txt=""): 
      return o(it=Sym, at=at, txt=txt, has={})

`Num`s also keep track of the smallest and largest
number seen so far (`lo`, `hi`)  as well as the mean `mu` and
standard devaition `sd`. Further, `Num`s also know if they
are a goal that needs minimization (if the last letter of its name
is `-`, then _better_ values are _smaller_).

    def Num(at=0, txt=" "): 
      return o(it=Num, at=at, txt=txt, lo=1e32, mu=0, m2=0, sd=0, n=0, 
               hi=-1e32, more = 0 if txt[-1] == "-" else 1)

`Num`s and `Syms` are generated from the names on row1 of
the  data. Upper case names generated `Num`s and other names
are `Sym`s. Columns have different roles; e.g. if their name ends in `+-` then
they are part
of the 
dependent output variables `y`. Otherwise, they are part of the
`x` indepdentent 
inputs. Apart from that, they are also present in the list of `all` columns. 

     def Cols(names):
       all, x, y, klass = [],[],[],None
       for c,s in enumerate(names):
         all += [(Num if s[0].isupper() else Sym)(c,s)]
         if s[-1] == "X": continue
         if s[-1] == "!": klass = all[-1]
         (y if s[-1] in "!-+" else x).append(all[-1])
       return o(it=Cols, names=names, all=all, x=x, y=y, klass=klass)
     
(Note if a column name ends in `X`
it should be skiiped by the inference. `Cols` implments this by skipping
over such columns and not adding them to the `x` or `y` roles.)

All these columns, and their associated ros
are stored within
a `Data`. This is just a set of `rows` and their sumamries in `cols`.
The first item in a input `src` of information is grabbed and used
by `COls` to create a list of `cols` (columns). Any remaining
items within that src are then added to the `Data` struct.

    def Data(src):
      src = iter(src)
      return adds(src, o(it=Data, n=0, rows=[], cols= Cols(next(src))))

    def adds(src, it=None):
       "A handy helper function for adding many values to some struct."
      it = it or Num()
      [add(it, x) for x in src]
      return it


import random, math, sys, re

def atom(s):
  for fn in [int,float]:
    try: return fn(s)
    except Exception as _: pass
  s = s.strip()
  return {'True':True,'False':False}.get(s,s)

the = o(**{k:atom(v) for k,v in re.findall(r"(\w+)=(\S+)",__doc__)})



## Code

The core of EZR is around 200 lines of Python. Around that core
are hundreds of lines of other code containing a test suite,
some statistical analysis, and a whole bunch of other methods
that are not essential or  recommmended, but inclde here for comparisons purposes.

The code inputs a csv file

When reading that file, it is best to start at the top and bottom. 
The bottom of the code contains a long ist of `eg__xxx` functions which
can be called from the command line `python3 ezr.py --xxx`. To get a list
of these functions, use the `--list` flag. The functions are listed
top to bottom, simplest to most complex.

```
> ezr --list

ezr.py [OPTIONS]

   --list        List all examples
   --the         Show the system config.
   --sym         Sym: demo.
   --Sym         Sym: demo of likelihood.
   --num         Num: demo.
   --Num         Num: demo of likelihood.
   --data        Data: demo of reading from file.
   --inc         Data: updates. Incremental adds and deletes.
   --bayes       Like: find likelihoods for all rows.
   --stats       Stats: numeric (effect size and significance tests).
   --sk20        Stats: Checking rankings of 20 treatmeents, for increaseing sd
   --confuse     Stats: discrete calcs for recall, precision etc..
   --diabetes    Naive Bayes classifier: test on diabetes.
   --soybean     Naive Bayes classifier: test on soybean.
   --distx       Dist: check x distance calcs.
   --disty       Dist: check y distance calcs.
   --irisKpp     Dist: check Kmeans++ centroids on iris.
   --irisK       Dist: check Kmeans on iris.
   --fmap        Dist:  diversity-based optimziation with fast map.
   --rand        Dist:  diversity-based optimziation with random point selection.
   --c           ABC: compare tree and bayes for exploring test data.
   --tree        ABC: Test the tree on test data.
   --klass       ABC: acquire using 'klass'.
   --old         ABC: compare diversity acquisition strategies.
   --liking      ABC: compare Bayesian acquisition strategies.
   --final       ABC: ompare the better acquisition strategies.
```

The top of the code's
`__docstring__`
shows the code's options, the most important of which are the `-A`,
`-B`, `-C` flags that control Any, Build, and Check. The rest of the flags do thigs like set the random numer seed (`-s`) and where to find input data
(`-f`). 

Python nodes
- meta-model. Doc strings in files and functions. globals (to get list of functions).

# Easer AI: Why?

This section offers motivation for exploring little AI tools like EZR.

## Config is a problem

asdas

## #Config is a very geenratl problem. 

HBO and icsmn '24

### Learning About AI

If we can make AI simpler, then we can make also simplify the teaching of AI.

EZR is an interesting candidate for study, for the following reasons:

- its system requirements are so low, it can  run on system that
  are already available to all of us;
- it is compact and accessible;
- it provides an extensive set of very usable facilities;
- it is intrinsically interesting, and in fact breaks new ground
  in a number of areas.

Not least amongst the charms and virtues of EZR is the compactness
of its source code: in just a few hundred ines of code
including tools for clustering, classification, regression,
optimization, explanation, active learning, statistical analysis,
documentation, and test-driven development.

Such a short code listing is important.  For **industrial
practitioners:**, short code examples are easier to understand,
adapt, test, maintain and (if required), port to different languages.
Another reason to explore short code solutions are the security
implications associated with building systems based on long supply
chains.  To say the least, it is prudent to replace long supply
chains with tiny local stubs.

Also,  for **teaching (or self-study)**, it has often been suggested
that 1,000 lines of code represents the practical limit in size for
a program which is to be understood and maintained by a single
individual[^lions96].  Most AI tools either exceed this limit by
two orders of magnitude, or else offer the user a very limited set
of facilities, i.e. either the details of the system are inaccessible
to all but the most determined, dedicated and long-suffering student,
or else the system is rather specialised and of little intrinsic
interest.

In my view, it is highly beneficial for anyone studying SE, AI, or
computer science to have the opportunity to study a working AI tool
in all its aspects.  Moreover it is undoubtedly good for students
majoring in Computer Science, to be confronted at least once in
their careers, with the task of reading and understanding a program
of major dimensions.

It is my hope that this doc will be of interest and value to students
and practitioners of AI.  Although not prepared primarily for use
as a reference work, some will wish to use it as such. For those
people, this code comes with extensive digressions on how parts of
it illustrate various aspects of SE, AI, or computer science.


## Coding Style

### No OO

No OO. hatton. 

### DRY 

docu 

### TDD

### Min LOC. Keep readability

#### Functional  
#### Ternary
#### Auto-typing
#### Comprehensions


### DSL 


Rule of three




Accordingly, EZR.py
usies active learnng to build models froma very small amunt of dat.
Its work can be sumamrised as A-B-C.

- **A**: Use **a**ny examples
- **B**: **B**uild a model
- **C**: **C**heck the model

EZR supports not just the code but allso the statsitical functions that
lets analst make clear concluios about (e.g.) what kinds of clustering leads
to better conclusions, sooner. With this it...

Teaching . illustrates much of what is missing in current programmer and sE ltierature (oatterns of productinve coding, isuess of documentation,
encapultion test drivend evelopment etc). It can also be used a minimal AI teaching toolkit that indotruces
students to clustering. Bayes inference, classfication, rule earling, tree elarning
as well as the stats required to devalauted which of these tools is best for some current data/

## Motivation

### Should make it simpler

### Can make i simpler

EZR was motivated by the current industrial obsession on Big AI
that seems to be forgetting centuries of experience with data mining.
As far back as 1901, Pearson[^pca] showed  that tables of data with
$N$ columns can be modeled with far fewer columns (where the latter
are derived from the  eigenvectors of a correlation information).

Decades of subsequent work  has shown that effective models can be
built from data that cover tiny fractions of the possible data
space[^witten].  Levnina and Biclet cwnote that

> "The only reason any (learning) methods work ...
  is that, in fact, the data are not truly high-dimensional. Rather,
  they are .. can be efficiently
   summarized in a space of a much lower dimension.

(This remarks echoes an early conclusion from Johnson and Lindenstrauss [^john84].).


For example:

- **Many rows can be ignored**: Data sets with thousands of rows
  can be modeled with just a few dozen samples[^me08a].
  To explain this, suppose we only want to use models that are  well
  supported by the data; i.e. supported by multiple rows in a table
  of data. This means that  many rows in a table can be be replaced
  by a smaller number of exemplars.
- **Many columns can be ignored**:
  High-dimensional tables (with many colummns) can be projected
  into lower dimensional tables while nearly preserving all pairwise
  distances[^john84].  This means that data sets with many columns
  can be modeled with surprisingly few columns.  e.g. A table of
  (say) of $C=20$ columns of binary variables have a total data
  space of $2^{20}$ (which is more than a million).  Yet with just
  dozens to hundred rows of training data, it is often possible to
  build predictors from test rows from that data space.  This is
  only possible if the signal in this data condenses to a small
  regions within the  total data space.
- Researchers in semi-supervised learning note that 
  high-dimensional data often lies on a simpler, lower-dimensional 
  ”manifold” embedded within that higher space [^zh05].

Numerous AI researchers studying NP-hard tasks
report the existence of a small number of key variables that
determine the behavior of the rest of the model. When
such keys are present, then the problem of controlling an
entire model simplifies to just the problem of controlling
the keys.

Keys have been discovered in AI many times and called many different
names: Variable subset selection, narrows, master variables, and
backdoors. In the 1960s, Amarel observed that search problems contain
narrows; i.e. tiny sets of variable settings that must be used in
any solution[^amarel].  Amarel’s work defined macros that encode
paths between the narrows in the search space, effectively permitting
a search engine to leap quickly from one narrow to another.  

In
later work, data mining researchers in the 1990s explored and
examined what happens when a data miner deliberately ignores some
of the variables in the training data. Kohavi and John report trials
of data sets where up to 80% of the variables can be ignored without
degrading classification accuracy[^kohavi97]. Note the similarity with
Amarel’s work: it is more important to reason about a small set of
important variables than about all the variables.  At the same time,
researchers in constraint satisfaction found “random search with
retries” was a very effective strategy.

Crawford and Baker reported that such searches
took less time than a complete search to find more solutions
using just a small number of retries[^crawford]. Their ISAMP
“iterative sampler” makes random choices within a model
until it gets “stuck”; i.e. until further choices do not
satisfy expectations. When “stuck”, ISAMP does not waste
time fiddling with current choices (as was done by older
chronological backtracking algorithms). Instead, ISAMP
logs what decisions were made before getting “stuck”. It
then performs a “retry”; i.e. resets and starts again, this
time making other random choices to explore.

Crawford and Baker explain the success of this strange
approach by assuming models contain a small set of master
variables that set the remaining variables (and this paper
calls such master variables keys). Rigorously searching
through all variable settings is not recommended when
master variables are present, since only a small number of
those settings actually matter. Further, when the master
variables are spread thinly over the entire model, it makes
no sense to carefully explore all parts of the model since
much time will be wasted “walking” between the far-flung
master variables. For such models, if the reasoning gets
stuck in one region, then the best thing to do is to leap at
random to some distant part of the model.

A similar conclusion comes from the work of Williams et
al.[^backdoor]. They found that if a randomized search is repeated
many times, that a small number of variable settings were
shared by all solutions. They also found that if they set
those variables before conducting the rest of the search,
then formerly exponential runtimes collapsed to low-order
polynomial time. They called these shared variables the
backdoor to reducing computational complexity.

Combining the above, we propose the following strategy
for faster reasoning about RE models. First, use random
search with retries to find the “key” decisions in RE models.
Second, have stakeholders debate, and then decide, about
the keys before exploring anything else. Third, to avoid
trivially small solutions, our random search should strive
to cover much of the model.
Code: 

    def Data(src):
      def _guess(row):
        return sum(interpolate(data,row,*pole) for pole in poles)/len(poles)
          
      head, *rows = list(src)
      data  = _data(head, rows)
      poles = projections(data)
      for row in rows: row[-1] = _guess(row)
      return data

### Data 

Shared datasets from research papers by Apel [2],
Chen [^chen22], and Menzies [^nair] are often used as case studies
of optimization in SE research papers. Chen and Menzies are
collaborating to curate the MOOT repository (Multi-Objective
Optimization Testing4) which offers datasets from recent SE
optimization papers for process tuning, DB configuration,
HPO, management decision making etc.


Since our focus is on configuration, we use MOOT data
related to that task (see Table I and II). Fig. 3 shows the typical
structure of those MOOT data sets. The goal in this data is
to tune Spout wait, Spliters, Counters in order to achieve the
best Throughput/Latency. In summary:

- MOOT datasets are tables with x inputs and y goals.
- The first row shows the column names.
- Numeric columns start with uppercase, all others are
/symbolic.
- Goal columns (e.g. Fig. 3’s Throughput+, Latency-) use
  +/- to denote maximize and minimize.

Data:

      x = independent values          | y = dependent values
      --------------------------------|----------------------
      Spout_wait, Spliters, Counters, | Throughput+, Latency-
         10,        6,       17,      |    23075,    158.68
          8,        6,       17,      |    22887,    172.74
          9,        6,       17,      |    22799,    156.83
          9,        3,       17,      |    22430,    160.14
        ...,      ...,      ...,           ...,    ...
      10000,        1,       10,      |   460.81,    8761.6
      10000,        1,       18,      |   402.53,    8797.5
      10000,        1,       12,      |   365.07,    9098.9
      10000,        1,        1,      |   310.06,    9421

Note that our data is much larger than the Table 3 example.
The 39 data sets in Table I have up to 86,000 rows, 88
independent variables, and three y goals.
For the purposes of illustration, the rows in Table 3 are
sorted from best to worst based on those goals. During
experimentation, row order should initially be randomized.

For the purposes of evaluation, all rows in MOOT data sets
contain all their y values. When evaluating the outcome of an
optimizer, these values are used to determine how well the
optimizer found the best rows.

For the purposes of optimization experiments, researchers
should hide the y-values from the optimizer. Each time the
optimizer requests the value of a particular row, this “costs”
one unit. For reasons described below, good optimizers find
good goals at least cost (i.e. fewest labels).

Notes from ase aper

## RQ5: Lmits

not generation.

Tabular data

## References
[^adams21]: Adams, G. S., Converse, B. A., Hales, A. H., & Klotz, L.
E. (2021). People systematically overlook subtractive changes.
Nature, 592(7853), 258-261.

[^amarel]: S. Amarel, “Program synthesis as a theory formation task:
problem representations and solution methods,” in Machine Learning:
An Artificial Intelligence Approach. Morgan Kaufmann, 1986.


[^apel20]: S. Apel, N. Siegmund, C. K¨astner, and A. Legay, “A case
for automated configuration of variability-intensive systems,” IEEE
Software, vol. 37, no. 3, pp. 26–33, 2020.

[^backdoor]: R. Williams, C. P. Gomes, and B. Selman, “Backdoors
to typical case complexity,” in Proceedings of the International
Joint Conference on Artificial Intelligence, 2003.


[^bird23]:  C. Bird et al., “Taking Flight with Copilot: Early
insights and opportunities of AI-powered pair-programming tools,”
Queue, vol. 20, no. 6, pp. 35–57, 2023, doi: 10.1145/3582083.

[^bubeck23]: S. Bubeck et al., “Sparks of artificial general
intelligence: Early experiments with GPT-4,” 2023, arXiv:2303.12712

[^chen22]: M. Li, T. Chen, and X. Yao, “How to evaluate solutions
in pareto-based search-based software engineering: A critical review
and methodological guidance,” IEEE Transactions on Software
Engineering, vol. 48, no. 5, pp. 1771–1799, 2022

[^crawford]: J. M. Crawford and A. B. Baker, “Experimental results
on the application of satisfiability algorithms to scheduling
problems,” in Proceedings of the Twelfth National Conference on
Artificial Intelligence (Vol. 2), Menlo Park, CA, USA, 1994, pp.
1092–1097.


[^fu17]: W. Fu and T. Menzies, “Easy over hard: a case study on
deep learning,” in Proceedings of the 2017 11th Joint Meeting on
Foundations of Software Engineering, ser. ESEC/FSE 2017. New York,
NY, USA: Association for Computing Machinery, 2017, p. 49–60.
[Online]. Available: https://doi.org/10.1145/3106237.  3106256

[^grin22]: L. Grinsztajn, E. Oyallon, and G. Varoquaux, “Why do
tree-based models still outperform deep learning on typical tabular
data?” in NeurIPS’22, 2022.

[^hipp21]: A.G. Bell 2021, The Untold Story of SQLite With Richard
Hipp Corecursive podcast. Interview by Adam Gordon Bell. November
30, 2020. Accessed July 19, 2025.
https://corecursive.com/066-sqlite-with-richard-hipp/

[^hou24]: X. Hou, Y. Zhao, Y. Liu, Z. Yang, K. Wang, L. Li, X. Luo,
D. Lo, J. Grundy, and H. Wang, “Large language models for software
engineering: A systematic literature review,” ACM Trans. Softw.
Eng. Methodol., vol. 33, no. 8, Dec. 2024. [Online]. Available:
https://doi.org/10.1145/3695988

[^john84]: W. B. Johnson and J. Lindenstrauss, “Extensions of
lipschitz mappings into a hilbert space,” Contemporary Mathematics,
vol. 26, pp. 189–206, 1984.

[^john24]: B. Johnson and T. Menzies, “Ai over-hype: A dangerous
threat (and how to fix it),” IEEE Software, vol. 41, no. 6, pp.
131–138, 2024.

[^kohavi97]: R. Kohavi and G. H. John, “Wrappers for feature subset
selection,” Artif. Intell., vol. 97, no. 1-2, pp. 273–324, Dec.
1997.

[^ling86]: X. Ling, T. Menzies, C. Hazard, J. Shu, and J. Beel,
“Trading off scalability, privacy, and performance in data synthesis,”
IEEE Access, vol. 12, pp. 26 642–26 654, 2024.

[^lions96]: Lions, John (1996). Lions' Commentary on UNIX 6th Edition
with Source Code. Peer-to-Peer Communications. ISBN 978-1-57398-013-5.


[^maju18]:  S. Majumder, N. Balaji, K. Brey, W. Fu, and T. Menzies,
“500+ times faster than deep learning,” in Proceedings of the 15th
International Conference on Mining Software Repositories. ACM, 2018.

[^mani23]: P, Maniatis and D, Tarlow, 2023 Large sequence models
for software development activities.” Google Research. [Online].
Available: https://research.google/blog/ large-sequence-models-for-software
-development-activities/

[^men08a]: T. Menzies, B. Turhan, A. Bener, G. Gay, B. Cukic, and
Y. Jiang, “Implications of ceiling effects in defect predictors,”
in Proceedings of the 4th international workshop on Predictor models
in software engineering, 2008, pp. 47–54.

[^men96a]: T. Menzies, “Applications of abduction: knowledge-level
modeling,” International journal of human-computer studies, vol.
45, no. 3, pp. 305–335, 1996.

[^men25a]: T. Menzies, "Retrospective: Data Mining Static Code
Attributes to Learn Defect Predictors" in IEEE Transactions on
Software Engineering, vol. 51, no. 03, pp. 858-863, March 2025,
doi: 10.1109/TSE.2025.3537406.


[^moot]: T. Menzies and T. Chen, MOOT repository of Multi-objective
optimization tests.  2025.
[http://github.com/timm/moot](http://github.com/timm/moot)

[^nair18]: V. Nair, Z. Yu, T. Menzies, N. Siegmund, and S. Apel,
“Finding faster configurations using flash,” IEEE Transactions on
Software Engineering, vol. 46, no. 7, pp. 794–811, 2018.

[^pca]:  Pearson, K. (1901). "On Lines and Planes of Closest Fit
to Systems of Points in Space". Philosophical Magazine. 2 (11):
559–572. 10.1080/14786440109462720.

[^sett09]: Settles, Burr. "Active learning literature survey." (2009).

[^somy24]:  S. Somvanshi, S. Das, S. A. Javed, G. Antariksa, and
A. Hossain, “A survey on deep tabular learning,” arXiv preprint
arXiv:2410.12034, 2024.


[^taba23]:  M. Tabachnyk and S. Nikolov, (20222) “MLenhanced code
completion improves developer productivity.” Google Research Blog.
[Online]. Available: https://research.google/blog/
ml-enhanced-code-completion -improves-developer-productivity/

[^tawo23]: V. Tawosi, R. Moussa, and F. Sarro, “Agile effort
estimation: Have we solved the problem yet? insights from a replication
study,” IEEE Transactions on Software Engineering, vol. 49, no. 4,
pp. 2677– 2697, 2023.

[^witten]:      I. Witten, E. Frank, and M. Hall.  Data Mining:
Practical Machine Learning Tools and Techniques Morgan Kaufmann
Series in Data Management Systems Morgan Kaufmann, Amsterdam, 3
edition, (2011)

[^zhu05]: X. Zhu, “Semi-supervised learning literature survey,”
Computer Sciences Technical Report, vol. 1530, pp. 1–59, 2005.
