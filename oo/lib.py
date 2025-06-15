import random,math,re

BIG=1E32
isa=isinstance

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

#----------------------------------------------------------------------
def see(v):
  "Converts most things to strings."
  it = type(v)
  if callable(v): return v.__name__ + "()"
  if it is float: return str(int(v)) if v == int(v) else f"{v:.3g}"
  if it is list : return "{" + ", ".join(map(see, v)) + "}"
  if it is dict : return see([f":{k} {see(v[k])}" for k in v
                          if not (isa(k,str) and k.startswith("_"))])
  if hasattr(v,"__dict__"): return type(v).__name__ + see(v.__dict__)
  return str(v)

def say(v): print(see(v)); return v

def of(doc):
  def decorator(fun):
    fun.__doc__ = doc
    meta = fun.__annotations__
    setattr(meta.get('i') or meta.get('self'),fun.__name__, fun)
    return fun
  return decorator

def atom(x):
  "Coerce string to int,float, bool, string"
  for fn in (int, float):
    try: return fn(x)
    except: pass
  x = x.strip()
  return x == "true" if x in ("true", "false") else x

def settings(txt):
  "Extract flag=default from strings like our doc string"
  seen = {}
  for k,v in re.findall(r"-\w+\s+(\w+)[^\(]*\(\s*([^)]+)\)",txt):
    assert k not in seen, f"duplicate flag for setting '{k}'"
    seen[k] = atom(v)
  return o(**seen)

def shuffle(lst):
  "Return lst, with contents shuffled in place."
  random.shuffle(lst)
  return lst

def doc(file):
  "Iterate thorugh all lines in a file."
  with open(file, 'r', newline='', encoding='utf-8') as f:
    for line in f: yield line

def csv(src):
  "Iterate thorugh all lines in a src."
  for line in src:
    if (line := line.strip()) and not line.startswith("#"):
      yield [atom(s) for s in line.strip().split(',')]
