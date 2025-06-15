import math
from lib import big
from data import Num,Sym

def mid(i):
  "Middle tendency."
  return i.mu        if i.it is Num else (
         mode(i.has) if i.it is Sym else (
         [mid(col) for col in i.cols.all]))

def spread(i):
  "Spread around middle tendency."
  return i.sd            if i.it is Num else (
         ent(i.has, i.n) if i.it is Sym else (
         [spread(col) for col in i.cols.all]))

def mode(d): 
  "Most common symbol."
  return max(d,key=d.get)

def ent(d,N): 
  "Symbolic complexity."
  return -sum(p*math.log(p,2) for n in d.values() if (p:=n/N) > 0)

def norm(num,v): 
  "For Nums, map v --> (0..1) for lo..hi."
  return v if v=="?" else (v-num.lo) / (num.hi-num.lo + 1/big)
