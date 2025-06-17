import re,sys; sys.path.insert(0, "../")
from ezr import csv,doc,see,the,main,_cols
from ezr import o,Data

def eg__all(_):
  for fn in [eg__col0, eg__cols, eg__stats,
             eg__summary,eg__addSubs]: fn(_)

def eg__col0(_):
  "How are col names turned to columns?"
  for col in _cols(["name","Weight","Salary+","Age-"]).all: print("\t",col)

def eg__cols(_):
  "How to read csv files into a Data?"
  data1 = Data(csv(doc(the.file)))
  for col in data1.cols.all: print("\t",col)

def eg__stats(_):
  "What are mid, spread of csv files."
  data1 = Data(csv(doc(the.file)))
  for col,m,s in zip(data1.cols.all, data1.mid(), data1.spread()):
    print("\t",see([col.txt,m,s]))

def eg__summary(_):
  "How many columns and rows in a csv file."
  data1 = Data(csv(doc(the.file)))
  print("\t",see(o(file=re.sub("^.*/","",the.file), 
                   rows=len(data1._rows),
                   x= len(data1.cols.x), 
                   y=len(data1.cols.y))))

def eg__addSubs(_):
  "Can we incrementally add and delete rows?"
  data1 = Data(csv(doc(the.file)))
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
    data2.sub(row, zap=True)

main(globals())
