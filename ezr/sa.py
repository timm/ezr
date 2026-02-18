from math import exp
import random
choice,choices,rand = random.choice, random.choices, random.random
from ez1 import nearest,disty,gauss,pick,csv,short,Sym,Col,Any

def sa(d:Data, b=4000, m=0.5) -> Row:
  def mutate(c:Col, v:Any) -> Any:
    if isa(c,Sym): return pick(c)
    lo, hi = c[0], c[-1]
    x = gauss(v if v != "?" else mid(c), sd(c))
    return lo + (x - lo) % (hi - lo + 1E-32)

  def score(r):
    near = nearest(d, r, d.rows)
    for i in d.cols.y: r[i] = near[i]
    return disty(d, r)

  s = choice(d.rows)[:]
  best, best_e = s[:], score(s)
  e = best_e
  for h in range(b):
    sn, xs = s[:], list(d.cols.x)
    for i in choices(xs, k=max(1, int(m * len(xs)))):
      sn[i] = mutate(d.cols.x[i], sn[i])
    if (en := score(sn)) < e or rand() < exp((e - en) / (1 - h/b)):
      s, e = sn, en
      if en < best_e:
        best, best_e = s[:], en
        yield h,best

if __name__ == "__main__":
  seed, file = sys.argv[1:]
  random.seed(cast(seed))
  d0 = Data(csv(file))
  d1 = ok(Data([d0.cols.names] + shuffle(d0.rows)[:50]))
  for h,row in sa(d1):
    print(h,[short(v) for v in row])
