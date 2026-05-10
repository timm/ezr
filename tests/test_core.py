"""Core primitives: Num, Sym, Data, Cols, csv, distance, formatting, config."""
from conftest import *
from ezr import *

def test_o():
  class Tmp:
    def __init__(i): i.x, i.y = 1, 2
  s_float = o(3.14159)
  s_list  = o([1, {"a": 2}, Tmp()])
  assert s_float.startswith("3.14")
  assert "Tmp{" in s_list and "x=1" in s_list and "y=2" in s_list
  assert "a=2" in s_list

def test_table():
  import io, contextlib
  lst = [{"name": "tim", "age": 21}, {"name": "tom", "age": 22}]
  buf = io.StringIO()
  with contextlib.redirect_stdout(buf): table(lst, w=8)
  out = buf.getvalue()
  lines = [l for l in out.splitlines() if l]
  assert len(lines) == 4
  assert "name" in lines[0]
  assert "tim" in lines[2]

def test_thing():
  assert thing("3.14") == 3.14
  assert thing(" true ") in [True, 1]
  assert thing(" false ") in [False, 0]
  assert thing("hello") == "hello"

def test_nest():
  t = S()
  nest(t, "a.b.c", 42)
  assert t.a.b.c == 42

def test_the():
  assert int == type(the.seed)

def test_csv():
  assert len(list(csv(str(EGOPT1)))) > 10

def test_num():
  c = adds([10, 20, 30, 40, 50], Num())
  assert c.mu == 30 and 15.8 < spread(c) < 15.9

def test_sym():
  c = adds("aaabbc", Sym())
  assert mid(c) == "a" and 1.4 < spread(c) < 1.5

def test_pick():
  c1 = adds([10, 20, 30, 40, 50], Num())
  c2 = adds(pick(c1) for _ in range(10000))
  assert abs(mid(c1) - mid(c2)) < 0.25
  assert abs(spread(c1) - spread(c2)) < 0.25
  c1 = adds("aaabbc", Sym())
  c2 = adds([pick(c1) for _ in range(1000)], Sym())
  assert mid(c1) == mid(c2)
  assert abs(spread(c1) - spread(c2)) < 0.1

def test_cols():
  cols = Cols(["name", "Age", "Weight-"])
  assert not cols.ys[0].heaven
  assert len(cols.xs) == 2 and len(cols.ys) == 1

def test_data():
  d = Data(csv(str(EGOPT1)))
  assert len(d.rows) > 0 and len(d.cols.ys) > 0

def test_addsub():
  d  = Data(csv(str(EGOPT1)))
  d2 = clone(Data(csv(str(EGOPT1))))
  for r in d.rows: add(d2, r)
  for r in d.rows: sub(d2, r)
  assert d2.cols.ys[0].n == 0

def test_distx():
  d = Data(csv(str(EGOPT1)))
  r1 = d.rows[0]
  assert distx(d, r1, r1) == 0
  srt = sorted(d.rows, key=lambda r2: distx(d, r1, r2))
  assert srt[0] == r1

def test_disty():
  d = Data(csv(str(EGOPT1)))
  ds = [disty(d, r) for r in d.rows]
  assert min(ds) >= 0 and max(ds) <= 1.0001

def test_extrapolate():
  d = Data(csv(str(EGOPT1)))
  a, b, c = d.rows[0], d.rows[1], d.rows[2]
  out = extrapolate(d.cols.xs, a, b, c, 0.5)
  for col in d.cols.ys:
    assert out[col.at] == a[col.at]
  out_all = extrapolate(d.cols.all, a, b, c, 0.5)
  assert len(out_all) == len(a)
