
Here is some code that does a 4x4 cross-val for a knn.
Adapt it to  explore k=1,2,5 neasest neghits.
also looking at the code HERE, try exploring a random subset of 
`train` of size 25,50,200,400
```lua
import sys,random
from stats import SOME,some0
from ezr import DATA, SYM, csv, xval

def knn(data,  row1, rows=None, k=2):
  seen = SYM()
  for row in data.neighbors(row1, rows=rows)[:k]:
    seen.add( row[data.cols.klass.at] )
  return seen.mode
  
def main(f): 
  random.seed(1)
  d = DATA().adds(csv(f))
  somes = []
    for n in [25,50,100,200,400]:
      some = SOME(txt=f"k{k}n{n}") 
      somes += [some]
      for train,test in xval(d.rows, 4,4):
        train = train # HERErandom.choices(train,k=n)
        n,acc = 0,0
        for row in test:
          want = row[ d.cols.klass.at ]
          got  = knn(d, row, train, k=2)
          acc += want==got
          n   += 1
        some.add(acc/n)
  some0(somes)

main(sys.argv[1]) 
```
