import sys; sys.path.insert(0, "../src")

import random
from about import o
from lib import go
from stats import scottKnott, cliffs,bootstrap

def eg__stats(_):
   def c(b): return 1 if b else 0
   b4 = [random.gauss(1,1)+ random.gauss(10,1)**0.5 for _ in range(59)]
   d=0.5
   while d < 1.5:
     now = [x+d*random.random() for x in b4]
     b1  = cliffs(b4,now)
     b2  = bootstrap(b4,now)
     print(o(agree=c(b1==b2), cliffs=c(b1), boot=c(b2),d=d))
     d += 0.05

def eg__rank(_):
  n=100
  rxs=dict(asIs = [random.gauss(10,1) for _ in range(n)],
          copy1 = [random.gauss(20,1) for _ in range(n)],
          now1  = [random.gauss(20,1) for _ in range(n)],
          copy2 = [random.gauss(40,1) for _ in range(n)],
          now2  = [random.gauss(40,1) for _ in range(n)])
  [print(o(rank=num.rank, mu=num.mu)) for num in scottKnott(rxs).values()]

def eg__rank2(_):
   n   = 100
   rxs = dict(asIs  = [random.gauss(10,1) for _ in range(n)],
              copy1 = [random.gauss(20,1) for _ in range(n)])
   [print(o(rank=num.rank, mu=num.mu)) for num in scottKnott(rxs).values()]

go(globals())
