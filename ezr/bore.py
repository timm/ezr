#!/usr/bin/env python3 -B
import sys, random
from ez import DATA, csv, disty, bucket, the,adds,BIG,o

def bore(data):
  def score(b, r): return b**2 / (b + r + 1e-30)

  def counts(best,rest):
    bestd,restd = {},{}
    for col in data.cols.x:
      for rows,d,n in ((best,bestd,B), (rest,restd,R)):
        for row in rows:
          if (v := row[col.at]) != "?":
            k     = (col.at, bucket(col,v))
            lo[k] = min(lo[k],v)
            hi[k] = max(hi[k],v)
            d[k]  = d.get(k,0) + 1 / n
    return bestd,restd

  def walk(best,rest):
    if rest and len(best) > the.leaf:
      bestd,restd = counts(best,rest)
      at,b = max(bestd, key=lambda k: score(bestd.get(k,0), restd.get(k,0)))
      col  = data.cols.all[at]
      best1 = [row for row in best if b == bucket(col,row[col.at])]
      if len(best1) < len(best):
        s = adds(disty(data,row) for row in best1)
        yield (col.txt,at,lo[(at,b)],hi[(at,b)],s.n, s.mu,at,b)
        yield from walk(best1, 
                          [row for row in rest if b == bucket(col,row[col.at])])
  
  lo = {(col.at,b):  BIG for col in data.cols.x for b in range(the.bins)}
  hi = {(col.at,b): -BIG for col in data.cols.x for b in range(the.bins)}
  data.rows.sort(key=lambda r: disty(data, r))
  n = int(len(data.rows)**0.5)
  B,R = n, len(data.rows) - n
  return list(walk(rows[:n],rows[n:]))

if __name__ == "__main__":
  d = DATA(csv("auto93.csv")) #
  rules = bore(d)
  print(f"\n{'Rule (Conjunction)':<30} | {'Score'}")
  print("-" * 45)
  for txt, at, lo, hi,n,mu,*_ in rules:
     print(f"IF {txt:<12} in [{o(lo):>4} .. {o(hi):>4}] | {mu:.4f} ({n})")
