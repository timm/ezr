#!/usr/bin/env python3 -B
import sys; import matplotlib.pyplot as plt
xs,ys = zip(*[map(float, l.split()) for l in sys.stdin if l.strip()])
plt.scatter(xs, ys,s=1); plt.grid(); plt.show()
