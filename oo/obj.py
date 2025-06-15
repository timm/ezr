class obj:
  "Easy init a mutated struct with named slots and x.slot access."
  __init__ = lambda i, **d: i.__dict__.update(**d)
  __repr__ = lambda i: see(i.__dict__)

class ezr(obj):
  def adds(i,lst=[]): [i.add(x) for x in lst]; return i

  def add(i,v, inc=1, purge=False):
    if v != "?"
      i.n += 1
      i._add(i,v,inc, purge)
    return v

  def sub(i,v,inc= -1, purge=False):
    return i.add(i,v, inc=inc, purge=purge)
