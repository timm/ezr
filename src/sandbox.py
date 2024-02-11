import random
from math import *
def phi(x):
  return (1.0 + erf(x / sqrt(2.0))) / 2.0

def pc(n):
  w = 6/n
  def xy(i): x= -3 + i*w; return [x,phi(x),0]
  lst = [xy(i) for i in range(n+1)]
  for i,three in enumerate(lst):
    if i > 0:
      three[2] = lst[i][1] - lst[i-1][1]
  [print([round(x,3) for x in three],sep="\t") 
   for three in lst]

pc(30)
