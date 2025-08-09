#!/usr/bin/env python3 -B
import traceback, random, math, sys, re
from typing import Any, Callable, Iterator, List
from types import SimpleNamespace as o

from ezr.about import __doc__ as helpstring

Number = int|float
Atom   = Number|str|bool
Row    = List[Atom]

#--------------------------------------------------------------------
def atom(s:str) -> Atom:
  "string coerce"
  for fn in [int,float]:
    try: return fn(s)
    except Exception as _: pass
  s = s.strip()
  return {'True':True,'False':False}.get(s,s)

the = o(**{k:atom(v) for k,v in
           re.findall(r"(\w+)=(\S+)",helpstring)})

#--------------------------------------------------------------------
def main(funs: dict[str,callable]) -> None:
  "from command line, update config find functions to call"
  for n,arg in enumerate(sys.argv):
    if (fn := funs.get(f"eg{arg.replace('-', '_')}")):
      random.seed(the.seed)
      try: fn()
      except Exception as _: 
          print("% Crash on",fn.__doc__,the.file)
          traceback.print_exc()
    else:
      for key in vars(the):
        if arg=="-"+key[0]: the.__dict__[key] = atom(sys.argv[n+1])

def mainAll(funs: dict[str,callable]) -> None: 
 "run all examples"
 for s,fn in funs.items():
   if s != "eg__all" and s.startswith("eg_") and not ((fn.__doc__ or "").strip().startswith("SLOW")):
     print(f"\n--| {s} |-------------"); random.seed(the.seed); fn()

def mainList(funs: dict[str,callable]) -> None:
  "list all examples"
  print("\npython3 ezr.py [OPTIONS]\n")
  for s, fn in funs.items():
    if s.startswith("eg_") and fn.__doc__: 
      if not s.startswith("eg__al_uncertainty"):
         print(f"\t{s[2:].replace('_','-'):10} {fn.__doc__}")

#--------------------------------------------------------------------
def csv(file:str) -> List[Row]:
  "iterate over a file"
  with open(file,encoding="utf-8") as f:
    for line in f:
      if (line := line.split("%")[0]):
        yield [atom(s.strip()) for s in line.split(",")]

def shuffle(lst: List) -> List:
  "randomize order of list"
  random.shuffle(lst); return lst

def pout(x:Any) -> None: print(out(x))

def out(x:Any) -> str:
  "pretty print anything"
  if callable(x): x= x.__name__
  if type(x) is float: x = int(x) if int(x)==float(x) else f"{x:.3f}"
  if hasattr(x,"__dict__"):
    x= "{" + ' '.join(f":{k} {out(v)}" 
             for k,v in x.__dict__.items() if str(k)[0] != "_") + "}"
  return str(x)

#--------------------------------------------------------------------
def eg__the(): 
  "show config"
  print(the)

def eg__csv():
  "read from csv files"
  [pout(x) for x in list(csv(the.file))[::30]]
