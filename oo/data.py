import obj
from Num import Num
from Sym import Sym

class Data(obj.ezr):
  "Data stores rows and columns."
  def __init__(i,inits=[]):
    inits = iter(inits)
    i.n     = 0
    i._rows = [],    ## rows
    i.cols  = i._cols(next(inits)) ## summaries of rows
    i.adds(inits)

 def _add(i,row,inc,purge):  
    "Update the rows acolumns"
    if inc > 0: i._rows.append(row) 
    elif purge: i._rows.remove(row) # slow for large lists
    for col in i.cols.all: col.add(row[col.at], inc)

  def _cols(i,names):
    "Factory. List[str] -> Dict[str, List[ Sym | Num ]]"
    all, x, y, klass = [], [], [], None
    for c, s in enumerate(names):
      col = (Num if s[0].isupper() else Sym)(at=c, txt=s)
      all += [col]
      if s[-1] != "X":
        if s[-1] == "!": klass = col
        (y if s[-1] in "+-" else x).append(col)
    return o(names = names,  ## all the column names
             klass = klass,  ## Target for classification
             all   = all,    ## all columns
             x     = x,      ## also, hold independents here
             y     = y)      ## also, hold dependent here

  def mid(i) : 
    "Central tendancy."
    return [mid(c) for c in i.cols.all]

  def spread(i): 
    "Deviation from central tendancy."
    return [spread(c) for c in i.cols.all]
