# set up details
import re, ast, sys, math, random
from fileinput import FileInput as file_or_stdin
from collections import Counter

class the:
   "place to store settings"
   m=2              # in naive bayes, handle low frequency classes
   k=1              # in naive bayes, handle low frequency attribute values
   best=0.5         # in smo, the n**best items are "best"      
   upper=0.8        # in smo, after sorting examples, keep top 80%
   budget0=4        # in smo, initially label 4 examples 
   budget1=20       # in smo, label at most another 20 examples
   p=2              # in distance calcs, use a Euclidean distance measure    
   seed=1234567891  # random number seed

random.seed(the.seed)
tiny= sys.float_info.min 

# Meta-knowledge about the text of column headers
def isNum(s):     return s[0].isupper()           # numeric columns start with upper case
def isGoal(s):    return s[-1] in "+-!"           # goal column end in extra characters.
def isHeaven(s):  return 0 if s[-1] == "-" else 1 # "-" denotes goals to minimize
def isIgnored(s): return s[-1] == "X"             # we should skip columns ending with "X"

def coerce(s):
  try: return ast.literal_eval(s)
  except Exception: return s

def csv(file=None):
  with file_or_stdin(file) as src:
    for line in src:
      line = re.sub(r'([\n\t\r"\’ ]|#.*)', '', line)
      if line: yield [coerce(s.strip()) for s in line.split(",")]

class EG:
  def smo(): 
    best,evals = DATA(csv(the.file)).smo()
    print("smo", evals, best)

  def sway(): 
    _,_,evals,best = DATA(csv(the.file)).sway()
    print("sway", evals, best)

  def sway3(): 
    _,_,evals,best = DATA(csv(the.file)).sway3()
    print("sway3", evals, best)

class SYM:
  "Place to summarize a stream of symbols"
  def __init__(self,txt=" ",at=0):
    self.txt, self.at, self.n = txt, at, 0
    self.has = Counter()

  def add(self,x): self.has[x] += 1

  def dist(self,x,y):
    return 1 if x=="?" and y=="?" else (0 if x==y else 1)     

  def like(self,x,m,prior): 
    return (self.has.get(x, 0) + m*prior) / (self.n + m)

class NUM:
  "Place to summarize a stream of numbers"
  def __init__(self, txt=" ",at=0):
   self.txt, self.at, self.n = txt, at, 0
   self.mu, self.m2, self.sd = 0,0,0
   self.heaven, self.lo, self.hi = isHeaven(txt), sys.maxsize, -sys.maxsize

  def add(self,x):
    "Incrementally update lo,hi, mu, and sd"
    if x !="?":
      self.lo  = min(x, self.lo)
      self.hi  = max(x, self.hi)
      self.n  += 1
      delta    = x - self.mu
      self.mu += delta / self.n
      self.m2 += delta * (x -  self.mu)
      self.sd  = 0 if self.n < 2 else (self.m2 / (self.n - 1))**.5

  def norm(self,x):
    "Return x normalized 0..1, min..max"
    return x=="?" and x or (x - self.lo) / (self.hi - self.lo + tiny)

  def dist(self,x,y):
    "Return distance between two numbers"
    if x=="?" and y=="?" : return 1 
    x, y = self.norm(x), self.norm(y) 
    if x=="?" : x= 1 if y<.5 else 0
    if y=="?" : y= 1 if x<.5 else 0 
    return abs(x-y) 

  def like(self,x,*_):
    "Return likelihood of x belong to this distribution"
    v     = self.sd**2 + tiny
    nom   = math.e**(-1*(x - self.mu)**2/(2*v)) + tiny
    denom = (2*math.pi*v)**.5
    return min(1, nom/(denom + tiny))

class DATA:
  "Place to hold rows, summarized in the column headers (self.cols)"
  def __init__(self, headerAndRows=[], order=False):
    self.names,*rows = list(headerAndRows) 
    self.rows = []
    self.cols = [(NUM(s) if isNum(s) else SYM(s)) for s in self.names] 
    self.ys   = [c for c in self.cols if isGoal(c.txt)]
    self.xs   = [c for c in self.cols if not isGoal(c.txt) and not isIgnored(c.txt)]
    [self.add(row) for row in rows] 
    if order: self.ordered()

  def add(self,row): 
    "Add row to self. Summarize the row in the column headers"
    self.rows += [row] 
    [col.add(x) for x,col in zip(row,self.cols) if x != "?"]

  def clone(self, rows=[], order=False):
    "Return a new DATA with the same structure as self"
    return DATA([self.names] + rows, order=order)

  def d2h(self,row):
    "Return Y-distance from row to best Y values"
    nom = sum(abs(col.heaven - col.norm(row[n]))**2 for n,col in self.ys.items())
    return (nom / len(self.ys))**.5
  
  def ordered(self):
    "Sort rows by distance to heaven"
    self.rows = sorted(self.rows, key = self.d2h)

  def dist(self, row1, row2):
    "Return X-distance row1 to row2, normalized to 0..1"
    d = sum(col.dist(row1[col.at], row2[col.at])**the.p for col in self.cols.y)
    return (d/len(self.cols.y))**(1/the.p) 

  def near(self, row1, rows=None):
    "Return all rows, sorted by their distance to row1"
    return sorted(rows or self.rows, key=lambda row2: self.dist(row1,row2))

  def loglike(self,row,nall,nh,m=1,k=2):
    "Return log likelihood of row belonging to this data"
    prior = (len(self.rows) + k) / (nall + k*nh)
    tmp   = [col.like(row[col.at], m, prior)  for col in self.cols.x if row[col.at] != "?"]
    return sum(math.log(x) for x in tmp + [prior])

  def smo(self, score=lambda B,R: 2*B-R, fun=None):
    "Predictive modeling to predict if a new example is 'best' or 'rest'"
    def like(row,data):
      "Return log likelihood of row belonging to data"
      return data.loglike(row, len(data.rows), 2, the.m, the.k)
    def acquire(best, rest, rows):
      "Sort rows best to rest, keep the first (say) 80%"
      chop = int(len(rows) * the.upper)
      return sorted(rows, key=lambda r: -score(like(r,best),like(r,rest)))[:chop]
    #------------------------
    random.shuffle(self.rows)
    done, todo = self.rows[:the.budget0], self.rows[the.budget0:]
    data1 = self.clone(done, order=True)
    for i in range(the.budget1):
      if len(todo) < 3: break
      n = int(len(done)**the.best + .5)
      top,*todo = acquire(self.clone(data1.rows[:n]),
                          self.clone(data1.rows[n:]),
                          todo)
      done.append(top)
      data1 = self.clone(done, order=True)
    return data1.rows[0],len(data1.rows)

  def far(self, rows, sortp=False, last=None):
    "Find two distant examples"
    n     = int(len(rows) * the.Far)
    left  = last or self.near(random.choice(rows),rows)[n]
    right = self.near(left,rows)[n]
    if sortp and self.d2h(right) < self.d2h(left): left,right = right,left
    return left, right 
    
  def half(self, rows, sortp=False, last=None):
    "Divide data by distance to two distant examples"
    def dist(r1,r2): return self.dist(r1, r2)
    def proj(row)  : return (dist(row,left)**2 + C**2 - dist(row,right)**2)/(2*C)
    left,right = self.far(random.choices(rows, k=min(the.Half, len(rows))),
                          sortp=sortp, last=last)
    lefts,rights,C = [],[], dist(left,right)
    for n,row in enumerate(sorted(rows, key=proj)):  
      (lefts if n < len(rows)/2 else rights).append(row)
    return lefts, rights, left

  def sway(self, rows=None, stop=None, rest=None, evals=1, last=None):
    "Recursively divide data in two, recurse into best half"
    rows = rows or self.rows
    stop = stop or 2*len(rows)**the.Min
    rest = rest or []
    if len(rows) > stop:
      lefts,rights,left  = self.half(rows, True, last)
      return self.sway(lefts, stop, rest+rights, evals+1, left)
    else:
      return rows, rest, evals, last

  def sway3(self):
    "Call SWAY twice, once down to 50, then again down to 4"
    random.shuffle(self.rows); 
    rows1, rest1, evals1, __   = self.sway(self.rows,50) 
    rows2, rest2, evals2, last = self.sway(rows1,4)
    return  rows2, rest1+rest2, evals1 + evals2 + 3, last
