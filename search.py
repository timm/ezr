#!/usr/bin/env python3 -B
"""search.py: simulated annealing, local search, differential evolution."""
from ezr import *

def last(gen) -> Any:
  """Final value from generator."""
  v = None
  for v in gen: pass
  return v

def oracleNearest(data, row):
  """Score: copy y-vals from nearest known row."""
  near = nearest(data, row)
  for col in data.cols.ys:
    row[col.at] = near[col.at]
  return disty(data, row)

def oneplus1(data, mutate, accept, oracle, budget=1000, restart=0):
  """(1+1) search: mutate, score, accept."""
  h, best, best_e = 0, None, 1E32
  s, e, imp = choice(data.rows)[:], 1E32, 0
  while h < budget:
    for sn in mutate(s):
      h += 1
      en = oracle(sn)
      if accept(e, en, h, budget):
        s, e = sn, en
      if en < best_e:
        best, best_e, imp = sn[:], en, h
        yield h, best_e, best
      if restart and h - imp > restart:
        s = choice(data.rows)[:]
        e, imp = 1E32, h
        break

def sa(d, oracle, restarts=0, m=0.5, budget=1000):
  """Simulated annealing."""
  n = max(1, int(m * len(d.cols.xs)))
  def accept(e, en, h, b):
    return en < e or rand() < exp((e - en) / (1 - h/b + 1E-32))
  def mutate(s): yield picks(d, s, n)
  return oneplus1(d, mutate, accept, oracle, budget, restarts)

def ls(d, oracle, restarts=100, p=0.5, tries=20, budget=1000):
  """Local search."""
  def accept(e, en, *_): return en < e
  def mutate(s):
    c = choice(d.cols.xs)
    for _ in range(tries if rand() < p else 1):
      s = s[:]
      s[c.at] = pick(c, s[c.at])
      yield s
  return oneplus1(d, mutate, accept, oracle, budget, restarts)

def de(data, oracle, budget=1000, NP=30, F=0.5):
  """Differential evolution (DE/rand/1). Population NP, blend F.
  Yields (evals, best_energy, best_row) on each improvement."""
  pop = [r[:] for r in sample(data.rows, min(NP, len(data.rows)))]
  es  = [oracle(r) for r in pop]
  h   = len(pop)
  best_i = min(range(len(pop)), key=lambda j: es[j])
  yield h, es[best_i], pop[best_i][:]
  while h < budget:
    for i in range(len(pop)):
      if h >= budget: break
      a_i, b_i, c_i = sample([j for j in range(len(pop)) if j != i], 3)
      trial = extrapolate(data.cols.xs, pop[a_i], pop[b_i], pop[c_i], F)
      en = oracle(trial); h += 1
      if en < es[i]:
        pop[i], es[i] = trial, en
        if en < es[best_i]:
          best_i = i
          yield h, en, trial[:]

def cli(argv):
  """ezr search {sa|ls|de} FILE — run search and report final energy."""
  if len(argv) < 2:
    print("usage: ezr search {sa|ls|de} FILE"); return
  algo, file = argv[0], argv[1]
  d0 = Data(csv(file))
  shuffle(d0.rows)
  known = clone(d0, d0.rows[:50])
  search = clone(d0, d0.rows[50:])
  oracle = lambda r: oracleNearest(known, r)
  fns = {"sa": lambda: sa(search, oracle, restarts=100),
         "ls": lambda: ls(search, oracle),
         "de": lambda: de(search, oracle)}
  if algo not in fns: print(f"unknown: {algo}"); return
  print(f"{'evals':>6} {'energy':>7}")
  for h, e, _ in fns[algo]():
    print(f"  {h:4}   {o(e):>5}")

if __name__ == "__main__":
  cli(sys.argv[1:])
