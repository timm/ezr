"""Search: sa, ls, de — assert energy decreases over budget."""
from conftest import *
from ezr import *
from search import sa, ls, de, oracleNearest, last

def _setup():
  d0 = Data(csv(str(EGOPT1)))
  shuffle(d0.rows)
  known = clone(d0, d0.rows[:50])
  search = clone(d0, d0.rows[50:])
  oracle = lambda r: oracleNearest(known, r)
  return d0, search, oracle

def test_sa():
  _, search, oracle = _setup()
  energies = [e for _, e, _ in sa(search, oracle, budget=500)]
  assert energies and energies[-1] < energies[0]

def test_ls():
  _, search, oracle = _setup()
  energies = [e for _, e, _ in ls(search, oracle, budget=500)]
  assert energies and energies[-1] < energies[0]

def test_de():
  _, search, oracle = _setup()
  energies = [e for _, e, _ in de(search, oracle, budget=500)]
  assert energies and energies[-1] < energies[0]

def test_compare():
  d0, search, oracle = _setup()
  W = wins(d0)
  out = {}
  for _ in range(5):
    shuffle(d0.rows)
    known  = clone(d0, d0.rows[:50])
    srch   = clone(d0, d0.rows[50:])
    orcle  = lambda r: oracleNearest(known, r)
    for name, fn in [("sa+r", lambda d: sa(d, orcle, restarts=100, budget=500)),
                     ("ls+r", lambda d: ls(d, orcle, budget=500)),
                     ("de  ", lambda d: de(d, orcle, budget=500))]:
      _, _, r = last(fn(srch))
      out.setdefault(name, Num(name))
      add(out[name], W(r))
  for k, v in out.items():
    assert mid(v) > 0, f"{k} mean wins {mid(v):.1f} <= median d2h"
