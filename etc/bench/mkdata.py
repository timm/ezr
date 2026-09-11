#!/usr/bin/env python3
"""Regenerate data.csv and gauss.txt. Both are committed; this only
documents how they were made. Seeded, so output is reproducible."""
import random

random.seed(1)
with open("data.csv", "w") as f:
  print("Clndrs,Volume,Model,origin,Lbs-,Acc+,Mpg+", file=f)
  for _ in range(200):
    print(",".join(str(x) for x in [
      random.choice([3, 4, 6, 8]), random.randint(70, 455),
      random.randint(70, 82), random.choice(["1", "2", "3"]),
      random.randint(1600, 5000), round(random.uniform(8, 25), 1),
      random.choice([10, 20, 30, 40])]), file=f)

random.seed(1)
with open("gauss.txt", "w") as f:
  for mu in (10, 10, 11):
    print(",".join(repr(random.gauss(mu, 1)) for _ in range(40)), file=f)
