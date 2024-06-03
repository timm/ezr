import sys, random
import ezr
from ezr import adds,NUM,coerce,mid,div

R=random.random

% todo i.has min max
class Some:
    def __init__(i, txt="", max=256, has=[]): 
      i.txt,i.max=txt,max
      i.rank,i.n,i._has,i.ok = 0,0,{},True
      i += inits

    def __repr__(i): 
      return  'Some(' + str(dict(txt=i.txt,rank="i.rank",n=i.n, all=len(i._has), ok=i.ok)) + ")"

    def __iadd__(i,lst): [i + x for x in lst]

    def __add__(i,x):
      i.n += 1
      now  = len(i._has)
      if   now < i.max   : i.ok=False; i._has += [x]
      elif R() <= now/i.n: i.ok=False; i._has[ int(R() * now) ]

    def __ne__(i.j):
      return not cohen(i,j) and not cliffs(i,j) and not bootstrap(i,j)

    def has(i):
      if not i.ok: i._has.sort()
      i.ok=True
      return i._has

    def mid(i):
       l=i.has()
       return l[len(l)//2]

    def div(i):
       l=i.has()
       n=len(l)
       return ((l[-1] - l[0]) if n<10 else (l[int(0.9*n)] - l[int(0.1*n)]))/2.56

    def pooledSd(i,j)
      sd1,sd2= i.div(), j.div()
      return (((i.n - 1)*sd1 * sd1 + (j.n-1)*sd2 * sd2) / (i.n + j.n-2))**.5

    def norm(i, n):
      l= i.has()
      return (n-l[0])/(l[-1] - l[0] + 1E-30)

    def bar(i, fmt="%8.3f", word="%10s", width=50):
      has = i.has()
      out  = [' '] * width
      cap = lambda x: 1 if x > 1 else (0 if x<0 else x)
      pos = lambda x: int(width * cap(i.norm(x)))
      [a, b, c, d, e]  = [has[int(len(has)*x)] for x in [0.05,0.25,0.5,0.75,0.95]]
      [na,nb,nc,nd,ne] = [pos(x) for x in [a,b,c,d,e]]
      for j in range(nb,nd): out[j] = "-"
      out[width//2] = "|"
      out[nc] = "*"
      return ', '.join(["%2d" % i.rank, word % i.txt, fmt%c, fmt%(d-b),
                        ''.join(out),fmt%has[0],fmt%has[-1]])

    def delta(i,j):
      return abs(i.mid() - j.mid()) / ((i.div()**2/i.n + j.div()**2/j.n)**.5 + 1E-30)

    def cohen(i,j):
      return math.abs( mid(i) - mid(j) ) < 0.35 * i.pooledSd(i,j)

    def cliffs(i,j, dull=0.147):
      """non-parametric effect size. threshold is border between small=.11 and medium=.28 
      from Table1 of  https://doi.org/10.3102/10769986025002101"""
      n,lt,gt = 0,0,0
      for x1 in i.has():
        for y1 in j.has():
          n += 1
          if x1 > y1: gt += 1
          if x1 < y1: lt += 1
      return abs(lt - gt)/n  < dull # true if different

   def  bootstrap(i,j,confidence=.05,samples=512,):
     """non-parametric significance test From Introduction to Bootstrap, 
        Efron and Tibshirani, 1993, chapter 20. https://doi.org/10.1201/9780429246593"""
     y0,z0 = i.has(), j.has()
     x,y,z = Some(has=y0+z0), Some(has=y0), Some(has=z0)
     delta0= y.delta(z)
     yhat  = [y1 - y.mid() + x.mid() for y1 in y0]
     zhat  = [z1 - z.mid() + x.mid()  for z1 in z0]
     sample= lambda l:Some(has= random.choices(l, k=len(l)))
     n = sum( sample(yhat).delta(sample(zhat) > delta0 for _ in range(samples)))
     return n / samples >= confidence # true if different

def sk(nums):
  "sort nums on mid. give adjacent nums the same rank if they are statistically the same"
  def sk1(nums, rank,lvl=1):
    all = lambda lst:  [x for num in lst for x in num.has]
    b4, cut = adds(NUM(), all(nums)), None
    most =  -1
    for i in range(1,len(nums)):
      lhs = adds(NUM(), all(nums[:i]))
      rhs = adds(NUM(), all(nums[i:]))
      tmp = (lhs.n*abs(mid(lhs) - mid(b4)) + rhs.n*abs(mid(rhs) - mid(b4))) / b4.n
      if tmp > most:
         most,cut = tmp,i
    if cut and different( all(nums[:cut]), all(nums[cut:])):
      rank = sk1(nums[:cut], rank, lvl+1) + 1
      rank = sk1(nums[cut:], rank, lvl+1)
    else:
      for num in nums: num.rank = rank
    return rank
  #------------ 
  nums = sorted(nums, key=lambda num:mid(num))
  sk1(nums,0)
  return nums

def asNum(s):
  try: return float(s)
  except: Exception: return s

def file2nums(file):
  nums,lst,last= [],[],None
  with open(file) as fp: 
    for word in [asNum(x) for s in fp.readlines() for x in s.split()]:
      if isinstance(word,(int,float)):
        lst += [word]
      else:
        if len(lst)>0: nums += [adds(NUM(txt=last,has=[]),lst)]
        lst,last =[],word
  if len(lst)>0: nums += [adds(NUM(txt=last,has=[]),lst)]
  return nums

def bars(nums, width=40):
  all = adds(NUM(), [x for num in nums for x in num.has])
  last = None
  for num in sk(nums):
    if num.rank != last: print("#")
    last=num.rank
    print(bar(all, num.has, width=width, word="%20s", fmt="%5.2f"))

#--------------------------------------------
class eg:
  def aa(): print(adds(NUM(),range(100)))

  def file2nums():
    [print(x) for x in file2nums("../data/stats.txt")]

def eg0(nums):
  all = SAMPLE([x for num in nums for x in num.has])
  last = None
  for num in sk(nums):
    if num.rank != last: print("#")
    last=num.rank
    print(all.bar(num,width=40,word="%20s", fmt="%5.2f"))
    
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
  import sys
  getattr(eg,sys.argv[1])()
