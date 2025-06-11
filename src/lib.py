import random,sys

def cli(d):
  if len(sys.argv) > 1 and (fn:= d.get(sys.argv[1])): fn()
  else: print("? no example found in ", sys.argv)

big = 1E32
pick = random.choice
picks = random.choices

def fyi(*l,**kw,): print(*l, end="", flush=True, file=sys.stderr, **kw)
def say(*l,**kw,): print(*l, end="", flush=True, **kw)

def shuffle(lst):
  random.shuffle(lst)
  return lst

# Iterate over lines in a file.
def doc(file):
  with open(file, 'r', newline='', encoding='utf-8') as f:
    for line in f: yield line

# Iterate over lines in a string.
def lines(s):
 for line in s.splitlines(): yield line

# Interate over rows read from lines.
def csv(src):
  for line in src:
    if line: yield [atom(s) for s in line.strip().split(',')]

# String to thing
def atom(x):
  for what in (int, float):
    try: return what(x)
    except Exception: pass
  x = x.strip()
  y = x.lower()
  return (y == "true") if y in ("true", "false") else x

# Thing to string.
def cat(v): 
  it = type(v)
  inf = float('inf')
  if it is list:  return "{" + ", ".join(map(cat, v)) + "}"
  if it is float: return str(int(v)) if -inf<v<inf and v==int(v) else f"{v:.3g}"
  if it is dict:  return cat([f":{k} {cat(w)}" for k, w in v.items()])
  if it in [type(abs), type(cat)]: return v.__name__ + '()'
  return str(v)

# Table pretty print (aligns columns).
def report(rows, head, decs=2):
  w=[0] * len(head)
  Str  = lambda x   : f"{x:.{decs}f}"     if type(x) is float else str(x)
  say  = lambda w,x : f"{x:>{w}.{decs}f}" if type(x) is float else f"{x:>{w}}"
  says = lambda row : ' |  '.join([say(w1, x) for w1, x in zip(w, row)])
  for row in [head]+rows: 
    w = [max(b4, len(Str(x))) for b4,x in zip(w,row)]
  print(says(head))
  print(' |  '.join('-'*(w1) for w1 in w))
  for row in rows: print(says(row))

# Easy class, easy inits. Can print itself.
class o:
  __init__ = lambda i, **d: i.__dict__.update(**d)
  __repr__ = lambda i: cat(i.__dict__)


