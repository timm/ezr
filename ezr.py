#!/usr/bin/env python3 -B
#
#      ___  ____   _____       ____    __  __
#     / _ \/_  /  / ___/      / __ \  / / / /
#    /  __/ / /_ / /     _   / /_/ / / /_/ / 
#    \___/ /___//_/     (_) / .___/  \__, /  

"""
ezr.py, multi objective.
(col) 2025, Tim Menzies <timm@ieee.org>, MIT license

 -a  act=xploit      (xplor | xploit | adapt | klass)
 -A  Any=4           on init, how many initial guesses?
 -B  Build=24        when growing theory, how many labels?
 -C  Check=5         when testing, how many checks?
 -D  Delta=smed     required effect size test for cliff's delta
 -F  Few=128         just explore a Few rows
 -g  guess=0.5       |hot| is |lit|**guess
 -K  Ks=0.95         confidence for Kolmogorov–Smirnov test
 -k  k=1             Bayes hack for rare classes
 -l  leaf=2          treeNodes in tree leaves
 -m  m=2             Bayes hack for rare attributes
 -p  p=2             distance calculation coefficient
 -s  seed=1234567891 random number seed
 -f  file=../moot/optimize/misc/auto93.csv
                     path to CSV file

 -h                  show help
 --list              list all examples
 --X                 run example X
 --all               run all examples
"""
from types import SimpleNamespace as o 
import random, math, sys, re

def coerce(s):
  "String to atom."
  for fn in [int,float]:
    try: return fn(s)
    except Exception as _: pass
  s = s.strip()
  return {'True':True,'False':False}.get(s,s)

# help --> config 
the = o(**{k:coerce(v) for k,v in re.findall(r"(\w+)=(\S+)",__doc__)})

#  _  _|_  ._        _  _|_   _ 
# _>   |_  |   |_|  (_   |_  _> 

Sym = dict
def Num(): return o(lo=1e32, mu=0, m2=0, sd=0, n=0, hi=-1e32, heaven=1)

def Data(src):
  "Store rows, and summarizes then in cols."
  def _cols(names):
    cols = o(names=names, all=[], x={}, y={}, klass=None)
    for c,s in enumerate(names):
      cols.all += [Num() if s[0].isupper() else Sym()]
      if s[-1] != "X":
        if s[-1] == "!": cols.klass=c
        if s[-1] == "-": cols.all[-1].heaven = 0
        (cols.y if s[-1] in "!-+" else cols.x)[c] = cols.all[-1]
    return cols

  src = iter(src)
  data = o(rows=[], cols= _cols(next(src)))
  [dataAdd(data,r) for r in src]
  return data 

def dataAdd(data, row, inc=1, zap=False):
  "Update data with a row (and to subtract, use inc= -1)."
  if inc>0: data.rows += [row]
  elif zap: data.rows.remove(row) # slow for long rows
  for c,col in enumerate(data.cols.all): add(col,row[c],inc)
  return row

def dataClone(data,rows=[]): 
  "Mimic the structure of an existing data."
  return Data([data.cols.names] + rows)

def dataRead(file):
  "Load a csv file into a data."
  data = None
  with open(file,encoding="utf-8") as f:
    for line in f:
      if (line := line.split("%")[0]):
        row= [coerce(val.strip()) for val in line.split(",")]
        if data: dataAdd(data,row)
        else: data = data or Data([row])
  return data

def  add(col, v, inc=1):
  "Update a col with a value (and to subtract, use inc= -1)."
  if v != "?":
    if type(col) is Sym: col[v] = inc + col.get(v,0)
    else:
      col.n += inc
      col.lo, col.hi = min(v, col.lo), max(v, col.hi)
      if inc < 0 and col.n < 2:
        col.sd = col.m2 = col.mu = col.n = 0
      else:
        d       = v - col.mu
        col.mu += inc * (d / col.n)
        col.m2 += inc * (d * (v - col.mu))
        col.sd  = 0 if col.n < 2 else (max(0,col.m2)/(col.n-1))**.5
  return v

def mids(data):
  "Return the central tendency for each column."
  return [mid(col) for col in data.cols.all]

def mid(col):
  return max(col, key=col.get) if type(col) is Sym else col.mu

def div(col):
  "Return the diversity)."
  if type(col) is not Sym: return col.sd
  N = sum(col.values())
  return -sum(n/N * math.log(n/N, 2) for n in col.values())

def norm(col, v): 
  "Normalize a number 0..1 for lo..hi."
  return v if v=="?" or type(col) is Sym else (v-col.lo)/(col.hi-col.lo + 1E-32)


#   _|  o   _  _|_   _.  ._    _   _  
#  (_|  |  _>   |_  (_|  | |  (_  (/_ 
          
def dist(src):
  "Generalized Minkowski distance with a variable power p."
  d,n = 0,0
  for v in src: n,d = n+1, d + v**the.p
  return (d/n) ** (1/the.p)

def disty(data, row):
  "Distance between goals and heaven."
  return dist(abs(norm(col, row[c]) - col.heaven) for c,col in data.cols.y.items())

def distx(data, row1, row2):
  "Distance between independent values of two rows."
  def _aha(col, a,b):
    if a==b=="?": return 1
    if type(col) is Sym: return a != b
    a,b = norm(col,a), norm(col,b)
    a = a if a != "?" else (0 if b>0.5 else 1)
    b = b if b != "?" else (0 if a>0.5 else 1)
    return abs(a-b)

  return dist(_aha(col, row1[c], row2[c])  for c,col in data.cols.x.items())

def distKpp(data, rows=None, k=20, few=None):
  "Return key centroids usually separated by distance D^2."
  few = few or the.Few
  rows = rows or data.rows[:]
  random.shuffle(rows)
  out = [rows[0]]
  while len(out) < k:
    tmp = random.sample(rows, few)
    ws  = [min(distx(data, r, c)**2 for c in out) for r in tmp]
    p   = sum(ws) * random.random()
    for j, w in enumerate(ws):
      if (p := p - w) <= 0: 
          out += [tmp[j]]; break
  return out

def distKmeans(data, rows=None, n=10, out=None, err=1, **key):
  "Return key centroids within data."
  rows = rows or data.rows
  centroids = [mids(d) for d in out] if out else distKpp(data,rows,**key)
  d,err1 = {},0
  for row in rows:
    col = min(centroids, key=lambda crow: distx(data,crow,row))
    err1 += distx(data,col,row) / len(rows)
    d[id(col)] = d.get(id(col)) or dataClone(data)
    dataAdd(d[id(col)],row)
  print(f'err={err1:.3f}')
  return (out if (n==1 or abs(err - err1) <= 0.01) else
          distKmeans(data, rows, n-1, d.values(), err=err1,**key))

def distProject(data,row,east,west,c=None):
  "Map row along a line east -> west."
  D = lambda r1,r2 : distx(data,r1,r2)
  c = c or D(east,west)  
  a,b = D(row,east), D(row,west)
  return (a*a +c*c - b*b)/(2*c + 1e-32)

def distFastmap(data,rows=None):
  "Sort rows along a line between 2 distant points."
  rows = rows or data.rows
  X = lambda r1,r2:distx(data,r1,r2)
  anywhere, *few = random.choices(rows, k=the.Few)
  here  = max(few, key= lambda r: X(anywhere,r))
  there = max(few, key= lambda r: X(here,r))
  c     = X(here,there)
  return sorted(rows, key=lambda r: distProject(data,r,here,there,c))

def distFastermap(data,rows, sway1=False):
  "Prune half the rows furthest from best distant pair."
  random.shuffle(rows)
  nolabel = rows[the.Any:]
  labels = dataClone(data, rows[:the.Any])
  Y  = lambda r: disty(labels,r)
  while len(labels.rows) < the.Build and len(nolabel) >= 2: 
    east, *rest, west = distFastmap(data,nolabel)
    dataAdd(labels, east)
    dataAdd(labels, west)
    n = len(rest)//2
    nolabel = nolabel[:n] if Y(east) < Y(west) else nolabel[n:]
    if not sway1 and len(nolabel) < 2:
      nolabel= [r for r in rows if r not in labels.rows]
      random.shuffle(nolabel)
  labels.rows.sort(key=Y)
  return o(labels= labels,
           nolabels= [r for r in rows if r not in labels.rows])

#  |  o  |    _  
#  |  |  |<  (/_ 
               
def like(col, v, prior=0):
  "How much does this COL like v?"
  if type(col) is Sym: 
    out=(col.get(v,0) + the.m*prior)/(sum(col.values()) + the.m+1e-32)
  else:
    var= 2 * col.sd * col.sd + 1E-32
    z  = (v - col.mu) ** 2 / var
    out=  math.exp(-z) / (2 * math.pi * var) ** 0.5
  return min(1, max(0, out))

def likes(data, row, nall=100, nh=2):
  "How much does this DATA like row?"
  prior = (len(data.rows) + the.k) / (nall + the.k*nh)
  tmp = [like(col,v,prior) 
         for c,col in data.cols.x.items() if (v:=row[c]) != "?"]
  return sum(math.log(n) for n in tmp + [prior] if n>0)    

def likeBest(datas,row, nall=None):
  "Which data likes this row the most?"
  nall = nall or sum(len(data.row) for data in datas.values())
  return max(datas, key=lambda k: likes(datas[k],row,nall,len(datas)))

def likeClassifier(file, wait=5):
  "Classify rows by how much each class likes a row."
  cf = Confuse()
  data = dataRead(file)
  wait,d,key = 5,{},data.cols.klass
  for n,row in enumerate(data.rows):
    want = row[key]
    d[want] = d.get(want) or dataClone(data)
    if n > wait: confuse(cf, want, likeBest(d,row, n-wait))
    dataAdd(d[want], row)
  return confused(cf)

#    _.   _   _.       o  ._   _  
#   (_|  (_  (_|  |_|  |  |   (/_ 
#              |                  

def acquire(data, rows, acq=None):
  acq = acq or the.acq
  nolabels = rows[:]; random.shuffle(nolabels)
  n1, n2 = round(the.Any**0.5), the.Any
  labels = dataClone(data, nolabels[:n2])
  labels.rows.sort(key=lambda r: disty(labels, r))
  best   = dataClone(data, labels.rows[:n1])
  rest   = dataClone(data, labels.rows[n1:])
  nolabels = nolabels[n2:]

  while len(nolabels) > 2 and len(labels.rows) < the.Build:
    if acq == "klass":
      good, nolabels = acquirePickKlass(best, rest, labels, nolabels)
    else:
      acqFun = acquireScore(acq, best, rest, labels)
      good, nolabels = acquirePick(acqFun, nolabels)

    dataAdd(labels, dataAdd(best, good))
    while len(best.rows) >= len(labels.rows)**0.5:
      best.rows.sort(key=lambda r: disty(best, r))
      dataAdd(rest, dataAdd(best, best.rows.pop(-1), -1))

  labels.rows.sort(key=lambda r: disty(labels, r))
  return o(labels=labels.rows,best=best,rest=rest,nolabels=nolabels)

def acquireScore(acq, best, rest, labels):
  n = len(labels.rows)
  def _score(row):
    b, r = likes(best, row, 2, n), likes(rest, row, 2, n)
    b, r = math.e**b, math.e**r
    if acq == "bore": return (b*b) / (r + 1e-32)
    p = n / the.Build
    q = {"xploit": 0, "xplor": 1}.get(acq, 1 - p)
    return (b + r*q) / abs(b*q - r + 1e-32)
  return _score

def acquirePick(acqFun, nolabels):
  scored = sorted(nolabels[:the.Few*2], key=acqFun, reverse=True)
  good, *nogood = scored
  nolabels= nogood[:the.Few] + nolabels[the.Few*2:] + nogood[the.Few:]
  return good, nolabels

def acquirePickKlass(best, rest, labels, nolabels):
  random.shuffle(nolabels)
  good, *nolabels = nolabels
  for i, row in enumerate(nolabels[:the.Few*2]):
    if ( likes(best,row,2,len(labels.rows)) >
         likes(rest,row,2,len(labels.rows)) ):
      good = nolabels.pop(i); break
  return good, nolabels


# _|_  ._   _    _  
#  |_  |   (/_  (/_ 

treeOps = {'<=' : lambda x,y: x <= y, 
           '==' : lambda x,y:x == y, 
           '>'  : lambda x,y:x > y}

def treeSelects(row,op,at,y): 
  "Have we selected this row?"
  return (x := row[at]) == "?" or treeOps[op](x, y)

def Tree(data, Klass=Num, Y=None, how=None):
  "Create regression tree."
  Y = Y or (lambda row: disty(data, row))
  data.kids, data.how = [], how
  data.ys = adds(Y(row) for row in data.rows)
  if len(data.rows) >= the.leaf:
    hows = [how for at,col in data.cols.x.items() 
            if (how := treeCuts(col,data.rows,at,Y,Klass))]
    if hows:
      for how1 in min(hows, key=lambda c: c.div).hows:
        rows1 = [r for r in data.rows if treeSelects(r, *how1)]
        if the.leaf <= len(rows1) < len(data.rows):
          data.kids += [Tree(dataClone(data,rows1), Klass, Y, how1)]
  return data

def treeCuts(col, rows, at, Y, Klass):
  "Divide a col into ranges."
  def _sym(sym):
    d, n = {}, 0
    for row in rows:
      if (x := row[at]) != "?":
        n += 1
        d[x] = d.get(x) or Klass()
        add(d[x], Y(row))
    return o(div = sum(c.n/n * div(c) for c in d.values()),
             hows = [("==",at,x) for x in d])
  
  def _num(num):
    out, b4, lhs, rhs = None, None, Klass(), Klass()
    xys = [(row[at], add(rhs, Y(row))) # add returns the "y" value
           for row in rows if row[at] != "?"]
    for x, y in sorted(xys, key=lambda z: z[0]):
      if x != b4 and the.leaf <= lhs.n <= len(xys) - the.leaf:
        now = (lhs.n * lhs.sd + rhs.n * rhs.sd) / len(xys)
        if not out or now < out.div:
          out = o(div=now, hows=[("<=",at,b4), (">",at,b4)])
      add(lhs, add(rhs, y, -1))
      b4 = x
    return out

  return (_sym if type(col) is Sym else _num)(col)


def treeNodes(data, lvl=0, key=None):
  "iterate over all treeNodes"
  yield lvl, data
  for j in sorted(data.kids, key=key) if key else data.kids:
    yield from treeNodes(j,lvl + 1, key)

def treeLeaf(data, row):
  "Select a matching leaf"
  for j in data.kids or []:
    if treeSelects(row, *j.how): return treeLeaf(j,row)
  return data

def treeShow(data, key=lambda d: d.ys.mu):
  "Display tree"
  print(f"{'d2h':>4} {'win':>4} {'n':>4}")
  print(f"{'----':>4} {'----':>4} {'----':>4}")
  s, ats = data.ys, {}
  win = lambda x: int(100 * (1-(x-data.ys.lo) / 
                             (data.ys.mu-data.ys.lo+1e-32)))
  for lvl, d in treeNodes(data,key=key):
    op, at, y = d.how if lvl else ('', '', '')
    name = data.cols.names[at] if lvl else ''
    expl = f"{name} {op} {y}" if lvl else ''
    indent = '|  ' * (lvl - 1)
    line = f"{d.ys.mu:4.2f} {win(d.ys.mu):4} {len(d.rows):4}    " \
           f"{indent}{expl}{';' if not d.kids else ''}"
    print(line)
    if lvl: ats[at] = 1
  used = [data.cols.names[at] for at in sorted(ats)]
  print(len(data.cols.x), len(used), ', '.join(used))

#   _  _|_   _.  _|_   _ 
#  _>   |_  (_|   |_  _> 

def Confuse(): 
  "Create a confusion stats for classification matrix."
  return o(klasses={}, total=0)

def confuse(cf, want, got):
  "Update the confusion matrix."
  for x in (want, got):
    if x not in cf.klasses: 
      cf.klasses[x] = o(label=x,tn=cf.total,fn=0,fp=0,tp=0)
  for c in cf.klasses.values():
    if c.label==want: c.tp += (got==want);    c.fn += (got != want)
    else            : c.fp += (got==c.label); c.tn += (got != c.label)
  cf.total += 1
  return got

def confused(cf, summary=False):
  "Report confusion metric statistics."
  p = lambda y, z: round(100 * y / (z or 1e-32), 0)  # one decimal
  def finalize(c):
    c.pd   = p(c.tp, c.tp + c.fn)
    c.prec = p(c.tp, c.fp + c.tp)
    c.pf   = p(c.fp, c.fp + c.tn)
    c.acc  = p(c.tp + c.tn, c.tp + c.fp + c.fn + c.tn)
    return c

  if summary:
    out = o(label="_OVERALL", tn=0, fn=0, fp=0, tp=0)
    for c in cf.klasses.values():
      c = finalize(c)
      for k in ["tn", "fn", "fp", "tp"]:
        setattr(out, k, getattr(out, k) + getattr(c, k))
    return finalize(out)
  [finalize(v) for v in cf.klasses.values()]
  return sorted(list(cf.klasses.values()) + 
                [confused(cf, summary=True)],
                key=lambda cf: cf.fn + cf.tp)

# While ks_code is elegant (IMHO), its slow for large samples. That
# said, it is nearly instantaneous  for the typical 20*20 cases.
def statsSame(x, y, ks=the.Ks, cliffs=the.Delta):
  "True if x,y indistinguishable and differ by just a small effect."
  x, y = sorted(x), sorted(y)
  n, m = len(x), len(y)

  def _cliffs():
    "How frequently are x items are gt,lt than y items?"
    gt = sum(a > b for a in x for b in y)
    lt = sum(a < b for a in x for b in y)
    return abs(gt - lt) / (n * m)

  def _ks():
    "Return max distance between cdf."
    xs = sorted(x + y)
    fx = [sum(a <= v for a in x)/n for v in xs]
    fy = [sum(a <= v for a in y)/m for v in xs]
    return max(abs(v1 - v2) for v1, v2 in zip(fx, fy))

  ks    = {0.1:1.22, 0.05:1.36, 0.01:1.63}[round(1 - ks,2)]
  cliffs= {'small':0.11,'smed':0.195,'medium':0.28,'large':0.43}[cliffs]
  return _cliffs() <= cliffs and _ks() <= ks * ((n + m)/(n * m))**0.5

def statsRank(rxs, reverse=False,same=statsSame, eps=0.01):
  "Sort rxs, recursively split them, stopping when two splits are same."
  items = [(sum(vs), k, vs, len(vs)) for k, vs in rxs.items()]
  return statsDiv(sorted(items,reverse=reverse),same,{},eps,rank=1)[1]

def statsDiv(groups, same, out, eps, rank=1):
  "Cut and recurse (if we find a cut). Else, use rank=rank, then inc rank." 
  def flat(lst): return [x for _, _, xs, _ in lst for x in xs]
  cut = statsCut(groups, eps)
  if cut and not same(flat(groups[:cut]), flat(groups[cut:])):
    return statsDiv(groups[cut:], same, out, eps,
                    rank=statsDiv(groups[:cut], same, out, eps, rank)[0])
  for _, k, _, _ in groups:  out[k] = rank
  return rank + 1, out

def statsCut(groups, eps):
  "Cut to maximize difference in means (if cuts differ bu more than eps)."
  sum1 = sum(s for s, _, _, _ in groups)
  n1   = sum(n for _, _, _, n in groups)
  mu   = sum1 / n1
  best = sum0 = n0 = score = 0
  for j, (s, _, _, n) in enumerate(groups[:-1]):
    sum0 += s; n0 += n
    sum1 -= s; n1 -= n
    mu0, mu1 = sum0 / n0, sum1 / n1
    now = n0 * (mu0 - mu)**2 + n1 * (mu1 - mu)**2
    if abs(mu0 - mu1) > eps and now > score:
      score, best = now, j + 1
  return best

#   _                                     
# _|_       ._    _  _|_  o   _   ._    _ 
#  |   |_|  | |  (_   |_  |  (_)  | |  _> 
                                                       
def adds(src, col=None):
  "Summarize src into col (if col is None, them and guess what col to use)."
  for row in src:
    col = col or (Num if type(row) in [int,float] else Sym)()
    add(col, row)
  return col

def pretty(v, prec=0):
  "Simplify print of numbers."
  if isinstance(v, float):
    return f"{v:.{prec}f}" if v != int(v) else str(int(v))
  return str(v)

def show(lst, pre="| ", prec=0):
  "Pretty print list of 'o' things, all with same labels."
  def fmt(row):
    return pre + " | ".join(c.rjust(w) for c, w in zip(row, gaps)) + " |"

  rows = [[pretty(x, prec) for x in vars(r).values()] for r in lst]
  head = list(vars(lst[0]))
  table = [head] + rows
  gaps = [max(len(row[i]) for row in table) for i in range(len(head))]
  print(fmt(head))
  print(pre + " | ".join("-" * w for w in gaps) + " |")
  for row in rows: print(fmt(row))

def all_egs(run=False):
  "Run all eg__* functions."
  for k,fn in globals().items():
    if k.startswith('eg__') and k != 'eg__all':
      if run:
        print("\n----["+k+"]"+'-'*40)
        random.seed(the.seed)
        fn()
      else:  
        print(" "+re.sub('eg__','--',k).ljust(10),"\t",fn.__doc__ or "")

#  _        _.  ._ _   ._   |   _    _
# (/_  ><  (_|  | | |  |_)  |  (/_  _> 
#                      |               

def eg_h()    : print(__doc__)
def eg__all() : all_egs(run=True)
def eg__list(): all_egs()

def eg__the(): print(the)
def eg__sym(): print(adds("aaaabbc"))
def eg__Sym(): s = adds("aaaabbc"); assert 0.44 == round(like(s,"a"),2)
def eg__num(): print(adds(random.gauss(10,2) for _ in range(1000)))
def eg__Num() : 
  n = adds(random.gauss(10,2) for _ in range(1000))
  assert 0.13 == round(like(n,10.5),2)

def eg__data(): [print(col) for col in dataRead(the.file).cols.all]

def eg__inc():
  "Check i can add/delete rows incrementally."
  d1 = dataRead(the.file)
  d2 = dataClone(d1)
  x  = d2.cols.x[1]
  for row in d1.rows:
    dataAdd(d2,row)
    if len(d2.rows)==100:  
      mu1,sd1 = x.mu,x.sd 
      print(mu1,sd1)
  for row in d1.rows[::-1]:
    if len(d2.rows)==100: 
      mu2,sd2 = x.mu,x.sd
      print(mu2,sd2)
      assert abs(mu2 - mu1) < 1.01 and abs(sd2 - sd1) < 1.01
      break
    dataAdd(d2,row,inc=-1,zap=True)

def eg__bayes():
  data = dataRead(the.file)
  assert all(-30 <= likes(data,t) <= 0 for t in data.rows)
  print(sorted([round(likes(data,t),2) for t in data.rows])[::20])

def eg__confuse():
  "check confuse calcs."
  # a b c <- got
  # ------. want
  # 5 1   | a
  #   2 1 | b
  #     3 | c
  cf = Confuse()   
  for want,got,n in [
      ("a","a",5),("a","b",1),("b","b",2),("b","c",1),("c","c",3)]:
    for _ in range(n): confuse(cf, want, got)
  xpect = {"a": {'pd':83,  'acc':92, 'pf':0,  'prec':100},
           "b": {'pd':67,  'acc':83, 'pf':11, 'prec':67},
           "c": {'pd':100, 'acc':92, 'pf':11, 'prec':75} }
  for y in confused(cf):
    if y.label != "_OVERALL":
       got = {'pd':y.pd, 'acc':y.acc, 'pf':y.pf, 'prec':y.prec}
       assert xpect[y.label] == got
  show(confused(cf))

def eg__stats():
   b4 = [random.gauss(1,1)+ random.gauss(10,1)**0.5
         for _ in range(20)]
   d, out = 0,[]
   while d < 1:
     now = [x+d*random.random() for x in b4]
     out += [f"{d:.2f}" + ("y" if statsSame(b4,now) else "n")]
     d += 0.05
   print(', '.join(out))

def daRx(t):
    if not isinstance(t,(tuple,list)): return str(t)
    return ':'.join(str(x) for x in t)

def eg__sk():
  n=20
  for sd in [0.1,1,10]:
    for eps in [1E-32,0.05,0.1,0.15,0.2]:
      print("\neps=",eps, "sd=",sd)
      rxs={}
      G=lambda m:[random.gauss(m,sd) for _ in range(n)]
      for i in range(20): 
        if   i<=  4 : rxs[chr(97+i)] = G(10)
        elif i <= 8 : rxs[chr(97+i)] = G(11)
        elif i <=12 : rxs[chr(97+i)] = G(12)
        elif i <=16 : rxs[chr(97+i)] = G(12)
        else        : rxs[chr(97+i)] = G(14)
      out=statsRank(rxs,eps=eps)
      print("\t",''.join(map(daRx,out.keys())))
      print("\t",''.join([str(x) for x in out.values()]))

def eg__diabetes(): 
  show(likeClassifier("../moot/classify/diabetes.csv"))

def eg__soybean():  
  show(likeClassifier("../moot/classify/soybean.csv"))

def eg__distx():
  data = dataRead(the.file)
  r1= data.rows[0]
  ds= sorted([distx(data,r1,r2) for r2 in data.rows])
  print(', '.join(f"{x:.2f}" for x in ds[::20]))
  assert all(0 <= x <= 1 for x in ds)

def eg__disty():
  data = dataRead(the.file)
  data.rows.sort(key=lambda row: disty(data,row))
  assert all(0 <= disty(data,r) <= 1 for r in data.rows)
  print(', '.join(data.cols.names))
  print("top4:");   [print("\t",row) for row in data.rows[:4]]
  print("worst4:"); [print("\t",row) for row in data.rows[-4:]]

def eg__irisKpp(): 
  [print(r) for r in distKpp(dataRead("../moot/classify/iris.csv"),k=10)]

def eg__irisK(): 
  for data in distKmeans(dataRead("../moot/classify/iris.csv"),k=10):
    print(mids(data)) 

def daBest(data,rows=None):
  rows = rows or data.rows
  Y=lambda r: disty(data,r)
  return Y(sorted(rows, key=Y)[0])

def eg__tree():
  "XXX: extend using best rest to select"
  data = dataRead(the.file)
  n = len(data.rows)//2
  repeats= 10
  for i in range(repeats):
    if i==0: treeShow(Tree(dataClone(data, acquire(data,data.rows,"klass").labels)))
    random.shuffle(data.rows)
    train, test = dataClone(data, data.rows[:n]), dataClone(data, data.rows[n:])

    rx0   = random.choices(test.rows,k=the.Check)
    tree  = Tree(dataClone(data, acquire(train,train.rows,"klass").labels))
    tree1 = Tree(dataClone(data, random.choices(train.rows,k=the.Build*10)))
    rx    = sorted(test.rows, key=lambda r: treeLeaf(tree,r).ys.mu)
    rx1   = sorted(test.rows, key=lambda r: treeLeaf(tree1,r).ys.mu)

    base = adds(disty(test,r) for r in test.rows)
    win  = (1 - (daBest(test,rx[:the.Check])  - base.lo)/(base.mu - base.lo))
    win0 = (1 - (daBest(test,rx0[:the.Check]) - base.lo)/(base.mu - base.lo))
    win1 = (1 - (daBest(test,rx1[:the.Check]) - base.lo)/(base.mu - base.lo))
    diff = 0 if abs(win - win1) < .35*base.sd else (win-win1)
    R    = lambda z:int(100*z)
    print(R(.35*base.sd), "tree", R(win), "tree10", R(win1), "rand", R(win0) , "diff", R(diff))

def eg__fmap():
  data = dataRead(the.file)
  for few in [32,64,128,256,512]:
    the.Few = few
    print(few)
    n=adds(daBest(data, distFastermap(data,data.rows).labels.rows) for _ in range(20))
    print("\t",n.mu,n.sd)

def eg__acq():
  print(1)
  data = dataRead(the.file)
  base = adds(disty(data,r) for r in data.rows)
  for few in [15,30,60]:
    the.Few = few
    print(few)
    for acq in ["klass"]: #["xplore", "xploit", "adapt","klass"]:
      the.acq = acq
      n=adds(daBest(data, acquire(data, data.rows).labels) for _ in range(20))
      print("\t",the.acq, base.mu, base.lo, n.mu,n.sd)

def eg__rand():
  data = dataRead(the.file)
  n = adds(daBest(data, random.choices(data.rows, k=the.Build)) for _ in range(20))
  print("\t",n.mu,n.sd)


def eg__old():
  data = dataRead(the.file)
  rxs = dict(
             distKpp   = lambda d: distKpp(d, d.rows),
             sway   = lambda d: distFastermap(d, d.rows, sway1=True).labels.rows,
         sway2  = lambda d: distFastermap(d, d.rows).labels.rows # <== winner #<== best
             )
  xper1(data,rxs)
# 77,  88, 96
#  195  #file                                       rows    |y|  |x|   asIs  min  distKpp:15  sway:15  sway2:15  distKpp:30  sway:30  sway2:30  distKpp:60  sway:60  sway2:60  distKpp:120  sway:120  sway2:120  win A
#  196  13                                                                         35      36       35        35      38       43        35      38       70        34       39        100           A
             
def eg__liking():
  data = dataRead(the.file)
  rxs = dict(#rand   = lambda d: random.choices(d.rows,k=the.Build),
             klass = lambda d: acquire(d,d.rows,"klass").labels, #<== klass
             xploit = lambda d: acquire(d,d.rows,"xploit").labels,
             xplor = lambda d: acquire(d,d.rows,"xplor").labels, 
           adapt  = lambda d: acquire(d,d.rows,"adapt").labels
             )
  xper1(data,rxs)

# win percentils 25,50,75 =  76, 84,95 
# #file,rows,|y|,|x|,asIs,min,klass:15,xploit:15,xplor:15,adapt:15,klass:30,xploit:30,xplor:30,adapt:30,klass:60,xploit:60,xplor:60,adapt:60,klass:120,xploit:120,xplor:120,adapt:120,win,A
# 13,,,,32,30,31,31,36,33,34,34,64,45,48,50,96,66,72,73,A


def eg__final():
  data = dataRead(the.file)
  rxs = dict(rand   = lambda d: random.choices(d.rows,k=the.Build),
             klass = lambda d: acquire(d,d.rows,"klass").labels, #<== klass
             sway2  = lambda d: distFastermap(d, d.rows).labels.rows # <== sway2
             )
  xper1(data,rxs)

# win percentils 25,50,75 =  78, 87,96 
   # 199  #file                                       rows    |y|  |x|   asIs  min  rand:15  klass:15  sway2:15  rand:30  klass:30  sway2:30  rand:60  klass:60  sway2:60  rand:120  klass:120  sway2:120  win A
   # 200  13                                                                         30       30        33        39       35        42        59       58        65        82        83         93            A
fyi=lambda s: print(s,file=sys.stderr, flush=True,end="")

def xper1(data,rxs):
  repeats=30
  builds=[15,30,60,120]
  base = adds(disty(data,r) for r in data.rows)
  win  = lambda x: 1 - (x - base.lo) / (base.mu - base.lo + 1e-32)
  out={}
  for build in builds: 
    the.Build = build
    fyi("+")
    for rx,fn in rxs.items():
      fyi("-")
      out[(rx,build)] = [daBest(data,fn(data)) for _ in range(repeats)]
  fyi("!")
  ranks = statsRank(out, eps=base.sd*0.2)
  rank1 = adds(x for k in ranks if ranks[k] == 1 for x in out[k])
  p = lambda z: round(100*z) #"1.00" if z == 1 else (f"{pretty(z,2)[1:]}" if isinstance(z,float) and z< 1 else str(z))
  q = lambda k: f" {'A' if ranks[k]==1 else ' '} {p(adds(out[k]).mu)}"
  print("#file","rows","|y|","|x|","asIs","min",*[daRx((rx,b)) for b in builds for rx in rxs],"win",sep=",")
  print(re.sub("^.*/","",the.file),
        len(data.rows), len(data.cols.y), len(data.cols.x), p(base.mu), p(base.lo),
        *[q((rx,b)) for b in builds for rx in rxs],p(win(rank1.mu)), sep=",")

#   __                                  
#  (_   _|_   _.  ._  _|_  __       ._  
#  __)   |_  (_|  |    |_      |_|  |_) 
#                                  |   

def main():
  "Update settings from CLI, run any eg functions."
  cli(the.__dict__)
  for arg in sys.argv:
    if (fn := globals().get(f"eg{arg.replace('-', '_')}")):
      random.seed(the.seed)
      fn() 

def cli(d):
  "Updated d's slots from  command line."
  for n,arg in enumerate(sys.argv):
    for key in d:
      if arg == "-"+key[0]: 
        d[key] = coerce(sys.argv[n+1])
  return d

if __name__ == "__main__": main()
