# vim : set et ts=2 sw=2 :
from fileinput import FileInput as file_or_stdin
import random,math,sys,ast,re
#----------------------------------------------------------------------------------------
huge = sys.maxsize
tiny = 1 / huge

class obj:
  def __init__(i,**d): i.__dict__.update(d)
  def __repr__(i)    : return i.__class__.__name__ +str(i.__dict__)
  def adds(i,lst): [i.add(x) for x in lst]; return i 

the = obj(bins=8,
          seed=31210,
          stop=1,
          better = .5,
          file="../data/auto93.csv")
#----------------------------------------------------------------------------------------
class COL(obj):
  def make(txt=" ",at=""):  
    return (NUM if txt[0].isupper() else SYM)(txt=txt,at=at)

  def __init__(i,txt=" ",at=0):
    i.n = 0; i.at = at; i.txt = txt
    i.heaven = -1 if txt[-1] == "-" else 1
    i.isGoal = txt[-1] in "+-!"

  def add(i,x):
    if x != "?": i.n += 1; i.add1(x)
    return x

  def bins(i,goal,rowss):
    return i.bins1(goal, sorted([(row[i.at], klass) 
                                 for klass,rows in rowss.items() 
                                 for row in rows if row[i.at] != "?"]))
#----------------------------------------------------------------------------------------
class SYM(COL):
  def __init__(i,**kw): super().__init__(**kw); i.has = {}
  def add1(i,x):   i.has[x] = 1 + i.has.get(x,0)
  def norm(i,x): return x
  def mode(i) : return max(i.has, key=i.has.get)
  def ent(i)  : return ent(i.has)
  def bins1(i,goal,xys):
    c={}
    for x,y in xys:  
      c[x] = c.get(x,{})
      c[x][y] = c[x].get(y,0) + 1
    return sorted([(ent(c[x]),eq,x,i.at) for x in c])[0] 
#----------------------------------------------------------------------------------------
class NUM(COL):
  def __init__(i,**kw):
    super().__init__(**kw)
    i.mu,i.m2,i.sd,i.lo,i.hi = 0,0,0, huge, -1* huge

  def add1(i,x): 
    i.lo  = min(x,i.lo)
    i.hi  = max(x,i.hi)
    delta = x - i.mu
    i.mu += delta / i.n
    i.m2 += delta * (x -  i.mu)
    i.sd  = 0 if i.n < 2 else (i.m2 / (i.n - 1))**.5

  def norm(i,x): return x=="?" and x or (x - i.lo) / (i.hi - i.lo + tiny)

  def bins1(i,goal,xys):
    n1,n2,c1,c2 = 0,len(xys),{},{}
    for x,y in xys:   
      c2[y] = c2.get(y,0) + 1
    small,min = len(xys)**.5, ent(c2) 
    for n,(x,y) in enumerate(xys):
      n2    -= 1; n1 += 1
      c2[y] -= 1; c1[y] = c1.get(y,0) + 1
      if n1>small and n2>small and x!=xys[n+1][0]:
        e=(n1*ent(c1) + n2*ent(c2))/(n1+n2)
        if e < min:
          min,cut = e,x 
    return (min,le,cut,i.at)
#----------------------------------------------------------------------------------------
class DATA(obj):
  def __init__(i,src=[],order=False): 
    i.rows, i.cols = [],[]
    i.adds(src) 
    if order: i.ordered()
    
  def ordered(i): i.rows = sorted(i.rows, key=i.d2h)

  def add(i,row): 
    if i.cols:
      i.rows += [[col.add(x) for x,col in zip(row,i.cols)]]
    else:
      i.cols = [COL.make(txt=s,at=n) for n,s in enumerate(row)] 
      i.ys   = {col.at:col for col in i.cols if col.isGoal}

  def clone(i, rows=[], order=False):
    return DATA([[col.txt for col in i.cols]] + rows, order=order)

  def d2h(i,row):
    n,d=0,0
    for col in i.ys.values():
      d += abs(col.norm(row[col.at]) - col.heaven)**2
      n += 1
    return (d/n)**.5

  def bins(i):
    i.ordered() 
    n = int(.5 + len(i.rows)**the.better)
    return sorted([col.bin("best",best=d.rows[:n],rest=d.rows[n:]) 
                  for col in i.cols if not col.isGoal])
  
  # def tree(i,rows,stop,path,out): 
  #   rows = rows or i.rows
  #   if len(rows) < stop or the.stop: 
  #     path.append(([True] + deepcopy(path))[::-1])
  #   else:
  #     _,how,x,at = i.bins()[0]
  #     left,right=[],[]
  #     for row in rows:
  #       (left if how(x,at,row) else right).append(row)
  #     for sub in i.tree(left,stop):
  #       yield ((how,i.tree,x,at), sub, True)
  #       yield ((how,i.tree,x,at), sub, False)
#----------------------------------------------------- 
def le(x,at,row): tmp=row[at]; return tmp =="?" or tmp <= x
def eq(x,at,row): tmp=row[at]; return tmp =="?" or tmp == x

def ent(d):
  n = sum(d.values())
  return - sum(v/n*math.log(v/n,2) for v in d.values() if v>0)

def coerce(s):
  try: return ast.literal_eval(s)
  except Exception: return s

def csv(file=None):
  with file_or_stdin(file) as src:
    for line in src:
      line = re.sub(r'([\n\t\r"\’ ]|#.*)', '', line)
      if line: yield [coerce(s.strip()) for s in line.split(",")]
#-----------------------------------------------------      
class Eg: 
  def all():
    sys.exit(sum(1 if getattr(Eg,s)()==False else 0 
                 for s in dir(Eg) if s[0] !="_" and s !="all"))
    
  def num():  
    assert 6.61  < NUM().adds([x**.5 for x in range(100)]).mu  < 6.62
    assert 13.31 < NUM().adds([46,	69	,32,	60,	52	,41]).sd < 13.32

  def sym():
    s = SYM().adds([1,1,1,1,2,2,3])
    assert 1.37 < s.ent() < 1.38
    assert s.mode() == 1 

  def col():
    print(COL.make(txt="Speed"))

  def data():
    d=DATA(csv(the.file)) 
  
  def order():
    d=DATA(csv(the.file),order=True) 
    for n,row in enumerate(d.rows):
      if n % 20 ==0: print(">",row)

  def bins():
    d=DATA(csv(the.file),order=True) 
    n = int(.5 + len(d.rows)**.5)
    for col in d.cols:
      if not col.isGoal:
        print("")
        print(col.at,col.txt)
        for x in col.bins("best",dict(best=d.rows[:n], rest=d.rows[n:])):
          print("\t",x) 
       

#----------------------------------------------------------------------------------------
if __name__ == "__main__" and len(sys.argv)>1:
  random.seed(the.seed)
  getattr(Eg, sys.argv[1], Eg.all)() 