> Due to teaching and admin commitments, this site has yet to stabilize. The   code base is also changing.. [danger/lite.py](danger/lite.py) contains my current working version of this system. If the code interests you, please contact me directly. 

# A Tiny AI Minifesto

<img src="docs/ezr.png" align=right width=400>

Recently, AI has gotten
very complicated.  The models are now so opaque that they are   hard
to understand or audit or repair.  The CPU required to build and
use them severely limits experimentation and scientific reproduction.
The complexity of this kind of reasoning also complicates industrial
deployment and teaching.

We ask, rhetorically, do all problems need data and CPU intensive
BIG AI methods? Must generative AI and large language models be
used for all reasoning?A alternative to Big AI and generative models
is _Tiny AI_ that uses _predictive models_ for tasks like optimization,
classification and regression.  

Lamentably, Tiny AI methods are
routinely ignored in research and industry.  In a recent systematic
review [^hou24] of 229 SE papers using large language models (LLMs),
only 13/229 (about 5%) of those papers compared LLMs to other
approaches. This is a methodological error since other methods can
produce results that are better and/or faster (See Table 1)


> Table1: Tiny AI versus Big AI

|When          | What|
|--------------|-----|
|2018 [^maju18] | Simple clustering plus predictive AI did better for text mining. | 
|2022 [^grin22] | Large language models may not be the best choice for tabular data. |
|2024 [^somv24] | Ditto |
|2022 [^taw23] | Predictive AI did better for management for agile software development. |
|2024 [^ling24] | Predictive AI did better for data synthesis. |
| 2024 [^john24] | Long list of errors seen in generative AI for software engineering. |



Why is  Tiny AI ignored? Perhaps it is not widely appreciated
the effectiveness of very  simple AI (just as long as we avoid CPU and data intensive
generative modeling). To fix that, this paper offers
EZR, a tiny baseline system
that implements explanations for incremental multi-objective
optimization.  The entire code based is under 500 lines of code
(with 250 lines of test cases). 
It is available as
a
free open source Tiny AI  Python package, accessible via

     pip install ezr

Internally, the code is a greedy elite-search algorithm that builds effective models
from minimal data. EZR sorts a  few labeled examples
into a  _best_ and _rest_ set.  Using cheap-to-collect attributes,
EZR guesses which unlabeled example is most likely _best_, labels it,
then loops.  It skips noisy data (not clearly best or rest) and
superfluous data (irrelevant to improvement), allowing EZR to model
effectively with only a few dozen samples.

(Aside: For readers familiar with AI, EZR sounds like an active learner or
reinforcement learner. While that is where this work
started, repeated simplifications revealed that much of that
complex machinery was unnecessary. For
example: (a) Parzen windows [^berg12] gave way to a
simple nearest-neighbor check against the centers of best and rest;
(b) months of designing explore–exploit heuristics [^settles09] ended in a single
principle: greedily search toward best.)

[^berg12]: Bergstra, James, and Yoshua Bengio. "Random search for hyper-parameter optimization." The journal of machine learning research 13.1 (2012): 281-305.

EZR has been extensively tested on over a 100 problems taken from recent
SE and AI publications. This test data is accessible via

     git clone http://github.com/timm/moot

MOOT, short for "multi-objective optimization tests", contains 118 
test cases with:

- 100 to 100,000 rows (median=1,000)
- 3 to 1000 independent $x$ variables (median=10)
- 1 to 8 dependent $y$ goals (median=3)

Using MOOT, we can measure how little data is needed for effective
modeling.  EZR selects the $x$ values most likely to yield optimal
$y$ values (while labeling as few rows as possible).  Its performance
is scored using a _win_ statistic (defined later), where a win of 0%
means EZR failed and 100% means it found the optimal row.  A labeling
budget controls how many examples EZR may label. As might be
expected, larger budgets
yield higher wins. That said, it is remarkably how little data
is needed for very big wins:

|budget|  median wins <br> for 118 test cases<br>(seen in 20 trails)|
|:-----:|:-----:|
| 10 | 58| 
| 20|  70|
| 30 | 77 |
| 40| 80|
| 80| 88|

With just 10 labeled examples, EZR reaches 58% of the optimum.
By 30 labels, it achieves 77%, which is often good enough for many applications.
If better results are required (e.g. for safety critical applications), 
increasing the budget helps, but with diminishing returns:
doubling the budget from 10 to 20 to 40 to 80
 yields only about 10% improvement each time. 

Since it labels so few examples,
EZR can also be an XAI tool (explanatory artificial intelligence).
For those labeled examples,
EZR  generates a
tiny decision tree that offers
succinct and simple explanation
of how to achieve good results (and  also what to do to improve
those results).  




[^cohen95]: Cohen, Paul R. Empirical methods for artificial intelligence. Vol. 139. Cambridge, MA: MIT press, 1995.

[^holte93]: Holte, Robert C. "Very simple classification rules perform well on most commonly used datasets." Machine learning 11.1 (1993): 63-90.

[^whigham15]: Whigham, Peter A., Caitlin A. Owen, and Stephen G. Macdonell. "A baseline model for software effort estimation." ACM Transactions on Software Engineering and Methodology (TOSEM) 24.3 (2015): 1-11.

[^mittas12]: Mittas, Nikolaos, and Lefteris Angelis. "Ranking and clustering software cost estimation models through a multiple comparisons algorithm." IEEE Transactions on software engineering 39.4 (2012): 537-551.

[^shepped12]: Shepperd, Martin, and Steve MacDonell. "Evaluating prediction systems in software project estimation." Information and Software Technology 54.8 (2012): 820-827.

[^kitch07]: Kitchenham, Barbara A., Emilia Mendes, and Guilherme H. Travassos. "Cross versus within-company cost estimation studies: A systematic review." IEEE Transactions on Software Engineering 33.5 (2007): 316-329.


This paper presents the software behind EZR. As shown below, that
code is very simple (and runs so fast).  Considering the simplicity
and effectiveness of SWAY , we, therefore, propose this approach
as a baseline method for search-based software engineering models,
especially for models that are very slow to execute.

It is very
useful to have a baseline system; i.e., an algorithm which can
generate floor performance values. Such baselines let a developer
quickly rule out any optimization option that falls “below the
floor”. In this way, researchers and industrial practitioners can
achieve fast early results, while also gaining some guidance in
all their subsequent experimentation (specifically: “try to beat the
baseline”).
In his textbook on Empirical Methods for AI, Cohen
[^cohen95] strongly advocates comparing supposedly sophisticated
systems against simpler alternatives. In the machine learning
community, Hotle [^holte93] uses the OneR baseline algorithm as a
scout that runs ahead of a more complicated learner as a way to
judge the complexity of up-coming tasks. Shepperd and Macdonnel
[^shepperd12] argue convincingly that measurements are best viewed
as ratios compared to measurements taken from some minimal baseline
system. Wolpert & Macready [^wolp] warn that no single algorithm can ever be best
for all problems. They caution that for every class of
problem where algorithm A performs best, there is some other
class of problems where A will perform poorly. Hence, when
commissioning a new domain, there is always the need for some
experimentation to match the particulars of the local model to
particular algorithms.




[^wolp]: Wolpert, David H., and William G. Macready. "No free lunch theorems for optimization." IEEE transactions on evolutionary computation 1.1 (2002): 67-82.

Just to be clear, the claim here is that EZR is always the best approach.
Indeed for generative tasks, we (as yet) need to use large langauge models
and Big AI. But not all tasks are generative. Some are predictive,
such as the decision making tasks explored here. 
Large language models train from data available “in the commons”; i.e. all the data generated by (say) programmers
who store their code in Github. In the commons, there may exist many acceptable solutions for (e.g.) how to build a
website in Python. Given a plethora of such solutions, LLMs can offer a useful response to a specific prompt.
However, there are problems that humans rarely address or, if they do, they rarely produce solution that a broad
community would find acceptable. For such “uncommon” tasks, LLMs may lack sufficient training data. Many of the
optimization tasks in MOOT are “uncommon”. For example, our XOMO* data sets come from books discussing process
options for software projects. These data sets list 24 parameters, usually discretized into five ranges (very low, low,
nominal, high, very high). While many publications mention these choices, we know of none that conclude that one
of these 524 ≈ 1016 choices is undeniably better than the rest. Also, several of our models refer to the configuration
of cloud-based software systems. We would also call this an “uncommon” problem since there are some few publicly
available examples of well-configured cloud environment

Also, not all domains support the data needed by big AI.

iJUstThe claim of this paper is not that EZR is always the
best choice exploring options and making decisions.
Rather, since EZR is so
simple and so fast, it is a reasonable first choice for benchmarking
other approaches.

## A Quick Example

Just to give this work some context, here’s a concrete case.

Say we want to configure a database to reduce energy use, runtime,
and CPU load. The system exposes dozens of tuning knobs—storage,
logging, locking, encryption, and more. Understanding how each
setting impacts performance is daunting.

When manual reasoning fails, we can ask AI to help.  Imagine we
have a log of 800+ configurations, each showing the measured effects
of settings to dozens of control settings (shown here as x1,x2,x3...).

```
choices                     Effects
----------------            -----------------------
x1,x2,x3,x4,x4,x5,...  →  Energy-,    time-,  cpu-
0,0,0,0,1,0,...               6.6,    248.4,   2.1   ← best
0,1,1,0,1,0,...               6.6,    250,     2.0   ← best
0,1,0,1,1,1,...              14.7,    510.8,  13.0   ← rest
1,1,0,1,1,1,...              16.8,    518.6,  14.1   ← rest
...
```
Note the "best" fast and energy efficient rows
appear on top (while the "rest" are slower and more energy hungry).

We say the better examples are those that are "closer to heaven".
Say each example achieves goals $g1,g2,...$ which we want to minimize, maximize,... (respectively).
Let the  $most_i$ 
of goal $g_i$ be 0,1 (for minimize, maximize). The distance to heaven $d_y$ of a row
is 
the Euclidean distance to the $most_i$ values:

$$d_y= \sqrt{\left(\sum_i abs(N(g_i)-most_i)^2\right) / len(goals)}$$

where `N` normalizes our goals values min..max as 0..1  The closer to heaven,
the better the example so we say _smaller_ $h$ values are _better_.
Using $d_y$, a list of examples seen-so-far can be sorted into
a small "best" set and a larger "rest" set. For example,  the four rows
shown above are sorted by $d_y$. 

To simplify the reporting, we define _optimal_ to
be the labeled example that is closest to heaven (i.e. has the smallest $d_y$ values).
If $\overline{d_y}$ is the mean $d_y$ of all the rows, and $d_{h}^0$ comes from the optimal
row, and our optimizer returns a row with a  score $d_y$ then the  _win_
of that estimation is the normalized distance from mean to best:

$$win = 100\left(1- \frac{d_y - d_y^0}{\overline{d_y}-d_y^0}\right)$$

A win of 100 means "we have reached the optimal" and a win less than 0 means
an optimization failure (since we are finding solutions worse than before.

Any number of AI tools could learn what separates “best” from “rest.”
But here's the challenge: **labeling** each configuration (e.g.,
by running all the benchmarks for all possible configurations) is
expensive. So the EZR challenge is how to learn an effective model
with minimal effort?

To handle that challenge,  EZR uses a minimalist A–B–C strategy:

- **A=Any**; i.e. "ask anything".
  Randomly label a few examples (say, _A = 4_) to seed the process.

- **B=Build**; i.e.  build a model.
  In this phase, we build separate models for “best” and “rest,” then label up to,
  say _B = 24_ more rows by picking the unlabeled row that maximizes
  the score _b/r_ (where `b` and `r` are likelihoods that a row
  belongs to the "best" and "rest" models).

- **C=Check**; i.e. check the model.
  Apply the learned model to unlabeled data and to select a small
  set (e.g., _C=5_) of the most promising rows. After labeling
  those rows, return the best one.

In this task, after labeling just 24 out of 800 rows (∼3%), EZR
constructs a binary decision tree from those 24 examples. In that
tree, left and right branches go best and worse examples. The
left-most branch of that tree is shown here (and to get to any line
in this tree, all the things above it have to be true).

    if crypt_blowfish == 0
    |  if memory_tables == 1
    |  |  if detailed_logging == 1
    |  |  |  if no_write_delay == 0; <== win=98%
    
These four conditions select rows that are very close
(98%) to  the optimal.

Note that this branch only mentions four
options, and two of those are all about what to turn off. That
is to say, even though this databased has dozens of configuration:q
options, there are two bad things to avoid and only two most
important thing to enable  (_memory\_tables_ and _detailed\_logging_).

EZR shows that with the right strategy, a handful of examples 
(in this case, 24) can
uncover nearly all the signal.  All of this took just a few dozen
queries—and a few hundred lines of code. It’s a striking illustraionof the Pareto principle:  **most of the value often comes from just
a small fraction of the effort**.

Another thing to note here is how fast EZR operates.
The table below shows how long it takes to find a few dozen usefyk examples,
then convert them into a tree.
The above tree came for
SS-M  (see http://github/timm/moot/optimize/config) and
has 862 rows,  3 goals and 17 control settings.
For reference, that table includes results from another problem
with many more colums and rows (in this example, called Scrum,
a  model had generated 10^3, 10^4, and 10^5 samples). In this sample,
 EZR's
runtimes scales linearly when columns are increased (see SS-M vs Scrum1K)
or rows are increased (see Scrum1K to Scrum10K to Scrum100K).

> Table 2: EZR, some performance details.

|file         |x  |y  |rows    | time (secs)| #vars in tree| #vars in branch|
|-------------|--:|---|-------:|------------|--------------|----------------|
|SS-M         | 17| 3 |    862 |       0.15 |            6 |              4 |
|Scrum1K      |124| 3 |  1,000 |       0.72 |            7 |              2 |
|Scrum10K     |124| 3 | 10,000 |       1.29 |            9 |              4 | 
|Scrum100K    |124| 3 |100,000 |       8.54 |           10 |              3 |

As to explaining the inference, EZR produces succinct, easy to read,  models.
The last two columns  show the number of
attributes seen in the generated model. The first row repeats what was shown above:
the SS-M model uses less than half the control settings (6 of 17) and the branch
to the best result only uses four settings. Much larger reductions in the space
of variables can be seen for the Scrum models. The last row
of this table tells us that of 124 settings, only 10 are needed overall and only
3 are found in the best recommendation.



As agents explore the world, choices are easy to spot, but consequences
are slow to measure.

- A shopper can scan hundreds of used cars in minutes but needs
hours of driving to gauge fuel economy.
- A captain can see all possible routes on a map but must spend
hours trawling to find fish.
- A project manager can survey many tools but must spend weeks
testing to know which works best for
  their kinds of programmers working at their specific company.

Formally, this is the _labeling_ problem.  Suppose our goal is to
learn how choices $x$ effect conquences $y$. To learn the   function
$y=f(x)$, we need some examples of ($x,y$) pairs.  There are many
ways to find $y$, each of which has problems:

- Ask  _subject matter expert_ what $y$ values are seen when $x$ happens.
Manual labeling by experts is
widely used but often error-prone.  One problem is that label quality
tends to degrade when experts are rushed to process large corpora [^mes80].
More careful elicitation methods; such as structured interviews can
require up to one to two hours of dedicated effort per
session [^valerdi10] [^kington09] [^lustosa24] to label just ten
examples with ten attributes.
- Consult an _historical log_ of $(x,y)$ pairs: Logs of past project activity provide
labels “for free,” but they frequently contain mistakes. Spot-checking
historical labels often uncovers significant errors: for instance,
Yu et al. [^yu20] found that 90% of technical debt entries marked
as “false positive” were actually correct. Similar mislabeling
issues have been reported in security datasets [^wu21], static
analysis outputs [^kang22], and software quality corpora [^shepperd13].
- Ask a _model_ to automatic labeling some $x$ values.  Naive
model-based labelling can lead to inconsistent or misleading ground
truths (e.g.  when defect prediction labels are gene1zreated by
simplistic matches to keywords like “bug,” “fix,” or “error” [^kamei12]).
More sophisticated models can be constructed, but validating them
requires some reliable ground truth which, once again, creates a
dependency on either expert input or verified historical logs. Large
language models (LLMs) offer a potential shortcut by supplying
general background knowledge, but recent studies [^Ahmed25] warn
that LLM outputs remain assistive rather than authoritative, and
their predictions still require careful human validation.


[^mes80]: Mark Easterby-Smith. The design, analysis and interpretation of repertory grids. In-
ternational Journal of Man-Machine Studies, 13(1):3–24, 1980

[^valerdi10]: Ricardo Valerdi. Heuristics for systems engineering cost estimation. IEEE Systems
Journal, 5(1):91–98, 2010.

[^kington09]: Kington, Alison (2009) Defining Teachers' Classroom Relationships. In: The Social Context of Education. Valentin Bucik., Ljubljana.efining Teachers' Classroom Relationships

[^lustosa24]: Andre Lustosa and Tim Menzies. Learning from very little data: On the value of land-
scape analysis for predicting software project health. ACM Transactions on Software
Engineering and Methodology, 33(3):1–22, 2024

[^kamei12]: Yasutaka Kamei, Emad Shihab, Bram Adams, Ahmed E Hassan, Audris Mockus, Anand
Sinha, and Naoyasu Ubayashi. A large-scale empirical study of just-in-time quality
assurance. IEEE Transactions on Software Engineering, 39(6):757–773, 2012

[^Ahmed25]: Toufique Ahmed, Premkumar Devanbu, Christoph Treude,
Michael Pradel, 2025, Can LLMs Replace Manual Annotation of Software
Engineering Artifacts? MSR'25.
https://software-lab.org/publications/msr2025_LLM-annotation.pdf


[^yu20]: Yu, Z., Fahid, F. M., Tu, H., & Menzies, T. (2020).
Identifying self-admitted technical debts with jitterbug: A two-step
approach. IEEE Transactions on Software Engineering, 48(5), 1676-1691.

[^wu21]: Wu, X., Zheng, W., Xia, X., & Lo, D. (2021). Data quality
matters: A case study on data label correctness for security bug
report prediction. IEEE Transactions on Software Engineering, 48(7),
2541-2556.

[^kang22]: Kang, H. J., Aw, K. L., & Lo, D. (2022, May). Detecting
false alarms from automatic static analysis tools: How far are we?.
In Proceedings of the 44th International Conference on Software
Engineering (pp. 698-709).

[^shepperd13]: Shepperd, M., Song, Q., Sun, Z., & Mair, C. (2013).
Data quality: Some comments on the nasa software defect datasets.
IEEE Transactions on software engineering, 39(9), 1208-1215.

f we sort rows in a MOOT data set (on their y-values), then we can find the rows
with the mean $y_\mu$ and most desirable  $y_0$ values. For that data set,
the output of EZR can then be scored
by how far it falls between the mean and most desirable values:

$$ win = 100*\left(1- \frac{y-y_0}{y_\mu - y_0}\right)$$

EZR is _minimal_: a few hundred lines with no pandas or scikit-learn.
It performs incremental multi-objective optimization via a greedy elite sampler

## Inser EZR ext

Whenever an unlabeled example seems promising, EZR grabs and labels it.

```python
def guess(best, rest, todo):
  for i,eg in enumerate(todo):
    if likelihood(best,eg) > likelihood(rest,eg): return i
  return 0 # default
```
The key point here, is that `likelihood` reflects only on the $x$ choices;
i.e. it does not need $y$ labels to guess if a row looks promising. EZR currently
implements six different `likelihood` functions such as the distance of a example's
$x$ variables
to the geometric center of a set of rows.


EZR maintains three lists:
- _todo_: unlabeled examples
- $N$ labeled examples divide into:
  - _best_: $\sqrt{N}$ promising labeled examples
  - _rest_: the $N - \sqrt{N}$ labeled examples that are not _best_

At initialization. EZR labels and sorts  a tiny sample
of rows,  picked at random. 
```python
#--- Control

ANY    = 4   # how many initial guesses
BUDGET = 24  # how many labels to collect
CHECK  = 5   # how often to apply model
```
Create _train,test_ data:

```python
#--- Create train,test data.

shuffle(rows)
n = len(rows)
train, test = rows[:n], rows[n:] # for validation
```

```Python
#--- Initialize a small best,rest set.

labeled        = []
unlabeled      = shuffle(train)
init,unlabeled = unlabeled[:ANY], unlabeled[ANY:]
init           = sort(init, key=y))
cut            = int(sqrt(ANY))
best, rest     = init[:cut], init[cut:]
```



```python
#--- Ensure we can evaluate labeled items.

Y(row) -> 
  ensureLabeled(row)
  dist2most(row)
```



```python
#--- If we find anything _good_, then refine our _best_ knowledge.

while len(labeled) <= BUDGET and unlabeled:
  if len(labeled) > ANY:
    best.add(
      todo.pop(
        guess(best,rest,unlabeled))) 
    if len(best) > sqrt(len(best) + len(rest)):
      add(all,
        add(best, row))
      if len(best) > sqrt(len(labeled)):
        add(rest,
          sub(best,
            best.sort(y).pop(-1)))
```

Test the generated knowledge.

```python
#--- Test the generated knowledge.

tree = Tree(labeled)
maybe = test.sort( row -> predict(tree,row))[:CHECK]
return maybe.sort(Y)[0]
```
      
```
Note that
EZR steadily grows _best_ by guessin likely  improvements, adding them to _best_,
then demoting its worst elites to _rest_.


END2


BEGIN2

END2

[^moot]: http://github.com/timm/moot

[^hou24]: Hou, X., Zhao, Y., Liu, Y., Yang, Z., Wang, K., Li, L., ... & Wang, H. (2024). Large language models for software engineering: A systematic literature review. ACM Transactions on Software Engineering and Methodology, 33(8), 1-79.

[^john84]: Johnson, B., & Menzies, T. (2024). Ai over-hype: A dangerous threat (and how to fix it). IEEE Software, 41(6), 131-138.

[^ling24]: Ling, X., Menzies, T., Hazard, C., Shu, J., & Beel, J. (2024). Trading off scalability, privacy, and performance in data synthesis. IEEE Access, 12, 26642-26654.

[^grin22]: Grinsztajn, Léo, Edouard Oyallon, and Gaël Varoquaux. "Why do tree-based models still outperform deep learning on typical tabular data?." Advances in neural information processing systems 35 (2022): 507-520

[^somv24]: Somvanshi, S., Das, S., Javed, S. A., Antariksa, G., & Hossain, A. (2024). A survey on deep tabular learning. arXiv preprint arXiv:2410.12034.

[^maju18]: Majumder, S., Balaji, N., Brey, K., Fu, W., & Menzies, T. (2018, May). 500+ times faster than deep learning: A case study exploring faster methods for text mining stackoverflow. In Proceedings of the 15th International Conference on Mining Software Repositories (pp. 554-563).

[^taw23]: V. Tawosi,l R. Moussa, and F. Sarro, “Agile effort
estimation: Have we solved the problem yet? insights from a replication
study,” IEEE Transactions on Software Engineering, vol. 49, no. 4,
pp. 2677– 2697, 2023.

[^shi22]: Jieke Shi, Zhou Yang, Bowen Xu, Hong Jin Kang, and David Lo. 2023. Compressing Pre-trained Models of Code into 3 MB. In Proceedings of the 37th IEEE/ACM International Conference on Automated Software Engineering (ASE '22). Association for Computing Machinery, New York, NY, USA, Article 24, 1–12. https://doi.org/10.1145/3551349.3556964


### Threats to Validity

Explore some, not all. Chen vs Golding mutation.

Why so few labels: human labelling.

pareto reasoning (evlutionary programming). too many labels. also, a strange effect super sampling gen1 does as well as reasonign owards.

aside chen evaluation

Active elarning xplore, explort, adaptive


Distance cacls: cheyshev vs distance to heaven.

Comapring emans not central entancies and their variabilist

results many aths not explored. eg. we apply model  dist, nayes etc. tree is better.


### Aside 1: What to Change?

In our experience, if you ever show a result like this to a subject
matter expert, they will  push back. For example, they might demand
to know what happens when `crypt_blowfish` is enabled.

(Just to explain: Blowfish is a
password hashing scheme.  It makes password protection slower but
it also  increases the computational effort required for attackers
to  brute-force attack the database's security.)

The full tree
generated by EZR shows what happens this feature is enabled.
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

### Aside 2: Run, re-run

In our experience, when subject matter experts discuss
these trees, it tends to surface other requirements. 
For example, a discussion about "should we use Blowfish?" rapidly
becomes "just how much do we value security in this application?".

For such interactive discussions, one advantage of EZR is its
runtime speed. 
Suppose, during a requirements discussion,
an new ``security+'' column was added into EZR's input data 
that (say) counted the number of enabled
controls settings with security implications. 
Results from a  new
"security-aware" run of 
EZR could then be ready for discussion in a few seconds.

## Background

This paper is mostly about the EZR code base.
But before looking at the code, it is be insightful to understand its
 empirical and theoretical background.

EZR arose from concerns about label quality in software engineering (SE) data.
We can easily collect many independent variables (\$x\$) like age, size, or color.
On the other hand, it is harder to
collect
dependent variables information (\$y\$)
about (say) is something broken, is it safe, or is it profitable.

> Table 3: On the value of less modeling.

| Year     | What                     | Who / System         | Notes                                                                                   |
|----------|--------------------------|-----------------------|-----------------------------------------------------------------------------------------|
| 130  |                         | Ptolemy (100-170)  | "We consider it a good principle to explain the phenomena by the simplest hypothesis possible."|
| 1300 | Occam's Razor            | William of Occam (1287-1347) | "Entities must not be multiplied beyond necessity." |
| 1902     | PCA                      | Pearson  [^pca]             | Larger matrices can be projected down to a few components.                                           |
| 1960s    | Narrows         | Amarel [^amarel]      | Search can be guided by tiny sets of key variable settings.                              |
| 1974     | Prototypes| Chang [^chang74] | Nearest neighbor reasoning is quicker after discarding 90% of the data and keeping  only the best exemplars.  |
| 1980s    | ATMS       | de Kleer [^atms]             | Diagnoses is quicker when it focus only on the core assumptions that do not depend on other assumptions. |
| 1984     | Distance-Preservation | Johnson and Lindenstrauss [^john84] | High-dimensional data can be embedded in low dimensions while preserving pairwise distances. |
| 1994     | ISAMP                    | Crawford & Baker [^craw94] | Best solutions lie is small parts of search space. Fast random tries and frequent retries is fast way to explore that space. |
| 1997     | Feature Subset Selection | John & Kohavi [^kohavi97] | Up to 80% of features can be ignored without hurting accuracy.                          |
| 2002     | Backdoors                | Williams et al. [^backdoor] | Setting a few variables beforehand reduces exponential runtimes to polynomial.                     |
| 2005     | Semi-Supervised Learning | Zhou et al. [^zhu05]   | Data often lies on low-dimensional manifolds inside high-dimensional spaces.            |
| 2008     | Exemplars                | Menzies [^me08a]      | Small samples can summarize and model large datasets.                                   |
| 2009     | Active Learning          | Settles [^settles09]  | Best results come from learners reflecting on their own models to select their own training examples. |
| 2005–20  | Key Vars in SE           | Menzies et al. [^me03a] [^me07a]  [^me21a]     | Dozens of SE models are controlled by just a few parameters.                                |
| 2010+    | Surrogate Models         | Various [^zul13] [^guo13]              | Optimizers can be approximated from small training sets.                                |
| 2020s    | Model Distillation       | Various    [^shi22] [^yang24]          | Large AI models can be reduced in size by orders of magnitude, with little performance loss.    |

[^settles09]: Settles, Burr. "Active learning literature survey." (2009).

[^me08a]: Menzies, T., Turhan, B., Bener, A., Gay, G., Cukic, B., & Jiang, Y. (2008, May). Implications of ceiling effects in defect predictors. In Proceedings of the 4th international workshop on Predictor models in software engineering (pp. 47-54).

[^zhu05]: Zhu, Xiaojin. "Semi-supervised learning literature survey." (2005), Dept. Computer Science, Wisconson, Technical Report 1530.

[^kohavi97]: Kohavi, R., & John, G. H. (1997). Wrappers for feature subset selection. Artificial intelligence, 97(1-2), 273-324.

[^kohavi97]: Kohavi, R., & John, G. H. (1997). Wrappers for feature subset selection. Artificial intelligence, 97(1-2), 273-324.

[^craw94]: Crawford, J. M., & Baker, A. B. (1994, July). Experimental results on the application of satisfiability algorithms to scheduling problems. In AAAI (Vol. 2, pp. 1092-1097).

[^atms]: De Kleer, J. (1986). An assumption-based TMS. Artificial intelligence, 28(2), 127-162.

[^pca]:  Pearson, K. (1901). "On Lines and Planes of Closest Fit
to Systems of Points in Space". Philosophical Magazine. 2 (11):
559–572. 10.1080/14786440109462720.

[^amarel]: S. Amarel, “Program synthesis as a theory formation task:
problem representations and solution methods,” in Machine Learning:
An Artificial Intelligence Approach. Morgan Kaufmann, 1986.

[^backdoor]: R. Williams, C. P. Gomes, and B. Selman, “Backdoors
to typical case complexity,” in Proceedings of the International
Joint Conference on Artificial Intelligence, 2003.

[^chang74]: Chang, C. L. (1974). Finding Prototypes for Nearest Neighbor Classifiers. IEEE Transactions on Computers, C-23(11), 1179–1184.--




[^zul13]: Zuluaga, M., Sergent, G., Krause, A., & Püschel, M. (2013, February). Active learning for multi-objective optimization. In International conference on machine learning (pp. 462-470). PMLR.

[^guo13]: Guo, J., Czarnecki, K., Apel, S., Siegmund, N., & Wąsowski, A. (2013, November). Variability-aware performance prediction: A statistical learning approach. In 2013 28th IEEE/ACM International Conference on Automated Software Engineering (ASE) (pp. 301-311). IEEE.

[^yang24]: Yang, Chuanpeng, Yao Zhu, Wang Lu, Yidong Wang, Qian Chen, Chenlong Gao, Bingjie Yan, and Yiqiang Chen. "Survey on knowledge distillation for large language models: methods, evaluation, and application." ACM Transactions on Intelligent Systems and Technology (2024).

[^sh21]: Shi, J., Yang, Z., Xu, B., Kang, H. J., & Lo, D. (2022, October). Compressing pre-trained models of code into 3 mb. In Proceedings of the 37th IEEE/ACM International Conference on Automated Software Engineering (pp. 1-12).

[^me03a]: Menzies, T., & Hu, Y. (2003). Data mining for very busy people. Computer, 36(11), 22-29.

[^me07a]: Menzies, T., Owen, D., & Richardson, J. (2007). The strangest thing about software. Computer, 40(1), 54-60.

[^me21a]: Menzies, T. (2021). Shockingly Simple:" Keys" for Better AI for SE. IEEE Software, 38(2), 114-118.

One way to mitgate the problem of labeling is to use less labels. Standard machine learning builtds models using
100s to 1000s to millions of examples,
and sometimes much more. But does learning need so much data? As shown in Table3, for centuries,
researchers have argued that
seeminlgy complex spaces can be compressed, without loss of signal, into a smaller represetation. 
If so, then we only need enough examples to cover the compressed space and not the whole space.

EZR employs several compression operators. For instance selection,  EZR avoids data that is noisy (i.e.
is clearly not "best" or "rest") and  superfluous  (i.e. that is not
relevant for "better" behavior). In this way EZR ignores most of the
data and builds its models using just a few dozens samples. 
For feature selection, EZR's decision trees are built only from a few dozen samples that distinguish
best from rest. In this way, that tree only contains features that make a big difference to the outcomes. THe effects of this
were seen in Table 2. After labeling just 24 rows, EZR's trees cotnained only a small percentage of the $x$ variables.

TO place that in context, 
sequential model-based optimzation algorithms
iteratively label some candidates, building a surrogate model that predicts “good” vs. “not good”. This model
is then use to prioritize what to explore next. Standard SMBO algorithms use elabroate sampling
and proiroization schemes via a range of estimated generated via   multiple. New data is explored in ther egion where (e.g.)
the estiamtes are best, yet have highest variance.

This has lead to some surprising results:

- For data mining, we kept find that models learned from $n \ll N$
carefully selected examples perform just as well as learning from
$N$ examples.
- For evolutionary algorithms, we previously reputed that if we
over-generated generation zero, then only search in that space,
then that works as well or better than multiple generations of
mutation, selection and cross-over.
- For reinforcement learning, balancing exploration (of  zones of
uncertainty) versus exploration (or zones of certainty) does no better than a
  greedy search.
- For active learners, intricate (and slow) uncertainty measurement
algorithms (like Gaussian Process Models)
  do not better than simple elite sampling.
- For many applications, simple elite-guided stochastic sampling
does as well as state-of-the-art
  complex software optimization packages such as NSGA-II, Hyperopt,
  or (most recently) DEHB.



## Algorithm

The core of EZE is a five step process

       seed → split → start -> explore → refine → repeat

That is, we guess some initial model and use that to split a sample of the data into 
"best" and rest". This is used to decide where to explore next. If any new data is discovered, 
then that refines our definitions of best and rest. Thie process then repeats.

We can summarize the code as follows:

```python
def y(row):
  ensure y has a  label
  return d2h(row)

def likely(data,  any=4, build=24):
  start = rows[:any].sort(y)                # initial seed, sorted by y values
  rows  = rows[any:]
  best, rest = start[:sqrt(any)], start[sqrt(any):]
  while rows:
    maybe, *rows = rows.sort(guess)
    best += [maybe]
    if |best| > sqrt(|best| + |rest|):
      best.sort(y)
      rest += [ best.pop(-1) ]
    if |best| + |rest| >= build: break
  return best.sort(y)
```

- gotta shffle
Sequential Model-Based Optimization (SMBO) / Bayesian Optimization (simplified form)


: It’s a one-shot, greedy SMBO / active classifier—almost Thompson sampling without probabilities, or greedy version of FOCUS/LIKE.


Explore the space adaptively, often prioritizing regions likely to improve the “best” set.

## Algorithms,

```python
% likes is all wrong
import math,random

def disty(row): return sum(row)                   # stub
def likes(group,row): return sum(sum(abs(x-y) for x,y in zip(g,row))
                                 for g in group)/(len(group) or 1)

def rebalance(best,rest):
    best.sort(key=disty)
    while len(best) > math.sqrt(len(best)+len(rest)):
        rest.append(best.pop(-1))

def bayes_score(best,rest,row,acq="xplor",build=1000,eps=1e-9):
    b,r=math.exp(likes(best,row)),math.exp(likes(rest,row))
    if acq=="bore": return (b*b)/(r+eps)
    q={"xploit":0,"xplor":1}.get(acq,1-build**-1)
    return (b+r*q)/abs(b*q-r+eps)

def likely1(best,rest,rows,few):
    for row in random.sample(rows,min(few*2,len(rows))):
        if likes(best,row)>likes(rest,row):
            rows.remove(row); return row

def likelier(best,rest,rows,few,acq="xplor",build=1000):
    cands=random.sample(rows,min(few*2,len(rows)))
    row=max(cands,key=lambda r:bayes_score(best,rest,r,acq,build))
    rows.remove(row); return row

def likely(data,acq_fn,build=1000,few=10,any=32):
    rows=random.sample(data.rows,len(data.rows))
    xy=sorted(rows[:any],key=disty)
    k=int(math.sqrt(any)); best,rest=xy[:k],xy[k:]
    while len(xy)<build and rows[any:]:
        row=acq_fn(best,rest,rows[any:],few)
        xy.append(row); best.append(row)
        rebalance(best,rest)
    return sorted(xy,key=disty)
```

## Simp
is only true for generative AI. For predictive AI, as shown here,

This code implements an AI agent explaining what they found as they
incrementally explore the world, updating their 
knowledge of what is best or rest.
As it walks the world, our agent finds rows of data
which have  one or more `x` independent  values
and one or more `y` goals (which must be mininized or maximized).

Our agent knows that 
getting `x` values is usually much faster and cheaper than getting `y` values.
For example,
in a  single glance, we can find all the colors of all the cars in  a used car lot.
But it takes hours of driving per car to determine their mileage.




This code is reversed engineers from decades of experiments by dozens
of graduate students exploring data science. 

To say that another way, this is an explanation algorithm
for active learning for
for multi-objective optimization.

Here's the core idea: our agent randmoly
walks around the world keeping a list
of best and rest things seen so far. If they find a new best thing,
then they revise  what it means to be "best":

```
best, rest = [], all
shuffle(rest)
 while rest not empty:
   if model(new_item := pop(rest)) says "best":
     push(best, new_item)
     rebuild_model(best, rest)  
```

This short description misses many improtant details. 

Firstly, what are we exploring? This code processes rows of data each of Firstly, what do we mean by "best"? We say the better examples
are those that are "closer to heaven"; i.e.
if each example achieves goals $g1,g2,...$; and 
the best valuse ever seen for  each goal is $n1,n2,..$; then

$$y= \sum_i(N(abs(g_i-n_i))^2) / len(goals)$$

where `N` normalizes our goals values 0..1.
The columns of these rows have names:
upper case names are for numerics; and anything marked with `+` or `-` is a goal to be maximzed
or minimized. 


to get started, we need to build an initial model.

```
Any=4    # inota;;y. ;abel Any items
Build=24 # labelling budget used when building models
Check= 5 # 

shuffle(all)
n= len(all)//2
train,test = all[:n],all[n:]

dark = train[Any:] 
lite = [label(x) for x in train[:Any]
lite.sort(y)
best, rest = lite[:Any/2], lite[Any//2:]

tooBig(best) -> len(best) > sqrt(len(best) + len(rest))
label(row)   -> add_Y_labels(row); return row
error(model,row) -> float  

while (Build--) > 0:
  model = train(best,rest)
  push(best, (new := label(pop(dark))))
  if tooBig(best):
    best.sort(row -> error(model, row))
    while tooBig(best):
      # move the worst best into rest
      push(rest, best.pop(-1)) 
best.sort(row -> error(model,row)) # ensure best is sorted
model = train(best,rest) 
# sort test on model, check the best guesses
return test.sort(row -> error(model,row))[:Check]
```

