<a href="https://doi.org/10.5281/zenodo.11183059"><img src="https://zenodo.org/badge/DOI/10.5281/zenodo.11183059.svg" alt="DOI"></a>

# ezr.py

Explanation system for semi=supervised multi-objective optimization. 


## Install

From pip: `pip install ezr`

From Gitug: download ez.py.

Test installation:

    ./ez.py -h

## Run

Find some csv data where the first row names the columns 

- Uppercase names denote numerics (all others are symbolic)
- Names ending in "+" or "-" are goals to be minimized.
- Names ending in "!" show the klass column (there can only be one).

For examples, see this [data](https://github.com/timm/ezr/tree/main/data) 
directory.
