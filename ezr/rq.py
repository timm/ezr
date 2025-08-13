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

def eg__overall():
  "run"
  data = Data(csv(the.file))
  rxRanks(data, [(b,acq,fn)
                 for acq in ["xploit","xplore","adapt"]
                 for b in   [20,40,60,80]
                 for fn in  [likely]])

def rxRanks(data, rxs, repeats=20):                    
  "rank different treatments"
  b4  = adds(disty(data, r) for r in data.rows)       
  win = lambda x: int(100*(1 - (x  -b4.lo) / (b4.mu - b4.lo)))        
  results, allnums = {}, Num()                        
  for budget, acq, fn in rxs:                         
    print(".", end="", flush=True, file=sys.stderr)
    the.acq, the.Budget = acq, budget                 
    train, holdout = rxTrainAndHoldOut(data, data.rows) 
    scores = [rxScore(data, train, holdout, fn)       
              for _ in range(repeats)]                
    for s in scores: add(allnums, s)                  
    results[(budget,acq,fn)] = scores                 
  ranks = statsRank(results, eps=.35*allnums.sd)      
  rxPrintResults(data, rxs, ranks, results, win)      

def rxTrainAndHoldOut(data, rows):                
  "generate a train and a hold-out set"
  rows = shuffle(rows); m = len(rows)//2          
  return clone(data, rows[:m]), rows[m:]          

def rxScore(data, train, holdout, fn):            
  "check hold-outs for 'good' rows (as guessed by model from training)"
  tree  = Tree(clone(train, fn(train)))           
  check = sorted(holdout, 
                 key=lambda r:treeLeaf(tree,r).ys.mu)[:the.Check]    
  return disty(data, distysort(data, check)[0])   

def rxPrintResults(data, rxs, ranks, results, win): 
  "print results"
  label = lambda k: f"{k[2].__name__}.{k[1]}.{k[0]}"
  winners = [label(k) for k in rxs]
  best_mu = adds(x for k,xs in results.items() if ranks[k]==1 
                 for x in xs).mu
  cells = [f'{label(k)}, {"!" if ranks[k]==1 else ""} {win(adds(results[k]).mu)}'
           for k in rxs]
  print(", ".join(cells),"|" ,
        len(data.rows), len(data.cols.x), len(data.cols.y), 
        win(best_mu),
        re.sub(".*/","", the.file), sep=",")
