from stats
import lite import *

def eg__ezr(repeats=20):
  "Example function demonstrating the optimization workflow"
  data = Data(csv(the.file))
  b4  = adds(disty(data,row) for row in data.rows)
  ab,abc=Num(s="ab"),Num(s="abc")
  [ezr1(data,b4,shuffle(data.rows),ab,abc) for _ in range(20)]
  print(the.Budget, *[int(x) for x in [ab.mu, abc.mu]])

def ezr1(data, b4, rows, ab, abc):
   win    = lambda v: int(100*(1 - (v - b4.lo)/(b4.mu - b4.lo)))
   best   = lambda rows: win(disty(data, distysort(data,rows)[0]))
   half   = len(data.rows)//2
   train, holdout = data.rows[:half], data.rows[half:]
   labels = likely(clone(data,train))
   add(ab, best(labels[:1]))
   tree   = Tree(clone(data,labels))
   some   = sorted(holdout,
                   key=lambda row: treeLeaf(tree,row).ys.mu)[:the.Check]
   add(abc, best(some))


def eg__10(): worker(range(10,11,10), *rxs())
def eg__20(): worker(range(10,21,10), *rxs())
def eg__40(): worker(range(10,41,10), *rxs())
def eg__80(): worker(range(10,81,10), *rxs())

def eg__nears(): 
  data = Data(csv(the.file))
  b4   = adds(disty(data,r) for r in data.rows)
  best = lambda rows: disty(data, distysort(data,rows)[0])
  win  = lambda v: int(100*(1 - (v - b4.lo)/(b4.mu - b4.lo)))
  for b in [10,20,40,80,160]:
    the.Budget=b
    print(b, adds(win(best(likely(data))) for _ in range(20)).mu)

def eg__rands(): 
  data = Data(csv(the.file))
  b4   = adds(disty(data,r) for r in data.rows)
  best = lambda rows: disty(data, distysort(data,rows)[0])
  win  = lambda v: int(100*(1 - (v - b4.lo)/(b4.mu - b4.lo)))
  for b in [10,20,40,80,160]:
    the.Budget=b
    print(b, adds(win(best(random.sample(data.rows,k=b))) for _ in range(20)).mu)

def rxs():
  data = Data(csv(the.file))
  return data, dict(rand = lambda b: random.sample(data.rows, k=b),
                    kpp  = lambda b: distKpp(data,            k=b),
                    near = lambda b: likely(data)
                    )

def worker(budgets,data, todo, repeats=20):
  t1   = time.time_ns()
  b4   = adds(disty(data,r) for r in data.rows)
  best = lambda rows: disty(data, distysort(data,rows)[0])
  win  = lambda v: int(100*(1 - (v - b4.lo)/(b4.mu - b4.lo)))
  wins = lambda a: win(sum(a)/len(a))
  out  = {}
  for b in budgets:
    fyi(b)
    the.Budget = b
    for k,fn in todo.items():
      fyi(".")
      out[(b,k)] = [best(fn(b)) for _ in range(repeats)] 
  eps = adds(x for k in out for x in out[k]).sd * 0.35
  top = sorted(stats.top(out,  eps = eps))
  mu  = adds(x for k in top for x in out[k]).mu
  print(win(mu), 
        re.sub(".*/","", the.file), 
        len(data.rows), len(data.cols.x), len(data.cols.y),
        int((time.time_ns() - t1) / (repeats * 1_000_000)),
        *[int(100*x) for x   in [eps, b4.mu, b4.lo, mu]], "|",
        *[f"{b}_{k},{wins(out[(b,k)])} " for b,k in top],
        sep=", " )
    
