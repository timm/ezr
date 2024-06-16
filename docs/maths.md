# Maths

We are learning 
 asdas

asas

```lua
function fred(a) return a end
```

asdas
# Just Enough Maths

functions:
indepnsent and dependent variables

finds of fucntions. numeroc prediction symbolic prediction


pdf and cdf

here are two boxes with a set of numbers of symols. are the same? can we fuse them rand reason about fewer boxes?

## non-numerics

- centrality = mid= mode
= -diversity = entropy

## Distributions

One number, N numbers, 
- centrality = mean 
- diversty = stamdard deviation 

computing sd
- welford
- nonparametric: median, (90=10)/2.58 (only keep some, resort when needed)

- are they distinguishable? significance
  - quick and nasty; cohen's D
  - more considered: bootstrap (nonparametric)
- are they different, enough?
  - effect size: cliffs delta

that's for two distributions.
- for n, we do a top down clustering (scott-knott)

## Distance
euclideam, manitbal, chekshev

aha's algorthm

curse of diensionality, synthesized dientions. PCA nystrom algorithms fastmap

### Manifold
### reduction
## comrpession

## Centrality

## Diversity
 entropy

in this paper, data are tables with rows and columns. Such tables are
examples of some function

$$Y=f(X)$$

abnd our goal is to learn $f$ from $X,Y$. 

XXX noisy. more X that Y

Columns are
also known as features, attributes, or variables. Rows contain
multiple X,Y features where X are the independent variables (that
can be observed, and sometimes controlled) while Y are the dependent
variables (e.g. number of defects). When Y is absent, then unsupervised
learners seek mappings between the X values. For example, clustering
algorithms find groupings of similar rows (i.e. rows with similar
X values). Usually most rows have values for most X values. But
with text mining, the opposite is true. In principle, text miners
have one column for each work in text’s language. Since not all
documents use all words, these means that the rows of a text mining
data set are often “sparse”; i.e. has mostly missing values. When
Y is present and there is only one of them (i.e. |Y | = 1) then
supervised learners seek mappings from the X features to the Y
values. For example, logistic regression tries to fit the X,Y mapping
to a particular equation. When there are many Y values (i.e. |Y| >
1), then another array W stores a set of weights indicating what
we want to minimize or maximize (e.g. we would seek to minimize Yi
when Wi < 0). In this case, multi-objective optimizers seek X values
that most minimize or maximize their associated Y values. So: •
Clustering algorithms find groups of rows; • and Classifiers (and
regression algorithms) find how those groups relate to the target
Y variables; • and Optimizers are tools that suggest “better”
settings for the X values (and, here, “better” means settings that
improve the expected value of the Y values). Apart from W,X,Y, we
add Z, the hyperparameter settings that control how learners performs
regression or clustering. For example, a KNeighbors algorithm needs
to know how manynearby rows to use for its classification (in which
case, that k ∈ Z). Usually the Z values are shared across all rows
(exception: some optimizers first cluster the data and use different
Z settings for different clusters). Two important detail not discussed
above are feature engineering and how to select performance metrics.
Feature engineering includes all the pre-processing algorithms
listed

