#!/usr/bin/env python3 -B
from data import *
from stats import *

#--------------------------------------------------------------------
def like(i:o, v:Any, prior=0) -> float :
  "probability of 'v' belong to the distribution in 'i'"
  if i.it is Sym:
    tmp = ((i.has.get(v,0) + the.m*prior) 
           /(sum(i.has.values())+the.m+1e-32))
  else:
    var = 2 * i.sd * i.sd + 1E-32
    z  = (v - i.mu) ** 2 / var
    tmp =  math.exp(-z) / (2 * math.pi * var) ** 0.5
  return min(1, max(0, tmp))

def likes(data:Data, row:Row, nall=100, nh=2) -> float:
  "How much does this DATA like row?"
  prior= (data.n + the.k) / (nall + the.k*nh)
  tmp= [like(c,v,prior) for c in data.cols.x if (v:=row[c.at]) != "?"]
  return sum(math.log(n) for n in tmp + [prior] if n>0)    

def likeBest(datas,row, nall=None):
  "Which data likes this row the most?"
  nall = nall or sum(len(data.row) for data in datas.values())
  return max(datas, key=lambda k: likes(datas[k],row,nall,len(datas)))

def likeClassifier(file, wait=5):
  "Classify rows by how much each class likes a row."
  cf = Confuse()
  data = Data(csv(file))
  wait,d,key = 5,{},data.cols.klass.at
  for n,row in enumerate(data.rows):
    want = row[key]
    d[want] = d.get(want) or clone(data)
    if n > wait: confuse(cf, want, likeBest(d,row, n-wait))
    add(d[want], row)
  return confused(cf)

#--------------------------------------------------------------------
def eg__Sym(): 
  "Sym: demo of likelihood."
  print(s := round(like(adds("aaaabbc"), "a"),2))
  assert s == 0.44

def eg__num(): 
  "Num: demo."
  print(x := round(adds(random.gauss(10,2) for _ in range(1000)).sd,2))
  assert x == 2.05
  
def eg__confuse():
  "Stats: discrete calcs for recall, precision etc.."
  # a b c <- got
  # ------. want
  # 5 1   | a
  #   2 1 | b
  #     3 | c
  cf = Confuse()   
  for want,got,n in [
      ("a","a",5),("a","b",1),("b","b",2),("b","c",1),("c","c",3)]:
    for _ in range(n): confuse(cf, want, got)
  xpect = {"a": {'pd':83,  'acc':92, 'pf':0,  'prec':100},
           "b": {'pd':67,  'acc':83, 'pf':11, 'prec':67},
           "c": {'pd':100, 'acc':92, 'pf':11, 'prec':75} }
  for y in confused(cf):
    if y.label != "_OVERALL":
       got = {'pd':y.pd, 'acc':y.acc, 'pf':y.pf, 'prec':y.prec}
       assert xpect[y.label] == got
  [pout(x) for x in confused(cf)]

def eg__diabetes(): 
  "Naive Bayes classifier: test on diabetes."
  [pout(x) for x in likeClassifier("../../moot/classify/diabetes.csv")]

def eg__soybean():  
  "Naive Bayes classifier: test on soybean."
  [pout(x) for x in likeClassifier("../../moot/classify/soybean.csv")]

#--------------------------------------------------------------------
def eg__all()             : mainAll(globals())
def eg__list()            : mainList(globals())
def eg_h()                : print(helpstring)
if __name__ == "__main__" : main(globals())
