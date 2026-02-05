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
  best      = clone(data, warmStart[:a//2])
  rest      = clone(data, warmStart[a//2:])
  train     = shuffle(train[a:]
  for r,row in enumerate(train):
    if len(best.rows) + len(rest.rows) > budget: break
    if distx(data,train[r],mid(best)) < distx(data,train[r],mid(rest)): 
      add(best, train.pop(r))
    if len(best.rows) > sqrt(r): 
      best.rows.sort(key=score)
      add(rest, sub(best, best.rows[-1]))
  return maybe, holdout
