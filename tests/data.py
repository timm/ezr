import sys; sys.path.insert(0, "../src")

from data import Cols
from lib import cat,cli

def eg__cols():
  ":         : List[str] --> columns"
  cols = Cols(["name","Age","Salary+"])
  for what,lst in (("x", cols.x), ("y",cols.y)):
    print("\n"+what)
    [print("\t"+cat(one)) for one in lst]

cli(dict(cols=eg__cols))
