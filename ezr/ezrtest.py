#!/usr/bin/env python3

import stats,sys
from ezr import *

sys.dont_write_bytecode = True

def eg__the(): 
  print(ok := str == type(the.Delta))
  assert ok,"str not found"

def eg__csv():
  print(n := sum(len(row) for row in csv(the.file)))
  assert n==3192, "missing cells"

def eg__sym(): 
  print(x := adds("aaaabbc",Sym()).has["a"])
  assert x==4

def eg__num(): 
  print(mu := round(adds(random.gauss(10,2) for _ in range(1000)).mu,1))
  print(sd := round(adds(random.gauss(10,2) for _ in range(1000)).sd,2))
  assert sd == 1.99 and mu == 10

def eg__data():
  print(x := round(sum(y.mu for y in Data(csv(the.file)).cols.y),2))
  assert x == 3009.84

def eg__distx():
  data = Data(csv(the.file))
  r1   = data.rows[0]
  ds   = adds(distx(data,r1,r2) for r2 in data.rows)
  assert 0.45 <= ds.mu <= 0.55 and ds.lo >= 0 and ds.hi <= 1

def eg__disty():
  data = Data(csv(the.file))
  data.rows.sort(key=lambda row: disty(data,row))
  assert all(0 <= disty(data,r) <= 1 for r in data.rows)

def eg__irisKpp(): 
  data = Data(csv("../../moot/classify/iris.csv"))
  mids = distKpp(data,k=10)
  assert distx(data, mids[0], mids[-1]) > 0.5

def eg__fmap(r=20):
  "Dist:  diversity-based optimziation with fast map."
  d    = Data(csv(the.file))
  b4   = adds(disty(d,row) for row in d.rows)
  win  = lambda v: int(100*(1 - (v - b4.lo)/(b4.mu - b4.lo)))
  best = lambda rows: win(disty(d, distysort(d,rows)[0]))
  for few in [12,25,50,100]:
    the.Few = few
    sway1 = adds(best(distFastermap(d,d.rows,False)) for _ in range(r))
    sway2 = adds(best(distFastermap(d,d.rows,True )) for _ in range(r))
    print( *[int(x) for x in [sway1.mu, sway2.mu]])

def eg__likes():
  data = Data(csv(the.file))
  ds   = sorted(likes(data,row) for row in data.rows)
  assert all(-15 < like < -5 for like in ds)

def eg__likely():
  data = Data(csv(the.file))
  b4   = adds(disty(data,row) for row in data.rows)
  win  = lambda v: int(100*(1 - (v - b4.lo)/(b4.mu - b4.lo)))
  best = lambda rows: win(disty(data, distysort(data,rows)[0]))
  for acq in ["near","xploit","xplor","bore","adapt"]:
    the.acq = acq
    print(best(likely(data)))


def eg__tree():
  "Example function demonstrating the optimization workflow"
  the.acq = "near"
  data    = Data(csv(the.file))
  D    = lambda rows: clone(data, rows)
  b4   = adds(disty(data,row) for row in data.rows)
  win  = lambda v: 100*(1 - (v - b4.lo)/(b4.mu - b4.lo))
  best = lambda rows: win(disty(data, distysort(data,rows)[0]))
  n    = len(data.rows)//2
  train, holdout= data.rows[:n], data.rows[n:]
  tree = Tree(clone(data, likely(D(train))))
  treeShow(tree)
  print(int(best(sorted(holdout, key=lambda row: treeLeaf(tree,row).ys.mu)[:the.Check])))

# def eg_ezr():
#   data = Data(csv(the.file))
#   def near(b,data1): the.acq="near"; the.Budget=b; return likely(clone(data,)

def funs(*lst):
  "Example function demonstrating the optimization workflow"
  d = Data(csv(the.file))
  D = lambda rows: clone(d, rows)
  def adapt( _, t,T): the.acq="adapt" ; return so(d,T, likely(D(t)))
  def all(   b, t,T):                   return so(d,T, t)
  def bore(  _, t,T): the.acq="bore"  ; return so(d,T, likely(D(t)))
  def check( b, t,T):                   return random.choices(T,k=the.Check)
  def kpp(   b, t,T):                   return so(d,T, distKpp(D(t), k=b))
  def near(  _, t,T): the.acq="near"  ; return so(d,T, likely(D(t)))
  def rand(  b, t,T):                   return so(d,T, random.choices(t,k=b))
  def sway1( _, t,T):                   return so(d,T, distFastermap(D(t), sway2=False))
  def sway2( _, t,T):                   return so(d,T, distFastermap(D(t), sway2=True))
  def xploit(_, t,T): the.acq="xploit"; return so(d,T, likely(D(t)))
  def xplor( _, t,T): the.acq="xplore"; return so(d,T, likely(D(t)))
  rxs= dict(adapt=adapt, all=all, bore=bore, check=check,
            kpp=kpp, neear=near, sway1=sway1, sway2=sway2,
            xploit=xploit, xplor=xplor)
  return d, [f for k,f in rxs.items() if k in lst]

def eg__dist():
  d, rxs = funs("kpp", "sway1", "sway2")
  _xper(d, [10,20,40,80], rxs)

def so(data, holdout, train):
  tree = Tree(clone(data, train))
  return sorted(holdout, key=lambda row: treeLeaf(tree,row).ys.mu)[:the.Check]

def _xper(data, budgets, funs, repeats=20):
  half = len(data.rows)//2
  b4   = adds(disty(data,row) for row in data.rows)
  win  = lambda v: 100*(1 - (v - b4.lo)/(b4.mu - b4.lo))
  best = lambda rows: win(disty(data, distysort(data,rows)[0]))
  rxs,times = {},{}
  for b in budgets:
    the.Budget = b
    for fun in funs:
      key = (b, fun.__name__); rxs[key]=[]; times[key]=[]
      for _ in range(repeats): 
        t0          = time.time_ns()
        data.rows   = shuffle(data.rows)
        rxs[key]   += [best(fun(b, data.rows[:half], data.rows[half:]))]
        times[key] += [(time.time_ns() - t0)/1_000_000]
  keys= sorted(list(rxs.keys()))
  print(keys)
  scores = adds(x for lst in rxs.values() for x in lst)
  top  = set(stats.top(rxs, reverse=True, eps=.35*scores.sd,
                            Ks=the.Ks, Delta=the.Delta))
  bang = lambda k: "!" if k in top else " "
  med  = lambda a: sum(a)/len(a)
  print("     ,    ,   ,   ",
        *["win"   for k in keys],
        *["msecs" for k in keys],sep=",")
  print("     ,    ,   ,   ",
        *[k[1] for k in keys],
        *[k[1] for k in keys],sep=",")
  print("     ,rows,x  ,y  ",
        *[k[0] for k in keys],
        *[k[0] for k in keys],
        "file", sep=",")
  print(int(scores.mu), len(data.rows), len(data.cols.x), len(data.cols.y),
        *[f"{int(med(rxs[k]))}{bang(k)}" for k in keys],
        *[f"{int(med(times[k]))}"  for k in keys],
        re.sub(".*/","",the.file), sep=",")

#--------------------------------------------------------------------
def prepare(file:str="../moot/text_mining/reading/processed/Hall.csv"):
  "SLOW: test text preprocessor"
  prep = Prep()
  loadData(prep, Data(csv(file)), txt_col="Abstract", klass_col="label")
  compute(prep)
  return prep

def eg__prep_hall():
  "SLOW: test text preprocessor with Hall dataset"
  return prepare("../../moot/text_mining/reading/raw/Hall.csv")

def eg__prep_radjenovic():
  "SLOW: test text preprocessor with Radjenovic dataset"
  return prepare("../moot/text_mining/reading/raw/Radjenovic.csv")

def eg__prep_kitchenham():
  "SLOW: test text preprocessor with Kitchenham dataset"
  return prepare("../moot/text_mining/reading/raw/Kitchenham.csv")

def eg__prep_wahono():
  "SLOW: test text preprocessor with Wahono dataset"
  return prepare("../moot/text_mining/reading/raw/Wahono.csv")
#--------------------------------------------------------------------

def text_mining(file: str, n_repeats: int = 5, norm: bool = False, n_pos: int = 20, n_neg: int = 80) -> bool:
    data = Data(csv(file))
    key, all_indices = data.cols.klass.at, set(range(len(data.rows)))
    pos_idx = [i for i, row in enumerate(data.rows) if row[key] == "yes"]
    safe_div = lambda num, den: num / den * 100 if den > 0 else 0
    results = []

    for _ in range(n_repeats):
        train_pos = random.sample(pos_idx, n_pos)
        train_rows = [data.rows[i] for i in train_pos + 
                      random.sample(list(all_indices - set(train_pos)), n_neg)]
        weights = cnbWeights(cnbStats(data, train_rows), norm=norm)
        preds = [(r[key] == 'yes', cnbBest(weights, r, data) == 'yes') for r in data.rows]
        tp, fn, fp, tn = (sum(w and g for w, g in preds), sum(w and not g for w, g in preds),
                          sum(not w and g for w, g in preds), sum(not w and not g for w, g in preds))
        results.append({"pd": safe_div(tp, tp+fn), "prec": safe_div(tp, tp+fp),
                        "pf": safe_div(fp, fp+tn), "acc": safe_div(tp+tn, tp+fn+fp+tn)})

    def _p(vals, p):
        if not vals: return 0
        s_vals, k = sorted(vals), (len(vals) - 1) * p
        f, c = math.floor(k), math.ceil(k)
        return s_vals[int(f)] + (s_vals[int(c)] - s_vals[int(f)]) * (k - f)

    _med = lambda v: _p(v, 0.5)
    _iqr = lambda v: _p(v, 0.75) - _p(v, 0.25)
    labels = {"pd": "Recall (pd)", "prec": "Precision", "pf": "False Alarm (pf)", "acc": "Accuracy"}
    border = '=' * 55
    header = f"EZR CNB RESULTS | {n_repeats} REPEATS | {n_pos} POS | {n_neg} NEG | {norm} NORM"

    print(f"\n{border}\n{header}\n{border}\n\nMedian (IQR) across {n_repeats} runs:")
    for key, name in labels.items():
        vals = [r[key] for r in results]
        print(f"{name}: {_med(vals):.1f} ({_iqr(vals):.1f})%")
    print(border)
    return True
  
def eg__cnbh():
  "SLOW: Run Complement Naive Bayes on Hall dataset."
  text_mining("../../moot/text_mining/reading/raw/Hall_minimally_processed.csv", n_pos=12, n_neg=12) # 96, 25
  text_mining("../../moot/text_mining/reading/raw/Hall_minimally_processed.csv", n_pos=16, n_neg=16) # 96, 20
  return

def eg__cnbk():
  "SLOW: Run Complement Naive Bayes on Kitchenham dataset."
  return text_mining("../moot/text_mining/reading/processed/Kitchenham.csv", n_pos=32, n_neg=32, norm=True) # 96, 49

def eg__cnbr():
  "SLOW: Run Complement Naive Bayes on Radjenovic dataset."
  return text_mining("../moot/text_mining/reading/processed/Radjenovic.csv", n_pos=16, n_neg=16, norm=True) # 95, 49

def eg__cnbw():
  "SLOW: Run Complement Naive Bayes on Wahono dataset."
  return text_mining("../../moot/text_mining/reading/processed/Wahono.csv", n_pos=20, n_neg=20) # 95, 29
#--------------------------------------------------------------------

def eg__all():
  for f in [eg__csv, eg__sym, eg__num, eg__data, eg__distx,
            eg__disty, eg__irisKpp, eg__fmap,eg__tree]:
      print("\n"+f.__name__); f()

if __name__ == "__main__": main(the, globals())
