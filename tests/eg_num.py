import random,sys; sys.path.insert(0, "../oo")

from num import Num

random.seed(1234567891)
num = Num([random.gauss(10,2) for _ in range(1000)])
assert 10 < num.mid() < 10.2 and 2 < num.spread() < 2.1
