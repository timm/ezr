"""
lite.py, lightweight multi objective.   
(col) 2025, Tim Menzies <timm@ieee.org>, MIT license   
   
    -a  acq=klass       acquisition function   
    -A  Any=4           on init, how many initial guesses?   
    -B  Build=24        when growing theory, how many labels?   
    -C  Check=5         when testing, how many checks?   
    -D  Delta=smed      required effect size test for cliff's delta
    -F  Few=128         sample size of data random sampling  
    -b  bins=7          number of bins   
    -k  k=1             bayes low frequency hack  
    -l  leaf=3          min items in tree leaves
    -K  Ks=0.95         confidence for Kolmogorov–Smirnov test
    -m  m=2             bayes low frequency hack  
    -p  p=2             distance co-effecient
    -s  seed=1234567891 random number seed   
    -f  file=../../moot/optimize/misc/auto93.csv  data file 
      
    -h                  show help   
    --all               run all examples.   
    --list              list all examples
"""
