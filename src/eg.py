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
      repeats=20
      ys=lambda row: [row[k] for k,_ in d.ys.items()]
      ds=lambda row: [col.d(row[k]) for k,col in d.ys.items()]
      r=lambda x:rnds(x,2)
      print(the.seed)
      d=DATA(csv(the.file),order=False) 
      print("names",ys(d.names),"D2h-",sep=",\t")
      print("mid", r(ys(d.mid())),r(d.d2h(d.mid())), sep=",\t");
      print("div", r(ys(d.div())),r(NUM([d.d2h(row) for row in d.rows]).sd), sep=",\t")
      tmp = [d.d2h(row) for row in d.rows]
      d2hs= NUM(tmp,txt="base")
      d2hSample = SAMPLE(tmp,txt="base")
      print(f"{the.cohen}d", r([y*the.cohen for y in ys(d.div())]),
            r(the.cohen*d2hs.sd), sep=",\t")
      print("#") 
      #---
      smoSample=SAMPLE(txt="smo")
      for one in  sorted([d.smo() for _ in range(repeats)], key=d.d2h):
        smoSample.add(d.d2h(one))
        print(f"smo{the.budget0+the.Budget}",r(ds(one)),
              r(d2hs.d(d.d2h(one))), sep=",\t")
      #---
      print("#")
      out=[]
      n = int(0.5 + math.log(1 - .95)/math.log(1 - .35/6))
      for _ in range(repeats):
        random.shuffle(d.rows)
        out += [d.clone(d.rows[:n], order=True).rows[0]]
      anySample=SAMPLE(txt="any")
      for one in  sorted(out, key=d.d2h):   
        anySample.add(d.d2h(one))
        print(f"any{n}", r(ds(one)), d2hs.d(r(d.d2h(one))), sep=",\t")
      #---
      all = d.clone(d.rows,order=True).rows[0]
      print("#\n100%", r(ds(all)), d2hs.d(r(d.d2h(all))), sep=",\t")
      print("\n#",r(d.d2h(all)))
      eg0([anySample, d2hSample,smoSample])


#----------------------------------------------------------------------------------------
if __name__ == "__main__":
  the.cli()
  random.seed(the.seed)
  getattr(Eg, the.todo,Eg.help)()
