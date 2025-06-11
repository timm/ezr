import sys; sys.path.insert(0, "../src")

import math
from lib import o,csv,lines,cli
from example import EXAMPLE

def eg__o():
  print(o(name="alan", age=41, p=math.pi))

def eg__csv():
  s,n = 0,0
  for i,row in enumerate(csv(lines(EXAMPLE))): 
    if not i % 20: print(row)
    assert len(row)==6
    if type(row[0]) is str: s += 1
    if type(row[0]) in [int,float]: n += 1
  assert s==1 and n==100

cli(dict(o=eg__o, csv=eg__csv))
