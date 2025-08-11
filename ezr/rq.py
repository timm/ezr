#!/usr/bin/env python3 -B
from ezr.tree import *
from ezr.stats import *
from ezr.likely import *

def eg__rq1():
  "run"
  data =Data(csv(the.file))
  treeShow(Tree(clone(data,likely(data))))

def eg__treeSelect():
  "run"
  repeats = 20
  data =Data(csv(the.file))
  b4 = adds(disty(data,r) for r in data.rows)
  win = lambda x: int(100*(1- (disty(data,x) - b4.lo)/(b4.mu - b4.lo)))
  trains,tests=Num(),Num()
  the.acq="klass"
  rxs=dict(build10=Num(), build20=Num(), build30=Num(), build40=Num(), build80=Num(), build120=Num(),
           check10=Num(), check20=Num(), check30=Num(), check40=Num(), check80=Num(), check120=Num())

  for budget in [10,20,30,40,80,120]:
    the.Budget = budget
    for _ in range(repeats):
      rows =shuffle(data.rows)
      m = len(rows)//2
      train,test = clone(data,rows[:m]), rows[m:]
      tmp =likely(train)
      trainTree  = Tree(clone(train,likely(train)))
      test = sorted(test,key=lambda r: treeLeaf(trainTree,r).ys.mu)[:the.Check]
      key1 = f"build{budget}"
      key2 = f"check{budget}"
      add(rxs[key1], win(tmp[0]))
      add(rxs[key2], win(distysort(data,test)[0]))
  print(' '.join(f"{key} {int(log.mu)}" for key,log in rxs.items()))

