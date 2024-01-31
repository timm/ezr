# vim : set et ts=2 sw=2 :

class struct:
  def __init__(self,**d) : self.__dict__.update(d)
  __repr__ = lambda self: o(self.__dict__, self.__class__.__name__)

def slots(x)
  if isa(x,dict):
    for k,v in x.items(): yield k,v
  else:
    for k,v in enumerate(x): yield k,v
  
def o(d,s=""): 
  return s+"{"+(", ".join([f":{k} {v}" for k,v in d.items() if k[0]!="_"]))+"}" 

def coerce(s):
  try: return ast.literal_eval(s)
  except Exception: return s

def entropy(d): 
  n = sum(d.values()) 
  return -sum(v/n*math.log(v/n,2) for _,v in d.items() if v>0)

def csv(file=None):
  with file_or_stdin(file) as src:
    for line in src:
      line = re.sub(r'([\n\t\r"\’ ]|#.*)', '', line)
      if line: yield [coerce(s.strip()) for s in line.split(",")]

isa=isinstance

def rnds(x,n=2): 
  if isa(x,(int,float)):  return x if int(x)==x else round(x,n)
  if isa(x,(list,tuple)): return [rnds(y,n) for y in x]
  return x
