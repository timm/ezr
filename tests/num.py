import sys; sys.path.append("..")
from ezr import NUM,adds,mid,div
import random

s = adds(NUM(),[random.random()**0.5 for _ in range(1000)])
print(round(mid(s),3), round(div(s),3))
