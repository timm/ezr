#!/usr/bin/env python3 -B
"""
ezr.py: explainable multi-objective optimization   
(c) 2026 Tim Menzies, timm@ieee.org, MIT license   
  
Usage: 
  ezr [OPTIONS] [ARGS]   
"""
HELP_TAIL = """
Command-line actions:
  --h                   show help
  --list                list all demos
  --egs file            run all demos safely
  --see   file          show tree (rung 1)   
  --act   file          test vs leaf (rung 2)   
  --imagine file        what-if (rung 3)   
  --acquire file        train/predict/score pipeline
  --cluster file        clustering benchmark table

Input is CSV. Header (row 1) defines column roles:   
  [A-Z]*  : Numeric        [a-z]*  : Symbolic
  [A-Z]*+ : Maximize       [A-Z]*- : Minimize
  [a-z]*! : Class          *X      : Ignored
  ?       : Missing value

To install and test, download http://githib.com/timm/lua/ezr.py. Then:   
   
    pip install ezr
    mkdir -p $HOME/gits   # download sample data       
    git clone http://github.com/timm/moot $HOME/gits/moot      
    ezr --see ~/gits/moot/optimize/misc/auto93.csv      

Run all tests:

    ezr.py --all  # option1
    pytest ezeg.py # option2 (if pytest installed)

"""
from ezr import *
import ezr
import textmine as tm
try:
  import pytest
  @pytest.fixture(autouse=True)
  def _seed(): random.seed(the.seed)
except ImportError: pass

egclass1=Path.home() / "gits/moot/classify/soybean.csv"
egclass2=Path.home() / "gits/moot/classify/diabetes.csv"
egopt1=  Path.home() / "gits/moot/optimize/misc/auto93.csv"

# ---- Evaluation helpers ----
def ready(file: Any) -> tuple:
  """Shuffle, split data into train/test."""
  d = (file if Data==type(file)
       else Data(csv(file)))
  random.shuffle(d.rows)
  half = len(d.rows) // 2
  return (d, clone(d, d.rows[:half][:the.few]),
             d.rows[half:])

def confused(cf: dict) -> list[S]:
  """Confusion stats, all metrics as int %."""
  klasses = sorted(set(cf.keys()).union(
    {g for w in cf.values()
     for g in w.keys()}))
  total = sum(cf[w][g]
              for w in cf for g in cf[w])
  p = lambda y,z: int(100*y/(z or 1e-32))
  out = []
  for c in klasses:
    tp = cf.get(c, {}).get(c, 0)
    fn = sum(cf.get(c, {}).values()) - tp
    fp = sum(cf.get(w, {}).get(c, 0)
             for w in cf if w != c)
    tn = total - tp - fn - fp
    pd, pr = p(tp,tp+fn), p(tp,fp+tp)
    sp = p(tn, tn+fp)
    out.append(S(tp=tp, fn=fn, fp=fp, tn=tn,
      pd=pd, pr=pr,
      f1=int(2*pd*pr/(pd+pr+1e-32)),
      g=int(2*pd*sp/(pd+sp+1e-32)),
      acc=p(tp+tn, total), label="  "+c))
  return out

# ---- Clustering ----
def kmeans(d, rs=None, k=10, n=10,
           cents=None) -> Datas:
  """Cluster rows into k groups."""
  rs, out = rs or d.rows, []
  cents = cents or choices(rs, k=k)
  for _ in range(n):
    out = [clone(d) for _ in cents]
    for r in rs:
      add(out[min(range(len(cents)),
        key=lambda j:distx(d,cents[j],r))],r)
    cents = [mids(kid)
             for kid in out if kid.rows]
  return out

def kpp(d,rs=None,k=10,few=256) -> Rows:
  """k-means++ centroid selection."""
  rs = rs or d.rows
  out = [choice(rs)]
  while len(out) < k:
    t = sample(rs, min(few, len(rs)))
    ws = {i: min(distx(d,t[i],c)**2
                 for c in out)
          for i in range(len(t))}
    out.append(t[pick(ws)])
  return out

def half(d, rs, few=20) -> tuple:
  """Divide rows by two extreme points."""
  t = sample(rs, min(few, len(rs)))
  gap, east, west = max(
    ((distx(d,r1,r2),r1,r2)
     for r1 in t for r2 in t),
    key=lambda z: z[0])
  proj = lambda r: (
    distx(d,r,east)**2 + gap**2 -
    distx(d,r,west)**2) / (2*gap+1e-32)
  rs = sorted(rs, key=proj)
  n = len(rs) // 2
  return (rs[:n], rs[n:],
          east, west, gap, proj(rs[n]))

def rhalf(d, rs=None, k=10,
          stop=None, few=20) -> Datas:
  """Recursively halve into clusters."""
  rs = rs if rs is not None else d.rows
  stop = stop or 20
  if len(rs) <= 2*stop:
    return [clone(d, rs)]
  l,r,east,west,gap,cut = half(d, rs, few)
  return (rhalf(d, l, k, stop, few) +
          rhalf(d, r, k, stop, few))

def neighbors(d, r1, ds,
              near=1, fast=False) -> Rows:
  """Find nearest rows or centroid."""
  c = min(ds,
    key=lambda c: distx(d, r1, mids(c)))
  return ([mids(c)] if fast else
    sorted(c.rows,
      key=lambda r2:distx(d,r1,r2))[:near])

def clustering(d0, build,
               near=1, fast=False):
  """Benchmark clustering algorithms."""
  t_build,t_apply,err,repeats = 0,0,0,10
  for _ in range(repeats):
    d, train, test = ready(d0)
    predict = lambda rs: (
      sum(disty(train,r) for r in rs)
      / len(rs) if rs else 0)
    t_1 = now()
    ds = build(train)
    t_2 = now()
    t_build += t_2 - t_1
    for r in test:
      near_rs = neighbors(train, r, ds,
                  near=near, fast=fast)
      err += abs(disty(d,r)
               - predict(near_rs))/len(test)
    t_apply += now() - t_2
  return [f"{x/repeats:>7.2f}"
    for x in [t_build/1e6,t_apply/1e6,err]]

# ---- 0. Utilities ----
def test_o():
  """Test string formatting of various data types."""
  class Tmp:
    def __init__(i): i.x, i.y = 1, 2
  print(o(3.14159)) 
  print(o([1, {"a": 2}, Tmp()]))

def test_table():
  """Test tabular formatting of dictionaries and objects."""
  lst = [
    {"name": "tim", "age": 21, "shoe": 10},
    {"name": "tom", "age": 22, "shoe": 9.5}
  ]
  table(lst, w=8)

def test_thing(): 
  """Test string coercion to correct types."""
  assert thing("3.14") == 3.14
  assert thing(" true ") in [True, 1]
  assert thing(" false ") in [False, 0]
  assert thing("hello") == "hello"
  print("ok")

def test_nest():
  """Test deep setting in a nested namespace."""
  t = S()
  nest(t, "a.b.c", 42)
  assert t.a.b.c == 42
  print(o(t))

def test_csv(file:str=egopt1): 
  """Test that CSV reader extracts data."""
  assert len(list(csv(file))) > 10

# ---- 1. Config & CLI ----
def cli() -> None:
  """Execute functions or update config via CLI args."""
  args = sys.argv[1:]
  while args:
    random.seed(the.seed)
    k = re.sub(r"^-+", "", args.pop(0))
    if fn := globals().get(f"test_{k}"): 
      fn(*[thing(args.pop(0)) for _ in fn.__annotations__ if args])
    else: 
      nest(the, k, thing(args.pop(0)))  

def test_h(): 
  """Print the help text."""
  print(__doc__)
  print(ezr.__doc__)
  print(HELP_TAIL)
 
def test_the(): 
  """Test that config dictionary parses correctly."""
  print(o(the)); assert int == type(the.seed)

def test_list():
  """List all available example functions and their signatures."""
  fns = {k: v for k, v in globals().items() if k[:5] == "test_"}
  for k, fn in fns.items():
    print(f"  --{k[5:]:12} {' '.join(fn.__annotations__)} {fn.__doc__}")

def test_egs(file:str=egopt1):
  """Run all test examples sequentially."""
  egs = {k: v for k, v in globals().items() if k[:5]=="test_" and k!="test_egs"}
  for k, fn in egs.items():
    print(f"\n--- {k} ----\n{fn.__doc__}")
    random.seed(the.seed)
    fn(file) if "file" in fn.__annotations__ else fn()

# ---- 2. Columns ----
def test_num():
  """Test numeric incremental updates."""
  c = adds([10, 20, 30, 40, 50], Num())
  assert c.mu == 30 and 15.8 < spread(c) < 15.9

def test_sym():
  """Test symbolic entropy calculations."""
  c = adds("aaabbc", Sym())
  assert mid(c) == "a" and 1.4 < spread(c) < 1.5

def test_pick():
  """Test numeric incremental updates."""
  c1 = adds([10, 20, 30, 40, 50], Num())
  c2 = adds(pick(c1) for _ in range(10000))
  assert abs(mid(c1)- mid(c2)) < 0.25
  assert abs(spread(c1) - spread(c2)) < 0.25
  c1 = adds("aaabbc", Sym())
  c2 = adds([pick(c1) for _ in range(1000)],Sym())
  assert mid(c1)== mid(c2)
  assert abs(spread(c1) - spread(c2)) < 0.1

# ---- 3. Data (Tables) ----
def test_cols(): 
  """Test column extraction logic."""
  cols = Cols(["name","Age","Weight-"])
  [print("x",o(c)) for c in cols.xs]
  [print("y",o(c)) for c in cols.ys]
  assert not cols.ys[0].heaven

def test_data(file:str=egopt1):
  """Test that Data objects properly populate their columns."""
  d = Data(csv(file)); assert len(d.rows) > 0 and len(d.cols.ys) > 0

def test_addsub(file:str=egopt1):
  """Test that rows can be cleanly added and subtracted."""
  d, d2 = Data(csv(file)), clone(Data(csv(file)))
  for r in d.rows:
    add(d2,r)
    if len(d2.rows)==50: m1 = mids(d2)
  print(o(mids(d2)))
  for r in d.rows[::-1]:
    sub(d2,r)
    if len(d2.rows)==50: m2 = mids(d2)
  print(o(m1))
  print(o(m2))
  assert all(abs(a-b) < 0.01 for a,b in zip(m1, m2))

# ---- 4. Bayes ----
def test_classify(file:str=egclass1):
  """Test incremental Naive Bayes classification."""
  print(file)
  for path in [Path.home() / "gits/moot/classify/soybean.csv",
               Path.home() / "gits/moot/classify/diabetes.csv"]:
    if not path.exists(): 
      return print(f"File not found: {path}")
    print(f"Naive Bayes (scaled 0..100) on: {path}\n")
    cf = classify(csv(str(path)))
    table(confused(cf), w=7)

# ---- 5. Distance ----
def test_distx(file:str=egopt1):
  """Test independent variable distance sorting."""
  d, r1 = Data(csv(file)), Data(csv(file)).rows[0]
  for r in sorted(d.rows, key=lambda r2: distx(d, r1, r2))[::30]: 
    print(*r, sep="\t")

def test_disty(file:str=egopt1):
  """Test dependent variable distance to optimal target."""
  d = Data(csv(file))
  for r in sorted(d.rows, key=lambda r: disty(d, r))[::30]: 
    print(*r, ":", round(disty(d, r), 2), sep="\t")

# ---- 6. Trees ----
def test_tree(file:str=egopt1): 
  """Test Rung 1: Show the associative properties of a grown tree."""
  _, d_train, _ = ready(file)
  treeShow(treeGrow(d_train, d_train.rows))

def test_see(file:str=egopt1):
    """Show tree built from active-learned examples."""
    _, d_train, _ = ready(file)
    lab = acquire(d_train)
    treeShow(treeGrow(d_train, lab.rows))

def test_funny(file:str=egopt1):
  """Test Rung 2: Run test rows down the tree to flag anomalies."""
  d, d_train, test = ready(file)
  t = treeGrow(d_train, d_train.rows)
  for r in sorted(test, key=lambda r: disty(d_train, r))[:10]:
    lf = treeLeaf(t, r)
    gap = disty(d_train, r) - mid(lf.ynum)
    flag = " !" if abs(gap) > spread(lf.ynum) else "  "
    print(f"{flag} actual={o(disty(d_train, r)):>5}  leaf={o(mid(lf.ynum)):>5}"
          f"  gap={o(gap):>6}  n={lf.ynum.n}")

def test_plan(file:str=egopt1):
  """Test Rung 3: Generate counterfactual plans to improve the worst row."""
  d, d_train, _ = ready(file)
  t = treeGrow(d_train, d_train.rows)
  here = treeLeaf(t, max(d.rows, key=lambda r: disty(d, r)))
  print(f"  now={o(mid(here.ynum))}")
  for dy, score, diff in sorted(treePlan(t, here)):
    print(f"  {o(score):>6} (dy={o(dy)}) if {', '.join(diff)}")

def test_acquire(file:str=egopt1):
  """Run full train/predict/score pipeline to optimize metrics.
  win1: same procedure on labelled (top-check by d2h, then best by d2h).
  win2: top-check by tree prediction on test, then best by actual d2h."""
  d0 = Data(csv(file))
  w1, w2n = Num(), Num()
  win = wins(d0)
  for _ in range(20):
    d, d_train, test_rows = ready(d0)
    lab = acquire(d_train)
    t = treeGrow(d_train, lab.rows)
    guess = sorted(test_rows, key=lambda r: mid(treeLeaf(t, r).ynum))
    add(w1, win(min(lab.rows[:the.learn.check], key=lambda r: disty(d_train, r))))
    add(w2, win(min(guess[:the.learn.check],    key=lambda r: disty(d_train, r))))
  print(f":budget {the.learn.budget} :check {the.learn.check} "
        f":train {int(mid(w1))} :test {int(mid(w2))}")

# ---- 7. Clustering ----
def test_cluster(file:str=egopt1):
  """Run clustering benchmark table comparing baseline, kmeans, and rhalf."""
  d = Data(csv(file)); k, near = 16, 1
  all_y = adds((disty(d, r) for r in d.rows), Num())
  
  results = []
  B  = lambda d1: [d1]
  S1 = lambda d1: [clone(d, sample(d.rows, 32))]
  RH = lambda d1: rhalf(d1, k=k)
  KM = lambda d1: kmeans(d1, k=k)
  KP = lambda d1: kmeans(d1, k=k, cents=kpp(d1, k=k))

  for txt, fn, fast in [("baseline", B, False), ("sample", S1, False),
                        ("rhalf", RH, False), ("kmeans", KM, False),
                        ("kpp", KP, False), ("rhalf f", RH, True),
                        ("kmeans f", KM, True), ("kpp f", KP, True)]:
    
    t_build, t_apply, err = clustering(d, fn, near, fast=fast)
    results.append(dict(Algorithm=txt, T_Build=t_build, 
                          T_Apply=t_apply, Err=err))
    
  print(f"Dataset small error threshold: {.35*spread(all_y):.2f}\n")
  table(results, w=12)

# ----- 8. Active learning -----
def test_acquire3(file:str=egopt1):
  """Test active learning with Bayes and centroid acquisition."""
  d = Data(csv(file))
  W = wins(d)
  Y = lambda r:disty(d,r)
  out = {}
  for _ in range(20):
    random.shuffle(d.rows)
    n       = len(d.rows)//2
    test    = d.rows[n:] 
    train   = d.rows[:n][:the.few]
    lab1    = train[:the.learn.budget]
    lab2 = acquire(clone(d,train))
    lab3 = acquire(clone(d,train),acquireWithCentroid)
    for how,lab in (("rand",lab1),("bayes",lab2.rows),("near",lab3.rows)):
       d2    = clone(d,lab)
       tree  = treeGrow(d2, d2.rows)
       guess = sorted(test, key=lambda r: mid(treeLeaf(tree,r).ynum))
       out[how] = out.get(how) or Num()
       add(out[how], W(sorted(guess[:the.learn.check],key=Y)[0]))
  for how,num in out.items(): print(int(mid(num)),how, end=" ")
  print(the.learn.budget,"budget")

# ---- 9. Search ----
def last(gen) -> Any:
  """Final value from generator."""
  v = None
  for v in gen: pass
  return v

def sa(d, oracle, restarts=0,
       m=0.5, budget=1000):
  """Simulated annealing."""
  n = max(1, int(m * len(d.cols.xs)))
  def accept(e, en, h, b):
    return en<e or rand()<exp(
             (e-en)/(1-h/b+1E-32))
  def mutate(s): yield picks(d, s, n)
  return oneplus1(d, mutate, accept,
                  oracle, budget, restarts)

def ls(d, oracle, restarts=100,
       p=0.5, tries=20, budget=1000):
  """Local search."""
  def accept(e, en, *_): return en < e
  def mutate(s):
    c = choice(d.cols.xs)
    for _ in range(tries if rand()<p else 1):
      s = s[:]
      s[c.at] = pick(c, s[c.at])
      yield s
  return oneplus1(d, mutate, accept,
                  oracle, budget, restarts)

def test_sa(file:str=egopt1):
  """Demo simulated annealing on sample data."""
  d0 = Data(csv(file))
  shuffle(d0.rows)
  known = clone(d0, d0.rows[:50])
  search = clone(d0, d0.rows[50:])
  oracle = lambda r: oracleNearest(known, r)
  print(f"{'evals':>6} {'energy':>7}")
  for h, e, row in sa(search, oracle):
    print(f"  {h:4}   {o(e):>5}")

def test_ls(file:str=egopt1):
  """Demo local search on sample data."""
  d0 = Data(csv(file))
  shuffle(d0.rows)
  known = clone(d0, d0.rows[:50])
  search = clone(d0, d0.rows[50:])
  oracle = lambda r: oracleNearest(known, r)
  print(f"{'evals':>6} {'energy':>7}")
  for h, e, row in ls(search, oracle):
    print(f"  {h:4}   {o(e):>5}")

def test_compare(file:str=egopt1):
  """Compare sa, ls, ls-noRestart, sa+restart (x20)."""
  d0 = Data(csv(file))
  W = wins(d0)
  out = {}
  for _ in range(20):
    shuffle(d0.rows)
    known = clone(d0, d0.rows[:50])
    search = clone(d0, d0.rows[50:])
    oracle = lambda r: oracleNearest(known, r)
    for name, fn in [
        ("sa-r", lambda d: sa(d, oracle)),
        ("ls+r", lambda d: ls(d, oracle)),
        ("ls-r", lambda d: ls(d, oracle, restarts=0)),
        ("sa+r", lambda d: sa(d, oracle, restarts=100))]:
      _, _, r = last(fn(search))
      if name not in out: out[name] = Num(name)
      add(out[name], W(r))
  print("\n",file)
  for k, v in sorted(out.items()):
    print(f"  {k:5} {o(mid(v)):>5} +/- {o(spread(v))}")
   
# ---- 10. Text mining -----
egcnb = Path.home() / "gits/moot/text_mining/reading/processed/Hall.csv"
egtxt = Path.home() / "gits/moot/text_mining/reading/Hall.csv"

def _need(f, *cols) -> str:
  """Return str(f) if file exists with required header cols, else skip (pytest) / fail."""
  p, msg = Path(f), None
  if not p.exists(): msg = f"missing {f}"
  elif cols and not all(c in next(tm._csv(str(p))) for c in cols):
    msg = f"{f} missing one of {cols}"
  if msg and "pytest" in globals(): pytest.skip(msg)
  if msg: raise AssertionError(msg)
  return str(p)

def test_cnb_like(file:str=egcnb):
  """Show CNB scores for first 5 rows."""
  data = Data(csv(_need(file, "klass!"))); ws = tm.cnb(data)
  rows = [["want", "got", "score"]]
  for r in data.rows[:5]:
    sc = max(tm.cnbLikes(ws, data, r, k) for k in ws)
    rows.append([r[data.cols.klass.at], tm._best(ws, data, r), round(sc, 2)])
  tm._align(rows)

def test_cnb_sweep(file:str=egcnb):
  """Vary sample size: 10, 20, 40."""
  f = _need(file, "klass!")
  for y in [10, 20, 40]:
    the.textmine.yes = the.textmine.no = y; tm.text_mining(f)

def test_cnb_data(file:str=egcnb):
  """Random baseline evaluation."""
  return tm.text_mining(_need(file, "klass!"))

def test_cnb_active(file:str=egcnb):
  """Active learning: warm start then acquire to budget."""
  return tm.active(_need(file, "klass!"))

def test_tokenize(file:str=egtxt):
  """Tokenize a text-mining CSV."""
  p = tm.tokenize(_need(file, "abstract", "label"))
  print(f"{len(p.docs)} docs")
  for d in p.docs[:3]: print(d.words[:8])

def test_nostop(file:str=egtxt):
  """Stop word removal demo."""
  p = tm.tokenize(_need(file, "abstract", "label")); b = p.docs[0].words[:12][:]
  tm.nostop(p)
  print(f"removed: {[w for w in b if w not in p.docs[0].words]}")
  print(f"before:  {b}\nafter:   {p.docs[0].words[:12]}")

def test_stem(file:str=egtxt):
  """Stemming demo."""
  p = tm.nostop(tm.tokenize(_need(file, "abstract", "label")))
  b = p.docs[0].words[:8][:]; tm.stem(p)
  for a, b1 in zip(b, p.docs[0].words[:8]): print(f"{a} -> {b1}")

def test_tfidf(file:str=egtxt):
  """TF-IDF top features."""
  p = tm.prepare(_need(file, "abstract", "label"))
  tm._align([[w, round(s, 2)] for w, s in p.top[:20]])

# ---- Go? -----
if __name__ == "__main__": cli()
