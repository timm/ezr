# vim : set et ts=2 sw=2 :

from etc  import *
from easy import *
import easy

class Eg:
  _all = locals()
  def all():
    errors = [f() for s,f in Eg._all.items() if s[0] !="_" and s !="all"]
    sys.exit(sum(0 if x==None else x for x in errors))
    
  def nothing(): pass

  def help(): 
    print(easy.__doc__);  

  def nums(): 
    print(NUM([x**.5 for x in range(100)]))
  
  def cols():
    d = DATA(csv(the.file), order=True)
    [print(x) for x in d.cols]
    
  def data():
    d = DATA(csv(the.file), order=True)
    for i,row in enumerate(d.rows):
       if i % 25 == 0 : print(i,row)

  def likes():
    d = DATA( csv(the.file),order=True)
    for i,row in enumerate(d.rows): 
      if i % 25 == 0: 
          print(i, rnds(d.d2h(row)),
                rnds(d.like(row, 1000, 2, m=the.m, k=the.k)))

  def smos():
    print(the.seed)
    d=DATA(csv(the.file),order=False) 
    print("names,",d.names)
    print("base,", rnds(d.mid()),2); print("#")
    random.shuffle(d.rows) 
    d.smo(lambda i,top: print(f"step{i}, ",rnds(top,2)))
    print("#\nbest,",rnds(d.clone(d.rows,order=True).rows[0]),2)

#----------------------------------------------------------------------------------------
if __name__ == "__main__":
  the.cli()
  random.seed(the.seed)
  getattr(Eg, the.todo,Eg.help)()
