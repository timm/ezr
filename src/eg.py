# vim : set et ts=2 sw=2 :
import sys
from datetime import datetime
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
          
  def dists():
    d = DATA( csv(the.file),order=True)
    row1=d.rows[0]
    for i,row3 in enumerate(sorted(d.rows,key=lambda row2:d.dist(row1,row2))):
      if i % 25 == 0: 
        print(i, row3, rnds(d.dist(row1,row3)))

  def halfs():
    d = DATA( csv(the.file),order=True)
    a,b,C = d.half(d.rows)
    print(len(a),len(b),C)
    
  def branch():
    d = DATA( csv(the.file),order=True)
    for i in range(20):
      random.shuffle(d.rows); rows0, *_ = d.branch(d.rows)
      random.shuffle(d.rows); 
      rows1, *_ = d.branch(d.rows,stop=50)
      rows2, *_ = d.branch(rows1, stop=4)
      print(joins([i,d.d2h(rows0[0]), d.d2h(rows1[0]), d.d2h(rows2[0])]))
 
   
  def bins():
    d = DATA( csv(the.file),order=True) 
    random.shuffle(d.rows); 
    best,rest,*_  = d.branch() 
    rest = random.choices(rest, k=len(best)*3) 
    for c,col in enumerate(d.cols):
      if c in d.xs:
        print("")
        for r in discretize(c,d.names[c],col,dict(best=best,rest=rest)):
          print(r)
      #print(joins([i,d.d2h(d.rows[0]), d.d2h(best[0]), d.d2h(rest[0])]))

  def smos():
    repeats=the.repeats
    r=lambda x:rnds(x,2)
    d=DATA(csv(the.file),order=False) 
    now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    print(f"date : {now},")
    print(f"file : {the.file},\nrepeats  : {repeats},\nseed : {the.seed},")
    print(f"rows : {len(d.rows)},")
    print(f"cols : {len(d.names)},")
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

  def smocompare(): 
      repeats = the.repeats
      e=math.exp(1)
      def say(*l): print(*l,end=" ",flush=True);
      r=lambda a: ', '.join([str(x) for x in rnds(a,2)])
      d=DATA(csv(the.file),order=False)  
      n3 = int(0.5 + len(d.rows)**.5)
      n5 = int(0.5 + len(d.rows)*.9)
      n6 = 15
      n7 = 9
      n8 = 20
      d2hs = NUM([d.d2h(row) for row in d.clone(d.rows,True).rows])
      now = datetime.now().strftime("%B/%m/%Y %H:%M:%S")
      print(f"date : {now},")
      print(f"file : {the.file},\nrepeats  : {repeats},\nseed : {the.seed},")
      print(f"rows : {len(d.rows)},")
      print(f"cols : {len(d.names)},")
      print(f"best : {rnds(d2hs.lo)},\ntiny : {rnds(d2hs.sd*.35)}")
      heavens = sorted([d.d2h(row) for row in d.rows])
      heavens = heavens[:int(len(heavens)*.5)]
      say("#base");all= [SAMPLE(heavens,        txt="base")] 

      for budget in sorted(set([n3,15,n5,n6,n7,n8])): 
        the.Budget = budget -  the.budget0 
        if budget < 100:
           say(f"#bonr{budget}"); all +=  [SAMPLE([d.d2h(d.smo(score=lambda B,R: abs(e**B+e**R)/abs(e**B-e**R + tiny)))
                                     for _   in range(repeats)],txt=f"#bonr{budget}")]

        say(f"#rand{budget}");all +=  [SAMPLE([d.d2h(d.clone(shuffle(d.rows)[:budget], order=True).rows[0]) 
                                    for _ in range(20)], txt=f"#rand{budget}")] 
      #-----------------------------------
      print(f"\n#report{len(all)}");eg0(all)

  def smoy():  
      repeats=the.Repeats
      e=math.exp(1)
      def say(*l): print(*l,end=" ",flush=True);
      r=lambda a: ', '.join([str(x) for x in rnds(a,2)])
      d=DATA(csv(the.file),order=False)  
      # n1 = int(0.5 + math.log(1 - .95)/math.log(1 - .35/6))
      # n2 = int(0.5 + math.log(n1,2))
      # n3 = int(0.5 + len(d.rows)**.5)
      # n4 = int(0.5 + min(len(d.names)*10, len(d.rows)*.9))
      # n5 = int(0.5 + len(d.rows)*.9)
      # n6 = 15
      # n7 = 9
      # n8 = 20
      # n9 = 30
      d2hs = NUM([d.d2h(row) for row in d.clone(d.rows,True).rows])
      now = datetime.now().strftime("%B/%m/%Y %H:%M:%S")
      print(f"date : {now},")
      print(f"file : {the.file},\nrepeats  : {repeats},\nseed : {the.seed},")
      print(f"rows : {len(d.rows)},")
      print(f"cols : {len(d.names)},")
      print(f"best : {rnds(d2hs.lo)},\ntiny : {rnds(d2hs.sd*.35)}")
      heavens = [d.d2h(row) for row in d.rows]
      heavens = sorted(heavens)[:int(len(heavens)*.95)]
      say("#base");all= [SAMPLE(heavens, txt=f"base,{len(d.rows)}")] 

      def _single(all):
        evals1 = 0
        lst   = []
        for _ in range(repeats):
          random.shuffle(d.rows); 
          _,__,evals1,last = d.branch(d.rows) 
          lst +=  [d.d2h(last)]
        all += [SAMPLE(lst, txt=f"rrp,{evals1}")]
        return 
      
      def _double(all):
        evals1,evals2 = 0,0
        lst   = []
        for _ in range(repeats):
          random.shuffle(d.rows); 
          rows1, _,evals1,__ = d.branch(d.rows,50) 
          _, __, evals2,last = d.branch(rows1,4)
          lst +=  [d.d2h(last)]
        all += [SAMPLE(lst, txt=f"2rrp,{evals1+evals2}")]
      
      say(f"#2rrp"); _double(all)
      say(f"#rrp"); _single(all)

      for budget in sorted(set([6,12,25,50,100,200,400,800])): 
        if budget > len(d.rows): continue
        the.Budget = budget -  the.budget0 
        if budget <= 80:
           say(f"#b{budget}"); all += [SAMPLE([d.d2h(d.smo(score=lambda B,R: B-R))
                                     for _   in range(repeats)],txt=f"b,{budget}")]
           say(f"#2b{budget}"); all += [SAMPLE([d.d2h(d.smo(score=lambda B,R: 2*B-R))
                                     for _   in range(repeats)],txt=f"2b,{budget}")]
           say(f"#bonr{budget}"); all +=  [SAMPLE([d.d2h(d.smo(score=lambda B,R: abs(e**B+e**R)/abs(e**B-e**R + tiny)))
                                     for _   in range(repeats)],txt=f"bonr,{budget}")]
        
        say(f"#rand{budget}");all +=  [SAMPLE([d.d2h(d.clone(shuffle(d.rows)[:budget], order=True).rows[0]) 
                                    for _ in range(repeats)], txt=f"rand,{budget}")] 
      #-----------------------------------
      print(f"\n#report{len(all)}");eg0(all)
     
#----------------------------------------------------------------------------------------
if __name__ == "__main__":
  the.cli() 
  random.seed(the.seed)
  getattr(Eg, the.todo, Eg.help)()
