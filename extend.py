# on my machine, i ran this with:  
#   python3.13 -B extend.py ../moot/optimize/[comp]*/*.csv

import sys,random
from ezr import the, DATA, csv, dot

def nth(k): return lambda z: z[k]

def myfun(i,train):
  random.seed(the.seed) #  not needed here, bt good practice to always take care of seeds
  d=DATA().adds(csv(train))
  x = len(d.cols.x)
  size = len(d.rows)
  dim = "lo" if x < 5 else ("med" if x < 10 else "hi")
  size = "small" if size< 500 else ("med" if size<5000 else "hi")
  return [i,dim, size, x,len(d.cols.y), len(d.rows), train]

print("n", "dim", "size","xcols","ycols","rows","file",sep="\t")
print(*["----"] * 7,sep="\t")
[print(*myfun(i,arg),sep="\t") for i,arg in enumerate(sys.argv)  if arg[-4:] == ".csv"]

# Ouput:
