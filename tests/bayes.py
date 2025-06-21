import random,sys,re; sys.path.insert(0, "../")
from ezr import csv,doc,Data,the,go,say,o,abcdReady,abcdWeighted

def eg__bayes(_):
  data = Data(csv(doc(the.file)))
  B    = lambda r1: round(data.like(r1), 3)
  assert all(-20 <= B(row)       <= -5 for row  in data._rows)
  print(sorted([B(row) for row in random.choices(data._rows,k=10)]))

def eg__nbcs(_):
  the.file="../../moot/classify/diabetes.csv"
  files = ["audiology", "breastcancer", "COMPAS53", 
            "diabetes", "german",
            "ionosphere", "primary.tumor","page.blocks", "soybean", "vote", 
              "wine", "zoo"]
  for f in files:
    eg__nbc("../../moot/classify/"+f+".csv")

def eg__nbc(file=None):
  the.file = file or the.file
  print("")
  data = Data(csv(doc(the.file)))
  log = abcdReady(data.nbc(10**6))
  for x in list(log.stats.values()) + [abcdWeighted(log)]:
    say(o(n=x.b+x.d, a=x.a,b=x.b,c=x.c,d=x.d,
          pd=x.pd,pf=x.pf,acc=x.acc,klass=x.txt,
          file=re.sub(r"^.*\/","",the.file)))



go(globals())
