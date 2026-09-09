#-- start-up ----------------------------------------------
def test_help():
  "Show usage, settings, demos"
  print(__doc__, "Demos:\n",
        *[f"  --{k[5:]:<10} {f.__doc__}"
          for k, f in globals().items() if k[:5] == "test_"],
        sep="\n")

def test_num():
  "Welford add matches textbook mean and sd"
  c = adds([2, 4, 4, 4, 5, 5, 7, 9])
  assert c[0] == 8 and c[1] == 5 and abs(sd(c)-2.138) < .01
  print(f"mu {c[1]} sd {round(sd(c), 3)}")

def test_sym():
  "Syms count; mid is mode; div is entropy"
  c = adds("aabbbc", Sym())
  assert c["b"]==3 and mid(c)=="b" and abs(div(c)-1.459)<.01
  print(f"mode {mid(c)} ent {round(div(c), 3)}")

def test_tbl():
  "Headers route columns to x, y, klass, or nowhere"
  t = Tbl([("Age","job!","SkipX","Weight-"), (2,"a",3,80)])
  assert t.x == [0] and t.y == {3: False} and t.klass == 1
  assert 2 not in t.cols
  print(f"x {t.x} y {t.y} klass {t.klass}")

def test_cuts():
  "cut returns a legal, routable split"
  t = Tbl(csv(the.File))
  rows = t.rows[:64]; ys = [ydist(t, r) for r in rows]
  at, v = cut(t, rows, ys, Num)
  e1, e2, go = routing(t, at, v)
  yes = sum(go(r) for r in rows)
  assert 0 < yes < len(rows)
  print(f"cut: {e1} yes={yes}; {e2} no={len(rows)-yes}")

def test_wins():
  "wins grades the best row 100"
  t = Tbl(csv(the.File))
  w = wins(t)(min(t.rows, key=lambda r: ydist(t, r)))
  assert w == 100; print(f"best row wins {w}")
