# vim : set et ts=2 sw=2 :

import re, ast, sys, math, random
from fileinput import FileInput as file_or_stdin

class struct:
  def __init__(self,**d) : self.__dict__.update(d)
  __repr__ = lambda self: o(self.__dict__, self.__class__.__name__)

class THE(struct):
  def __init__(self,txt):
    self._help = txt
    d = {m[1]:coerce(m[2]) for m in re.finditer(r"--(\w+)[^=]*=\s*(\S+)",txt)}
    self.__dict__.update(d)
    
  def cli(self):
    for k,v in self.__dict__.items(): 
      v = str(v)
      for c,arg in enumerate(sys.argv):
        after = "" if c >= len(sys.argv) - 1 else sys.argv[c+1]
        if arg in ["-"+k[0], "--"+k]: 
          v = "false" if v=="true" else ("true" if v=="false" else after)
          self.__dict__[k] = coerce(v)

def coerce(s):
  try: return ast.literal_eval(s)
  except Exception: return s

def csv(file=None):
  with file_or_stdin(file) as src:
    for line in src:
      line = re.sub(r'([\n\t\r"\’ ]|#.*)', '', line)
      if line: yield [coerce(s.strip()) for s in line.split(",")]

def joins(lst,rnd=2,sep=","):
  return sep.join([str(x) for x in rnds(lst,rnd)])

isa = isinstance

def merges(b4, merge):
  i, now, most = 0,[],len(b4)
  while i <  most:
    a = b4[i] 
    if i <  most - 1: 
      if tmp := merge(a, b4[i+1]): 
        a   = tmp
        i  += 1
    now += [a]
    i += 1
  return now if len(now) == len(b4) else merges(now, merge)

def o(d, s = ""): 
  return s+"{"+(", ".join([f":{k} {rnds(v)}" for k,v in d.items() if k[0]!="_"]))+"}" 

def rnds(x,n=2): 
  if isa(x,(int,float)):  return x if int(x)==x else round(x,n)
  if isa(x,(list,tuple)): return [rnds(y,n) for y in x]
  return x

def shuffle(lst):
  random.shuffle(lst)
  return lst

def slots(x):
  if isa(x,dict):
    for k,v in x.items(): yield k,v
  else:
    for k,v in enumerate(x): yield k,v