<!-- vi: set spell spelllang=en_us: -->

# Insde EZR.py

Tim Menzies   
timm@ieee.org  
July 2025

EZR was an experiment with "little AI". Big AI assumes that model
building needs massive amounts of data and CPU. Little AI takes an
alternate approach and assumes that models are tiny gems that hide,
obscured, by vast amounts of irrelevant, noise, or redundant
information.

EZR was motivated by the current focus on Big AI that seems to be overlooking
centuries of experience with data mining. As far back as 1901, Pearson [^pca] taught us that
tables of data with $N$ columns can be modeled with far fewer columns (where the latter
are derived from the  eigenvectors of a correlation information. 
Decades of data mining has shown that 


    def Data(src):
      def _guess(row):
        return sum(interpolate(data,row,*pole) for pole in poles)/len(poles)
    
      head, *rows = list(src)
      data  = _data(head, rows)
      poles = projections(data)
      for row in rows: row[-1] = _guess(row)
      return data

asdasds


## References

[^pca]:  asdas
