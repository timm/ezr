"""
n2m.py: tiny AI. multi objective, explainable, AI
(c) 2025 Tim Menzies, <timm@ieee.org>. MIT license

Options, with (defaults):

  -f   file       : data name (../../moot/optimize/misc/auto93.csv)
  -r   rseed      : set random number rseed (123456781)
  -F   Few        : a few rows to explore (128)
  -l   leaf       : tree learning: min leaf size (2)
  -p   p          : distance calcs: set Minkowski coefficient (2)

Bayes:
  -k   k          : bayes hack for rare classes (1)
  -m   m          : bayes hack for rare attributes (2)

Active learning:
  -A   Acq        : xploit or xplore or adapt (xploit)  
  -G   Guess      : division best and rest (0.5)
  -s   start      : guesses, initial (4)
  -S   Stop       : guesses, max (20)
  -T   Test       : test guesses (5)

Stats:
  -B   Boots      : significance threshold (0.95)
  -b   bootstrap  : num. bootstrap samples (512)
  -C   Cliffs     : effect size threshold (0.197)
 """
import re
from lib import atom,o

the = o(**{k:atom(v) for k,v in 
           re.findall(r"-\w+\s+(\w+)[^\(]*\(\s*([^)]+)\)", __doc__)})
