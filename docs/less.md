.

# Introduction: All you Need is Less

Suppose we want to use data to make decisions about what to do,
what to avoid, what to do better, etc etc. How to do that?

This process is called _analytics_, i.e. the reduction of large
amounts of low-quality data into tiny high-quality statements. Think
of it like "finding the diamonds in the dust".  For example, in one
survey of managers at   Microsoft, researchers found many kinds  of
analytics functions [^buse]. As shown in the following table, those
functions include regression, topic analysis, anomaly detection,
what-if analysis, etc:

[^buse]: Buse and zimemrmann, info neeeds

<img  width=900 src="img/buse.png">

But is analytics as complicated as all that? Are all these functions
really different or do they share a common core? And if they share
a common core, does that mean if we coded up, say, regression then
everything could be coded very quickly?  More importantly, if we
found someway to optimize that core, would that optimization apply
to many kinds of analytics?

We think so.  We've been working on applications of analytics for
decades. In that work, we've explored data--driven
applications in spacecraft control, fairness, explanation,
configuration, cloud computing,  security, literature reviews,
technical  debt,  vulnerability prediction, defect prediction,
effort estimation,  and the management of open source software
projects. And in all that work, one constant has been the  
_compressability_ of the data:

- Many data sets can be pruned down to a surprisingly small set of rows and columns,
without loss of signal.
- In that compressed space, modeling becomes more manageable and
all our functions algorithms run faster (since there is less to
explore).
- Also, data becomes private since we threw away so much in the
compression process.
- Further, explanation is easier since this there is less to explain.
This means, in turn, that is easier to understand/ audit/critique
our solutions.

We are not the first to say these things.  For example, many
researcher accept that higher dimensional data can often be reduced
to a _lower dimensional latent manifolds_ inside that
high-dimensional space [^zhu2005semi].  As a consequence, many
data sets that appear to initially require many variables to describe,
can actually be described by a _comparatively small number of variables_.

[^zhu2005semi]: ss



