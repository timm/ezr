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

Code: 

    def Data(src):
      def _guess(row):
        return sum(interpolate(data,row,*pole) for pole in poles)/len(poles)
          
      head, *rows = list(src)
      data  = _data(head, rows)
      poles = projections(data)
      for row in rows: row[-1] = _guess(row)
      return data
### data 

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
