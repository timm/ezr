<!-- vi: set spell spelllang=en_us: -->

# Insde EZR.py

Tim Menzies   
timm@ieee.org  
July 2025

EZR was an experiment with "little AI". Big AI assumes that model
building needs massive amounts of data and CPU. Little AI takes an
alternate approach and assumes that models are tiny gems that hide,
obscured, by vast amounts of irrelevant, noise, or redundant
information. Under that assumption:

> The best thing to do with most data, is throw it away.

EZR was motivated by the current monofocus on Big AI that seems to
overlook centuries of experience with data mining. As far back
as 1901, Pearson[^pca] showed  that tables of data with $N$ columns
can be modeled with far fewer columns (where the latter are derived
from the  eigenvectors of a correlation information).

Decades of subsequent work  has shown that effective models can be
built from data that cover tiny fractions of the possible data
space[^witten].  Levnina and Biclet cwnote that

> "The only reason any (learning) methods work ...
  is that, in fact, the data are not truly high-dimensional. Rather,
  they are .. can be efficiently
   summarized in a space of a much lower dimension.

(This remarks echoes an early concusion from Jhnson and Lindenstrauss [^john84].).

For example:


- **Many rows can be ignored**: Data sets with thousands of rows can be modeled with just a few dozen samples[^me08a].
  To explain this, suppose we only want to use models that are  well supported by the data;
  i.e. supported
  by multiple rows in a table of data. This means that  many rows
  in a table can be be replaced by a smaller number of exemplars.
- **Many columns can be ignored**:
  High-dimensional tables (with many colummns) can be projected into lower dimensional tables while
  nearly preserving all pairwise distances[^john84].
  This means that
  data sets with many columns can
  be modeled with surprisingly few columns.
  e.g. A table of (say) of $C=20$ columns of binary variables
  have a total data space of $2^{20}$ (which is more than a million).
  Yet with just dozens to hundred rows of training data, it is often
  possible to build predictors from test rows from that data space.
  This is only possible if the signal in this data condenses to a
  small regions within the  total data space.
- Researchers in semi-supervised learning note that 
  high-dimensional data often lies on a simpler, lower-dimensional ”manifold” embedded within that higher space [^zh05].

    def Data(src):
      def _guess(row):
        return sum(interpolate(data,row,*pole) for pole in poles)/len(poles)
    
      head, *rows = list(src)
      data  = _data(head, rows)
      poles = projections(data)
      for row in rows: row[-1] = _guess(row)
      return data

### Caveats

not generation.

Tabular data

## References

[^john84]: W. B. Johnson and J. Lindenstrauss, “Extensions of lipschitz mappings
into a hilbert space,” Contemporary Mathematics, vol. 26, pp. 189–206,
1984.

[^me08a:] T. Menzies, B. Turhan, A. Bener, G. Gay, B. Cukic, and Y. Jiang,
“Implications of ceiling effects in defect predictors,” in Proceedings
of the 4th international workshop on Predictor models in software
engineering, 2008, pp. 47–54.

[^pca]:  Pearson, K. (1901). "On Lines and Planes of Closest Fit
to Systems of Points in Space". Philosophical Magazine. 2 (11):
559–572. 10.1080/14786440109462720.

[^witten:]      I. Witten, E. Frank, and M. Hall.  Data Mining:
Practical Machine Learning Tools and Techniques Morgan Kaufmann
Series in Data Management Systems Morgan Kaufmann, Amsterdam, 3
edition, (2011)

[^zhu05]: X. Zhu, “Semi-supervised learning literature survey,” Computer Sciences
Technical Report, vol. 1530, pp. 1–59, 2005.
