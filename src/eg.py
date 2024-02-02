# vim : set et ts=2 sw=2 :

from etc  import *
from ez import *
import ez

class Eg: 
  def all():
    sys.exit(sum(1 if getattr(Eg,s)()==False else 0 
                 for s in dir(Eg) if s[0] !="_" and s !="all"))
    
  def nothing(): pass

  def help(): 
    print(ez.__doc__);  

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
                rnds(d.loglike(row, 1000, 2, m=the.m, k=the.k)))

  def smos():
    repeats=20
    r=lambda x:rnds(x,2)
    print(the.seed)
    d=DATA(csv(the.file),order=False) 
    print("names",d.names,sep=",\t")
    print("mid", r(d.mid()),r(d.d2h(d.mid())), sep=",\t");
    print("div", r(d.div()),sep=",\t"); print("#")
    #---
    for one in  sorted([d.smo() for _ in range(repeats)], key=d.d2h):
      print(f"smo{the.budget0+the.Budget}",r(one),r(d.d2h(one)), sep=",\t")
    #---
    print("#")
    out=[]
    n = int(0.5 + math.log(1 - .95)/math.log(1 - .35/6))
    for _ in range(repeats):
       random.shuffle(d.rows)
       out += [d.clone(d.rows[:n], order=True).rows[0]]
    for one in  sorted(out, key=d.d2h):   
       print(f"any{n}", r(one), r(d.d2h(one)), sep=",\t")
    #---
    all = d.clone(d.rows,order=True).rows[0]
    print("#\n100%", r(all), r(d.d2h(all)), sep=",\t")

    #print("#\nbest,",rnds(d.clone(d.rows,order=True).rows[0]),2)

#----------------------------------------------------------------------------------------
if __name__ == "__main__":
  the.cli()
  random.seed(the.seed)
  getattr(Eg, the.todo,Eg.help)()
