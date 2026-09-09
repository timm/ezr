#-- distance ----------------------------------------------
def norm(col, v):
  z = max(-3, min(3, (v - col[1]) / (1e-32 + sd(col))))
  return 1 / (1 + exp(-1.7 * z))

def mid(col):
  return max(col, key=col.get) if type(col) is Sym else col[1]

def mids(tbl): # centroid; only ever read over x columns
  return {at: mid(tbl.cols[at]) for at in tbl.x}

def ydist(tbl, row):
  return (sum(abs(norm(tbl.cols[at], row[at]) - w) ** the.P
             for at, w in tbl.y.items()) / len(tbl.y))**(1/the.P)

def _dist(col, a, b):
  if a == "?" or b == "?": return 1
  return (a != b if type(col) is Sym
          else abs(norm(col, a) - norm(col, b)))

def xdist(tbl, row, m):
  return (sum(_dist(tbl.cols[at], row[at], m[at]) ** the.P
              for at in tbl.x) / len(tbl.x)) ** (1 / the.P)

def ymu(tbl, rows):
  return sum(ydist(tbl, r) for r in rows) / len(rows)

def ymids(tbl, rows):
  return [sum(r[at] for r in rows)/len(rows) for at in tbl.y]
