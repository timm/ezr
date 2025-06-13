import random,sys,re

big = 1E32
pick = random.choice
picks = random.choices

def go(fns):
  "Run a function from the command line."
  for i,s in enumerate(sys.argv):
    if fn := fns.get("eg" + s.replace("-", "_")):
      from about import the
      cli(the.__dict__)
      random.seed(the.rseed)
      fn(None if i==len(sys.argv) - 1 else atom(sys.argv[i+1]))

def cli(d):
  "Update slot `k` in dictionary `d` from CLI flags matching `k`."
  for k, v in d.items():
    for c, arg in enumerate(sys.argv):
      if arg == "-" + k[0]:
        d[k] = atom("False" if str(v) == "True" else (
                    "True" if str(v) == "False" else (
                    sys.argv[c + 1] if c < len(sys.argv) - 1 else str(v))))

def fyi(*l,**kw,): 
  print(*l, end="", flush=True, file=sys.stderr, **kw)

def say(*l,**kw,): 
  print(*l, end="", flush=True, **kw)

def shuffle(lst):
  random.shuffle(lst); return lst

def nway(rows, m=5, n=5):
  rows = rows[:]
  fold = len(rows) // n
  for _ in range(m):
    random.shuffle(rows)
    for b in range(n):
      lo = b * fold
      hi = lo + fold if b < n - 1 else len(rows)
      yield rows[:lo] + rows[hi:], rows[lo:hi]

def doc(file):
  with open(file, 'r', newline='', encoding='utf-8') as f:
    for line in f: yield line

def lines(s):
 for line in s.splitlines(): yield line

def csv(src):
  for line in src:
    if line: yield [atom(s) for s in line.strip().split(',')]

def atom(x):
  for what in (int, float):
    try: return what(x)
    except Exception: pass
  x = x.strip()
  y = x.lower()
  return (y == "true") if y in ("true", "false") else x

def cat(v): 
  it = type(v)
  inf = float('inf')
  if it is list:  return "{" + ", ".join(map(cat, v)) + "}"
  if it is float: 
    return str(int(v)) if -inf<v<inf and v==int(v) else f"{v:.3g}"
  if it is dict:  
    return cat([f":{k} {cat(w)}" for k, w in v.items()])
  if it in [type(abs), type(cat)]: 
    return v.__name__ + '()'
  return str(v)

def report(rows, head, decs=2):
  w=[0] * len(head)
  def Str(x):
    return f"{x:.{decs}f}" if type(x) is float else str(x)
  def say(w,x):
    return f"{x:>{w}.{decs}f}" if type(x) is float else f"{x:>{w}}"
  def says(row):
    return ' |  '.join([say(w1, x) for w1, x in zip(w, row)])
  for row in [head]+rows: 
    w = [max(b4, len(Str(x))) for b4,x in zip(w,row)]
  print(says(head))
  print(' |  '.join('-'*(w1) for w1 in w))
  for row in rows: print(says(row))

class o:
  __init__ = lambda i, **d: i.__dict__.update(**d)
  __repr__ = lambda i: cat(i.__dict__)
