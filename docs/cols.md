---
documentclass: scrbook  
classoption:
  - twocolumn
  - landscape 
...

H1
==============

H2 - A
--------------
 

### H3 - a
Blah blah blah...

### H3 - b
Blah blah blah...

### H3 - c
Blah blah blah...

\vfill\eject

```python
class SYM(Counter):
  "Adds `add` to Counter"
  def add(self,x,n=1): self[x] += n #1 

  def entropy(self): 
    n = sum(self.values()) 
    return -sum(v/n*math.log(v/n,2) for _,v in self.items() if v>0)
  
  def __add__(i,j):
    k=SYM()
    [k.add(x,n) for old in [i,j] for x,n in old.items()]
    return k
class SYM(Counter):
  "Adds `add` to Counter"
  def add(self,x,n=1): self[x] += n

  def entropy(self): 
    n = sum(self.values()) 
    return -sum(v/n*math.log(v/n,2) for _,v in self.items() if v>0)
  
  def __add__(i,j):
    k=SYM()
    [k.add(x,n) for old in [i,j] for x,n in old.items()]
    return k 
class SYM(Counter):
  "Adds `add` to Counter"
  def add(self,x,n=1): self[x] += n

  def entropy(self): 
    n = sum(self.values()) 
    return -sum(v/n*math.log(v/n,2) for _,v in self.items() if v>0)
  
  def __add__(i,j):
    k=SYM()
    [k.add(x,n) for old in [i,j] for x,n in old.items()]
    return k
```
H2 - B
--------------
Blah blah blah...
