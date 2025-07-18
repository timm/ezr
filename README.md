---
title: "Inside Easier AI"
author:  "Tim Menzies<br>timm@ieee.org"
date: "July, 2025"
---



------------------------------------------------------
_"Perfection is achieved not when there is nothing more to add, but when there is nothing left to take away."_ <br>- Antoine de Saint-Exupéry

_"Less, but better."_ <br>- Dieter Rams
------------------------------------------------------

Much current work focuses on "big AI" methods that assume massive
CPU and enormous quantities of training data.  While successful for
a range of generative tasks[^mani23] [^taba23] [^bird23] [^bubeck23],
they have many limitations[^john24].  For example, it is hard to
reproduce results using resource intensive methods.  Hence, it is
hardly surprising that there is very few comparison of big AI to other
methods. A recent systematic review[^hou24] of 229
SE papers using large language models (a big AI method), only 13/229 ≈ 5% of
those papers compared themselves to other approaches.  This is a
methodological error since other methods can produce results that
are better and/or faster [^hou24] [^fu17] [^grin22]
[^ling86] [^maju18] [^somy24] [^tawo23].

So what are alternative approaches for AI (that do not assume deep
learning or large language models)?  One place to start is that,
for the most part, big AI research overlooks decades of work showing
that models are often tiny gems, obscured by vast amounts of detail
that is irrelevant or noisy or superfluous.
"Little AI" assumes that:

> The best thing to do with most data, is throw it away.

EZR is an  active learner; i.e. it  reflects on a tiny model built
so far, to select the next thing to explore.  In this way it can
avoid superfluous, irrelevant, and noisy data.  EZR's  results are
startling.  In just a few hundred lines of code, EZR supports
numerous basic AI tasks.  Using those basic tasks, it then it becomes
quick to code numerous common AI tasks like  clustering or
classification or regression or active learning or multi-objective
optimization or explanation.

This research note describe the "why", "how", and "so what?" of EZR.
After motivating  the work, a code walk
through explores the internals of the tool. EZR is then assessed
using 100+ examples taken from the software engineering optimization
literature.  These examples, available at the MOOT repository[^moot],
are quite diverse and include software process decisions, optimizing
configuration parameters, and tuning learners for better analytics.
Successful MOOT modeling results in better advice for project
managers, better control of   software options, and enhanced analytics
from learners that are better tuned to the local data.

Using MOOT, we can answer many questions about EZR:

- **RQ1**: Is it simple? As seen below, EZR has a very short and
  straight-forward code base.
- **RQ2**: Is it fast?  In milliseconds, EZR can complete tasks
  that take hours using big data methods.
- **RQ3**: Is it effective? In a result supporting the little data 
  assumption, MOOT's active learners  can achieve near-optimal results after
  processing just a few dozen examples.
- **RQ4**: Is it insightful?  Our discussion section argues that
  MOOT offers a unique perspective on science and engineering,
  and what it means to explore the world.
- **RQ5:** Is it general? All our conclusions are based on the MOOT data.
  Hence it is prudent to ask what are the limits of conclusions
  drawn from that kind of experience. For example, our EZR tool is
  not (yet) a tool for generation tasks (for that, you need a large
  language mode like ChatGPT). Nevertheless. its fast runtime and
  explanation tools make it the preferred approach when models must
  be built quickly or critiqued externally.

## A Quick Demo

The file ezr.py contains numerous demos that can be executed from the command line.
For example, k-means clustering groups together similar examples by (a) picking
$k$ centroids at random from amongst the rows of data; (b) labelling each example with he iid of of its nearest centroid; then (c) 

<table>
<tr><td>Fig1: axxx</td></tr><tr><td>

The file ezr.py contains numerous demos that can be executed from the command line.
For example, k-means clustering groups together similar examples by (a) picking
$k$ centroids at random from amongst the _rows_ of data; (b) labelling each example with he iid of of its nearest centroid; then (c) 
</td></tr></table>


# Easer AI: Why?

This section offers motivation for exploring little AI tools like EZR.

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


## A Quick Demo

- A 
- B
- C
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
a
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


[^moot]: T. Menzies and T. Chen, MOOT repository of Multi-objective
optimization tests.  2025.
[http://github.com/timm/moot](http://github.com/timm/moot)

[^nair18]: V. Nair, Z. Yu, T. Menzies, N. Siegmund, and S. Apel,
“Finding faster configurations using flash,” IEEE Transactions on
Software Engineering, vol. 46, no. 7, pp. 794–811, 2018.

[^pca]:  Pearson, K. (1901). "On Lines and Planes of Closest Fit
to Systems of Points in Space". Philosophical Magazine. 2 (11):
559–572. 10.1080/14786440109462720.

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
