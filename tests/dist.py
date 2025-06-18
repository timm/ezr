
import re,sys; sys.path.insert(0, "../")
from ezr import csv,doc,see,the,main,xdist,ydist,kpp,ydists,Num,Data,o

def eg__dist(_):
  print(the.file)
  data = Data(csv(doc(the.file)))
  row1 = data._rows[0]
  Y    = lambda r     : round(data.ydist(r),2)
  X    = lambda r1,r2 : data.xdist(r1,r2)
  assert all(0 <= Y(row)       <= 1 for row  in data._rows)
  assert all(0 <= X(row1,row2) <= 1 for row2 in data._rows)
  tmp = data.ydists()
  [print(Y(r), r) for r in tmp[:3]]; print(" ")
  [print(Y(r), r) for r in tmp[-3:]]

def eg__kpp(_):
  data = Data(csv(doc(the.file)))
  Y    = lambda r: data.ydist(r)
  one  = lambda  : Y(min(data.kpp(), key=Y))
  b4   = Num(Y(r) for r in data._rows)
  print("kpp ",o(mu   = b4.mu, lo=b4.lo, 
                 vals = [sorted(one() for _ in range(20))]))

main(globals())

