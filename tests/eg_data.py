import sys; sys.path.insert(0, "../oo")
from lib import csv,doc
from data import the,Data,_cols
from obj import say

for col in _cols(["name","Age","Salary+","Age-"]).all: print(col)

data = Data(csv(doc(the.file)))
for col in data.cols.all: print(col)
for col,m,s in zip(data.cols.all, data.mid(),data.spread()):
  say([col.at,m,s])
