import random,sys,re; sys.path.insert(0, "../")
from ezr import csv,doc,Data,the,go,shuffle

def eg__bayes(_):
  print(the.file)
  data = Data(csv(doc(the.file)))
  B    = lambda r1: round(data.like(r1), 3)
  assert all(-20 <= B(row)       <= -5 for row  in data._rows)
  print(sorted([B(row) for row in random.choices(data._rows,k=10)]))

go(globals())
