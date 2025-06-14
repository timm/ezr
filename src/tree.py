from about import o,the
from data  import Num,Sym,clone
from adds  import add,sub
from dist  import ydist
from query import spread
from bayes import acquires

# ge, eq, gt
ops = {'<=' : lambda x,y: x <= y,
       "==" : lambda x,y: x == y,
       '>'  : lambda x,y: x >  y}

def selects(row, op, at, y): 
  "Select a row."
  x=row[at]; return  x=="?" or ops[op](x,y) 

def cuts(col,rows,Y,Klass): 
  "What cuts of what cols most reduces spread?"
  return (_sym if col.it is Sym else _num)(col,rows,Y,Klass)

def _sym(sym,rows,Y,Klass): 
  "Report the entropy after dividing the col on its syms."
  n,d = 0,{}
  for row in rows:
    if (x := row[sym.at]) != "?":
      n = n + 1
      d[x] = d[x] if x in d else Klass()
      add(d[x], Y(row))
  return o(div = sum(c.n/n * spread(c) for c in d.values()),
           hows = [("==",sym.at, k) for k,_ in d.items()])

def _num(num,rows,Y,Klass):
  "What num most reduces entropy? Report the results of that cut."
  out, b4, lhs, rhs = None, None, Klass(), Klass()
  xys = [(r[num.at], add(rhs, Y(r))) for r in rows if r[num.at] != "?"]
  xpect = rhs.sd
  for x, y in sorted(xys, key=lambda xy: xy[0]):
    if x != b4:
      if the.leaf <= lhs.n <= len(xys) - the.leaf:
        tmp =  (lhs.n * lhs.sd + rhs.n * rhs.sd) / len(xys)
        if tmp < xpect:
          xpect, out = tmp, [("<=", num.at, b4), (">", num.at, b4)]
    add(lhs, sub(rhs,y))
    b4 = x
  if out: 
    return o(div=xpect, hows=out)

def tree(data, Klass=Num, Y=None, how=None):
  "Split data on best cut. Recurse on each split."
  Y         = Y or (lambda row: ydist(data,row))
  data.kids = []
  data.how  = how
  data.ys   = Num(Y(row) for row in data._rows)
  if data.n >= the.leaf:
    tmp = [x for c in data.cols.x if (x := cuts(c,data._rows,Y,Klass=Klass))]    
    if tmp:
      for how1 in sorted(tmp, key=lambda cut: cut.div)[0].hows:
        rows1 = [row for row in data._rows if selects(row, *how1)]
        if the.leaf <= len(rows1) < data.n:
          data.kids += [tree(clone(data,rows1), Klass, Y, how1)]  
  return data

def nodes(data1, lvl=0, key=None): 
  "Iterate over all nodes."
  yield lvl, data1
  for data2 in (sorted(data1.kids, key=key) if key else data1.kids):
    yield from nodes(data2, lvl + 1, key=key)

def leaf(data1,row):
  "Return leaf selected by row."
  for data2 in data1.kids or []:
    if selects(row, *data2.how): 
      return leaf(data2, row)
  return data1

def show(data, key=lambda z:z.ys.mu):
  "Pretty print a tree."
  stats = data.ys
  win = lambda x: int(100*(1 - ((x-stats.lo)/(stats.mu - stats.lo))))
  print(f"{'d2h':>4} {'win':>4} {'n':>4}  ")
  print(f"{'----':>4} {'----':>4} {'----':>4}  ")
  ats={}
  for lvl, node in nodes(data, key=key):
    leafp = len(node.kids)==0
    post = ";" if leafp else ""
    xplain = ""
    if lvl > 0:
      op,at,y = node.how
      ats[at] = 1
      xplain = f"{data.cols.all[at].txt} {op} {y}"
    indent = (lvl - 1) * "|  "
    print(f"{node.ys.mu:4.2f} {win(node.ys.mu):4} {node.n:4}    "
          f"{indent}{xplain}{post}")
  print(', '.join(sorted([data.cols.names[at] for at in ats])))

def acquired(data):
  "Test the built tree on the hold-it"
  a = acquires(data,stop = the.Stop - the.Test)
  t = tree(clone(data, a.best._rows + a.rest._rows))
  return sorted(a.test, key=lambda z:leaf(t,z).ys.mu)[:the.Test]
