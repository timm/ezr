#!/usr/bin/env python3 -B
from __future__ import annotations
import sys, math,random
#import ezr 
#from ezr import adds,NUM,coerce,mid,div

R=random.random
 
class Some:
    def __init__(i, inits=[], txt="", max=512): 
      i.txt,i.max=txt,max
      i.lo, i.hi = 1E30, -1E30
      i.rank,i.n,i._has,i.ok = 0,0,[],True
      i.adds(inits)  

    def __repr__(i): 
      return  'Some(' + str(dict(
                txt=i.txt,rank="i.rank",n=i.n, all=len(i._has), ok=i.ok)) + ")"

    def adds(i,a): 
      for b in a:
        if   isinstance(b,(list,tuple)): [i.adds(c) for c in b] 
        #elif callable(b):                [i.adds(c) for c in b()]
        elif isinstance(b,Some):         [i.add(c) for c in b._has]
        else: i.add(b) 

    def add(i,x):  
      i.n += 1
      i.lo = min(x,i.lo)
      i.hi = max(x,i.hi)
      now  = len(i._has)
      if   now < i.max   : i.ok=False; i._has += [x]
      elif R() <= now/i.n: i.ok=False; i._has[ int(R() * now) ]

    def __ne__(i,j:Some):
      return not i.cohen(j) and not i.cliffs(j) and not i.bootstrap(j)

    def has(i):
      if not i.ok: i._has.sort()
      i.ok=True
      return i._has

    def mid(i):
       l = i.has()
       return l[len(l)//2]

    def div(i):
       l = i.has()
       n = len(l)//10
       return ((l[-1] - l[0]) if n<10 else (l[int(9*n)] - l[int(1*n)]))/2.56

    def pooledSd(i,j:Some):
      sd1, sd2 = i.div(), j.div()
      return (((i.n - 1)*sd1 * sd1 + (j.n-1)*sd2 * sd2) / (i.n + j.n-2))**.5

    def norm(i, n):
      return (n-i.lo)/(i.hi - i.lo + 1E-30)

    def bar(i, some, fmt="%8.3f", word="%10s", width=50):
      has = some.has() 
      out = [' '] * width
      cap = lambda x: 1 if x > 1 else (0 if x<0 else x)
      pos = lambda x: int(width * cap(i.norm(x)))
      [a, b, c, d, e]  = [has[int(len(has)*x)] for x in [0.1,0.3,0.5,0.7,0.9]]
      [na,nb,nc,nd,ne] = [pos(x) for x in [a,b,c,d,e]] 
      for j in range(na,nb): out[j] = "-"
      for j in range(nd,ne): out[j] = "-"
      out[width//2] = "|"
      out[nc] = "*" 
      return ', '.join(["%2d" % some.rank, word % some.txt, fmt%c, fmt%(d-b),
                        ''.join(out),fmt%has[0],fmt%has[-1]])

    def delta(i,j:Some): 
      return abs(i.mid() - j.mid()) / ((i.div()**2/i.n + j.div()**2/j.n)**.5 + 1E-30)

    def cohen(i,j:Some):
      return abs( i.mid() - j.mid() ) < 0.35 * i.pooledSd(j)

    def cliffs(i,j:Some, dull=0.147):
      """non-parametric effect size. threshold is border between small=.11 and medium=.28 
      from Table1 of  https://doi.org/10.3102/10769986025002101"""
      n,lt,gt = 0,0,0
      for x1 in i.has():
        for y1 in j.has():
          n += 1
          if x1 > y1: gt += 1
          if x1 < y1: lt += 1
      return abs(lt - gt)/n  < dull # true if different

    def  bootstrap(i,j:Some,confidence=.05,samples=512,):
      """non-parametric significance test From Introduction to Bootstrap, 
        Efron and Tibshirani, 1993, chapter 20. https://doi.org/10.1201/9780429246593"""
      y0,z0  = i.has(), j.has()
      x,y,z  = Some(inits=y0+z0), Some(inits=y0), Some(inits=z0)
      delta0 = y.delta(z)
      yhat   = [y1 - y.mid() + x.mid() for y1 in y0]
      zhat   = [z1 - z.mid() + x.mid() for z1 in z0] 
      pull  = lambda l:Some(random.choices(l, k=len(l))) 
      n      = sum(pull(yhat).delta(pull(zhat)) > delta0 for _ in range(samples)) 
      return n / samples >= confidence # true if different

def sk(somes):
  "sort nums on mid. give adjacent nums the same rank if they are statistically the same"
  def sk1(somes, rank, cut=None):
    most, b4 = -1, Some(somes)
    for j in range(1,len(somes)):
      lhs = Some(somes[:j])
      rhs = Some(somes[j:])
      tmp = (lhs.n*abs(lhs.mid() - b4.mid()) + rhs.n*abs(rhs.mid() - b4.mid())) / b4.n
      if tmp > most:
         most,cut = tmp,j
    if cut and Some(somes[:cut]) != Some(somes[cut:]):
      rank = sk1(somes[:cut], rank) + 1
      rank = sk1(somes[cut:], rank)
    else:
      for some in somes: some.rank = rank
    return rank
  #------------ 
  somes = sorted(somes, key=lambda some: some.mid()) #lambda some : some.mid())
  sk1(somes,0)
  return somes

def file2somes(file):
  def asNum(s):
    try: return float(s)
    except Exception: return s
  #-------------------------
  somes=[]
  with open(file) as fp: 
    for word in [asNum(x) for s in fp.readlines() for x in s.split()]:
      if isinstance(word,str): some = Some(txt=word); somes.append(some)
      else                   : some.add(word)    
  return somes

def bars(somes, width=40):
  all = Some(somes)
  last = None
  for some in sk(some):
    if some.rank != last: print("#")
    last=some.rank
    print(all.bar(some.has(), width=width, word="%20s", fmt="%5.2f"))

#--------------------------------------------
def normal(mu,sd):
  return mu+sd*math.sqrt(-2*math.log(R())) * math.cos(2*math.pi*R())

def eg0(somes):
  all = Some(somes)
  last = None
  for some in sk(somes):
    if some.rank != last: print("#")
    last=some.rank
    print(all.bar(some,width=40,word="%20s", fmt="%5.2f"))

class eg:
  def basic(): 
    s=Some([x for x in range(100)])
    print(s.mid(), s.div(), s)

  def errors():
    for k in [32,64,128,256,512,1024, 2048]:
      print("")
      for n in [10,100,1_000,10_000,100_000]:
        s=Some([normal(10,2) for x in range(n)],max=k)
        print([round(x,3) for x in [100*(s.mid()-10)/10, 100*(s.div()-2)/2]],k,n)

  def file2somes():
    [print(x) for x in file2somes("../data/stats.txt")]

  def rand():
    l=[10,20,30,40]
    s=lambda lst:Some(random.choices(lst, k=len(lst)))
    print(s(l)._has)
    
  def eg1():
    print("inc","\tcd","\tboot","\tc+b", "\tsd/3")
    x=1
    while x<1.5:
      a1 = [random.gauss(10,3) for x in range(20)]
      a2 = [y*x for y in a1]
      s1 = Some(a1)
      s2 = Some(a2)  
      s12= Some(a1+a2)
      t1 = s1.cliffs(s2) 
      t2 = s1.bootstrap(s2) 
      t3= abs(s1.mid()-s2.mid()) < s12.div()/3
      print(round(x,3),t1, t2,t1 and t2, t3, sep="\t")
      x *= 1.02
    
  def eg2(n=5):
    eg0([ Some([0.34, 0.49 ,0.51, 0.6]*n,   txt="x1"),
          Some([0.6  ,0.7 , 0.8 , 0.89]*n,  txt="x2"),
          Some([0.13 ,0.23, 0.38 , 0.48]*n, txt="x3"),
          Some([0.6  ,0.7,  0.8 , 0.9]*n,   txt="x4"),
          Some([0.1  ,0.2,  0.3 , 0.4]*n,   txt="x5")])
    
  def eg3():
    eg0([ Some([0.32,  0.45,  0.50,  0.5,  0.55],    "one"),
          Some([ 0.76,  0.90,  0.95,  0.99,  0.995], "two")])

  def eg4(n=20):
    eg0([ Some([0.24, 0.25 ,0.26, 0.29]*n,   "x1"),
          Some([0.35, 0.52 ,0.63, 0.8]*n,   "x2"),
          Some([0.13 ,0.23, 0.38 , 0.48]*n, "x3"),
          ])

if __name__ == "__main__": 
  random.seed(1234567891)
  getattr(eg,sys.argv[1])()
