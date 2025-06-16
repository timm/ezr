"""
Print options:

  -r rnd   Number of decimal places for print print (3)
"""
from lib import settings,isa

class o:
  "A mutatable struct with named slots,  x.slot access, pretty print."
  __init__ = lambda i, **d: i.__dict__.update(**d)
  __repr__ = lambda i: see(i.__dict__)

the = o(**settings(__doc__))

class obj(o):
  def adds(i,lst=[]): [i.add(x) for x in lst]; return i

  def add(i,v, inc=1, purge=False):
    if v != "?":
      i.n += inc
      i._add(v,inc,purge) # implemented by subclass 
    return v

  def sub(i,v,inc= -1, purge=False):
    return i.add(v, inc=inc, purge=purge)

def see(v):
  "Converts most things to strings."
  it = type(v)
  if callable(v): return v.__name__ + "()"
  if it is list : return "{" + ", ".join(map(see, v)) + "}"
  if hasattr(v,"__dict__"): return see(v.__dict__)
  if it is float: 
        return str(int(v)) if v==int(v) else f"{v:.{1+the.rnd}g}"
  if it is dict : return see([f":{k} {see(v[k])}" for k in v
                               if not (isa(k,str) and k[0] == "_")])
  return str(v)

def say(v): print(see(v)); return v
