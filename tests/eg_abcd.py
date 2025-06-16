import sys; sys.path.insert(0, "../oo")
from root import o
from abcd import abcds
import random

"""
#  n   a   b   c   d  acc pd  pf  prec f  g  class     
# -------------------------------------------------
# 22   0   5   5  17  63  77 100  77  77  0  a         
#  5  17   5   5   0  63   0  23   0  77  0  b       

a b c <-- got
5 1 0 a <-- want
0 2 1 b <-- want
0 0 3 c <-- want
"""

random.seed(1234567891)
for _ in range(5):  w=abcds("a","a",w)
for _ in range(1):  x=abcds("a","b",x)
for _ in range(2):  x=abcds("b","b",x)
for _ in range(1):  x=abcds("b","c",x)
for _ in range(3):  x=abcds("c","a",x)

for k,x in w.stats.items():
  print(k, o(pd=x.pd, acc=x.acc, 
             pf=x.pf, prec=x.prec))
