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

## Introduction

Much of today’s AI research is dominated by resource-intensive
methods. Such “Big AI” depends on massive training datasets and prolonged
compute time. When so much effort is concentrated in one direction,
it becomes essential to ask: what might we be missing by not exploring
alternatives?

That question surfaced during a graduate AI course, when a student
asked:

> Why do our models need so much data?

“Maybe they don’t,” I replied. “Maybe we just haven’t learned how
to ask the right questions.”

So we tried. We built a simple prototype—ABC (version 0)—that
randomly labeled a few examples, split them into "best" and "rest,"
and used a basic Bayes classifier to pick what to label next
(ABC explored
examples likely to be most “best” and least “rest”). 
The whole
rig was fast (millisecond run time)
and very small (less than 250 lines of Python that did not
need elaborate packages like "pandas" or "scikit-learn").
Nevertheless,
after just 20–30
labels, ABC could achive near-optimal
car designs.
Further, ABC's decision tree could
summarized the
labeled data, yielding clear, compact explanations. 
 
This suprising success of ABC lead to another question:

> “Was this just a fluke?  Were the datasets used above unusually
easy?”

To test whether our initial success was just luck, we went looking
for harder problems. We gathered over 110 real-world case studies
from recent, peer-reviewed software engineering research—covering
configuration optimization, architecture tuning, effort estimation,
and more. Then we reran the experiment at scale.

Again, it worked—quickly and effectively.

That result shifted our thinking. This wasn’t luck—it pointed to
something deeper: an approach to software engineering and AI where
a few well-chosen examples outperform brute-force data collection.
For centuries, researchers have relied on contrastive reasoning,
key variable selection, and strategic sampling to solve complex
problems efficiently (see Table 1).

Yet despite this legacy of elegant minimalism, today’s trends often
favor the opposite: ever-larger models, more data, and growing
complexity. There are many reasons for this[^subtract], but a major
one is inertia—we tend to add rather than subtract, mistaking bloat
for progress.





| Year     | What                     | Who / System         | Notes                                                                                   |
|----------|--------------------------|-----------------------|-----------------------------------------------------------------------------------------|
| 1902     | PCA                      | Pearson               | Large datasets projected to a few components.                                           |
| 1960s    | Narrows         | Amarel [^amarel]      | Chess search guided by tiny sets of key variable settings.                              |
|1974|     | Prototypes| Chang [^chang74] | Speeding up nearest neighbor. Only use best exemplars. Discard 90% of data. |
| 1980s    | ATMS       | de Kleer              | Diagnoses focus only on assumptions independent of others.                              |
| 1984     | Distance-Preseration | Johnson and Lindenstrauss [^john84] | High-dimensional data can be embedded in low dimensions while preserving pairwise distances. |
| 1996     | ISAMP                    | Crawford & Baker [^crawford] | Fast random retries outperform exhaustive backtracking.                                  |
| 1997     | Feature Subset Selection | John & Kohavi [^kohavi97] | Up to 80% of features can be ignored without hurting accuracy.                          |
| 2002     | Backdoors                | Williams et al. [^backdoor] | Setting a few variables reduces exponential runtimes to polynomial.                     |
| 2005     | Semi-Supervised Learning | Zhou et al. [^zh05]   | Data often lies on low-dimensional manifolds inside high-dimensional spaces.            |
| 2008     | Exemplars                | Menzies [^me08a]      | Small samples can summarize and model large datasets.                                   |
| 2009     | Active Learning          | Settles [^settles09]  | Selectively query the most informative examples. <br>Unlike semi-supervised methods, the learner actively shapes its training set. |
| 2005–20  | Key Vars in SE           | Menzies et al.        | Dozens of SE models controlled by just a few parameters.                                |
| 2010+    | Surrogate Models         | Various               | Optimizers can be approximated from small training sets.                                |
| 2020s    | Model Distillation       | Various               | Large AI models reduced in size by orders of magnitude with little performance loss.    |


[^chang74]: Chang, C. L. (1974). Finding Prototypes for Nearest Neighbor Classifiers. IEEE Transactions on Computers, C-23(11), 1179–1184.--



So what to do? Perhaps, what is needed is an example. Some tiny code base running over many data sets achieving good performance without needing much data.
Enter this doc
We need to ask:

> Can we still get most of the value with much less?



So this document is about:
- an idea: **less, but better**
- a very small code base: **that operationalizes that idea**
- and a large test suite: **that checks if the idea generalizes across diverse domains**

Using this code and data, we ask five questions:

- **RQ1: Is it simple?**  
  Is our code base  compact abd readable and suitabke for teaching and tinkering?

- **RQ2: Is it fast?**  
  Can our code complete tasks in milliseconds rather than hours?

- **RQ3: Is it effective?**  
  Can our achieve strong results after seeing only a few examples?

- **RQ4: Is it insightful?**  
  Does our code support explainability, critique, and understanding?

- **RQ5: Is it general?**  
  Does our code apply across varied SE optimization tasks?


All the code and data used here can be accessed as fllows

    mkdir demo; cd demo
    git clone https://github.com/timm/moot # <== data
    git clone https://github.com/timm/ezr  # <== code
    cd ezr
    python3 -B ezr.py -f ../moot/optimize/config/SS-M.csv # <== test case 

## A Quick Example

Just to give this some context, here’s a concrete case.

Say we want to configure a database to reduce energy use, runtime, and CPU load. The system exposes dozens of tuning knobs—storage, logging, locking, encryption, and more. Understanding how each setting impacts performance is daunting.

Imagine we have a log of 800+ configurations, each showing the settings and their measured effects. Some settings lead to excellent results:

```
choices                     Effects
----------------            -----------------------
control settings →            Energy-, time-,  cpu-
0,0,0,0,1,0,...               6.6,    248.4,   2.1   ← best
1,1,0,1,1,1,...              16.8,    518.6,  14.1   ← rest
...
```

In theory, any number of AI tools could learn what separates “best” from “rest.” But here's the challenge: **labeling** each configuration—e.g., by running benchmarks—is expensive. So how can we learn a model with minimal effort?

That’s where **EZR** comes in. It uses a minimalist A–B–C strategy:

- **A: Ask anything**  
  Randomly label a few examples (e.g., _A = 4_) to seed the process.

- **B: Build a model**  
  Build contrastive models for “best” and “rest,” then label up to _B = 24_ more rows that maximize the score _b/r_, where `b` and `r` are likelihoods from those two models.

- **C: Check the model**  
  Apply the learned model to unlabeled data and evaluate a small set (e.g., _C = 5_) of the most promising rows.

In this task, after labeling just 24 out of 800 rows (∼3%), EZR constructs a readable decision tree. One high-performing path looks like this:

```
if crypt_blowfish == 0 and 
   memory_tables == 1 and 
   small_log == 0 and 
   logging == 0 and 
   txc_mvlocks == 0 and 
   no_write_delay == 0
then win ≈ 99%
```

That “win” score means we’re nearly matching the globally best result—using only a fraction of the available data.

In testing, EZR applied its model to all 800 configurations, selected the top _C = 5_, and found that the best of those was within 2% of the known global best.

All of this took just a few dozen queries—and a few hundred lines of code. It’s a striking illustration of the Pareto principle: **most of the value often comes from just a small fraction of the effort**. EZR shows that with the right strategy, a handful of examples can uncover nearly all the signal.  
**EZR is Pareto on steroids.** While Pareto said that 80% of the results come from 20% of the effort, **EZR is more like 99% of the gain from 1% of the work**.


## Discussion: Why This Works

### Why not label everything?

Because labeling is costly:

- Benchmarks take time to run.
- Some configurations require complex rebuilds.
- Human evaluation is slow, expensive, and error-prone.

Prior work has shown that even with big compute, building labeled datasets takes **months or years**. EZR sidesteps this by labeling only what matters most.

---

### So how does EZR help?

EZR operates under a **tiny-AI assumption**: most of the signal is buried under a layer of irrelevant or redundant data. It learns by contrast—focusing on what most separates good from bad using a simple `b/r` score.

This means:
- Fewer labeled examples  
- Less noise  
- Faster inference  
- Smaller, more transparent models  

---

### Why use a decision tree?

Decision trees are:

- **Fast to train**  
- **Sparse by nature**  
- **Easy to read**

As physicist Ernest Rutherford famously quipped:  
> “A theory that you can’t explain to a bartender is probably no damn good.”

Each path in the tree offers a **human-readable recipe for improvement**, grounded in real measurements.

---

### How is “win” defined?

We normalize utility as:

```python
win = 100 × (1 - (x - best) / (median - best))
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

XXXX need to explain ABC

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


Note that, one time in ten, even dumb guessing gets lucky and does  surprisingly well (the 10% case where "dumb" is 12% better than ABC).
But we do not want to be "dumb"
since dumb reasoning does not generalize. On the other hand, **ABC’s trees provide both performance and understanding.** To say that another way,
dumb reasonng just says yes or now. ABC tells you how and why.

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
