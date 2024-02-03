# vim : set et ts=2 sw=2 :

from etc  import *
from ez import *
from stats import eg0,SAMPLE
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
    print("names",d.names,"D2h-",sep=",\t")
    print("mid", r(d.mid()),r(d.d2h(d.mid())), sep=",\t");
    print("div", r(d.div()),r(NUM([d.d2h(row) for row in d.rows]).sd), sep=",\t"); print("#") 
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

  def smoy():
      repeats=10
      e=math.exp(1)
     
      r=lambda a: ', '.join([str(x) for x in rnds(a,2)])
      d=DATA(csv(the.file),order=False)  
      n1 = int(0.5 + math.log(1 - .95)/math.log(1 - .35/6))
      n2 = int(0.5 + math.log(n1,2))
      n3 = int(0.5 + len(d.rows)**.5)
      n4 = int(0.5 + min(len(d.names)*10, len(d.rows)*.9))
      n5 = int(0.5 + len(d.rows)*.9)
      n6 = 12
      n7 = 9
      n8 = 20
      d2hs = NUM([d.d2h(row) for row in d.clone(d.rows,True).rows])
      print(f"file : {the.file},\nrepeats  : {repeats},\nseed : {the.seed},\nrows : {len(d.rows)},")
      print(f"cols : {len(d.names)},\nbest : {rnds(d2hs.lo)},\ntiny : {rnds(d2hs.sd*.35)}")
      print("#base");all= [SAMPLE([d.d2h(row) for row in d.rows],        txt="base")] 
      for budget in [n1,n2,n3,n4,n5,n6,n7,n8]: 
        the.Budget = budget -  the.budget0 
        if budget < 100:
           print(f"#b{budget}"); all += [SAMPLE([d.d2h(d.smo(score=lambda B,R: B-R))
                                     for _   in range(repeats)],txt=f"#b{budget}")]
           print(f"#bonr{budget}"); all +=  [SAMPLE([d.d2h(d.smo(score=lambda B,R: abs(e**B+e**R)/abs(e**B-e**R + tiny)))
                                     for _   in range(repeats)],txt=f"#bonr{budget}")]
        
        print(f"#rand{budget}");all +=  [SAMPLE([d.d2h(d.clone(shuffle(d.rows)[:budget], order=True).rows[0]) 
                                    for _ in range(20)], txt=f"#rand{budget}")] 
      #-----------------------------------
      print(f"#report{len(all)}");eg0(all)
     
    
      


#----------------------------------------------------------------------------------------
if __name__ == "__main__":
  the.cli()
  random.seed(the.seed)
  getattr(Eg, the.todo,Eg.help)()