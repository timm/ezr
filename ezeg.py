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
  --test  file          train/predict/score pipeline   
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

def test_test(file:str=egopt1):
  """Run full train/predict/score pipeline to optimize metrics."""
  d0 = Data(csv(file))
  outs, win = Num("win"), wins(d0)
  for _ in range(20):
    d, d_train, test_rows = ready(d0)
    t = treeGrow(d_train, acquire(d_train).rows)
    guess = sorted(test_rows, key=lambda r: mid(treeLeaf(t, r).ynum))
    top = min(guess[:the.learn.check], key=lambda r: disty(d_train, r))
    add(outs, win(top))
  print(int(mid(outs)))

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
def test_acquire(file:str=egopt1):
  """Test active learning with Bayes and centroid acquisition."""
  d = Data(csv(file))
  W = wins(d)
  Y = lambda r:disty(d,r)
  n = len(d.rows)//2
  out = Num()
  for _ in range(20):
    random.shuffle(d.rows)
    test = d.rows[n:] 
    traind = acquire( clone(d, d.rows[:n][:the.few]))
    tree  = treeGrow(traind, traind.rows)
    guess = sorted(test, key=lambda r: mid(treeLeaf(tree,r).ynum))
    add(out, W(min(guess[:the.learn.check],key=Y)))
  print(int(out.mu), int(out.sd))

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

if __name__ == "__main__": cli()
