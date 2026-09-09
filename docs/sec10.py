def test_tree():
  "Acquire, grow and show the.File's tree"
  tbl = Tbl(csv(the.File)); lab = acquire(tbl)
  print(f"{the.File} n={len(tbl.rows)}"
        f" mid={round(ymu(tbl, tbl.rows), 3)}"
        f" ezr={round(ydist(tbl, lab[0]), 3)}")
  show(tbl, tree(tbl, lab))

def test_holdout():
  "Mean win over 20 train/test holdouts"
  tbl = Tbl(csv(the.File))
  win = wins(tbl)
  mu = sum(win(holdout(tbl)) for _ in range(20)) / 20
  print(f"win {round(mu)}")

def _klass(*fits): # each fit(tbl, rows, y) --> predictor(row)
  tbl = Tbl(csv(the.Klass))
  y = lambda r: r[tbl.klass]
  n = len(tbl.rows) // 2
  splits = [random.sample(tbl.rows, len(tbl.rows))
            for _ in range(the.Repeats)] # same splits, all fits
  def one(fit):
    accs, pairs = [], []
    for rows in splits:
      got = fit(tbl, rows[:n], y)
      now = [(got(r), y(r)) for r in rows[n:]]
      pairs += now
      accs += [sum(g == w for g, w in now) / len(now)]
    for c in confuse(pairs).values():
      pc = lambda v: round(100 * v)
      print(f"{fit.__name__:<10} {pc(c.acc):>3} {pc(c.pd):>3}"
            f" {pc(c.pf):>3} {pc(c.prec):>4}"
            f" {tbl.cols[tbl.klass].get(c.l, 0):>6}  {c.l}")
    return accs
  print(f"{'rx':<10} {'acc':>3} {'pd':>3} {'pf':>3}"
        f" {'prec':>4} {'n':>6}  class")
  return [one(fit) for fit in fits]

def fitTree(tbl, rows, y): # sqrt-sized leaves
  the.Leaf = int(sqrt(len(rows)))
  tt = tree(clone(tbl, rows), rows, y=y)
  return lambda r: leaf(tt, r)[2]

def fitBayes(tbl, rows, y):
  tbls = {}
  for r in rows:
    if y(r) not in tbls: tbls[y(r)] = clone(tbl)
    addRow(tbls[y(r)], r)
  return lambda r: liked(tbls, r)

def test_klass():
  "Tree vs bayes, same splits: confusions, then same?"
  a, b = _klass(fitTree, fitBayes)
  x, z = adds(a), adds(b)
  print(f"\nfitTree {round(100*x[1])} ({round(100*sd(x))})"
        f" fitBayes {round(100*z[1])} ({round(100*sd(z))})"
        f" delta {round(100*abs(x[1] - z[1]))}"
        f" : {'same' if same(a, b, eps=0.01) else 'different'}")

def test_same():
  "Stats tests tell noise from signal"
  x = [random.gauss(10, 1) for _ in range(40)]
  y = [random.gauss(10, 1) for _ in range(40)]
  z = [random.gauss(11, 1) for _ in range(40)]
  assert same(x, y) and not same(x, z)
  print(f"same {same(x, y)} diff {not same(x, z)}")

def test_all():
  "Run every demo; exit code counts the crashes"
  sys.exit(sum(print(f"\n# {k[5:]}") or run(f)
               for k, f in list(globals().items())
               if k[:5] == "test_" and f is not test_all))
