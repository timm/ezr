import sys; sys.path.insert(0, "../")
from ezr import Sym

sym = Sym("aaaabbc")
assert "a"==sym.mid() and 1.3 < sym.spread() < 1.4


