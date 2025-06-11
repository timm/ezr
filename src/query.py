import math
from lib import big
from data import Num,Sym

# Middle tendency.
def mid(i):
  return i.mu        if i.it is Num else (
         mode(i.has) if i.it is Sym else (
         [mid(col) for col in i.cols.all]))

# Spread around middle tendency.
def spread(i):
  return i.sd            if i.it is Num else (
         ent(i.has, i.n) if i.it is Sym else (
         [spread(col) for col in i.cols.all]))

# Most common symbol.
def mode(d): 
  return max(d,key=d.has.get)

# Symbolic complexity.
def ent(d,N): 
  return -sum(p*math.log(p,2) for n in d.values() if (p:=n/N) > 0)

# For Nums, map v --> (0..1) for lo..hi.
def norm(num,v): 
  return v if v=="?" else (v-num.lo) / (num.hi-num.lo + 1/big)
