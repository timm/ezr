def acquire(data, rows, score, a=20, budget=50):
  scores = {}
  def score(row):
    k = id(row)
    if k not in scores: scores[k] = score(row)
    return scores[k]

  random.shuffle(rows)
  half = len(rows) // 2
  train, holdout = rows[:half], rows[half:]
  warmStart = sorted(train[:a], key=Score)
  best = clone(data, warmStart[:a//2])
  rest = clone(data, warmStart[a//2:])
  maybe = lambda r: dist(data,r,mid(best)) < dist(data,r,mid(rest))
  for row in train[a:]:
    if len(scores) >= budget: break
    if not maybe(row): add(rest, row)
    else:
      if score(row) > score(best.rows[-1]): add(rest, row)
      else:
        add(best, row)
        best.rows.sort(key=score)
        if len(best.rows) > sqrt(len(train)): add(rest,sub(best,best.rows[-1]))
  return maybe, holdout


def label(row): return row

def likely(data, rows, b=50, a=4, stop=512):
  rows = shuffle(rows[:])
  rows, init = rows[a:], sorted(rows[:a], key=lambda row: disty(data, row))
  xy = clone(data, init)
  best, rest = clone(data, init[:a//2]), clone(data, init[a//2:])
  maybe = lambda row: likes(best,row,xy.n,2) > likes(rest,row,xy.n,2)
  while len(rows) > 2 and xy.n < b:
    for i, row in enumerate(rows[:stop]):
      if maybe(row): break
    add(xy, add(best, label(rows.pop(i))))
    if best.n > sqrt(xy.n)
      best.rows.sort(key=lambda row:disty(xy,row))
      add(rest, sub(best, best.rows[-1]))
  return maybe

