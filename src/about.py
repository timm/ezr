"""
ezr: a tiny AI toolkit for multi objective explainable AI
(c) 2025 Tim Menzies, <timm@ieee.org>. MIT license

Options, with (defaults):

  -f   file       : data name (../../moot/optimize/misc/auto93.csv)
  -r   rseed      : set random number rseed (123456781)
  -F   Few        : a few rows to explore (128)
  -l   leaf       : tree learning: min leaf size (2)
  -p   p          : distance calcs: set Minkowski coefficient (2)

Active learning:
  -A   Assume     : initial guesses (4)
  -B   Build      : build a modell from this number of samples (20)
  -C   Check      : test the model, allowing this many checks (5)
  -a   acq        : in building, xploit or xplore or adapt? (xploit)  
  -g   guess      : division best and rest (0.5)

Bayes:
  -k   k          : bayes hack for rare classes (1)
  -m   m          : bayes hack for rare attributes (2)

Stats:
  -s   samples    : samples used for bootstralling (0.95)
  -b   bootstrap  : num. bootstrap samples (512)
  -c   Cliffs     : effect size threshold (0.197)
 """
import re
from aux import atom,o

the = o(**{k:atom(v) for k,v in 
           re.findall(r"-\w+\s+(\w+)[^\(]*\(\s*([^)]+)\)", __doc__)})

