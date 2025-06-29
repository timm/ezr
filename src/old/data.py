from lib import big, o

def adds(i,lst): 
  "Bulk additions."
  from adds import add # dodges a cyclic dependancy issue
  [add(i,x) for x in lst]
  return i

def Num(inits=[],at=0, txt=" ", rank=0):
  "Summary of numeric columns."
  return adds(o(it=Num, 
    n      = 0,               ## items seen  
    at     = at,              ## column position
    txt    = txt,             ## column name
    mu     = 0,               ## mean
    sd     = 0,               ## standard deviation
    m2     = 0,               ## second moment
    hi     = -big,            ## biggest seen
    lo     = big,             ## smallest seen
    rank   = rank,            ## used by stats, ignored otherwise
    heaven = (0 if txt[-1] == "-" else 1), ## 0,1 = min,max
    ), inits)

def Sym( inits=[], at=0, txt=" "):
  "Summary of symbolic columns."
  return adds(o(it=Sym, 
    n     = 0,                ## items see
    at    = at,               ## column position 
    txt   = txt,              ## column name
    has   = {}                ## counts of symbols seen
    ), inits)

def Cols(names): 
  "Factory. List[str] -> Dict[str, List[ Sym | Num ]]"
  all,x,y = [],[],[]
  for c,s in enumerate(names):
    all += [(Num if s[0].isupper() else Sym)(at=c, txt=s)]
    if s[-1] != "X":
      (y if s[-1] in "+-" else x).append(all[-1])
  return o(it=Cols, 
    names = names,            ## all the column names
    all   = all,              ## all the columns
    x     = x,                ## also, independent columns stored here
    y     = y)                ## also, dependent columns stored here

def Data(inits): 
  "Data stores rows and columns."
  inits = iter(inits)
  return adds( o(it=Data, 
    n     = 0,                ## items seen
    _rows = [],               ## rows
    cols  = Cols(next(inits)) ## columns (summarizes the rows)
    ), inits)

def clone(data, rows=[]):
  "Copy structure of an existing table."
  return Data([data.cols.names]+rows)
