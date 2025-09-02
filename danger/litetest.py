#!/usr/bin/env python3 -B

import stats
from lite import *

def eg__the(): 
  print(ok := str == type(the.Delta))
  assert ok,"str not found"

def eg__csv():
  print(n := sum(len(row) for row in csv(the.file)))
  assert n==3192, "missing cells"

def eg__sym(): 
  print(x := adds("aaaabbc",Sym()).has["a"])
  assert x==4

def eg__num(): 
  print(mu := round(adds(random.gauss(10,2) for _ in range(1000)).mu,1))
  print(sd := round(adds(random.gauss(10,2) for _ in range(1000)).sd,2))
  assert sd == 1.99 and mu == 10

def eg__data():
  print(x := round(sum(y.mu for y in Data(csv(the.file)).cols.y),2))
  assert x == 3009.84

def eg__distx():
  data = Data(csv(the.file))
  r1   = data.rows[0]
  ds   = adds(distx(data,r1,r2) for r2 in data.rows)
  assert 0.45 <= ds.mu <= 0.55 and ds.lo >= 0 and ds.hi <= 1

def eg__disty():
  data = Data(csv(the.file))
  data.rows.sort(key=lambda row: disty(data,row))
  assert all(0 <= disty(data,r) <= 1 for r in data.rows)

def eg__irisKpp(): 
  data = Data(csv("../../moot/classify/iris.csv"))
  mids = distKpp(data,k=10)
  assert distx(data, mids[0], mids[-1]) > 0.5

def eg__fmap(r=20):
  "Dist:  diversity-based optimziation with fast map."
  d    = Data(csv(the.file))
  b4   = adds(disty(d,row) for row in d.rows)
  win  = lambda v: int(100*(1 - (v - b4.lo)/(b4.mu - b4.lo)))
  best = lambda rows: win(disty(d, distysort(d,rows)[0]))
  for few in [12,25,50,100]:
    the.Few = few
    sway1 = adds(best(distFastermap(d,d.rows,False)) for _ in range(r))
    sway2 = adds(best(distFastermap(d,d.rows,True )) for _ in range(r))
    print( *[int(x) for x in [sway1.mu, sway2.mu]])

def eg__likes():
  data = Data(csv(the.file))
  ds   = sorted(likes(data,row) for row in data.rows)
  assert all(-15 < like < -5 for like in ds)

def eg__likely():
  data = Data(csv(the.file))
  b4   = adds(disty(data,row) for row in data.rows)
  win  = lambda v: int(100*(1 - (v - b4.lo)/(b4.mu - b4.lo)))
  best = lambda rows: win(disty(data, distysort(data,rows)[0]))
  for acq in ["near","xploit","xplor","bore","adapt"]:
    the.acq = acq
    print(best(likely(data)))

def eg__ezr(repeats=20):
  "Example function demonstrating the optimization workflow"
  data = Data(csv(the.file))
  b4   = adds(disty(data,row) for row in data.rows)
  win  = lambda v: int(100*(1 - (v - b4.lo)/(b4.mu - b4.lo)))
  best = lambda rows: win(disty(data, distysort(data,rows)[0]))
  half = len(data.rows)//2
  ab, abc, rand, check         = Num(), Num(), Num(), Num()
  all, sway1,sway2             = Num(), Num(), Num()
  near,xploit,xplor,bore,adapt = Num(), Num(), Num(), Num(), Num()
  for i in range(repeats): 
    data.rows = shuffle(data.rows)
    train, holdout = data.rows[:half], data.rows[half:]
    al   = likely(clone(data, train))
    base = best(rx1(data, holdout, al))
    add(abc,   base)
    add(sway1, best(rx1(data,holdout,distFastermap(data,data.rows,False))))
    add(sway2, best(rx1(data,holdout,distFastermap(data,data.rows,True ))))
    add(ab,    best(al))
    add(rand,  best(rx1(data, holdout, train[:the.Budget])))
    add(check, best(holdout[:the.Check]))
    add(all,   best(rx1(data, holdout, train)))
    the.acq="near";   add(near,   best(rx1(data,holdout,likely(clone(data,train)))))
    the.acq="xploit"; add(xploit, best(rx1(data,holdout,likely(clone(data,train)))))
    the.acq="xplor";  add(xplor,  best(rx1(data,holdout,likely(clone(data,train)))))
    the.acq="bore";   add(bore,   best(rx1(data,holdout,likely(clone(data,train)))))
    the.acq="adapt";  add(adapt,  best(rx1(data,holdout,likely(clone(data,train)))))
  print(the.Budget, the.leaf, ab.n,  
        int(abc.mu),  "|",
        "ab",     int(ab.mu),    
        "rand",   int(rand.mu), 
        "check",  int(check.mu),
        "all",    int(all.mu),
        "sway1",  int(sway1.mu),
        "sway2",  int(sway2.mu),
        "near",   int(near.mu),
        "xploit", int(xploit.mu),
        "xplor",  int(xplor.mu),
        "bore",   int(bore.mu),
        "adapt",  int(adapt.mu),
        re.sub(".*/","",the.file)) 

def rx1(data, holdout, labels):
  tree = Tree(clone(data, labels))
  return sorted(holdout, key=lambda row: treeLeaf(tree,row).ys.mu)[:the.Check]

def eg__all():
  for f in [eg__csv, eg__sym, eg__num, eg__data, eg__distx,
            eg__disty, eg__irisKpp, eg__fmap, eg__ezr]:
      print("\n"+f.__name__); f()

if __name__ == "__main__": main(the, globals())
