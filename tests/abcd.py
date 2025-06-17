import sys; sys.path.insert(0, "../")
from ezr import abcds,main,o

"""
a b c <- got
------. want
5 1   | a  
  2 1 | b   
    3 | c  
"""

def eg__abcds(_):
  "checking confusion matrices."
  x = None
  for _ in range(5): x = abcds("a","a",x)
  for _ in range(1): x = abcds("a","b",x)
  for _ in range(2): x = abcds("b","b",x)
  for _ in range(1): x = abcds("b","c",x)
  for _ in range(3): x = abcds("c","c",x)
  a=x.stats["a"]; a1= dict(pd=a.pd, acc=a.acc, pf=a.pf, prec=a.prec)
  b=x.stats["b"]; b1= dict(pd=b.pd, acc=b.acc, pf=b.pf, prec=b.prec)
  c=x.stats["c"]; c1= dict(pd=c.pd, acc=c.acc, pf=c.pf, prec=c.prec)
  assert a1 == dict(pd=83, acc=91, pf=0, prec=100)
  assert b1 == dict(pd=66, acc=83, pf=11, prec=66)
  assert c1 == dict(pd=100, acc=91, pf=11, prec=75)
  for k,y in x.stats.items():
    print(k, o(pd=y.pd, acc=y.acc, pf=y.pf, prec=y.prec))

main(globals())
