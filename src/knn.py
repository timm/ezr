# # KNN
# Here is some code that does a 5x5 cross-val for a knn.
# Adapt it to  explore k=1,2,5 neasest neghits.
# also looking at the code HERE, try exploring a random subset of 
# `train` of size 25,50,200,400
# 
# ```python
import random,sys
sys.path.insert(0, '..')
from  stats import SOME,some0
from  ezr import DATA, SYM, csv, xval, the
      
def dot(): print(".", file=sys.stderr, flush=True, end="")

def knn(data,  k, row1, rows=None):
  seen = SYM()
  for row in data.neighbors(row1, rows=rows)[:k]:
    seen.add( row[data.cols.klass.at] )
  return seen.mode

def one(data,k,p, train,test):
  n,acc = 0,0
  the.p=p
  for row in test:
    want = row[ data.cols.klass.at ]
    got  = knn(data, k, row, train)
    acc += want==got
    n   += 1
  return acc/n
 
def main(file): 
  random.seed(1234567891)
  data = DATA().adds(csv(file))
  somes = []
  for n in [25,50,100,200,100000]:
    for k in [1,2,5]:
      for p in [1,2,3,4]:
        dot()
        somes  += [SOME(txt=f"k{k}p{p}n{n}")]
        for train,test in xval(data.rows, 5,5, n):
          somes[-1].add(one(data, k, p, train, test))
  print("\n" + file)
  some0(somes)

for file in sys.argv[1:]: main(file)
# ```
