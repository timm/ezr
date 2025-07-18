---
title: "Inside Easier AI"
author:  "Tim Menzies<br>timm@ieee.org"
date: "July, 2025"
---

_"Hush! Or I will replace you with a very small shell script."_

-------------------------------

This doc is an attempt to explain in detail the
nucleus of some of the more interesting AI methods to appear in recent years.

EZR.py is a "little AI" tool. Big AI needs
massive amounts of data and CPU. Little AI, on the other hand,
assumes that models are tiny gems,
obscured by vast amounts of detail that is irrelevant or noisy or superfluous.
Under that assumption:

> The best thing to do with most data, is throw it away.

EZR is an interesting candidate for formal
study , for the following reasons:

- its system requirements are so lwo, it can  run on system that are already available to all of us;
- it is compact and accessible;
- it provides an extensive set of very usable facilities;
- it is intrinsically interesting, and in fact breaks
  new ground in a number of areas.

Not least amongst the charms and virtues of EZR
is the compactness of
its source code: comfortable less than 1,000 lines of code including tools for clustering,
classification, regression, optimization, explanation, active learning, statistical analysis,
documentation, and test-driven development.

Such a short code listing
is important since it has often been suggested that 1,000 lines of
code represents the practical limit in size for a program which is to be understood and maintained by
a single individual[^lions96]. Most AI tools
either
exceed this limit by one or even two orders of magnitude, or else offer the user a very limited set of
facilities, i.e. either the details of the system are
inaccessible to all but the most determined, dedicated and long-suffering student, or else the system
is rather specialised and of little intrinsic interest.

In my opinion, it is highly beneficial for students to have the opportunity to study a working
AI tool in all its aspects.
Moreover it is undoubtedly good for students
majoring in Computer Science, to be confronted at
least once in their careers, with the task of reading
and understanding a program of major dimensions.

It is my hope that this doc will be of interet
and value to students and practitioners of AI.
Although not prepared primarily
for use as a reference work, some will wish to use it
as such.




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

[^backdoor]: R. Williams, C. P. Gomes, and B. Selman, “Backdoors
to typical case complexity,” in Proceedings of the International
Joint Conference on Artificial Intelligence, 2003.

[^amrel]: S. Amarel, “Program synthesis as a theory formation task:
problem representations and solution methods,” in Machine Learning:
An Artificial Intelligence Approach. Morgan Kaufmann, 1986.

[^crawford]: J. M. Crawford and A. B. Baker, “Experimental results
on the application of satisfiability algorithms to scheduling
problems,” in Proceedings of the Twelfth National Conference on
Artificial Intelligence (Vol. 2), Menlo Park, CA, USA, 1994, pp.
1092–1097.

[^kohavi97]: R. Kohavi and G. H. John, “Wrappers for feature subset
selection,” Artif. Intell., vol. 97, no. 1-2, pp. 273–324, Dec.
1997.

[^men96a]: T. Menzies, “Applications of abduction: knowledge-level
modeling,” International journal of human-computer studies, vol.
45, no. 3, pp. 305–335, 1996.


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

[^apel20]: . Apel, N. Siegmund, C. K¨astner, and A. Legay, “A case for automated
configuration of variability-intensive systems,” IEEE Software, vol. 37,
no. 3, pp. 26–33, 2020.

[^chen22]: M. Li, T. Chen, and X. Yao, “How to evaluate solutions in pareto-based
search-based software engineering: A critical review and methodological
guidance,” IEEE Transactions on Software Engineering, vol. 48, no. 5,
pp. 1771–1799, 2022

[^nair18]: V. Nair, Z. Yu, T. Menzies, N. Siegmund, and S. Apel, “Finding faster
configurations using flash,” IEEE Transactions on Software Engineering,
vol. 46, no. 7, pp. 794–811, 2018.


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

### Caveats

not generation.

Tabular data

## References

[^john84]: W. B. Johnson and J. Lindenstrauss, “Extensions of
lipschitz mappings into a hilbert space,” Contemporary Mathematics,
vol. 26, pp. 189–206, 1984.

[^lions96]: Lions, John (1996). Lions' Commentary on UNIX 6th Edition
with Source Code. Peer-to-Peer Communications. ISBN 978-1-57398-013-5.

[^me08a]: T. Menzies, B. Turhan, A. Bener, G. Gay, B. Cukic, and
Y. Jiang, “Implications of ceiling effects in defect predictors,”
in Proceedings of the 4th international workshop on Predictor models
in software engineering, 2008, pp. 47–54.

[^pca]:  Pearson, K. (1901). "On Lines and Planes of Closest Fit
to Systems of Points in Space". Philosophical Magazine. 2 (11):
559–572. 10.1080/14786440109462720.

[^witten]:      I. Witten, E. Frank, and M. Hall.  Data Mining:
Practical Machine Learning Tools and Techniques Morgan Kaufmann
Series in Data Management Systems Morgan Kaufmann, Amsterdam, 3
edition, (2011)

[^zhu05]: X. Zhu, “Semi-supervised learning literature survey,”
Computer Sciences Technical Report, vol. 1530, pp. 1–59, 2005.
