import sys; sys.path.insert(0, "../")
from ezr import abcds,main,o

"""
#  n   a   b   c   d  acc pd  pf  prec f  g  class     
# -------------------------------------------------
# 22   0   5   5  17  63  77 100  77  77  0  a         
#  5  17   5   5   0  63   0  23   0  77  0  b       

a b c <-- got
5 1 0 a <-- want
0 2 1 b <-- want
0 0 3 c <-- want

a b <- got
11 1  a <-- want
2  12 b <-- got
"""

def eg__abcds(_):
  x = None
  for _ in range(5): x = abcds("a","a",x)
  for _ in range(1): x = abcds("b","a",x)
  for _ in range(2): x = abcds("b","b",x)
  for _ in range(1): x = abcds("b","c",x)
  for _ in range(3): x = abcds("a","c",x)
  for k,y in x.stats.items():
    print(k, o(pd=y.pd, acc=y.acc, 
               pf=y.pf, prec=y.prec))

main(globals())
