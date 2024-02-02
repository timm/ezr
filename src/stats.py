# vim : set et ts=2 sw=2 :

import sys, random

def of(s):
    try: return float(s)
    except ValueError: return s

def slurp(file):
  SAMPLEs,lst,last= [],[],None
  with open(file) as fp: 
    for word in [of(x) for s in fp.readlines() for x in s.split()]:
      if isinstance(word,float):
        lst += [word]
      else:
        if len(lst)>0: SAMPLEs += [SAMPLE(lst,last)]
        lst,last =[],word
  if len(lst)>0: SAMPLEs += [SAMPLE(lst,last)]
  return SAMPLEs

class SAMPLE:
  "stores mean, standard deviation, low, high, of a list of SAMPLEbers"
  def __init__(self,lst,txt="",rank=0):
    self.has = sorted(lst)
    self.txt, self.rank = txt,0
    self.n, self.sd, self.mu, self.lo, self.hi = len(lst),0,0, sys.maxsize, -sys.maxsize
    if self.n != 0: 
      tmp, self.mu  = 0, sum(lst) / self.n
      for x in lst: 
        tmp += (x-self.mu)**2; self.hi=max(x,self.hi); self.lo=min(x,self.lo)
      self.sd = (tmp/(self.n - 1+1E-30))**.5 

  def mid(self): return self.has[len(self.has)//2]

  def bar(self, SAMPLE, fmt="%8.3f", word="%10s", width=50):
    out  = [' '] * width
    pos = lambda x: int(width * (x - self.has[0]) / (self.has[-1] - self.has[0] + 1E-30))
    [a, b, c, d, e]  = [SAMPLE.has[int(len(SAMPLE.has)*x)] for x in [0.1,0.3,0.5,0.7,0.9]]
    [na,nb,nc,nd,ne] = [pos(x) for x in [a,b,c,d,e]]
    for i in range(na,nb): out[i] = "-"
    for i in range(nd,ne): out[i] = "-"
    out[width//2] = "|"
    out[nc] = "*"
    return ', '.join(["%2d" % SAMPLE.rank, word % SAMPLE.txt, fmt%c, fmt%(d-b),
                      ''.join(out), ', '.join([(fmt % x) for x in [a,b,c,d,e]])])

def different(x,y):
  "non-parametric effect size and significance test"
  return _cliffsDelta(x,y) and _bootstrap(x,y)

def _cliffsDelta(x, y, effectSize=0.2):
  """non-parametric effect size. threshold is border between small=.11 and medium=.28 
     from Table1 of  https://doi.org/10.3102/10769986025002101"""
  #if len(x) > 10*len(y) : return cliffsDelta(random.choices(x,10*len(y)),y)
  #if len(y) > 10*len(x) : return cliffsDelta(x, random.choices(y,10*len(x)))
  n,lt,gt = 0,0,0
  for x1 in x:
    for y1 in y:
      n += 1
      if x1 > y1: gt += 1
      if x1 < y1: lt += 1
  return abs(lt - gt)/n  > effectSize # true if different

def _bootstrap(y0,z0,confidence=.05,Experiments=512,):
  """non-parametric significance test From Introduction to Bootstrap, 
     Efron and Tibshirani, 1993, chapter 20. https://doi.org/10.1201/9780429246593"""
  obs = lambda x,y: abs(x.mu-y.mu) / ((x.sd**2/x.n + y.sd**2/y.n)**.5 + 1E-30)
  x, y, z = SAMPLE(y0+z0), SAMPLE(y0), SAMPLE(z0)
  d = obs(y,z)
  yhat = [y1 - y.mu + x.mu for y1 in y0]
  zhat = [z1 - z.mu + x.mu for z1 in z0]
  n      = 0
  for _ in range(Experiments):
    ySAMPLE = SAMPLE(random.choices(yhat,k=len(yhat)))
    zSAMPLE = SAMPLE(random.choices(zhat,k=len(zhat)))
    if obs(ySAMPLE, zSAMPLE) > d:
      n += 1
  return n / Experiments < confidence # true if different

def sk(SAMPLEs):
  "sort SAMPLEs on median. give adjacent SAMPLEs the same rank if they are statistically the same"
  def sk1(SAMPLEs, rank,lvl=1):
    all = lambda lst:  [x for SAMPLE in lst for x in SAMPLE.has]
    b4, cut = SAMPLE(all(SAMPLEs)) ,None
    max =  -1
    for i in range(1,len(SAMPLEs)):  
      lhs = SAMPLE(all(SAMPLEs[:i])); 
      rhs = SAMPLE(all(SAMPLEs[i:])); 
      tmp = (lhs.n*abs(lhs.mid() - b4.mid()) + rhs.n*abs(rhs.mid() - b4.mid()))/b4.n 
      if tmp > max:
         max,cut = tmp,i 
    if cut and different( all(SAMPLEs[:cut]), all(SAMPLEs[cut:])): 
      rank = sk1(SAMPLEs[:cut], rank, lvl+1) + 1
      rank = sk1(SAMPLEs[cut:], rank, lvl+1)
    else:
      for SAMPLE in SAMPLEs: SAMPLE.rank = rank
    return rank
  #------------ 
  SAMPLEs = sorted(SAMPLEs, key=lambda SAMPLE:SAMPLE.mid())
  sk1(SAMPLEs,0)
  return SAMPLEs

def egSlurp():
  eg0(slurp("stats.txt"))

def eg0(SAMPLEs):
  all = SAMPLE([x for SAMPLE in SAMPLEs for x in SAMPLE.has])
  [print(all.bar(SAMPLE,width=40,word="%4s", fmt="%5.2f")) for SAMPLE in sk(SAMPLEs)] 
    
def eg1():
  x=1
  print("inc","\tcd","\tboot","\tc+b", "\tsd/3")
  while x<1.5:
    a1 = [random.gauss(10,3) for x in range(20)]
    a2 = [y*x for y in a1]
    n1=SAMPLE(a1)
    n2=SAMPLE(a2)
    n12=SAMPLE(a1+a2)
    t1=_cliffsDelta(a1,a2)
    t2= _bootstrap(a1,a2)
    t3= abs(n1.mu-n2.mu) > n12.sd/3
    print(round(x,3),t1, t2,t1 and t2, t3, sep="\t")
    x *= 1.02
  
def eg2(n=5):
  eg0([SAMPLE([0.34, 0.49 ,0.51, 0.6]*n,   "x1"),
        SAMPLE([0.6  ,0.7 , 0.8 , 0.89]*n,  "x2"),
        SAMPLE([0.13 ,0.23, 0.38 , 0.38]*n, "x3"),
        SAMPLE([0.6  ,0.7,  0.8 , 0.9]*n,   "x4"),
        SAMPLE([0.1  ,0.2,  0.3 , 0.4]*n,   "x5")])
  
def eg3():
  eg0([SAMPLE([0.32,  0.45,  0.50,  0.5,  0.55],"one"),
        SAMPLE([ 0.76,  0.90,  0.95,  0.99,  0.995],"two")])

def eg4(n=5):
  eg0([
        SAMPLE([0.34, 0.49 ,0.51, 0.6]*n,   "x1"),
        SAMPLE([0.35, 0.52 ,0.63, 0.8]*n,   "x2"),
        SAMPLE([0.13 ,0.23, 0.38 , 0.38]*n, "x4"),
        ])
 

if __name__ == "__main__":
  random.seed(1)
  eg1()
  #[print("\n",f()) for f in [eg1,eg2,eg3,eg4]]
