import random,sys,re; sys.path.insert(0, "../oo")

from lib import csv,doc
from data import the,Num,Data,_cols
from obj import obj,see,say

print("\nCol headers, no rows")
for col in _cols(["name","Age","Salary+","Age-"]).all: print("\t",col)

file=sys.argv[1] if len(sys.argv)>1 else the.file

data1 = Data(csv(doc(file)))

print("\nCol headers, after reading rows")
for col in data1.cols.all: print("\t",col)

print("\nStats of each column")
for col,m,s in zip(data1.cols.all, data1.mid(), data1.spread()):
  print("\t",see([col.txt,m,s]))

print("\nSummary stats")
print("\t",see(obj(file=re.sub("^.*/","",file), 
                   rows=len(data1._rows),
                   x= len(data1.cols.x), 
                   y=len(data1.cols.y))))

def eg__addSubs(data1):
  print("\nCan data can incrementally add/subtract rows?")
  data2 = data1.clone()
  mids = spreads = None
  for row in data1._rows:
    data2.add(row)
    if len(data2._rows)==100:
      mids    = data2.mid()
      spreads = data2.spread()
  for row in data1._rows[::-1]:
    if len(data2._rows)==100:
      assert sum((a-b) for a,b in zip(mids,   data2.mid())) < 0.1
      assert sum((a-b) for a,b in zip(spreads, data2.spread())) < 0.1
      print("- yes!")
      return
    data2.sub(row, purge=True)

eg__addSubs(data1)
