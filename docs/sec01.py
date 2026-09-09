#-- structs -----------------------------------------------
Num = lambda: (0, 0, 0) # n, mu, m2: all Welford keeps
Sym = dict

def sd(col): return 0 if col[0] < 2 else sqrt(col[2]/(col[0]-1))

def add(col, v, inc=1): # new Num, or updated Sym; inc=-1 undoes
  if v == "?": return col
  if type(col) is Sym: col[v] = col.get(v, 0) + inc; return col
  n, mu, m2 = col
  n += inc
  d = v - mu
  mu += inc * d / max(1, n)
  return (n, mu, max(0, m2 + inc * d * (v - mu)))

def adds(lst, it=None): # accumulate a list into it
  if it is None: it = Num()   # NB: "it or Num()" would
  for y in lst: it = add(it, y)  # clobber an empty Sym()
  return it

def size(col):
  return sum(col.values()) if type(col) is Sym else col[0]

def div(col): # Num: sd. Sym: entropy
  if type(col) is not Sym: return sd(col)
  n = sum(col.values())
  return -sum(v/n * log2(v/n) for v in col.values() if v>0)

def Tbl(src):
  tbl = o(rows=[], cols={}, x=[], y={}, names=src[0], klass=None)
  for at, s in enumerate(tbl.names):
    if not s.endswith("X"):
      tbl.cols[at] = Num() if s[0].isupper() else Sym()
      if   s[-1] == "!":  tbl.klass = at
      elif s[-1] in "+-": tbl.y[at] = s[-1] == "+"
      else: tbl.x.append(at)
  for row in src[1:]: addRow(tbl, row)
  return tbl

def clone(tbl, rows=[]): return Tbl([tbl.names] + rows)

def addRow(tbl, row=None, inc=1): # inc=-1 pops the last row
  if inc > 0: tbl.rows.append(row)
  else: row = tbl.rows.pop()
  for at in tbl.cols:
    tbl.cols[at] = add(tbl.cols[at], row[at], inc)
  return row
