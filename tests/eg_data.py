import sys; sys.path.insert(0, "../src")

from data import Cols
from lib import cat,go

# need an eg to reports stats... show you can walk around the data model
def eg__cols(_):
  ":         : List[str] --> columns"
  cols = Cols(["name","Age","Salary+"])
  for what,lst in (("x", cols.x), ("y",cols.y)):
    print("\n"+what)
    [print("\t"+cat(one)) for one in lst]

go(globals())
