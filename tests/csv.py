import sys; sys.path.append("..")
from ezr import csv,the

for n,row in enumerate(csv("../" + the.train)) :
  if n % 50 == 0: print(row)
