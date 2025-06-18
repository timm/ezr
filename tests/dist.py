
import random,sys; sys.path.insert(0, "../")
from ezr import csv,doc,the,go,Num,Data,o,see

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
  Y    = lambda r : data.ydist(r)
  run  = lambda fn: Y(min(fn(), key=Y))
  one  = lambda   : data.kpp()
  two  = lambda   : random.choices(data._rows,k=the.Build)
  print(Num(Y(r) for r in data._rows))
  print("kpp",see([sorted(run(one) for _ in range(20))]))
  print("any",see([sorted(run(two) for _ in range(20))]))

go(globals())

