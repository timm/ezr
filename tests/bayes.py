import random,sys,re; sys.path.insert(0, "../")
from ezr import csv,doc,Data,the,go,shuffle

def eg__bayes(_):
  data = Data(csv(doc(the.file)))
  B    = lambda r1: round(data.like(r1), 3)
  assert all(-20 <= B(row)       <= -5 for row  in data._rows)
  print(sorted([B(row) for row in random.choices(data._rows,k=10)]))

def eg__nbc(_):
  the.file="../../moot/classify/diabetes.csv"
  "audiolog",
  "breastcance",
  "COMPAS5",
  "diabete",
  "germa",
  "ionospher",                 solar.flare2.csv               weathernom.csv
  ""primary.tumo",
  "page.blocks",
  "soybean
  "vote "wine "zoo]
column3C.csv                   iris.csv
  o
  data = Data(csv(doc(the.file)))
  for x  in data.nbc(10**6).stats.values():
    print("["+x.txt+"]", x.pd, x.pf,  x.acc)

go(globals())
