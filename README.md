---
title: "Just Enough AI for Software Engineers"
author:  "Tim Menzies<br>timm@ieee.org"
date: "July, 2025"
---

------------------------------------------------------
_"The best thing to do with most data is throw it away."_ --me

_"YAGNI"_ (you aren't gonna need it) --Kent Beck

_"Less, but better."_  --Dieter Rams  

_"Subtract."_ --Leidy Klotz
------------------------------------------------------

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


## A Quick Demo

Just for a quick overview of what EZR can do, suppose we want to configure a database.
For this example, we want our
database to run quick, without burning up too much energy or CPU time

Looking in the  database's  compiler control files, we see an overwhelming number of options for configuring the database,
including:

- storage and indexing options dealing with
  _table\_type, memory\_tables, cached\_tables, small\_cache, large\_cache, small\_log_;
- transaction and locking options that deal with _transaction\_control\_ policies and various other txc (transaction ) issues
  such as  _txc\_mvlocks_, _txc\_mvcc_, and _txc\_locks_
- Logging and durability options that described options for  _detailed\_logging_ and _write\_delay_
- Security options such as  _crypt\_aes_ and _crypt\_blowfish_;
- Compression (which might be enabled or disabled);
- etc

Like many people, you are probably puzzled on how any of these
these effect runtimes, cpu, or energy usage. 
But suppose you had access
to a of log of the effects of these option.
We could  sort the log such that the good rows are first and
the bad rows are last. In the following, all the 0,1 show it if used or ignored
any of the options listed above:

                                                     Energy-, time-,  cpu- 
    0, 0, 0, 0, 1, 0, 1, 0, 1, 1, 0, 0, 0, 1, 1, 1, 0,   6.6, 248.4,  2.1
    0, 0, 0, 0, 1, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0,   6.6, 248.6,  2.0
    0, 0, 0, 0, 1, 0, 0, 1, 1, 1, 0, 0, 0, 1, 0, 0, 0,   6.6, 249.2,  2.0
    0, 0, 0, 0, 1, 0, 0, 1, 1, 1, 0, 0, 0, 1, 1, 0, 0,   6.6, 248.6,  2.1

    [skipping 800 lines...]

    0, 1, 0, 1, 1, 1, 0, 0, 1, 0, 1, 1, 0, 0, 0, 0, 1,  16.7, 519.8, 14.1
    1, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1, 1, 0, 1, 0, 0, 1,  16.8, 518.8, 14.1
    1, 1, 0, 1, 1, 1, 0, 0, 1, 0, 1, 1, 0, 0, 0, 0, 1,  16.7, 519.0, 14.1
    1, 1, 0, 1, 1, 1, 0, 0, 1, 0, 1, 1, 0, 1, 1, 0, 1,  16.8, 518.6, 14.1



ALl these rows show what happens when we run the same benchmark suite of tests.
The _control options_ are shown at left (these are all the 0,1s) and the _effects_
are shown at right (_energy, time, cpu_).
Observe how:

- the four first rows have low energy, runtimes, and cpu;
- while the final four rows run much slower and use more energy and cpu.

So (begin sarcasm), all we have to do is use the control options from  the best rows.
But here are so many things wrong with doing that. 
Firstly, as shown above, some columns seem to be using the same settings in the best and worst rows.
  So we really need to be looking at _contrast sets_; i.e. things that are usually seen in best **and**
  not seen in rest. What EZR does it builds two predictive models: one for the best examples and one for the rest.
  These models check candidate configurations before we waste time running bad ones.
  Each of these models guesses how likely a candidate is _best_ or _rest_. It then only runs
  candidates where _likelihood(best)_ &gt; _likelihood(rest)_.

Secondly, and this one is a huge problem,  it can be hard to access a large log
of data showing the control options **and** their effects.
In this example, we got lucky: some
  researchers in Europe were kind enough to melt down their CPU farm and run nearly 1000 configurations.
  In practice, this rarely happens. For one thing, it can be slow, expensive,
  or impossible to run a large number of benchmarks.

- Some benchmarks are so CPU expensive that we cannot run more a few dozen.
- Some models (and their associated data collection and pre-processing) are so expensive to run more than a few times.
- Some data sets measure the effects of their control variables using data collected from the field. For anything
  associated with data from communities of humans, it can be impossible to ask (say) a software development team
  to reset and rebuidl from scratch their entire product using diffeernt tools.

For this reason, SE makes extensive use of manual annotation methods[^ahmed25],  i.e. some subejct matter
expert
makes up values for the effects columns within a data set.
  But manual annocation
  can be both be  expensive[^costly] and error prone[^error]. Some resarechers have recently turned to large
  language models to automate that kind of reasoning, with only mixed resuts. In one recent detailed
  study on four differnt SE domains. Ahmed et al.[^ahmed25] concluded that these large
  language models
  should be used
as conditional collaborators rather than drop-in replacements for human annotators
sicne their their utility depends on careful deployment, the use of confidence
thresholds, and restriction to tasks with well-structured, repetitive data.


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

To EZR's task is to find control options that lead to the better effects,
_without_ having access to all those effects. If some control setting
looks promising, it can ask that someone finds out its assocaited effects.
But for all the above reasons, it really needs to ask the fewest number of times.

To achieve this magic, EZR uses active learning. Four 
control settings are randomly selected, their effects accessed,
then sorted into the two _best_ and the two _rest_ rows.
At this point EZr's memory contains a few rows with labelled effects;
and many more rows 
where we know what control optinons might be set, but we do not know their effects:

                                                     Energy-, time-,  cpu- 
    0, 0, 0, 0, 1, 0, 1, 0, 1, 1, 0, 0, 0, 1, 1, 1, 0,   6.6, 248.4,  2.1 <== Best1
    0, 0, 0, 0, 1, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0,   6.6, 248.6,  2.0 <== Best2
    0, 1, 0, 1, 1, 1, 0, 0, 1, 0, 1, 1, 0, 0, 0, 0, 1,  16.7, 519.8, 14.1 <== Rest1
    1, 1, 0, 1, 1, 1, 0, 0, 1, 0, 1, 1, 0, 1, 1, 0, 1,  16.8, 518.6, 14.1 <== Rest2
    0, 1, 0, 1, 1, 1, 0, 0, 1, 0, 1, 1, 0, 0, 0, 0, 1,     ?,     ?,    ?
    1, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1, 1, 0, 1, 0, 0, 1,     ?,     ?,    ?
    1, 1, 0, 1, 1, 1, 0, 0, 1, 0, 1, 1, 0, 0, 0, 0, 1,     ?,     ?,    ?
    1, 1, 0, 1, 1, 1, 0, 0, 1, 0, 1, 1, 0, 1, 1, 0, 1,     ?,     ?,    ?

    [skipping 800 lines...]

Next, for anything not yet labelled, EZR looks for one row that is
more more likely to be _best_,
then _rest_. This labelled and sorted into _best_ or  _rest_ rows.
If _best_ ever grows in size more than the square root of the number of labels,
then the worst _best_ row is jumped over to _rest_. In this way, _best_ 
progressively contains more and more of the better rows. 

EZR repeats this, a few dozen times, to generate a few dozen labelled rows. This
is given to a tree learner that generates:
    
     d2h  win    n
    ---- ---- ----
    0.09    0   24
    0.02   74   21    crypt_blowfish == 0
    0.01   90   18    |  memory_tables == 1
    0.00   96   11    |  |  small_log == 0
    0.00   97    6    |  |  |  logging == 0
    0.00   98    5    |  |  |  |  txc_mvlocks == 0
    0.00   99    2    |  |  |  |  |  no_write_delay == 0;   <==== LEAF #1
    0.00   97    3    |  |  |  |  |  no_write_delay == 1
    0.00   97    2    |  |  |  |  |  |  encryption == 1;
    0.01   95    5    |  |  |  logging == 1
    0.01   95    4    |  |  |  |  no_write_delay == 1
    0.01   96    2    |  |  |  |  |  encryption == 1;
    0.01   95    2    |  |  |  |  |  encryption == 0;
    0.02   80    7    |  |  small_log == 1
    0.02   84    6    |  |  |  txc_mvcc == 0
    0.01   87    4    |  |  |  |  compressed_script == 0
    0.01   90    2    |  |  |  |  |  encryption == 0;
    0.01   85    2    |  |  |  |  |  encryption == 1;
    0.02   76    2    |  |  |  |  compressed_script == 1;
    0.11  -23    3    |  memory_tables == 0
    0.11  -15    2    |  |  compressed_script == 0;
    0.56 -518    3    crypt_blowfish == 1
    0.34 -273    2    |  txc_mvlocks == 0;
    17 9 compressed_script, encryption, crypt_blowfish, txc_mvlocks, 
        txc_mvcc, memory_tables, logging, no_write_delay, small_log
    

taht
To answer those questions, first you have to check out the log (from the MOOT repository) and our code:

    mkdir demo; cd demo
    git clone https://github.com/timm/moot # <== data
    git clone https://github.com/timm/ezr  # <== code
    cd ezr
    python3 -B ezr.py -f ../moot/optimize/config/SS-M.csv --tree 

SS.M.csv is a comma-seperated fi

he problem of finding and exmaplin the dofference between good deas na dnbad dieas.
In this apprtciualr example, for a ``good idea'', we suppose we are tweaking the control paraameters
on how to compile software for a database file. Such compiation is controlled by a Makefile
cotnaining nmerous choises incuding the whether or not to do 11 things A,B...K.
SLOC XXX


A- =

      3.0247 * B +
      1.7922 * C +
      0.6417 * D +
      2.2354 * E +
      1.6558 * F +
      1.1448 * G +
     15.6973 * H +
     12.4552 * I +
     16.5112 * J +
     16.8096 * K +
    200.4093

B- =

     -0.1742 * C +
      0.2132 * F +
      0.1585 * G +
    -11.7985 * H +
      2.2523 * I +
      0.7718 * J +
     -0.7594 * K +
     27.0068

|what | notes|
|-----+------|
|file  | SS-L.csv |
|ows   | 1023 |
|y    | 2 |
|x    | 11 |
|asIs   | 63 |
|min    | 16 |

|Samples |explit     | exokire| adapt |
|--------+-----------+--------+-------|
|15      |   29      |     38 |    30 |
| 30     |  23       |     35 |    30 |
|45      | **18 !!** |     35 |    38 |
|60      | **20 !!** |     38 |    31 |
|75      | **17 !!** |     33 |    28 |
|100     | **17 !!** |     28 |    28 |


 d2h  win    n
---- ---- ----
0.53    0   24
0.38   60   10    K <= 0
0.32   81    2    |  G <= 0;
0.39   54    8    |  G > 0
0.37   61    4    |  |  F <= 0
0.36   66    2    |  |  |  D <= 0;
0.38   57    2    |  |  |  D > 0;
0.41   47    4    |  |  F > 0
0.40   52    2    |  |  |  D <= 0;
0.42   43    2    |  |  |  D > 0;
0.63  -42   14    K > 0
0.62  -35   12    |  H > 0
0.61  -34    8    |  |  D > 0
0.60  -31    6    |  |  |  G > 0
0.59  -25    4    |  |  |  |  F > 0;
0.63  -41    2    |  |  |  |  F <= 0;
0.64  -44    2    |  |  |  G <= 0;
0.62  -38    4    |  |  D <= 0
0.61  -33    2    |  |  |  F <= 0;
0.64  -43    2    |  |  |  F > 0;
0.74  -85    2    |  H <= 0;

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
