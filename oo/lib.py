import random, sys, re
sys.dont_write_bytecode = True

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
  d = {}
  for k,v in re.findall(r"-\w+\s+(\w+)[^\(]*\(\s*([^)]+)\)",txt):
    assert k not in d, f"duplicate flag for setting '{k}'"
    d[k] = atom(v)
  return d

def shuffle(lst):
  "Return lst, with contents shuffled in place."
  random.shuffle(lst)
  return lst

def cli(d):
  "Update slot `k` in dictionary `d` from CLI flags matching `k`."
  for k, v in d.items():
    for c, arg in enumerate(sys.argv):
      if arg == "-" + k[0]:
        d[k] = atom("False" if str(v) == "True" else (
                    "True" if str(v) == "False" else (
                    sys.argv[c + 1] if c < len(sys.argv) - 1 else str(v))))

def go(config,fns):
  "Run a function from the command line."
  for i,s in enumerate(sys.argv):
    if fn := fns.get("eg" + s.replace("-", "_")):
      cli(config)
      random.seed(config.get("rseed",1))
      fn(None if i==len(sys.argv) - 1 else atom(sys.argv[i+1]))


