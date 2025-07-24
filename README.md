---
title: "A Little Less AI (tiny models, more power)"
author:  "Tim Menzies<br>timm@ieee.org"
date: "July, 2025"
---

------------------------------------------------------
_"The best thing to do with most data is throw it away."_ --me

_"YAGNI"_ (you aren't gonna need it) --Kent Beck

_"Less, but better."_  --Dieter Rams  

_"Subtract."_ --Leidy Klotz
------------------------------------------------------

To say the least, everyone is focused on big AI right that assumes

What should we be teaching newcomers to software engineering? Talking
with fellow instructors, we’ve noticed two growing challenges.
First, students often lack practice in analyzing and critiquing
code. Post-COVID learners, raised on search engines and chatbots,
are great at vibing with code—copying, tweaking, prompting—but less
adept at understanding what makes it tick. Second, the systems they
encounter often feel too large or opaque to examine. As Leidy Klotz notes, people systematically overlook
subtractive changes—we keep adding, even when taking away would
serve us better. This leads to complexity and bloat.
In teaching, it overwhelms. Such complexity means that code is
something that appears on a screen, not something they can explore and own and shape.

These challenges are connected. Simpler systems invite deeper
engagement and more ownership.  D. Richard Hipp, creator of SQLite,
says “If you want to be free, that means doing
things yourself.”[^hipp21] He likens it to backpacking—carrying
only what you need to move freely. You do not need to build Microsoft
Windows; you need just enough to do something meaningful. This book
shows how powerful results can emerge from surprisingly little code
and data.

That ethic—simplicity, self-reliance, deep understanding—is fading.
For many, that’s fine; it means producing more code, more quickly.
But for engineers tasked with building reliable, high-quality systems
under real-world constraints, that loss matters. We must teach what
happens inside the code, especially the complex systems that power
today’s AI. As these tools proliferate, we need code surgeons who
can diagnose, intervene, and improve what lies beneath the surface.
We need to reclaim authorship of our code, encouraging understanding
and fostering a mindset of critique rather than cargo cult reuse.



This reluctance to look inside has serious consequences. Chief among
them is the crisis of *reproducibility*: big AI experiments are
difficult to replicate, and comparative evaluations are rare. For
example, a recent review[^hou24] of 229 software engineering papers
using LLMs (a big AI technique) found that only 13 (just 5%)
compared their results to any alternative. This lack of introspection
is not only methodologically flawed; it also suppresses innovation.
As seen in the _[Example](#examples)_ section, simpler approaches
can often perform just as well—or better—while being faster, more
transparent, and easier to critique_[^hou24] [^fu17] [^grin22]
[^ling86] [^maju18] [^somy24] [^tawo23].

So what are those alternatives? “Less AI” offers one path forward.
Where big AI emphasizes volume, less AI assumes that useful models
are tiny gems obscured by irrelevant or noisy or redundant data.
Finding useful models is a hence a progress of pruning anything
that  is superfluous or confusing. To say that another way:

> **Menzies's 4th law:** The best thing to do with most data is throw it away[^men25a].

**EZR** is a compact implementation of this law. It is an incremental
_active learner_[^sett09], which means "what to do next" is determined
from "what has been seen so far". By peeking at the data before
processing it, tools like **EZR** can avoid irrelevancies, redundancies,
and noisy data.  In this way, models can be built, very quickly,
from very little data.  In just a few hundred lines of code, EZR
supports a wide range of core AI tasks—classification, clustering,
regression, active learning, multi-objective optimization, and
explainability.

This research note introduces EZR and explains its design, motivation,
and implications. After a code walk-through, we evaluate EZR using
over 100 diverse examples from the [MOOT
repository](https://github.com/timm/moot)[^moot], which captures
problems from software engineering optimization, such as tuning
analytic tools, adjusting configuration parameters, and guiding
software process decisions.

The MOOT benchmarks help answer several core questions
about EZR:

- **RQ1: Is it simple?**  
  Yes- EZR has a compact, readable codebase, ideal for teaching 
  and tinkering.

- **RQ2: Is it fast?**  
  Yes— EZR completes tasks in milliseconds that take 
  hours for big AI.

- **RQ3: Is it effective?**  
  Yes— MOOT's active learners achieve near-optimal results 
  after seeing just a few dozen examples.

- **RQ4: Is it insightful?**  
  Yes— EZR reveals a perspective on learning that encourages explanation and critical analysis, not just automation.

- **RQ5: Is it general?**
  Within the scope of MOOT-style optimization of SE tasks, yes. While not
  designed for text generation (you’ll still need LLMs for that),
EZR excels at fast model building and external critique—an essential
  capability when teaching students to open up and reason about AI
  systems.


[^ahmed25]:  Toufique Ahmed, Premkumar Devanbu, Christoph Treude, and
Michael Pradel. Can LLMs replace manual annotation of software
engineering artifacts? In MSR’25, 2025

[^costly]: slow Recently Tu et al.[^tu20] we were studying one same
of 700+ software projects, including 476K commit files. After an
extensive analysis, they proposed a cost model for labeling that
data. Assuming two people checking per commit, that data would need
three years of effort to label the data.

[^tu20]: Tu, Huy, Zhe Yu, and Tim Menzies. "Better data labelling
with emblem (and how that impacts defect prediction)." IEEE
Transactions on Software Engineering 48.1 (2020): 278-294.

[^error]: Human annotators often make many mismakes.  For example,
Yu et al.’s technical debt analysis [^yu22] revealed that 90% of
purported false positives actually represented manual labeling er-
rors. Similar patterns of errors in manual annotations are found
in security defect identification [^wu22] and static analysis false
positive classification [^yang22].

[^wu22]: Xiaoxue Wu, Wei Zheng, Xin Xia, and David Lo. Data quality
matters: A case study on data label correctness for security bug
report prediction. IEEE Transactions on Software Engineering,
48(7):2541–2556, 2022.

[^yu22]: Zhe Yu, Fahmid Morshed Fahid, Huy Tu, and Tim Menzies.
Identifying self-admitted technical debts with jitterbug: A two-step
approach. IEEE Transactions on Software Engineering, 48(5):1676–1691,
2022.

[^yan22]: Hong Jin Kang, Khai Loong Aw, and David Lo. Detecting
false alarms from automatic static analysis tools: How far are we?
In Proceedings of the 44th International Con- ference on Software
Engineering, ICSE ’22, page 698–709, New York, NY, USA, 2022.
Association for Computing Machinery

## Installation

To run the examples of this book:

    mkdir demo; cd demo
    git clone https://github.com/timm/moot # <== data
    git clone https://github.com/timm/ezr  # <== code
    cd ezr
    python3 -B ezr.py -f ../moot/optimize/config/SS-M.csv 

## A Quick Example

Just to give all this a little context, here's a quick example to get us going.

Say we want to configure a database to reduce energy use,
runtime, and CPU load. The database exposes dozens of tuning
options—storage, logging, locking, compression, encryption, and
more. Understanding how each setting impacts performance is daunting.

Imagine we have a log of 800+ configurations, each showing binary
control options and their effects. Some settings are "best"
and lead to low energy, runtime and cpu usage; e.g. 

```
choices                     Effects
----------------            -----------------------
control settings →            Energy-, time-,  cpu-
0,0,0,0,1,0,...               6.6,    248.4,   2.1   ← best
1,1,0,1,1,1,...              16.8,    518.6,  14.1   ← rest
...
```

Given such a log, any number of AI tools could learn a model for what predicts for "best"
and what avoids "rest".
But here’s the problem: most real-world scenarios don’t come with
complete logs. Labeling each configuration (e.g., by running benchmarks
or consulting some human expert) is expensive, slow, and (sometimes) even impossible. So
how can we learn anything useful, with least effort (i.e. after asking for fewest labels).

That’s where **EZR** comes in. It uses a minimalist **A-B-C** strategy:

- **A: Ask anything**  
  Randomly sample a few rows (e.g., _A = 4_) and label them to seed the process. In this seed,
  we build two models (one for "best" and one for "rest"). For unballed rows, this
  models can report 
  the likelihood that
  some new example belongs to "best" or "rest" (these are called _b,r_).
  
- **B: Build a model**  
  Iteratively label up to _B = 24_ additional rows. Each new row is selected based on its potential to improve the model
  (specifically, we look for things that maximize $b/r$).

- **C: Check the model**  
  Apply the model to all unlabeled rows, then evaluate just a few (e.g., _C = 5_) of the most promising ones.


In this example, after labeling just 24 out of 800 rows (∼4%), EZR constructs a decision tree with interpretable rules. One path to a near-optimal configuration is:

```
if crypt_blowfish == 0 and 
   memory_tables == 1 and 
   small_log == 0 and 
   logging == 0 and 
   txc_mvlocks == 0 and 
   no_write_delay == 0
then win ≈ 99%
```

In the above "win" is a measure of how close we get to optimum. A
"win" of zero means we have not changed anything and a "win" of 100
means we are found ways to select for the best values. This branch
achieves a 99% "win" so it very nearly perfect.

To test this model, EZR applies it to all 800 rows and selects the
top _C = 5_ rows it predicts to be best. The actual measured
performance of those five rows confirms the model's judgment: the
top pick is within 2% of the global best.

All this was achieved with only a few dozen queries, processed by just a few hundred lines of code.  
Think of it as the Pareto principle on steroids. **Vilfredo Pareto** proposed that 80% of the gain often comes from just 20% of the work — and throughout the history of AI, many analogous results reinforce this idea:

The history of "Less AI":

| Year     | What                     | Who / System         | Notes                                                                                   |
|----------|--------------------------|-----------------------|-----------------------------------------------------------------------------------------|
| 1902     | PCA                      | Pearson               | Large datasets projected to a few components.                                           |
| 1960s    | Narrows         | Amarel [^amarel]      | Chess search guided by tiny sets of key variable settings.                              |
| 1980s    | ATMS       | de Kleer              | Diagnoses focus only on assumptions independent of others.                              |
| 1984     | Distance-Preseration | Johnson & Lindenstrauss [^john84] | High-dimensional data can be embedded in low dimensions while preserving pairwise distances. |
| 1996     | ISAMP                    | Crawford & Baker [^crawford] | Fast random retries outperform exhaustive backtracking.                                  |
| 1997     | Feature Subset Selection | John & Kohavi [^kohavi97] | Up to 80% of features can be ignored without hurting accuracy.                          |
| 2002     | Backdoors                | Williams et al. [^backdoor] | Setting a few variables reduces exponential runtimes to polynomial.                     |
| 2005     | Semi-Supervised Learning | Zhou et al. [^zh05]   | Data often lies on low-dimensional manifolds inside high-dimensional spaces.            |
| 2008     | Exemplars                | Menzies [^me08a]      | Small samples can summarize and model large datasets.                                   |
| 2009     | Active Learning          | Settles [^settles09]  | Selectively query the most informative examples. <br>Unlike semi-supervised methods, the learner actively shapes its training set. |
| 2005–20  | Key Vars in SE           | Menzies et al.        | Dozens of SE models controlled by just a few parameters.                                |
| 2010+    | Surrogate Models         | Various               | Optimizers can be approximated from small training sets.                                |
| 2020s    | Model Distillation       | Various               | Large AI models reduced in size by orders of magnitude with little performance loss.    |

---


Inspired by all this, I once write a quick and dirty demonstrator while teaching a graduate class
The resulting code (EZR, version 0.1) 
 peeked at a random sample of the data to learn two tiny models _best_ and _rest_ models. 
 It performed startlingly well. That led to several papers comparing EZR’s minimalist approach to state-of-the-art optimizers. In all cases, **EZR’s “less AI” performed just as well as the more complex systems.**

**Long story short**: with EZR, as with much of intelligent system design,
**success does not come from reasoning about everything**, but from identifying and leveraging just the **right few things**. This idea is widely known but rarely applied. In most cases, new problems are still tackled with overly complex, heavyweight AI tools. Perhaps we need to change that


[^amarel]: S. Amarel, "On representations of problems of reasoning about actions", 1960s.  
[^crawford]: C. Crawford & A. Baker, "Experimental Results with ISAMP", 1994.  
[^john84]: W. Johnson and J. Lindenstrauss, "Extensions of Lipschitz mappings...", 1984.  
[^kohavi97]: R. Kohavi and G. John, "Wrappers for feature subset selection", 1997.  
[^zh05]: D. Zhou et al., "Learning with Local and Global Consistency", 2005.  
[^backdoor]: R. Williams et al., "Backdoors to typical case complexity", 2002.  
[^me08a]: T. Menzies, "The Few Key Rows", 2008 (or your actual source).  
[^settles09]: B. Settles, "Active Learning Literature Survey", 2009.


## Discussion: Why This Works

### Why not label everything?

Because labeling is expensive:

- Some benchmarks are slow to run.
- Some require rebuilding complex systems.
- Manual annotation is costly and error-prone.

Prior work shows that labeling large datasets can take years[^tu20][^yu22][^wu22]. Even using big AI and large language models has limitations: they help only in narrow, well-structured tasks and still require careful deployment[^ahmed25].

### So how does EZR help?

The tiny AI assumption is that 
models are  tiny gems obscured by much irrelevant or noisy or redundant data.
Internally, EZR is an **contrastive active learner**. 
By focusing on examples with large $b/r$ score, EZR 
only processes a handful of examples that most distinguish good from bad.
It labels only the most informative rows (and updates in models from that label).
As a side-effect, this also  dodges 
superfluous or confusing data.
In this way, EZR 
we can very quickly build very effective 
models.

To say all that another way, you do not  need a mountain of information—just the right few examples.


### Why use a decision tree?

Doing, without learning, means you are doomed to doing it all again, every time that  need arises.
But if you can learn some generalization, then the next time something comes up, you already
know how to handle it. According the physicist Enrst Rutherford, your explainations should be as simple
as possible.


> Ernst Rutherford: A theory that you can't explain to a bartender is probably no damn good

Decision trees learned from $_B=24_$ examples are:

- Fast to learn  
- Interpretable  
- Naturally sparse  

Each node splits examples based on a binary feature. Leaves group similar configurations. A single path in the tree becomes a recipe for improvement.

### How is "win" defined?

EZR uses a normalized utility score:

    win = 100 × (1 - (x - best) / (median - best))

Here `x` is the performance of a configuration, `best` is the global best, and `median` is a typical value.  
    - A win of **100** means matching the best.  
    - A win of **0** means average.  
    - Negative wins mean regression.

### How General is This?

For years, we have been collecting what are known as "search-based
SE" problems into the MOOT repository (MOOT= multi-objective
optimization tests).  The above case study is one of over 110 data
sets in MOOT.  As shown by the following table, MOOT data can have up tp
has 100,000 rows, over 1000 choices, and up to 3 effects. More usually,
MOOT data
has 10,000 rows,9 choices and 3 effects.

|percentile|25| 50| 75|100|
|---------:|---:|------:|-:|--:|
|#rows     | 1023| 10,000|10,000| 100,000| 
|#choices  | 5  | 9 | 20 |1,044|
|#effects  | 2 | 3 | 3|3|


To assess EZR on all that data, ten times, we divided each data set into a train and test set (50:50). Next:

- A tree was built by EZR on the training data;
- Test rows were sorted using the tree's predictions;
- The top _C=5_  predictions were then labelled and the win of the best row was printed. 
- Just as a prudence check, this was compared against dumb guessing. _C=5_ rows were picked random from the test set, sorted them by their labels, and win of the best row (selected by this
dumb 
   method) was printed.

For this experiment, we used the same control parameters as seen above; i.e. _A,B,C_=4,24,5.
Across these 10 experiments with 110 case studies, EZR usually found a "win" of 70%.

|percentile| EZR | delta = EZR - dumb|
---------:|-----:|-----:|
|10 | 17 | -12|
|20|  35| 0|
| 30|  42| 0|
| 40|  59| 3|
| 50|  70| 8|
| 60|  81| 15|
| 70|  93| 27|
| 80|  99| 43|
| 90| 100 | 64|
| 100| 100| 148|

Here if the delta to "dumb" is zero or less, then EZR's trees do no better than dumb guessing.
Note that "dumb" dies surprisingly well: 30% of the time, just bumbling around looking at five things does as good as anything else. 
The success of "dumb" speaks volumes on the current obsession with big AI. Sure, sometimes we need very complex solutions. But in a surprisingly
large number of cases, dumb old guessing does very well.

That said, we should not use "dumb":

- EZR's trees  often do  much better than dumb (see the large number of positive deltas). 
- With the dumb method, there is no generalizing. From five randomly selected rows, it is hard to learn any generalization about the domain.
- On the other hand, EZR does not just make recommendations. It also returns a 
  tree describing how those recommendations are generated. That is, EZR lets other people audit or critique (or even complain) about how decisions are being made.

It might be argued that "dumb" is preferred to EZR since it it so simple. That is perhaps not the  strongest argument. As shown below, EZR is not complex code (just a few hundred lines). 
Also, it runs very
fast. The entire experiment described about (10 trials over 110 data sets) took
just 65 seconds (on a 10 core mac mini with no GPUs and only 16GB of memory.).

### And what does all this tell us?

That, sometimes, complexity is unnecessary. With small tools, small data, and smart strategies, we can solve real problems efficiently.

**EZR** demonstrates how to teach and practice software engineering grounded in:

- Simplicity  
- Critique  
- Ownership  

all without sacrificing performance.


[^tu20]: Tu, Huy, Zhe Yu, and Tim Menzies. "Better data labelling with emblem (and how that impacts defect prediction)." *IEEE TSE*, 48.1 (2020): 2



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
