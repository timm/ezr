import obj
import math

class Sym(obj.ezr):
  "Summary of symbolic columns."
  def __init__(i, inits=[], at=0, txt=""):
    i.n   = 0     ## items see
    i.at  = at    ## column position 
    i.txt = txt   ## column name
    i.has = {}    ## counts of symbols seen
    i.adds(inits)

  def _add(i,s,inc,_):
    "Update symbol counts."
    i.has[s] = i.has.get(s,0) + inc

  def mid(i): 
    "Central tendancy (most common key)."
    return max(i.has, key=i.has.get)

  def spread(i):
    "Deviation around central tendancy."
    d = i.has
    return -sum(p * math.log(p, 2) for v in d.values() if (p:=v/i.n) > 0)
