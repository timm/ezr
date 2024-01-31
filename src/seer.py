# vim : set et ts=2 sw=2 :
"""
seer: look around
(c) 2023, Tim Menzies, <timm@ieee.org>, BSD-2  
  
USAGE:    
python3 seer.py [OPTIONS]   
  
OPTIONS:  

     -b --budget0     initial evals                   = 4  
     -B --Budget      subsequent evals                = 6   
     -c --cohen       small effect size               = .35  
     -c --confidence  statistical confidence          = .05
     -e --effectSize  non-parametric small delta      = 0.2385
     -E --Experiments number of Bootstraps            = 512
     -f --file        csv data file name              = '../data/auto93.csv'  
     -h --help        print help                      = false
     -k --k           low class frequency kludge      = 1  
     -m --m           low attribute frequency kludge  = 2  
     -s --seed        random number seed              = 31210   
     -t --todo        start up action                 = 'help'   
     -T --Top         best section                    = .5   
"""

import re,sys,ast,math,random
from collections import Counter
from fileinput import FileInput as file_or_stdin
from stats import NUM,sk

#----------------------------------------------------------------------------------------
def strOfGoal(s):   return s[-1] in "+-!"
def strOfHeaven(s): return 0 if s[-1] == "-" else 1
def strOfNum(s):    return s[0].isupper() 
def colOfSym(x):    return isinstance(x,Counter)

#----------------------------------------------------------------------------------------
class struct:
  def __init__(self,**d) : self.__dict__.update(d)
  __repr__ = lambda self: o(self.__dict__, self.__class__.__name__)

class NUM(struct):
  def __init__(self,lst,txt=" ",rank=0):
   self.txt, self.rank, self.n, self.mu, self.m2, self.has = txt,rank,0,0,0,sorted(lst)
   for x in lst:
     self.n += 1
     delta = x - self.mu
     self.mu += delta / self.n
     self.m2 += delta * (x -  self.mu)
   self.heaven = 0 if txt[-1] == "-" else 1
   if len(lst) > 1: self.sd = (self.m2 / (self.n - 1))**.5

  def d(self,x):
    if x=="?": return x
    tmp = (self.heaven==0 and (self.mu-x) or (x-self.mu))/(self.sd*the.cohen)
    return 0 if -1 <= tmp and tmp <= 1 else tmp 

  def norm(self,x):
    return x=="?" and x or (x - self.has[0]) / (self.has[-1] - self.has[0])
  
  def d2h(self,x):
     return abs(self.heaven - self.norm(x))
#----------------------------------------------------------------------------------------
class COLS(struct):
  def __init__(self,names,rows):
    self.names= names
    rotated  = [[y for y in x if y !="?"] for x in zip(*rows)]
    self.all = [(NUM if strOfNum(s) else Counter)(lst) for s,lst in zip(names,rotated)]
    self.ys  = {n:c for n,(s,c) in enumerate(zip(self.names,self.all)) if strOfGoal(s)}

#----------------------------------------------------------------------------------------
class DATA(struct):
  def __init__(self, lsts, order=False):
    names,*rows = list(lsts)
    self.cols = COLS(names,rows)
    self.rows = sorted(rows, key=lambda row:self.d2h(row)) if order else rows

  def mid(self): 
    return [max(col,key=col.get) if colOfSym(col) else col.mu 
            for col in enumerate(self.cols.all)] 
  
  def clone(self, rows=[], order=False):
    return DATA([self.cols.names] + rows, order=order)  

  def d2h(self,lst):  
    ys = self.cols.ys
    return (sum(col.d2h(lst[n]))**2 for n,col in ys.items()) / len(ys))**.5 

  def like(self,row,nall,nh,m=1,k=2):
    def num(col,x):
      v = col.sd**2 + 10**-64
      nom = math.e**(-1*(x - col.mu)**2/(2*v)) + 10**-64
      denom = (2*math.pi*v)**.5
      return min(1, nom/(denom + 10**-64))
    def sym(col,x):
      return (col.get(x, 0) + m*prior) / (len(self.rows) + m)
    #------------------------------------------
    prior = (len(self.rows) + k) / (nall + k*nh)
    out   = math.log(prior)
    for c,x in slots(row):
      if x != "?" and c not in self.cols.ys:
        col  = self.cols.all[c]
        inc  = (sym if colOfSym(col) else num)(col, x) 
        out += math.log(inc)
    return out

  def smo(self,fun=None):  
    done, todo = self.rows[:the.budget0], self.rows[the.budget0:]
    for i in range(the.Budget):
      data1 = self.clone(done, order=True)
      n = int(len(done)**the.Top + .5)
      j = smo1(i+the.budget0,
                  self.clone(data1.rows[:n],order=True), 
                  self.clone(data1.rows[n:]),
                  len(self.rows),
                  todo,
                  fun) 
    done.append(todo.pop(j))

def smo1(i,best,rest,nall,rows,fun):
  todo,max,selected = 0,-1E300,[]
  for k,row in enumerate(rows):
    b = best.like(row,nall,2,the.m,the.k)
    r = rest.like(row,nall,2,the.m,the.k) 
    if b>r: selected.append(row)
    tmp = b - r 
    if tmp > max: todo,max = k,tmp  
  if fun: fun(i,best.rows[0])
  return todo

#----------------------------------------------------------------------------------------
class THE(struct):
  def __init__(self,txt):
    self._help = txt
    d = {m[1]:coerce(m[2]) for m in re.finditer(r"--(\w+)[^=]*=\s*(\S+)",txt)}
    self.__dict__.update(d)
    
  def cli(self):
    for k,v in self.__dict__.items(): 
      v = str(v)
      for c,arg in enumerate(sys.argv):
        after = "" if c >= len(sys.argv) - 1 else sys.argv[c+1]
        if arg in ["-"+k[0], "--"+k]: 
          v = "false" if v=="true" else ("true" if v=="false" else after)
          self.__dict__[k] = coerce(v)
          
#----------------------------------------------------------------------------------------
class Eg:
  _all = locals()
  def all():
    errors = [f() for s,f in Eg._all.items() if s[0] !="_" and s !="all"]
    sys.exit(sum(0 if x==None else x for x in errors))
    
  def nothing(): pass

  def help(): 
    print(__doc__);  

  def nums(): 
    print(NUM([x**.5 for x in range(100)]))
  
  def data():
    for i,row in enumerate(DATA(csv(the.file),order=True).rows):
       if i % 500 == 0 : print(i,row)

  def likes():
    d = DATA( csv(the.file),order=True)
    for i,row in enumerate(d.rows): 
      if i % 25 == 0: 
          print(i, rnds(d.d2h(row)),
                rnds(d.like(row, 1000, 2, m=the.m, k=the.k)))

  def smos():
    print(the.seed)
    d=DATA(csv(the.file),order=False) 
    print("names,",d.cols.names)
    print("base,", rnds(d.mid()),2); print("#")
    random.shuffle(d.rows) 
    d.smo(lambda i,top: print(f"step{i}, ",rnds(top,2)))
    print("#\nbest,",rnds(d.clone(d.rows,order=True).rows[0]),2)

#----------------------------------------------------------------------------------------
the = THE(__doc__)
if __name__ == "__main__":
  the.cli()
  random.seed(the.seed)
  getattr(Eg, the.todo,Eg.help)()
