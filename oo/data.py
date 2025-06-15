from obj import ezr,obj
from num import Num
from sym import Sym

the=obj(file="../../moot/optimize/misc/auto93.csv")

class Data(ezr):
  "Data stores rows and columns."
  def __init__(i,inits=[]):
    inits   = iter(inits)
    i.n     = 0
    i._rows = []   ## rows
    i.cols  = _cols(next(inits)) ## summaries of rows
    i.adds(inits)

  def _add(i,row,inc,purge):  
    "Update the rows acolumns"
    if inc > 0: i._rows.append(row) 
    elif purge: i._rows.remove(row) # slow for large lists
    for col in i.cols.all: col.add(row[col.at], inc)

  def mid(i) : 
    "Central tendancy."
    return [c.mid() for c in i.cols.all]

  def spread(i): 
    "Deviation from central tendancy."
    return [c.spread() for c in i.cols.all]

def _cols(names):
  "Factory. List[str] -> Dict[str, List[ Sym | Num ]]"
  cols= obj(names = names, ## all the column names
            klass = None,   ## Target for classification
            all   = [],     ## all columns
            x     = [],    ## also, hold independents here
            y     = [])    ## also, hold dependent here
  cols.all = [_col(at, name, cols)  for at,name in enumerate(cols.names)]
  return cols

def _col(at,name,cols): 
  col = (Num if name[0].isupper() else Sym)(txt=name, at=at) 
  if name[-1] != "X":
    if name[-1] == "!": cols.klass = col
    (cols.y if name[-1] in "+-" else cols.x).append(col)
  return col 
