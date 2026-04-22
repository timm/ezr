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
  """Run full train/predict/score pipeline to optimize metrics."""
  d0 = Data(csv(file))
  train_w, test_w, win = Num(), Num(), wins(d0)
  for _ in range(20):
    d, d_train, test_rows = ready(d0)
    lab = acquire(d_train)
    t = treeGrow(d_train, lab.rows)
    guess = sorted(test_rows, key=lambda r: mid(treeLeaf(t, r).ynum))
    add(test_w,  win(min(guess[:the.learn.check], key=lambda r: disty(d_train, r))))
    add(train_w, win(min(lab.rows,                key=lambda r: disty(d_train, r))))
  print(f":train_wins_mu {int(mid(train_w))} :train_wins_sd {int(spread(train_w))} "
        f":test_wins_mu {int(mid(test_w))} :test_wins_sd {int(spread(test_w))}")

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
