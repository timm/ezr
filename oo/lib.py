import random,math,re
from obj import obj, ezr

BIG=1E32
isa=isinstance

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

def csv(src):
  "Iterate thorugh all lines in a src."
  for line in src:
    if (line := line.strip()) and not line.startswith("#"):
      yield [atom(s) for s in line.strip().split(',')]

def doc(file):
  "Iterate thorugh all lines in a file."
  with open(file, 'r', newline='', encoding='utf-8') as f:
    for line in f: yield line

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
