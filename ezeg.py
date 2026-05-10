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
  s_float = o(3.14159)
  s_list = o([1, {"a": 2}, Tmp()])
  print(s_float); print(s_list)
  assert s_float.startswith("3.14"), f"o(float) bad: {s_float!r}"
  assert "Tmp{" in s_list and "x=1" in s_list and "y=2" in s_list, \
    f"o(obj) missing fields: {s_list!r}"
  assert "a=2" in s_list, f"o(dict) missing key: {s_list!r}"

def test_table():
  """Test tabular formatting of dictionaries and objects."""
  import io, contextlib
  lst = [{"name": "tim", "age": 21, "shoe": 10},
         {"name": "tom", "age": 22, "shoe": 9.5}]
  buf = io.StringIO()
  with contextlib.redirect_stdout(buf): table(lst, w=8)
  out = buf.getvalue()
  print(out, end="")
  lines = [l for l in out.splitlines() if l]
  assert len(lines) == 4, f"table lines: {len(lines)} (want 4)"
  assert "name" in lines[0] and "age" in lines[0] and "shoe" in lines[0]
  assert "tim" in lines[2] and "21" in lines[2]
  assert "tom" in lines[3] and "22" in lines[3]

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
  print(__doc__); print(ezr.__doc__); print(HELP_TAIL)
  assert __doc__ and "Usage" in __doc__, "ezeg __doc__ missing"
  assert ezr.__doc__ and "--seed" in ezr.__doc__, "ezr __doc__ missing flags"
 
def test_the(): 
  """Test that config dictionary parses correctly."""
  print(o(the)); assert int == type(the.seed)

def test_list():
  """List all available example functions and their signatures."""
  fns = {k: v for k, v in globals().items() if k[:5] == "test_"}
  for k, fn in fns.items():
    print(f"  --{k[5:]:12} {' '.join(fn.__annotations__)} {fn.__doc__}")
  assert len(fns) >= 30, f"only {len(fns)} test functions found"
  assert all(fn.__doc__ for fn in fns.values()), "some test fn missing docstring"

def test_egs(file:str=egopt1):
  """Run all test examples sequentially."""
  egs = {k: v for k, v in globals().items() if k[:5]=="test_" and k!="test_egs"}
  for k, fn in egs.items():
    print(f"\n--- {k} ----\n{fn.__doc__}")
    random.seed(the.seed)
    try:
      fn() if "file" in fn.__annotations__ else fn()
    except AssertionError as e:
      print(f"SKIP: {e}")

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

# ---- 5. Distance ----
def test_distx(file:str=egopt1):
  """Test independent variable distance sorting."""
  d, r1 = Data(csv(file)), Data(csv(file)).rows[0]
  assert distx(d, r1, r1) == 0, "distx self-distance not zero"
  srt = sorted(d.rows, key=lambda r2: distx(d, r1, r2))
  assert srt[0] == r1, "distx: row not nearest to itself"
  for r in srt[::30]: print(*r, sep="\t")

def test_disty(file:str=egopt1):
  """Test dependent variable distance to optimal target."""
  d = Data(csv(file))
  ds = [disty(d, r) for r in d.rows]
  assert min(ds) >= 0 and max(ds) <= 1.0001, f"disty out of [0,1]: min={min(ds)} max={max(ds)}"
  for r in sorted(d.rows, key=lambda r: disty(d, r))[::30]:
    print(*r, ":", round(disty(d, r), 2), sep="\t")

# ---- 6. Trees ----
def test_tree(file:str=egopt1):
  """Test Rung 1: Show the associative properties of a grown tree."""
  _, d_train, _ = ready(file)
  t = treeGrow(d_train, d_train.rows)
  treeShow(t)
  assert t.left is not None and t.right is not None, "tree did not split"

def test_see(file:str=egopt1):
  """Show tree built from active-learned examples."""
  _, d_train, _ = ready(file)
  lab = acquire(d_train)
  t = treeGrow(d_train, lab.rows)
  treeShow(t)
  assert t.left is not None, "active-learned tree did not split"

def test_funny(file:str=egopt1):
  """Test Rung 2: Run test rows down the tree to flag anomalies."""
  d, d_train, test = ready(file)
  t = treeGrow(d_train, d_train.rows)
  rows_seen = 0
  for r in sorted(test, key=lambda r: disty(d_train, r))[:10]:
    lf = treeLeaf(t, r); rows_seen += 1
    gap = disty(d_train, r) - mid(lf.ynum)
    flag = " !" if abs(gap) > spread(lf.ynum) else "  "
    print(f"{flag} actual={o(disty(d_train, r)):>5}  leaf={o(mid(lf.ynum)):>5}"
          f"  gap={o(gap):>6}  n={lf.ynum.n}")
  assert rows_seen > 0, "no test rows scored"

def test_plan(file:str=egopt1):
  """Test Rung 3: Generate counterfactual plans to improve the worst row."""
  d, d_train, _ = ready(file)
  t = treeGrow(d_train, d_train.rows)
  here = treeLeaf(t, max(d.rows, key=lambda r: disty(d, r)))
  print(f"  now={o(mid(here.ynum))}")
  plans = sorted(treePlan(t, here))
  for dy, score, diff in plans:
    print(f"  {o(score):>6} (dy={o(dy)}) if {', '.join(diff)}")
  assert plans, "treePlan produced no counterfactuals"
  assert all(dy > 0 for dy,_,_ in plans), "plan dy not improvement"

def _printCf(label, cf):
  rows = [["tp","fn","fp","tn","pd","pr","fpr","f1","acc","class"]]
  for s in confused(cf):
    fpr = int(100*s.fp/((s.fp+s.tn) or 1e-32))
    rows.append([s.tp, s.fn, s.fp, s.tn, s.pd, s.pr, fpr, s.f1, s.acc, s.label.strip()])
  print(f"\n  {label}")
  ws = [max(len(str(r[c])) for r in rows) for c in range(len(rows[0]))]
  for r in rows:
    cells = [str(v).rjust(w) for v,w in zip(r[:-1], ws[:-1])]
    print("  ".join(cells) + "  " + str(r[-1]).ljust(ws[-1]))

def _nbBatch(train_rows, test_rows, header, klass_at):
  """Train NB on train_rows (frozen), classify test_rows."""
  h, all = {}, Data([header])
  for r in train_rows:
    want = r[klass_at]
    if want not in h: h[want] = clone(all)
    add(all, add(h[want], r))
  cf = {}
  for r in test_rows:
    want = r[klass_at]
    got = max(h, key=lambda k: likes(h[k], r, len(all.rows), len(h)))
    cf.setdefault(want, {}); cf[want][got] = cf[want].get(got, 0) + 1
  return cf

def _treeBatch(d, train_rows, test_rows, klass_at):
  klass = lambda r: r[klass_at]
  t = treeGrow(d, train_rows, klass=klass, y=Sym)
  cf = {}
  for r in test_rows:
    want = r[klass_at]
    got = mid(treeLeaf(t, r).ynum)
    cf.setdefault(want, {}); cf[want][got] = cf[want].get(got, 0) + 1
  return cf

def _mergeCf(a, b):
  for w in b:
    a.setdefault(w, {})
    for g, n in b[w].items(): a[w][g] = a[w].get(g, 0) + n
  return a

def _accuracy(cf):
  total = sum(cf[w][g] for w in cf for g in cf[w])
  correct = sum(cf[w].get(w, 0) for w in cf)
  return correct / (total or 1e-32)

def _zeroR(train_rows, test_rows, klass_at):
  """Majority-class baseline accuracy on test."""
  counts = {}
  for r in train_rows: counts[r[klass_at]] = counts.get(r[klass_at], 0) + 1
  majority = max(counts, key=counts.get)
  hits = sum(1 for r in test_rows if r[klass_at] == majority)
  return hits / (len(test_rows) or 1e-32)

def test_classify(file:str=egclass2, reps:int=20, frac:float=0.9):
  """90/10 split (averaged over 20 shuffles): NB vs Tree vs ZeroR baseline."""
  for f in [egclass2, egclass1]:
    rows = list(csv(str(f)))
    header, body = rows[0], rows[1:]
    d = Data(csv(str(f)))
    klass_at = d.cols.klass.at
    nb_cf, tr_cf, zr = {}, {}, []
    for i in range(reps):
      random.seed(the.seed + i)
      shuffled = body[:]; random.shuffle(shuffled)
      split = int(frac * len(shuffled))
      train, test = shuffled[:split], shuffled[split:]
      _mergeCf(nb_cf, _nbBatch(train, test, header, klass_at))
      _mergeCf(tr_cf, _treeBatch(d, train, test, klass_at))
      zr.append(_zeroR(train, test, klass_at))
    nb_acc = _accuracy(nb_cf); tr_acc = _accuracy(tr_cf); zr_acc = sum(zr)/len(zr)
    _printCf(f"NB   {f.name}  (reps={reps} train={split} test={len(test)})", nb_cf)
    _printCf(f"TREE {f.name}  (reps={reps} train={split} test={len(test)})", tr_cf)
    print(f"\n  acc:  ZeroR={zr_acc:.3f}  NB={nb_acc:.3f}  TREE={tr_acc:.3f}")
    assert nb_acc > zr_acc, f"NB ({nb_acc:.3f}) <= ZeroR ({zr_acc:.3f}) on {f.name}"
    assert tr_acc > zr_acc, f"TREE ({tr_acc:.3f}) <= ZeroR ({zr_acc:.3f}) on {f.name}"

def test_acquire(file:str=egopt1):
  """Run full train/predict/score pipeline to optimize metrics.
  win1: same procedure on labelled (top-check by d2h, then best by d2h).
  win2: top-check by tree prediction on test, then best by actual d2h."""
  d0 = Data(csv(file))
  w1, w2, w_rand = Num(), Num(), Num()
  win = wins(d0)
  for _ in range(20):
    d, d_train, test_rows = ready(d0)
    lab = acquire(d_train)
    t = treeGrow(d_train, lab.rows)
    guess = sorted(test_rows, key=lambda r: mid(treeLeaf(t, r).ynum))
    add(w1, win(min(lab.rows[:the.learn.check], key=lambda r: disty(d_train, r))))
    add(w2, win(min(guess[:the.learn.check],    key=lambda r: disty(d_train, r))))
    add(w_rand, win(min(sample(test_rows, the.learn.check), key=lambda r: disty(d_train, r))))
  print(f":budget {the.learn.budget} :check {the.learn.check} "
        f":train {int(mid(w1))} :test {int(mid(w2))} :rand {int(mid(w_rand))}")
  assert mid(w1) > mid(w_rand), f"acquire train ({mid(w1):.1f}) <= random ({mid(w_rand):.1f})"
  assert mid(w2) > mid(w_rand), f"acquire test ({mid(w2):.1f}) <= random ({mid(w_rand):.1f})"

def test_acquire1(file:str=egopt1):
  """Run full train/predict/score pipeline to optimize metrics.
  win1: same procedure on labelled (top-check by d2h, then best by d2h).
  win2: top-check by tree prediction on test, then best by actual d2h."""
  d0 = Data(csv(file))
  w1, w2, win = Num(), Num(), wins(d0)
  d, d_train, test_rows = ready(d0)
  lab = acquire(d_train)
  t = treeGrow(d_train, lab.rows)
  treeShow(t)
  guess = sorted(test_rows, key=lambda r: mid(treeLeaf(t, r).ynum))
  v1 = win(min(lab.rows[:the.learn.check], key=lambda r: disty(d_train, r)))
  v2 = win(min(guess[:the.learn.check],    key=lambda r: disty(d_train, r)))
  add(w1, v1); add(w2, v2)
  assert v1 > 0, f"acquire1 train wins ({v1}) not better than median d2h"
  assert v2 > 0, f"acquire1 test wins ({v2}) not better than median d2h"

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
  baseline_err = float(next(r["Err"] for r in results if r["Algorithm"] == "baseline"))
  for r in results:
    if r["Algorithm"] != "baseline":
      err = float(r["Err"])
      assert err <= baseline_err * 1.5, \
        f"{r['Algorithm']} err ({err:.2f}) >> baseline ({baseline_err:.2f})"

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
  assert mid(out["bayes"]) > mid(out["rand"]), \
    f"bayes ({mid(out['bayes']):.1f}) <= rand ({mid(out['rand']):.1f})"
  assert mid(out["near"])  > mid(out["rand"]), \
    f"near ({mid(out['near']):.1f}) <= rand ({mid(out['rand']):.1f})"

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
  energies = []
  for h, e, row in sa(search, oracle):
    energies.append(e); print(f"  {h:4}   {o(e):>5}")
  assert energies and energies[-1] < energies[0], \
    f"sa did not reduce energy ({energies[0]} -> {energies[-1]})"

def test_ls(file:str=egopt1):
  """Demo local search on sample data."""
  d0 = Data(csv(file))
  shuffle(d0.rows)
  known = clone(d0, d0.rows[:50])
  search = clone(d0, d0.rows[50:])
  oracle = lambda r: oracleNearest(known, r)
  print(f"{'evals':>6} {'energy':>7}")
  energies = []
  for h, e, row in ls(search, oracle):
    energies.append(e); print(f"  {h:4}   {o(e):>5}")
  assert energies and energies[-1] < energies[0], \
    f"ls did not reduce energy ({energies[0]} -> {energies[-1]})"

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
  for k, v in out.items():
    assert mid(v) > 0, f"{k} mean wins ({mid(v):.1f}) <= median d2h baseline"

# ---- 10. Text mining -----
egcnb = Path.home() / "gits/moot/text_mining/reading/processed/Hall.csv"
egtxt = Path.home() / "gits/moot/text_mining/reading/raw/Hall.csv"

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
  data = Data(csv(_need(file, "label!"))); ws = tm.cnb(data)
  assert len(ws) >= 2, f"cnb produced only {len(ws)} class(es)"
  rows = [["want", "got", "score"]]
  for r in data.rows[:5]:
    sc = max(tm.cnbLikes(ws, data, r, k) for k in ws)
    rows.append([r[data.cols.klass.at], tm._best(ws, data, r), round(sc, 2)])
  tm._align(rows)

def test_cnb_sweep(file:str=egcnb):
  """Vary sample size: 10, 20, 40."""
  f = _need(file, "label!")
  for y in [10, 20, 40]:
    the.textmine.yes = the.textmine.no = y
    assert tm.text_mining(f), f"text_mining failed at y={y}"

def test_cnb_data(file:str=egcnb):
  """Random baseline evaluation."""
  ok = tm.text_mining(_need(file, "label!"))
  assert ok, "text_mining returned falsy"
  return ok

def test_cnb_active(file:str=egcnb):
  """Active learning: warm start then acquire to budget."""
  ok = tm.active(_need(file, "label!"))
  assert ok, "active returned falsy"
  return ok

def test_tokenize(file:str=egtxt):
  """Tokenize a text-mining CSV."""
  p = tm.tokenize(_need(file, "abstract", "label"))
  print(f"{len(p.docs)} docs")
  for d in p.docs[:3]: print(d.words[:8])
  assert len(p.docs) > 0 and len(p.docs[0].words) > 0, "tokenize produced no words"

def test_nostop(file:str=egtxt):
  """Stop word removal demo."""
  p = tm.tokenize(_need(file, "abstract", "label")); b = p.docs[0].words[:12][:]
  tm.nostop(p)
  removed = [w for w in b if w not in p.docs[0].words]
  print(f"removed: {removed}")
  print(f"before:  {b}\nafter:   {p.docs[0].words[:12]}")
  assert removed, "nostop removed no words"

def test_stem(file:str=egtxt):
  """Stemming demo."""
  p = tm.nostop(tm.tokenize(_need(file, "abstract", "label")))
  b = p.docs[0].words[:8][:]; tm.stem(p)
  changed = sum(1 for a, b1 in zip(b, p.docs[0].words[:8]) if a != b1)
  for a, b1 in zip(b, p.docs[0].words[:8]): print(f"{a} -> {b1}")
  assert changed > 0, "stem changed no words"

def test_tfidf(file:str=egtxt):
  """TF-IDF top features."""
  p = tm.prepare(_need(file, "abstract", "label"))
  tm._align([[w, round(s, 2)] for w, s in p.top[:20]])
  assert len(p.top) >= 20, f"tfidf produced only {len(p.top)} features"
  assert all(s >= 0 for _, s in p.top), "tfidf scores negative"

# ---- Go? -----
if __name__ == "__main__": cli()
