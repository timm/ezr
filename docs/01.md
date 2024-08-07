% How Much Data Needed for Learning?
% Tim Menzies
% August 22, 2024

## How Much data Do we need for Learning?

- “The Unreasonable Effectiveness of Data,” by Google’s then Chief Scientist
  Peter Norvig 
  - “Billions of trivial data points can
    lead to understanding” [^nor11] (a claim he supports with numerous
    examples from vision research).
- In software analytics,  data-hungry researchers assume that if
  data is useful, then even more data is much more useful. For
  example:
  - “..as long as it is large; the resulting prediction performance is likely to be boosted more by the size of the
    sample than it is hindered by any bias polarity that may
    exist” [^rahman13].
  - “It is natural to think that a closer previous release
    has more similar characteristics and thus can help to
    train a more accurate defect prediction model. It is also
    natural to think that accumulating multiple releases can
    be beneficial because it represents the variability of a
    project” [^amasaki20].
  - “Long-term JIT models should be trained using a cache
    of plenty of changes” [^mcintosh17].

[^rahman13]: F. Rahman, D. Posnett, I. Herraiz, and P. Devanbu,
“Sample size vs.  bias in defect prediction,” in Proceedings of the
2013 9th joint meeting on foundations of software engineering. ACM,
2013, pp. 147–157.

[^amasaki20]: S. Amasaki, “Cross-version defect prediction: use
historical data, crossproject data, or both?” Empirical Software
Engineering, pp. 1–23, 2020.

[^mcintosh17]: S. McIntosh and Y. Kamei, “Are fix-inducing changes
a moving target?  a longitudinal case study of just-in-time defect
prediction,” IEEE Transactions on Software Engineering, vol. 44,
no. 5, pp. 412–428, 2017.

[^nor11]: P. Norvig. (2011) The Unreasonable Effectiveness of
Data. Youtube.  https://www.youtube.com/watch?v=yvDCzhbjYWs


## A more informed position: The question is wrong

- It depends on the nature of the data
  - e.g. if i show you, one at a time, 100 "1"s then we are pretty sure the 101-th thing will be "1".
  - So if data clusters to regions with not much variance
    - then once we find those regions, we can stop
- And sometimes its not what the data is...
  - .. but when we collect it
  - Shrikanth and Menzies: the early bird hypothesis
    - data learned from the first 150 commits builds a 
      model as good as anything else [^majumder21];
    - data from the early in the lifecycle is richer in examples of things going wrong

<img width="898" alt="image" src="https://github.com/txt/aa24/assets/29195/51809d84-6c32-4d86-849d-0af40273c83f">


[^majumder21]: S. N.C., S. Majumder and T. Menzies, 
"Early Life Cycle Software Defect Prediction. Why? How?," 2021 IEEE/ACM 43rd International Conference on Software Engineering (ICSE), Madrid, ES, 2021, pp. 448-459, doi: 10.1109/ICSE43902.2021.00050.

## Another question: How much data can you handle?

For very fast decision making, there is a cognitive science  case that we work
from less than a dozen examples:

- Larkin et al. [^larkin80] characterize human expertise in terms of very
small short term memory, or STM (used as a temporary scratch
pad for current observation) and a very large long term memory,
or LTM. 
- The LTM holds separate tiny rule fragments that explore
the contents of STM to say “when you see THIS, do THAT”. 
- When
an LTM rule triggers, its consequence can rewrite STM contents
which, in turn, can trigger other rules
- Short term memory is very small, perhaps even as small as four
to seven items [^cowan01] [^miller56].
- Experts are experts, says Larkin et al. [^larkin80]
because the patterns in their LTM patterns dictate what to do,
without needing to pause for reflection. 
- Novices perform worse
than experts, says Larkin et al., when they fill up their STM with
too many to-do’s where they plan to pause and reflect on what to
do next. 
- Since, experts post far fewer to-do’s in their STMs, they
complete their tasks faster because (a) they are less encumbered
by excessive reflection and (b) there is more space in their STM
to reason about new information. 

While first proposed in 1981,
this STM/LTM theory still remains relevant [^mri]. This theory can
be used to explain both expert competency and incompetency in
software engineering tasks such as understanding code [^wiedenbeck93].

[^mri]: Recently, Ma et al. [^wei14] used evidence from neuroscience and functional MRIs to
argue that STM capacity might be better measured using other factors than “number of
items”. But even they conceded that “the concept of a limited (STM) has considerable
explanatory power for behavioral data”.

[^wei14]: Wei Ji Ma, Masud Husain, and Paul M Bays. 2014. Changing concepts of working
memory. Nature neuroscience 17, 3 (2014), 347–356.

[^wiedenbeck93]: Susan Wiedenbeck, Vikki Fix, and Jean Scholtz. 1993. Characteristics of the
mental representations of novice and expert programmers: an empirical study.
International Journal of Man-Machine Studies 39, 5 (1993), 793–812.


[^miller56]: George A Miller. 1956. The magical number seven, plus or minus two: some
limits on our capacity for processing information. Psychological review 63, 2
(1956), 81.

[^cowan01]: N. Cowan. 2001. The magical number 4 in short-term memory: a reconsideration
of mental storage capacity. Behav Brain Sci 24, 1 (Feb 2001), 87–114.

[^larkin80]: Jill Larkin, John McDermott, Dorothea P. Simon, and Herbert A. Simon. 1980.
Expert and Novice Performance in Solving Physics Problems. Science 208,
4450 (1980), 1335–1342. DOI:http://dx.doi.org/10.1126/science.208.4450.1335
arXiv:http://science.sciencemag.org/content/208/4450/1335.full.pdf


## Another question: How much data can you get?

How fast can we gather expert opinion?

- Some can monitor products on an assembly line, 1000s of items per day
  - And there will be some error rate
- But suppose we have a panel of experts?
  - And suppose they have to check with everyone else before making a decision?
  - Then everything they conclude has to be analysed, certified

Evidence from "cost estimation"

- Valerdi [^valerdi10] reports that panels of human experts required 
  three meetings (three hours each) to reach convergence on the influence of 
  10 variables on 10 examples (in the domain of cost estimation). 

[^valerdi10]: Valerdi, Ricardo. "Heuristics for systems engineering cost estimation." IEEE Systems Journal 5.1 (2010): 91-98.

Evidence from "Repertory Grids"

- A structure interview technique, learn the dimensions incrementally as we go:
  1. Take three examples $E_1,E_2,E_3$: 
    - Which one is most distant?
    - Along what dimension $D_i$ is it distant?
    - Score those examples on this dimensions. 
  2. Goto to step 1.

<img align=600 
     src="https://csdl-images.ieeecomputer.org/mags/so/2007/02/figures/s20534.gif">

Advice on how long to fill in a rep grid?

- Kington [^king90]:
  - One hour to walk thorugh $E=16$ examples with $D=16$ dimensions.
- Easterby-Smith [^easter80]:
  - Keep the grid small. 
  - A grid containing ten elements and ten constructs may take two hours to complete. 
  - Larger grids may take substantially more time
- Edwards's [^edwards09] rep grid interview sessions lasted, on average, for one hour 
  (although the shortest was 30 min) and these were recorded for later analysis.

[^edwards09]:  Helen M. Edwards, Sharon McDonald, S. Michelle Young,
The repertory grid technique: Its place in empirical software engineering research,
Information and Software Technology, Volume 51, Issue 4, 2009, Pages 785-798, ISSN 0950-5849,

[^king90]: Kington, Alison. "Defining Teachers' Classroom Relationships." (2009).  https://eprints.worc.ac.uk/1885/1/Kington%202009.pdf

[^easter80]: Easterby-Smith, Mark. “The Design, Analysis and Interpretation of 
Repertory Grids.” Int. J. Man Mach. Stud. 13 (1980): 3-24.

Overall, we get, for reflective labels on data:

- 10 to 20 examples per 1-4 hours

## Advice from Mathematics

One commonly cited rule of thumb [^call] is to have at least 10 times the number of training data 
instances attributes [^austin17] [^peduzzi96].

- by this rule, 20 attributes needs 200 rows

[^austin17]: Austin PC, Steyerberg EW. Events per variable (EPV) and the relative performance of different strategies for estimating the out-of-sample validity of logistic regression models. Stat Methods Med Res. 2017 Apr;26(2):796-808. doi: 10.1177/0962280214558972. Epub 2014 Nov 19. PMID: 25411322; PMCID: PMC5394463.

[^peduzzi96]: Peduzzi P, Concato J, Kemper E, Holford TR, Feinstein AR. A simulation study of the number of events per variable in logistic regression analysis. J Clin Epidemiol. 1996 Dec;49(12):1373-9. doi: 10.1016/s0895-4356(96)00236-3. PMID: 8970487.

## Historically, how much data was enough?

- Semi-supervised learning: $\sqrt{N}$ is enough
  - Alvarez [^alvarez23] recursively bi-cluster down to $\sqrt{N}$ then collect one
    data point per leaf cluster.

[^alvarez23]: Alvarez, L., & Menzies, T. (2023). Don’t Lie to Me: Avoiding Malicious Explanations With STEALTH. IEEE Software, 40(3), 43-53.

- Zhu et al. [^zhu16]
  - Numerous examples from facial recognition where face accuracy plateaus at $M> 100$ examples

- Incremental learning in SE: [^Me08]
  - Sort data on historical order;
  - Train up to time $t$, test of data after $t$.
  - Even with 1000s of examples
    - Learning on 25 defective examples + 25 non-defective
    - Did as good as anything else.

[^Me08]: Menzies, T., Turhan, B., Bener, A., Gay, G., Cukic, B., &
predictors. In Proceedings of the 4th international workshop on
Predictor models in software engineering (pp. 47-54).

[^zhu16]: Zhu, X., Vondrick, C., Fowlkes, C.C. et al. Do We Need More Training Data?. 
Int J Comput Vis 119, 76–92 (2016). https://doi-org.prox.lib.ncsu.edu/10.1007/s11263-015-0812-2

## Maths

### Chess board model

Data is spread out across a d-dimensional chessboard where each dimension
is divided into $b$ bins [^nam18].

- Data is skewed by some factor $k$ such that not all cells have data.
- a standard chess board is $d,b=2,8$

The target is some subset of the data that falls into some of the chessboard
cells:

- $c=b^{-d}$  is the probability of picking a particular cell; 
- $C=1-(1-p)^n$ is the certainties  that once we arrive at a cells, 
  that we can find the signal after $n$ attempts
  (which occurs at probability $p$ in that cell)
- So lets do some simulations. 1,000 times pick at random from the following:  
  - $k \in \{ 1, 2, 3, 4, 5\}$
  - $d \in \{ 3, 4, 5, 6, 7\}$  dimensions;
  - $b \in \{ 2 , 3, 4, 5, 6, 7\}$ bins;
  - $p \in \{0.1, 0.2, 0,3, 0.4\}$
  - We gave the whole thing to a decision tree learner, asking what factors
    predicts for more than 67% chance of finding the target.
    - and the learnt tree told us:
      - We need up to 200 examples when the defect signal is rare ($p\le 10$ 
        percent)
      - But far fewer when the signal occurs at $p > 10$ percent.

### Probable Correctness Theory

Richard Hamlet, Probable correctness theory, 1980 [^hamlet80].

[^hamlet80]: Hamlet, Richard G. "Probable correctness theory." Information processing letters 25.1 (1987): 17-25.

- Confidence $C$ that we will see an event at probability $p$ after $n$ random trials:
  - $C(p,n) =1-(1-p)^n$
- Which re-arranges to:
  - $n(C,p) = \frac{\log(1-C)}{\log(1-p)}$
- And if we have a sorting trick to divide examples into _best_ and _rest_
  - then the number of evals is $\log_2(n(C,p))$

Some what ifs:
- If we apply Cohen's rule (things are indistinguishable if less than $d{\times}\sigma$ apart,
  - And if variables are Gaussian ranging $-3 \le x \le 3$.
  - Then that space divides into regions of size $p=\frac{d}{6}$  

scenario |d  | p | C |  n(c,p) | $\log_2(n(c,p))$
:---------|:---|:---|:---|:---------|:-----------------
medium effect, non-safety critical|0.35|0.06|0.95|50|6
small effect, safety criticali     |0.2   |0.03            |0.9999|272|8
tiny effects, ultra-safety critical | n/a | one in a million|six sigma<br> (0.999999)|13,815,504| 24

Note the above table makes some very optimistic assumptions about the problem:

- It is single variable Gaussian
- Solutions are spaced equally across the x-axis

But it also tells us that the only way we can reason about safety critical systems
is via some sorting heuristic (so we can get the log2 effect)
[^call]:  Application of machine learning techniques in small sample clinical studies, 
from StackExchange.com
https://stats.stackexchange.com/questions/1856/application-of-machine-learning-techniques-in-small-sample-clinical-studies

[^nam18]: J. Nam, W. Fu, S. Kim, T. Menzies and L. Tan, "Heterogeneous Defect Prediction," in 
IEEE Transactions on Software Engineering, vol. 44, no. 9, pp. 874-896, 1 Sept. 2018, doi: 10.1109/TSE.2017.2720603.

# # Few shot Learning 

In the following, the author says **LLMs** not **learners** but given the results of this subject, I think an edit is in order:

- A particularly exciting aspect of **learners** is their knack for few-shot and zero-shot learning: they can learn to perform a task with very few examples. Few- shotting has particular synergies in software engineering, where there are a lot of phenomena (identifier names, APIs, terminology, coding patterns) that are known to be highly project-specific. However, project-specific data can be quite limited, especially early in the history of a project; thus the few-shot learning capacity of **learners** might be very relevant. 
- In the extreme case, training data consists of only one instance for each target class, which is known as one-shot learning

Need another name

- Few-shot learning is usually a neural model concept
  - Uses a large language models trained on massive code corpora
  - Generalize to new tasks via a sequence of prompts, starting  composed of natural language instructions, then  few instances of task demonstration, and a query 
- Few-shot learning (version 2.0)
  - takes no model as an input (but it could be initialized from a model learned at a prior session) 
  - Generalize to new tasks via a sequence of queries to the data, selected by the model built so far.  
- Perhaps it might be useful to combine SMO and few-shot into another term

Generalize to new tasks via a sequence of prompts, starting  composed of natural language instructions,

- Data-Efficient Sequential Learning (DESL)
  - Sequential Decision-Making  : how to making decisions one after another, where each decision is based on prior outcomes. 
  - Data Selection Strategy : how to selecting which data points to label or otherwise interact with next. In SMO, this is the acquire function. 
  - Model Adaptivity : how to update your models for SDM and/or DSS as a result of the interaction seen in DSS
  - Label Efficiency : concerns the cost of labelling. DESL is least useful when the label effeciency is high.
- Other analogous terms include active learning which  in statistics literature also called optimal experimental design or query learning,
    is a class of strategies to choose the data from which to learn.

Few-shot learning is a subfield of machine learning and deep learning that aims to teach AI models how to learn from only a small number of labeled training data.

More generally  "n-shot learning" a category of artificial intelligence that also includes:

- one-shot learning (in which there is only one labeled example of each class to be learned)
- and zero-shot learning (in which there are no labeled examples at all

Applications:

- Healthcare: rarity of certain conditions or the expertise required to accurately annotate medical data (like MRIs or echocardiography) 
  can make the acquisition of a large number of labeled samples prohibitively difficult
- Robotics:  enable robots to quickly adapt to new environments
- SE: Any learning task when labels are short: e.g. what tests to run next, etc etc


Methods:

- Transfer learning (use knowledge from elsewhere)
  - adapt a pre-trained model
  - e.g. for us in SMO, initialize our best,rest models from prior applications
    - this can be very useful since, rarely, do we ever do things once
    - if it is important, we will do it again and again and again...
- Data-level approach
  -  automatically generate additional training samples
  - Data generation
    - GANs (generative adaptive networks)
      - Two models discriminator  and adversary
      - Model1 produces
      - Model2 classifies as right,wrong
      - Model1 stops when model2 can  no long distinguish good from bad
      - Feedback from one model can be used to guide the other
      - And if you thought one deep learner was slow, try running two
  - Data augmentation
    - Find ways to add in the missing bits
    - Semi-supervised learning e.g. RRP, label once per leaf, share the label across entire leaf
    - Active learning; e.g. SMO, only ask for labels on most informative examples. 


### Few Shot Learning in SE

March 2024: Google query: "few-shot learning and 'software engineering'"

In the first 100 returns, after paper70, no more published few shot learning papers in SE.

In the remaining 70 papers:

|year|citations|venue|j=journal; <br>c=conf;<nr> w=workshop|title|pdf|data|
|--|--|--|--|--|--|--| 
|2023|1|Icse_NLBSE|w|Few-Shot Learning for Issue Report Classification|[pdf](Few-Shot_Learning_for_Issue_Report_Classification.pdf)|200 + 200|
|2023|2|SSBSE|c|. Search-based Optimisation of LLM Learning Shots for Story Point Estimation|[pdf](SB_LLM_Shot_optimisation.pdf)|6 to 10|
|2023|2|ICSE|c|Log Parsing with Prompt-based Few-shot Learning|[pdf](Log_Parsing_with_Prompt-based_Few-shot_Learning.pdf)|4 to 128. most improvement before 16|
|2023|3|AST|c|FlakyCat: Predicting Flaky Tests Categories using Few-Shot Learning|[pdf](FlakyCat_Predicting_Flaky_Tests_Categories_using_Few-Shot_Learning.pdf)|400+|
|2023|5|ICSE|c|Retrieval-Based Prompt Selection for Code-Related Few-Shot Learning|[pdf](Retrieval-Based_Prompt_Selection_for_Code-Related_Few-Shot_Learning.pdf)|6-7 (for code generation (40 to 50 (for code repair)|
|2022|7|Soft.Lang.Eng|c|Neural Language Models and Few Shot Learning for Systematic Requirements Processing in MDSE|[pdf](3567512.3567534.pdf)|8 to 11|
|2023|12|ICSE|c|Towards using Few-Shot Prompt Learning for Automating Model Completion|[pdf](Towards_using_Few-Shot_Prompt_Learning_for_Automating_Model_Completion.pdf)|212 classes|
|2020|15|IEEE ACCECSS|j|Few-Shot Learning Based Balanced Distribution Adaptation for Heterogeneous Defect Prediction|[pdf](Few-Shot_Learning_Based_Balanced_Distribution_Adaptation_for_Heterogeneous_Defect_Prediction.pdf)|100s - 1000s|
|2019|21| Big Data|j|. Exploring the applicability of low-shot learning in mining software repositories|[pdf](s40537-019-0198-z.pdf)|100 =>70% accuracy; 100s ==> 90% accuracy|
|2021|27|ESEM|c|An Empirical Examination of the Impact of Bias on Just-in-time Defect Prediction||10^3 samples of defects|
|2020|29|ICSE|c|Unsuccessful Story about Few Shot Malware Family Classification and Siamese Network to the Rescue|[pdf](3377811.3380354.pdf)|10,000s ?|
|2022|65|ASE|c|Few-shot training LLMs for project-specific code-summarization|[pdf](3551349.3559555.pdf)|10 samples|
|2022|101|FSE|c|Less Training_ More Repairing Please: Revisiting Automated Program Repair via Zero-Shot Learning|[pdf](3540250.3549101.pdf)|?|





