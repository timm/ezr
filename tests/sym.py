import sys; sys.path.insert(0, "../")
from ezr import Sym,go

def eg__sym(_):
  sym = Sym("aaaabbc")
  assert "a"==sym.mid() and 1.3 < sym.spread() < 1.4

go(globals())


