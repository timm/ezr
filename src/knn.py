#!/usr/bin/env python3 -B
# # KNN
# Here is some code that does a 5x5 cross-val for a knn.
# Adapt it to  explore k=1,2,5 and  the distance coeffience p
# of 1,2,3, 4. Also see what happens in use just n=[25,50,100,200,100000]
# rows (selected at random) where selecting 100000 should means "just 
# use all the rows.
# 
# ```python
import random,sys
sys.path.insert(0, '..')
from  stats import SOME,report
from  ezr import DATA, SYM, csv, xval, the, dot
      
def knn(data,  k, row1, rows=None):
  seen = SYM()
  for row in data.neighbors(row1, rows=rows)[:k]:
    seen.add( row[data.cols.klass.at] )
  return seen.mode

def one(data,k,train,test):
  n,acc = 0,0
  for row in test:
    want = row[ data.cols.klass.at ]
    got  = knn(data, k, row, train)
    acc += want==got
    n   += 1
  return acc/n
 
def main(file): 
  data = DATA().adds(csv(file))
  somes = []
  d=0
  for k in [1,2,5]:
     d += 1
     dot(d % 10)
     somes  += [SOME(txt=f"k{k}")]
     for train,test in xval(data.rows, 5,5):
       somes[-1].add(one(data, k, train, test))
  print("\n" + file)
  report(somes)

random.seed(1234567891)
for file in sys.argv[1:]: main(file)
# ```
