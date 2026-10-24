# Related work: why simple keeps winning

This repo keeps finding the same thing. A naive Bayes over binned
columns, or a tree grown on a few hundred labels, lands within a
point or two of LightGBM while running an order of magnitude
faster in a hundredth of the code. That is not a surprise. It is a
thirty-year-old result that gets rediscovered every time the
tooling changes.

What follows is the lineage, in three waves, then the part this
repo is actually adding.

## Wave 1: the simplicity results (1992-2001)

**One attribute is often enough.** Holte's 1R bins each column,
picks the single best one, and classifies by it
[@holte1993]. Across 16 UCI sets it came within a few points of
C4.5. Holte's own diagnosis is the one that matters: most
benchmark datasets have few real attribute interactions, so most
of what a complex learner models is not there. Iba and Langley had
the same finding for decision stumps [@iba1992].

**Naive Bayes is wrong about probability and right about the
answer.** Domingos and Pazzani separated the two
[@domingos1997]. NB's probability estimates are badly calibrated
whenever the independence assumption fails, which is always, but
the `argmax` survives a great deal of that error. Under 0/1 loss
you only need the right class to come first.

**And the reason is bias-variance.** Friedman showed that bias and
variance do not add under 0/1 loss the way they do under squared
error [@friedman1997]. A low-variance estimator can carry a large
bias and still win. This is the mechanism behind every other
result on this page.

**Binning beats fitting a Gaussian.** Dougherty, Kohavi and Sahami
found that a discretized NB beats a Gaussian NB [@dougherty1995];
Yang and Webb worked out how many bins, tying the count to
sqrt(n) [@yang2009]. A `BINS` sweep is their experiment, run
again. Webb's AODE and AnDE sit at the other end of the same
dial: relax independence a little, pay a little [@webb2005;
@webb2012].

**Said out loud, in statistics.** Hand and Yu, *Idiot's Bayes --
Not So Stupid After All?* [@hand2001]; and later Hand's
*Classifier Technology and the Illusion of Progress*
[@hand2006], which argues that most reported gains do not survive
contact with deployment.

## Wave 2: the "is anyone actually winning?" audits (2014-2020)

**179 classifiers, 121 datasets.** Fernandez-Delgado et al. ran
everything against everything [@delgado2014]. Random forests came
first, but the margins between the top dozen families are small
enough that dataset choice decides the ranking.

**Recommenders.** Dacrema, Cremonesi and Jannach could reproduce
only 7 of 18 recent neural recommenders, and simple baselines beat
6 of those 7 [@dacrema2019].

**Metric learning.** Musgrave, Belongie and Lim re-ran thirteen
years of claimed progress under one honest protocol and got a
flat line [@musgrave2020].

**Information retrieval.** Lin's *The Neural Hype and Comparisons
Against Weak Baselines*: a properly tuned BM25 is still a hard
target [@lin2019].

## Wave 3: tabular data specifically (2021-2024)

**Deep learning is not all you need** [@shwartz2022]: across 11
datasets, XGBoost beats the deep tabular architectures that
claimed to beat it, and an ensemble of both beats either.

**Why trees still win** [@grinsztajn2022]: three named causes --
targets that are irregular functions of the inputs, uninformative
features that trees can ignore and MLPs cannot, and the
rotation-invariance of a neural net being the wrong inductive bias
for data whose columns mean different things.

**When do neural nets win?** McElfresh et al., 19 algorithms over
176 datasets [@mcelfresh2023]: the gap is usually negligible, and
light tuning of a GBDT buys more than the choice of family. Also:
GBDTs tolerate skewed and heavy-tailed features; neural nets do
not.

**The honest counterweight** [@kadra2021]: a plain MLP with a
well-chosen regularization cocktail is competitive. The
architecture was never the point; the regularization was.

## The software engineering thread

This is the literature this repo is written out of, and it is the
one that got to pd/pf first.

**Defect prediction.** Menzies, Greenwald and Frank: a log-filtered
naive Bayes, scored on pd and pf rather than accuracy, beats the
complicated alternatives [@menzies2007]. The measure is what lets
the simple method show -- on skewed data, accuracy rewards
predicting the majority class and nothing else. Provost, Fawcett
and Kohavi had made the general case a decade earlier
[@provost1998]. Then the ceiling: Menzies et al. showed that
further gains in that setting were bounded by information in the
data, not by the learner [@menzies2008].

**Easy over hard.** Fu and Menzies: a tuned SVM beats deep
learning for linking Stack Overflow posts, in a fraction of the
runtime [@fu2017]. Same shape as Wave 2, three years earlier, in
SE.

**The option space is mostly redundant.** DODGE: if two
configurations score within epsilon of each other, do not explore
both [@agrawal2021dodge; @agrawal2021simpler]. The space of
hyperparameters collapses to a handful of distinct behaviours.
This is why a `BINS` sweep over 3, 7, 11, 14 and 17 comes back
flat -- not a null result, a predicted one.

**Baselines in effort estimation.** Whigham, Owen and MacDonell's
ATLM: an automatically transformed linear model, proposed
precisely because the field kept publishing gains over nothing
[@whigham2015].

**Few labels.** FRUGAL [@tu2021] and the early-bird results
[@majumder2022] both argue that a small, cheaply labelled sample
gets most of the available signal. That is the premise of ezr's
`grabs`/`acquire` budget.

## What this repo adds

Everything above argues *simple is about as accurate*. Almost none
of it treats **runtime and lines of code as first-class results**
measured against a modern gradient booster, on a modern suite,
under pd/pf.

Measured here, 60 `moot/classify` datasets, 20 seeds, 75:25:

| arm | d2h w/t/l vs LightGBM | median gap | suite seconds (1 seed) |
|---|---|---|---|
| nb, 7 bins, all training rows | 21/3/36 | +.02 | 3.3 |
| ezr tree, 256 random labels | 2/10/48 | +.07 | 1.5 |
| ezr tree, 50 random labels | 2/5/53 | +.16 | 0.3 |
| LightGBM | -- | -- | 69.2 |

So: 20x faster for a two-point d2h gap, in about 100 lines. And a
tree that never sees more than 256 labels still ties LightGBM on
10 datasets.

Two further things no one on this page reports:

1. **The loser log.** `etc/explore.md` records every variant that
   failed -- TAN, DFE, A2DE, four ensembles, two
   pick-by-holdout schemes -- with the numbers and the date. The
   publication record only holds the winners, which is exactly why
   Wave 2 had to happen.
2. **pf = 1 - pd, exactly, for k=2.** Under a macro (unweighted)
   mean over one-vs-rest classes, the two measures are
   algebraically the same measure on a two-class problem --
   verified to 1e-6 on all 27 binary datasets in the suite. So on
   nearly half this benchmark, pd, pf and d2h are one number wearing
   three hats.

## Bibliography

```bibtex
@article{holte1993,
  author  = {Holte, Robert C.},
  title   = {Very Simple Classification Rules Perform Well on Most
             Commonly Used Datasets},
  journal = {Machine Learning},
  volume  = {11}, number = {1}, pages = {63--91}, year = {1993},
  doi     = {10.1023/A:1022631118932}}

@inproceedings{iba1992,
  author    = {Iba, Wayne and Langley, Pat},
  title     = {Induction of One-Level Decision Trees},
  booktitle = {Machine Learning Proceedings 1992 (ML92)},
  pages     = {233--240}, year = {1992}}

@article{domingos1997,
  author  = {Domingos, Pedro and Pazzani, Michael},
  title   = {On the Optimality of the Simple Bayesian Classifier
             under Zero-One Loss},
  journal = {Machine Learning},
  volume  = {29}, number = {2--3}, pages = {103--130}, year = {1997},
  doi     = {10.1023/A:1007413511361}}

@article{friedman1997,
  author  = {Friedman, Jerome H.},
  title   = {On Bias, Variance, 0/1---Loss, and the
             Curse-of-Dimensionality},
  journal = {Data Mining and Knowledge Discovery},
  volume  = {1}, number = {1}, pages = {55--77}, year = {1997},
  doi     = {10.1023/A:1009778005914}}

@inproceedings{dougherty1995,
  author    = {Dougherty, James and Kohavi, Ron and Sahami, Mehran},
  title     = {Supervised and Unsupervised Discretization of
               Continuous Features},
  booktitle = {ICML},
  pages     = {194--202}, year = {1995}}

@article{yang2009,
  author  = {Yang, Ying and Webb, Geoffrey I.},
  title   = {Discretization for Naive-{B}ayes Learning: Managing
             Discretization Bias and Variance},
  journal = {Machine Learning},
  volume  = {74}, number = {1}, pages = {39--74}, year = {2009},
  doi     = {10.1007/s10994-008-5083-5}}

@article{webb2005,
  author  = {Webb, Geoffrey I. and Boughton, Janice R. and Wang, Zhihai},
  title   = {Not So Naive {B}ayes: Aggregating One-Dependence
             Estimators},
  journal = {Machine Learning},
  volume  = {58}, number = {1}, pages = {5--24}, year = {2005},
  doi     = {10.1007/s10994-005-4258-6}}

@article{webb2012,
  author  = {Webb, Geoffrey I. and Boughton, Janice R. and Zheng, Fei
             and Ting, Kai Ming and Salem, Houssam},
  title   = {Learning by Extrapolation from Marginal to
             Full-Multivariate Probability Distributions:
             Decreasingly Naive {B}ayesian Classification},
  journal = {Machine Learning},
  volume  = {86}, number = {2}, pages = {233--272}, year = {2012},
  doi     = {10.1007/s10994-011-5263-6}}

@article{hand2001,
  author  = {Hand, David J. and Yu, Keming},
  title   = {Idiot's {B}ayes---Not So Stupid After All?},
  journal = {International Statistical Review},
  volume  = {69}, number = {3}, pages = {385--398}, year = {2001},
  doi     = {10.1111/j.1751-5823.2001.tb00465.x}}

@article{hand2006,
  author  = {Hand, David J.},
  title   = {Classifier Technology and the Illusion of Progress},
  journal = {Statistical Science},
  volume  = {21}, number = {1}, pages = {1--14}, year = {2006},
  doi     = {10.1214/088342306000000060}}

@article{delgado2014,
  author  = {Fern{\'a}ndez-Delgado, Manuel and Cernadas, Eva and
             Barro, Sen{\'e}n and Amorim, Dinani},
  title   = {Do We Need Hundreds of Classifiers to Solve Real World
             Classification Problems?},
  journal = {Journal of Machine Learning Research},
  volume  = {15}, pages = {3133--3181}, year = {2014}}

@inproceedings{dacrema2019,
  author    = {Dacrema, Maurizio Ferrari and Cremonesi, Paolo and
               Jannach, Dietmar},
  title     = {Are We Really Making Much Progress? A Worrying
               Analysis of Recent Neural Recommendation Approaches},
  booktitle = {RecSys},
  pages     = {101--109}, year = {2019},
  doi       = {10.1145/3298689.3347058}}

@inproceedings{musgrave2020,
  author    = {Musgrave, Kevin and Belongie, Serge and Lim, Ser-Nam},
  title     = {A Metric Learning Reality Check},
  booktitle = {ECCV},
  pages     = {681--699}, year = {2020},
  doi       = {10.1007/978-3-030-58595-2_41}}

@article{lin2019,
  author  = {Lin, Jimmy},
  title   = {The Neural Hype and Comparisons Against Weak Baselines},
  journal = {SIGIR Forum},
  volume  = {52}, number = {2}, pages = {40--51}, year = {2019},
  doi     = {10.1145/3308774.3308781}}

@article{shwartz2022,
  author  = {Shwartz-Ziv, Ravid and Armon, Amitai},
  title   = {Tabular Data: Deep Learning Is Not All You Need},
  journal = {Information Fusion},
  volume  = {81}, pages = {84--90}, year = {2022},
  doi     = {10.1016/j.inffus.2021.11.011}}

@inproceedings{grinsztajn2022,
  author    = {Grinsztajn, L{\'e}o and Oyallon, Edouard and
               Varoquaux, Ga{\"e}l},
  title     = {Why Do Tree-Based Models Still Outperform Deep
               Learning on Typical Tabular Data?},
  booktitle = {NeurIPS Datasets and Benchmarks Track},
  year      = {2022}, eprint = {2207.08815}}

@inproceedings{mcelfresh2023,
  author    = {McElfresh, Duncan and Khandagale, Sujay and
               Valverde, Jonathan and Prasad C, Vishak and
               Ramakrishnan, Ganesh and Goldblum, Micah and
               White, Colin},
  title     = {When Do Neural Nets Outperform Boosted Trees on
               Tabular Data?},
  booktitle = {NeurIPS},
  year      = {2023}, eprint = {2305.02997}}

@inproceedings{kadra2021,
  author    = {Kadra, Arlind and Lindauer, Marius and Hutter, Frank
               and Grabocka, Josif},
  title     = {Well-Tuned Simple Nets Excel on Tabular Datasets},
  booktitle = {NeurIPS},
  year      = {2021}, eprint = {2106.11189}}

@article{menzies2007,
  author  = {Menzies, Tim and Greenwald, Jeremy and Frank, Art},
  title   = {Data Mining Static Code Attributes to Learn Defect
             Predictors},
  journal = {IEEE Transactions on Software Engineering},
  volume  = {33}, number = {1}, pages = {2--13}, year = {2007},
  doi     = {10.1109/TSE.2007.256941}}

@inproceedings{menzies2008,
  author    = {Menzies, Tim and Turhan, Burak and Bener, Ayse and
               Gay, Gregory and Cukic, Bojan and Jiang, Yue},
  title     = {Implications of Ceiling Effects in Defect Predictors},
  booktitle = {PROMISE},
  pages     = {47--54}, year = {2008},
  doi       = {10.1145/1370788.1370801}}

@inproceedings{provost1998,
  author    = {Provost, Foster and Fawcett, Tom and Kohavi, Ron},
  title     = {The Case Against Accuracy Estimation for Comparing
               Induction Algorithms},
  booktitle = {ICML},
  pages     = {445--453}, year = {1998}}

@inproceedings{fu2017,
  author    = {Fu, Wei and Menzies, Tim},
  title     = {Easy over Hard: A Case Study on Deep Learning},
  booktitle = {ESEC/FSE},
  pages     = {49--60}, year = {2017},
  doi       = {10.1145/3106237.3106256}}

@article{agrawal2021dodge,
  author  = {Agrawal, Amritanshu and Fu, Wei and Chen, Di and
             Shen, Xipeng and Menzies, Tim},
  title   = {How to {``DODGE''} Complex Software Analytics},
  journal = {IEEE Transactions on Software Engineering},
  volume  = {47}, number = {10}, pages = {2182--2194}, year = {2021},
  doi     = {10.1109/TSE.2019.2945020}}

@article{agrawal2021simpler,
  author  = {Agrawal, Amritanshu and Yang, Xueqi and Agrawal, Rishabh
             and Yedida, Rahul and Shen, Xipeng and Menzies, Tim},
  title   = {Simpler Hyperparameter Optimization for Software
             Analytics: Why, How, When?},
  journal = {IEEE Transactions on Software Engineering},
  volume  = {48}, number = {8}, pages = {2939--2954}, year = {2022},
  doi     = {10.1109/TSE.2021.3073242}}

@article{whigham2015,
  author  = {Whigham, Peter A. and Owen, Caitlin A. and
             MacDonell, Stephen G.},
  title   = {A Baseline Model for Software Effort Estimation},
  journal = {ACM Transactions on Software Engineering and
             Methodology},
  volume  = {24}, number = {3}, articleno = {20}, year = {2015},
  doi     = {10.1145/2738037}}

@inproceedings{tu2021,
  author    = {Tu, Huy and Menzies, Tim},
  title     = {{FRUGAL}: Unlocking Semi-Supervised Learning for
               Software Analytics},
  booktitle = {ASE},
  pages     = {394--406}, year = {2021},
  doi       = {10.1109/ASE51524.2021.9678617}}

@article{majumder2022,
  author  = {Majumder, Suvodeep and Mody, Pranav and Menzies, Tim},
  title   = {Revisiting Process versus Product Metrics: A Large
             Scale Analysis},
  journal = {Empirical Software Engineering},
  volume  = {27}, number = {3}, pages = {60}, year = {2022},
  doi     = {10.1007/s10664-021-10068-4}}
```
