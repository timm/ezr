import random
R=random.random

class o:
  __init__ = lambda i,**d : i.__dict__.update(d)
  __repr__ = lambda i     : i.__class__.__name__+"("+dict2str(i.__dict__)+")"

the = o(
  seed  = 1234567891, 
  round = 2,
  stats = o(cohen=0.35,
            cliffs=0.195, #border between small=.11 and medium=.28 
            bootstraps=512,
            confidence=0.05))

class SOME:
    "Non-parametric statistics using reservoir sampling."
    def __init__(i, inits=[], txt="", max=512): 
      "Start stats. Maybe initialized with `inits`. Keep no more than `max` numbers."
      i.txt,i.max,i.lo, i.hi  = txt,max, 1E30, -1E30
      i.rank,i.n,i._has,i.ok = 0,0,[],True
      i.adds(inits)  

    def __repr__(i): 
      "Print the reservoir sampling."
      return  'SOME('+str(dict(txt=i.txt,rank="i.rank",n=i.n,all=len(i.has()),ok=i.ok))+")"

    def adds(i,a):  
      "Handle multiple nests samples."
      for b in a:
        if   isinstance(b,(list,tuple)): [i.adds(c) for c in b]  
        elif isinstance(b,SOME):         [i.add(c) for c in b.has()]
        else: i.add(b) 

    def add(i,x):  
      i.n += 1
      i.lo = min(x,i.lo)
      i.hi = max(x,i.hi)
      now  = len(i._has)
      if   now < i.max   : i.ok=False; i._has += [x]
      elif R() <= now/i.n: i.ok=False; i._has[ int(R() * now) ]

    def __eq__(i,j):
      "True if all of cohen/cliffs/bootstrap say you are the same."
      return  i.cliffs(j) and i.bootstrap(j) ## ordered slowest to fastest

    def has(i) :
      "Return the numbers, sorted."
      if not i.ok: i._has.sort()
      i.ok=True
      return i._has

    def mid(i):
      "Return the middle of the distribution."
      l = i.has(); return l[len(l)//2]

    def div(i):
       "Return the deviance from the middle." 
       l = i.has(); return (l[9*len(l)//10] - l[len(l)//10])/2.56

    def pooledSd(i,j):
      "Return a measure of the combined standard deviation."
      sd1, sd2 = i.div(), j.div()
      return (((i.n - 1)*sd1 * sd1 + (j.n-1)*sd2 * sd2) / (i.n + j.n-2))**.5

    def norm(i, n):
      "Normalize `n` to the range 0..1 for min..max"
      return (n-i.lo)/(i.hi - i.lo + 1E-30)

    def bar(i, some, fmt="%8.3f", word="%-50s ", width=50):
      "Pretty print `some.has`."
      has = some.has() 
      out = [' '] * width
      cap = lambda x: 1 if x > 1 else (0 if x<0 else x)
      #pos = lambda x: int(width * cap(i.norm(x)))
      pos = lambda x: min(int(width * cap(i.norm(x))), width - 1)
      [a, b, c, d, e]  = [has[int(len(has)*x)] for x in [0.1,0.3,0.5,0.7,0.9]]
      [na,nb,nc,nd,ne] = [pos(x) for x in [a,b,c,d,e]] 
      for j in range(na,nb): out[j] = "-"
      for j in range(nd,ne): out[j] = "-"
      out[width//2] = "|"
      out[nc] = "*" 
      #return ', '.join(["%2d" % some.rank, word % some.txt, fmt%c, fmt%(d-b), ''.join(out)])
      return ', '.join(["%2d" % some.rank, some.txt.rjust(25," "), fmt%c, fmt%(d-b), ''.join(out),
                        ', '.join([fmt % x for x in 
                                      [a,b,c,d,e]])])

    def delta(i,j):
      "Report distance between two SOMEs, modulated in terms of the standard deviation."
      return abs(i.mid() - j.mid()) / ((i.div()**2/i.n + j.div()**2/j.n)**.5 + 1E-30)

    def cohen(i,j):
      return abs( i.mid() - j.mid() ) < the.stats.cohen * i.pooledSd(j)

    def cliffs(i,j, dull=None):
      """non-parametric effect size. threshold is border between small=.11 and medium=.28 
      from Table1 of  https://doi.org/10.3102/10769986025002101"""
      n,lt,gt = 0,0,0
      for x1 in i.has():
        for y1 in j.has():
          n += 1
          if x1 > y1: gt += 1
          if x1 < y1: lt += 1 
      return abs(lt - gt)/n  < (dull or the.stats.cliffs or 0.197)  

    def  bootstrap(i,j,confidence=None,bootstraps=None):
      """non-parametric significance test From Introduction to Bootstrap, 
        Efron and Tibshirani, 1993, chapter 20. https://doi.org/10.1201/9780429246593"""
      y0,z0  = i.has(), j.has()
      x,y,z  = SOME(inits=y0+z0), SOME(inits=y0), SOME(inits=z0)
      delta0 = y.delta(z)
      yhat   = [y1 - y.mid() + x.mid() for y1 in y0]
      zhat   = [z1 - z.mid() + x.mid() for z1 in z0] 
      pull   = lambda l:SOME(random.choices(l, k=len(l))) 
      samples= bootstraps or the.stats.bootstraps or 512
      n      = sum(pull(yhat).delta(pull(zhat)) > delta0  for _ in range(samples)) 
      return n / samples >= (confidence or the.stats.confidence or 0.05)

# ---------------------------------------------------------------------------------------
def sk(somes,epsilon=0.01):
  "Sort nums on mid. give adjacent nums the same rank if they are statistically the same"
  def sk1(somes, rank, cut=None):
    most, b4 = -1, SOME(somes)
    for j in range(1,len(somes)):
      lhs = SOME(somes[:j])
      rhs = SOME(somes[j:])
      tmp = (lhs.n*abs(lhs.mid() - b4.mid()) + rhs.n*abs(rhs.mid() - b4.mid())) / b4.n
      if tmp > most and (somes[j].mid() - somes[j-1].mid()) > epsilon:
         most,cut = tmp,j
    if cut:
      some1,some2 = SOME(somes[:cut]), SOME(somes[cut:])
      if True: #not some1.cohen(some2): # and abs(some1.div() - some2.div()) > 0.0001: 
        if some1 != some2:
          rank = sk1(somes[:cut], rank) + 1
          rank = sk1(somes[cut:], rank)
          return rank
    for some in somes: some.rank = rank
    return rank
  somes = sorted(somes, key=lambda some: some.mid()) #lambda some : some.mid())
  sk1(somes,0)
  return somes

def file2somes(file):
  "Reads text file into a list of `SOMEs`."
  def asNum(s):
    try: return float(s)
    except Exception: return s
  somes=[]
  with open(file) as fp: 
    for word in [asNum(x) for s in fp.readlines() for x in s.split()]:
      if isinstance(word,str): some = SOME(txt=word); somes.append(some)
      else                   : some.add(word)    
  return somes

def bars(somes, width=40,epsilon=0.01,fmt="%5.2f"):
  "Prints multiple `somes` on the same scale."
  all = SOME(somes)
  last = None
  for some in sk(some, epsilon):
    if some.rank != last: print("#")
    last=some.rank
    print(all.bar(some.has(), width=width, word="%20s", fmt=fmt))
 
def report(somes,epsilon=0.01,fmt="%5.2f"):
  all = SOME(somes)
  last = None
  #print(SOME(inits=[x for some in somes for x in some._has]).div()*the.stats.cohen)
  for some in sk(somes,epsilon):
    if some.rank != last: print("#")
    last=some.rank
    print(all.bar(some,width=40,word="%20s", fmt=fmt))

# ---------------------------------------------------------------------------------------
def some1(n=5):
  report([ SOME([0.34, 0.49 ,0.51, 0.6]*n,   txt="x1"),
        SOME([0.6  ,0.7 , 0.8 , 0.89]*n,  txt="x2"),
        SOME([0.09 ,0.22, 0.28 , 0.5]*n, txt="x3"),
        SOME([0.6  ,0.7,  0.8 , 0.9]*n,   txt="x4"),
        SOME([0.1  ,0.2,  0.3 , 0.4]*n,   txt="x5")])
  
def some2():
  report([ SOME([0.32,  0.45,  0.50,  0.5,  0.55],    "one"),
        SOME([ 0.76,  0.90,  0.95,  0.99,  0.995], "two")])

def some3(n=20):
  report([ SOME([0.24, 0.25 ,0.26, 0.29]*n,   "x1"),
        SOME([0.35, 0.52 ,0.63, 0.8]*n,   "x2"),
        SOME([0.13 ,0.23, 0.38 , 0.48]*n, "x3"),
        ])

if __name__ == "__main__": 
  for fun in [some1,  some2, some3]:
    print("\n# " + ("-" * 90))
    fun()
