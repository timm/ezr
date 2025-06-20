
import random,sys,re; sys.path.insert(0, "../")
from ezr import csv,doc,lines,the,go,shuffle
from ezr import Num,Data,o,see,say,sway,EXAMPLE

def eg__ydists(_):
  data = Data(csv(lines(EXAMPLE)))
  for row in data.ydists():
    print(row)

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

def eg__kmeans(_):
  print(the.file)
  data = Data(csv(doc(the.file)))
  _, errs = data.kmeans(data._rows)
  say(errs)

def eg__kpp(_):
  data = Data(csv(doc(the.file)))
  Y    = lambda r : data.ydist(r)
  run  = lambda fn: sorted(Y(min(fn(), key=Y)) for _ in range(20))
  one  = lambda   : data.kpp()
  two  = lambda   : random.choices(data._rows,k=the.Build)
  print(Num(Y(r) for r in data._rows))
  print("kpp",see(run(one)))
  print("any",see(run(two)))

def eg__sway(_):
  data = Data(csv(doc(the.file)))
  Y    = lambda r  : data.ydist(r)
  Ys   = lambda fn : Y(min(fn(), key=Y))
  raw  = lambda fn : sorted(Ys(fn) for _ in range(20))
  kpp  = lambda    : data.kpp(rows())
  rand = lambda    : random.choices(rows(),k=the.Build)
  sway = lambda    : data.sway(rows()).done
  knn  = lambda    : data.kmeans(rows(), k=the.Build)[0]
  asIs = Num(Y(r) for r in data._rows)
  for few in [32,64,128,256,512]:
    the.Few = few
    rows = lambda : shuffle(data._rows)[:the.Few]
    stats =dict(
            rand = Num(raw(rand)),
            knn  = Num(raw(knn)),
            kpp  = Num(raw(kpp)),
            sway = Num(raw(sway)))
    win  = lambda n: int(100*(1 - (asIs.mu - n)/(asIs.mu - asIs.lo)))
    for k,num in stats.items():
      print(k, see(num.mu), win(num.mu),sep=", ",end=", ")
    print("asIs", see(asIs.mu), see(asIs.lo),win(asIs.mu),
          the.Build, the.Few, len(data._rows), 
          len(data.cols.y), len(data.cols.x),
          re.sub(".*/","",the.file),sep=", ")

go(globals())

