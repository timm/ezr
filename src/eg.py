# vim : set et ts=2 sw=2 :

from etc  import *
from ez import *
import ez

class Eg:
  _all = locals()
  def all():
    errors = [f() for s,f in Eg._all.items() if s[0] !="_" and s !="all"]
    sys.exit(sum(0 if x==None else x for x in errors))
    
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
                rnds(d.like(row, 1000, 2, m=the.m, k=the.k)))

  def smos():
    r=lambda x:rnds(x,2)
    print(the.seed)
    d=DATA(csv(the.file),order=False) 
    print("names",d.names,sep=",\t")
    print("mid", r(d.mid()),r(d.d2h(d.mid())), sep=",\t");
    print("div", r(d.div()),sep=",\t"); print("#")
    out=[]
    for i in range(20):
       d=DATA(csv(the.file),order=False) 
       random.shuffle(d.rows) 
       out += [d.smo()]
    for one in sorted(out,key=d.d2h):
        print("smo",r(one),r(d.d2h(one)), sep=",\t")
    best = d.clone(d.rows,order=True).rows[0]
    print("#\n100%", r(best), r(d.d2h(best)), sep=",\t")

    #print("#\nbest,",rnds(d.clone(d.rows,order=True).rows[0]),2)

#----------------------------------------------------------------------------------------
if __name__ == "__main__":
  the.cli()
  random.seed(the.seed)
  getattr(Eg, the.todo,Eg.help)()
